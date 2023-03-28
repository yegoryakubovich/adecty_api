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

from flask import Blueprint

from app.database.account import Account
from app.database.account.models import AccountActions
from app.database.pay import Wallet
from app.database.pay.models import WalletActions, WalletAction, Offer
from app.functions.data_input import data_input
from app.functions.data_output import data_output, ResponseStatus


blueprint_pay_wallet = Blueprint('blueprint_pay_wallet', __name__, url_prefix='/wallet')


@blueprint_pay_wallet.route('/create', endpoint='pay_wallet_create', methods=('GET',))
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


@blueprint_pay_wallet.route('/get', endpoint='pay_wallet_get', methods=('GET',))
@data_input(schema={
    'account_session_token': {'wallet': True},
})
def pay_wallet_get(wallet: Wallet):
    return data_output(
        status=ResponseStatus.successful,
        account_id=wallet.account_id,
        company_id=wallet.company_id,
        balance=wallet.balance,
        balance_frozen=wallet.balance_frozen,
    )


@blueprint_pay_wallet.route('/actions/get', endpoint='pay_wallet_actions_get', methods=('GET',))
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


@blueprint_pay_wallet.route('/offers/get', endpoint='pay_wallet_offers_get', methods=('GET',))
@data_input(schema={
    'account_session_token': {'wallet': True},
    'page': {'type': 'integer'},
})
def pay_wallet_offers_get(wallet: Wallet, page: int):
    wallet_offers = [
        {
            'id': wo.id,
            'type': wo.type,
            'system': {
                'currency': {
                    'name': wo.system.currency.name,
                    'description': wo.system.currency.description,
                },
                'name': wo.system.name,
                'description': wo.system.description,
            },
            'value_from': wo.value_from,
            'value_to': wo.value_to,
            'rate': wo.rate,
            'updated_datetime': wo.updated_datetime,
            'active': wo.active,
        } for wo in Offer.select().where((Offer.wallet == wallet) &
                                         (Offer.deleted == False)).limit(10).offset(10 * page - 10)
    ]
    return data_output(
        status=ResponseStatus.successful,
        page=page,
        wallet_offers=wallet_offers,
    )
