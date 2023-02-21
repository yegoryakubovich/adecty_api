#
# (c) 2022, Yegor Yakubovich
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
from json import dumps, loads

from flask import Blueprint

from app.database.pay import Wallet
from app.database.pay.models import OfferType, System, Offer, OfferActions, WalletActions
from app.web.functions.data_input import data_input
from app.web.functions.data_output import data_output, ResponseStatus


blueprint_pay_wallet_offer = Blueprint('blueprint_pay_wallet_offer', __name__, url_prefix='/wallet/offer')


@blueprint_pay_wallet_offer.route('/create', endpoint='pay_wallet_offer_create', methods=('GET',))
@data_input(schema={
    'account_session_token': {'wallet': True},
    'offer_type': {'value_in': [OfferType.input, OfferType.output]},
    'system_name': {'value_in': 'systems'},
    'system_data': {'type': 'dictionary'},
    'value_from': {'type': 'integer'},
    'value_to': {'type': 'integer'},
    'rate': {'type': 'integer'},
})
def pay_wallet_offer_create(wallet: Wallet, offer_type: str, system_name: str, system_data: dict,
                            value_from: int, value_to: int, rate: int):
    if value_from < 1000 or value_to > 10000000:
        return data_output(
            status=ResponseStatus.error,
            message='value_from must not be less than 1000 and value_to must be greater than 10000000',
        )
    if wallet.balance < value_to:
        return data_output(
            status=ResponseStatus.error,
            message='The amount in your wallet must be greater than or equal to {value_to}. '
                    'We will freeze this amount and return it when you cancel the offer '
                    'to be sure that you are not a scammer. Your balance: {wallet_balance}'.format(
                value_to=value_to,
                wallet_balance=wallet.balance,
            ),
        )

    system = System.get(System.name == system_name)
    system_data_required = loads(system.data)
    for key in system_data_required.keys():
        if key not in system_data.keys():
            return data_output(
                status=ResponseStatus.error,
                message='system_data must include the key {key}'.format(key=key),
            )

    offer = Offer(
        wallet=wallet,
        type=offer_type,
        system=system,
        system_data=dumps(system_data),
        value_from=value_from,
        value_to=value_to,
        rate=rate,
        updated_datetime=datetime.now(timezone.utc),
    )
    offer.save()

    offer.account_session = wallet.account_session

    offer.action_create(
        action=OfferActions.create,
    )
    offer.action_create(
        action=OfferActions.update,
        data={
            'system_data': system_data,
            'rate': offer.rate,
            'active': offer.active,
        },
    )
    wallet.action_create(
        action=WalletActions.offer_create,
        data={
            'offer_id': offer.id,
        },
    )

    wallet.balance -= value_to
    wallet.balance_frozen += value_to
    wallet.save()

    wallet.action_create(
        action=WalletActions.balance_frozen,
        data={
            'reason': WalletActions.offer_create,
            'offer_id': offer.id,
            'balance_before': wallet.balance + value_to,
            'balance_frozen_before': wallet.balance_frozen - value_to,
            'frozen': value_to,
            'balance': wallet.balance,
            'balance_frozen': wallet.balance_frozen,
        },
    )

    return data_output(
        status=ResponseStatus.successful,
    )


@blueprint_pay_wallet_offer.route('/get', endpoint='pay_wallet_offer_get', methods=('GET',))
@data_input(schema={
    'account_session_token': {'wallet': True},
    'offer_id': {'type': 'integer'},
    'system_data': {'type': 'dictionary', 'optional': True},
    'rate': {'type': 'integer', 'optional': True},
    'active': {'type': 'boolean', 'optional': True},
})
def pay_wallet_offer_get(wallet: Wallet, offer_id: int):
    offer = Offer.get_or_none((Offer.wallet == wallet) &
                              (Offer.id == offer_id) &
                              (Offer.deleted == False))
    if not offer:
        return data_output(
            status=ResponseStatus.error,
            message='This offer does not exist',
        )

    return data_output(
        status=ResponseStatus.successful,
        offer={
            'id': offer.id,
            'type': offer.type,
            'system': {
                'currency': {
                    'name': offer.system.currency.name,
                    'description': offer.system.currency.description,
                },
                'name': offer.system.name,
                'description': offer.system.description,
            },
            'value_from': offer.value_from,
            'value_to': offer.value_to,
            'rate': offer.rate,
            'updated_datetime': offer.updated_datetime,
            'active': offer.active,
        }
    )


@blueprint_pay_wallet_offer.route('/update', endpoint='pay_wallet_offer_update', methods=('GET',))
@data_input(schema={
    'account_session_token': {'wallet': True},
    'offer_id': {'type': 'integer'},
    'system_data': {'type': 'dictionary', 'optional': True},
    'rate': {'type': 'integer', 'optional': True},
    'active': {'type': 'boolean', 'optional': True},
})
def pay_wallet_offer_update(wallet: Wallet, offer_id: int,
                            system_data: dict = None, rate: int = None, active: bool = None):
    offer = Offer.get_or_none((Offer.wallet == wallet) &
                              (Offer.id == offer_id) &
                              (Offer.deleted == False))
    if not offer:
        return data_output(
            status=ResponseStatus.error,
            message='This offer does not exist',
        )

    offer.system_data = offer.system_data if system_data is None else system_data
    offer.rate = offer.rate if rate is None else rate
    offer.active = offer.active if active is None else active
    offer.updated_datetime = datetime.now(timezone.utc)
    offer.save()

    offer.account_session = wallet.account_session

    offer.action_create(
        action=OfferActions.update,
        data={
            'system_data': offer.system_data,
            'rate': offer.rate,
            'active': offer.active,
        },
    )

    return data_output(
        status=ResponseStatus.successful,
    )


@blueprint_pay_wallet_offer.route('/delete', endpoint='pay_wallet_offer_delete', methods=('GET',))
@data_input(schema={
    'account_session_token': {'wallet': True},
    'offer_id': {'type': 'integer'},
})
def pay_wallet_offer_delete(wallet: Wallet, offer_id: int):
    offer = Offer.get_or_none((Offer.wallet == wallet) &
                              (Offer.id == offer_id) &
                              (Offer.deleted == False))
    if not offer:
        return data_output(
            status=ResponseStatus.error,
            message='This offer does not exist',
        )

    offer.deleted = True
    offer.updated_datetime = datetime.now(timezone.utc)
    offer.save()

    offer.account_session = wallet.account_session

    offer.action_create(
        action=OfferActions.delete,
    )

    return data_output(
        status=ResponseStatus.successful,
    )
