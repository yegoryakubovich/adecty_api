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
from json import loads

from flask import Blueprint

from app.database.account import Account
from app.database.account.models import AccountActions
from app.database.pay import Wallet
from app.database.pay.models import WalletActions, WalletAction, OfferType, Offer, System, OfferActions
from app.web.functions.data_input import data_input
from app.web.functions.data_output import data_output, ResponseStatus

blueprint_pay = Blueprint('blueprint_pay', __name__, url_prefix='/pay')


@blueprint_pay.route('/wallet/create', endpoint='pay_wallet_create', methods=('GET',))
@data_input(schema={
    'account_session_token': {'account': True},
})
def pay_wallet_create(account: Account):
    wallet = Wallet.get_or_none(Wallet.account_id == account.id)
    if wallet:
        return data_output(
            status=ResponseStatus.error,
            message='A wallet for this account has already been created',
        )

    wallet = Wallet(
        account_id=account.id,
    )
    wallet.save()
    wallet.account_session = account.account_session

    account.action_create(
        action=AccountActions.pay_wallet_create,
        data={
            'wallet_id': wallet.id,
        },
    )
    wallet.action_create(
        action=WalletActions.create,
    )

    return data_output(
        status=ResponseStatus.successful,
    )


@blueprint_pay.route('/wallet/get', endpoint='pay_wallet_get', methods=('GET',))
@data_input(schema={
    'account_session_token': {'wallet': True},
})
def pay_wallet_get(wallet: Wallet):
    return data_output(
        status=ResponseStatus.successful,
        account_id=wallet.account_id,
        company_id=wallet.company_id,
        balance=wallet.balance,
    )


@blueprint_pay.route('/wallet/actions/get', endpoint='pay_wallet_actions_get', methods=('GET',))
@data_input(schema={
    'account_session_token': {'wallet': True},
    'page': {'type': 'integer'},
})
def pay_wallet_actions_get(wallet: Wallet, page: int):
    wallet_actions = [
        {
            'action': wa.action,
            'data': loads(wa.data),
            'datetime': wa.datetime,
        } for wa in WalletAction.select().where(WalletAction.wallet == wallet).limit(10).offset(10 * page - 10)
    ]
    return data_output(
        status=ResponseStatus.successful,
        page=page,
        wallet_actions=wallet_actions,
    )


@blueprint_pay.route('/offer/create', endpoint='pay_offer_create', methods=('GET',))
@data_input(schema={
    'account_session_token': {'wallet': True},
    'offer_type': {'value_in': [OfferType.input, OfferType.output]},
    'system_name': {'value_in': 'systems'},
    'value_from': {'type': 'integer'},
    'value_to': {'type': 'integer'},
    'rate': {'type': 'integer'},
})
def pay_offer_create(wallet: Wallet, offer_type: str, system_name: str, value_from: int, value_to: int, rate: int):
    if value_from < 1000 or value_to > 10000000:
        return data_output(
            status=ResponseStatus.error,
            message='value_from must not be less than 1000 and value_to must be greater than 10000000',
        )
    if wallet.balance < value_to:
        return data_output(
            status=ResponseStatus.error,
            message=
            'The amount in your wallet must be greater than or equal to {value_to}. '
            'We will freeze this amount and return it when you cancel the offer '
            'to be sure that you are not a scammer. Your balance: {wallet_balance}'.format(
                value_to=value_to,
                wallet_balance=wallet.balance,
            ),
        )

    system = System.get(System.name == system_name)
    print(datetime.now(timezone.utc))
    offer = Offer(
        wallet=wallet,
        type=offer_type,
        system=system,
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
            'rate': rate,
        },
    )
    wallet.action_create(
        action=WalletActions.offer_create,
        data={
            'offer_id': offer.id,
        },
    )

    wallet.balance = wallet.balance - value_to
    wallet.balance_frozen = wallet.balance_frozen + value_to
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
