#
# (c) 2023, Yegor Yakubovich
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from json import loads

from flask import request

from app.database.account import AccountSession, AccountSessionDevice
from app.database.pay import Wallet, System, Currency
from app.functions.data_output import data_output, ResponseStatus


def device_get(account_session=None):
    name = request.headers.get('User-Agent')
    ip_4 = request.remote_addr
    account_session_device = AccountSessionDevice.get_or_none(
        (AccountSessionDevice.name == name) &
        (AccountSessionDevice.ip_4 == ip_4)
    )
    if not account_session:
        return name, ip_4
    if not account_session_device:
        account_session_device = AccountSessionDevice(
            account_session=account_session,
            name=name,
            ip_4=ip_4,
        )
        account_session_device.save()
    return account_session


def data_input(schema: dict):
    def wrapper(function):
        def validator(*args):
            data = {}

            if request.is_json:
                for key, value in request.json.items():
                    if key not in schema.keys():
                        continue

                    requirements = schema[key]

                    # Request requires an account
                    if key == 'account_session_token':
                        account_session = AccountSession.get_or_none(AccountSession.token == value)
                        if not account_session:
                            return data_output(
                                status=ResponseStatus.error,
                                message='Token does not exist',
                            )
                        account_session: AccountSession
                        if account_session.closed:
                            return data_output(
                                status=ResponseStatus.error,
                                message='Token expired',
                            )

                        account = account_session.account
                        account.device = device_get(account_session=account_session)
                        account.account_session = account_session

                        for requirement_type, requirement_value in requirements.items():
                            if requirement_type == 'account' and requirement_value == True:
                                data['account'] = account
                            if requirement_type == 'wallet' and requirement_value == True:
                                wallet = Wallet.get_or_none(Wallet.account_id == account.id)
                                if not wallet:
                                    return data_output(
                                        status=ResponseStatus.error,
                                        message='Wallet not created for this account',
                                    )
                                wallet.account_session = account_session
                                data['wallet'] = wallet

                    if key == 'currency':
                        currency = Currency.get_or_none(Currency.name == value)
                        if not currency:
                            return data_output(
                                status=ResponseStatus.error,
                                message='{key} must be from the list {currencies}'.format(
                                    key=key,
                                    currencies=[currency.name for currency in Currency.select()],
                                ),
                            )
                        value = currency

                    # Validation data
                    for requirement_type, requirement_value in requirements.items():
                        if requirement_type == 'type' and requirement_value == 'string':
                            if type(value) != str:
                                return data_output(
                                    status=ResponseStatus.error,
                                    message='Key {key} must match the type {key_type}'.format(
                                        key=key,
                                        key_type=requirement_value,
                                    ),
                                )
                        if requirement_type == 'type' and requirement_value == 'integer':
                            if not str(value).isdigit():
                                return data_output(
                                    status=ResponseStatus.error,
                                    message='Key {key} must match the type {key_type}'.format(
                                        key=key,
                                        key_type=requirement_value,
                                    ),
                                )
                            value = int(value)
                        if requirement_type == 'type' and requirement_value == 'dictionary':
                            try:
                                value = loads(value)
                            except TypeError:
                                return data_output(
                                    status=ResponseStatus.error,
                                    message='Key {key} must match the type {key_type}'.format(
                                        key=key,
                                        key_type=requirement_value,
                                    ),
                                )
                        if requirement_type == 'type' and requirement_value == 'boolean':
                            if type(value) != bool:
                                return data_output(
                                    status=ResponseStatus.error,
                                    message='Key {key} must match the type {key_type}'.format(
                                        key=key,
                                        key_type=requirement_value,
                                    ),
                                )
                        if requirement_type == 'length_min':
                            if len(value) < requirement_value:
                                return data_output(
                                    status=ResponseStatus.error,
                                    message='Key length {key} be at least {requirement_value} characters. '
                                            'Your length: {length}'.format(
                                        key=key,
                                        requirement_value=requirement_value,
                                        length=len(value),
                                    ),
                                )
                        if requirement_type == 'length_max':
                            if len(value) > requirement_value:
                                return data_output(
                                    status=ResponseStatus.error,
                                    message='Key length {key} must be no more than '
                                            '{requirement_value} characters. Your length: {length}'.format(
                                        key=key,
                                        requirement_value=requirement_value,
                                        length=len(value),
                                    ),
                                )
                        if requirement_type == 'characters_allowed':
                            for character in value:
                                if character not in requirement_value:
                                    return data_output(
                                        status=ResponseStatus.error,
                                        message='{key} must contain only characters {requirement_value}. '
                                                'Forbidden symbol used: {character}'.format(
                                            key=key,
                                            requirement_value=requirement_value,
                                            character=character,
                                        ),
                                    )
                        if requirement_type == 'value_in':
                            if requirement_value == 'systems':
                                requirement_value = [
                                    system.name for system in System.select()
                                ]
                            if value not in requirement_value:
                                return data_output(
                                    status=ResponseStatus.error,
                                    message='{key} must be from the list {requirement_value}'.format(
                                        key=key,
                                        requirement_value=requirement_value,
                                    ),
                                )

                    data[key] = value

            for key, requirements in schema.items():
                if key not in data.keys():
                    if 'optional' in requirements.keys():
                        continue
                    return data_output(
                        status=ResponseStatus.error,
                        message='Missing key {key}'.format(
                            key=key,
                        )
                    )

            data.pop('account_session_token', None)

            return function(*args, **data)

        return validator

    return wrapper
