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


from datetime import datetime, timezone

from flask import Blueprint

from app.database.account.models import Account, AccountSession, AccountActions, password_hash, token_create
from app.functions.data_input import data_input, device_get
from app.functions.data_output import data_output, ResponseStatus


blueprint_account = Blueprint('blueprint_account', __name__, url_prefix='/account')


password_charset_allowed = '!#$%&()*+,-./:;<=>?@[\]^_`{|}~' \
                           'ABCDEFGHIJKLMNOPQRSTUVWXYZ' \
                           'abcdefghijklmnopqrstuvwxyz' \
                           '0123456789'
username_charset_allowed = '_-.' \
                           'ABCDEFGHIJKLMNOPQRSTUVWXYZ' \
                           'abcdefghijklmnopqrstuvwxyz' \
                           '0123456789'


@blueprint_account.route('/create', endpoint='account_create', methods=('GET',))
@data_input(schema={
    'username': {'type': 'string', 'length_min': 8, 'length_max': 32, 'characters_allowed': username_charset_allowed},
    'password': {'type': 'string', 'length_min': 8, 'length_max': 64, 'characters_allowed': password_charset_allowed},
})
def account_create(username: str, password: str):
    username = username.lower()

    account = Account.get_or_none(Account.username == username)
    if account:
        return data_output(
            status=ResponseStatus.error,
            message='This username is already taken',
        )
    account = Account(
        username=username,
        password=password_hash(password=password),
        datetime=datetime.now(timezone.utc),
    )
    account.save()

    device_name, device_ip_4 = device_get()

    account.action_create(
        action=AccountActions.account_create,
        data={
            'device_name': device_name,
            'device_ip_4': device_ip_4,
            'account_id': account.id,
            'username': account.username,
        },
    )

    return data_output(
        status=ResponseStatus.successful,
    )


@blueprint_account.route('/get', endpoint='account_get', methods=('GET',))
@data_input(schema={
    'account_session_token': {'account': True},
})
def account_get(account: Account):
    return data_output(
        status=ResponseStatus.successful,
        account_id=account.id,
    )


@blueprint_account.route('/session/create', endpoint='account_session_create', methods=('GET',))
@data_input(schema={
    'username': {'type': 'string', 'length_min': 8, 'length_max': 32, 'characters_allowed': username_charset_allowed},
    'password': {'type': 'string', 'length_min': 8, 'length_max': 64, 'characters_allowed': password_charset_allowed},
})
def account_session_create(username: str, password: str):
    username = username.lower()

    account = Account.get_or_none(Account.username == username)
    if not account:
        return data_output(
            status=ResponseStatus.error,
            message='Account {username} does not exist'.format(
                username=username,
            ),
        )
    if not account.password_check(password=password):
        return data_output(
            status=ResponseStatus.error,
            message='Password is wrong',
        )

    token = token_create()
    account_session = AccountSession(account=account, token=token)
    account_session.save()

    account_session_device = device_get(account_session=account_session)
    account_session_device.save()

    account.account_session = account_session

    account.action_create(
        action=AccountActions.account_token_create,
    )

    return data_output(
        status=ResponseStatus.successful,
        token=token,
    )
