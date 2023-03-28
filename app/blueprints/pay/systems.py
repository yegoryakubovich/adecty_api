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
from app.database.pay.models import WalletActions, WalletAction, Offer, Currency, System
from app.functions.data_input import data_input
from app.functions.data_output import data_output, ResponseStatus


blueprint_pay_systems = Blueprint('blueprint_pay_systems', __name__, url_prefix='/systems')


@blueprint_pay_systems.route('/get', endpoint='pay_systems_get', methods=('GET',))
@data_input(schema={
    'currency': {},
})
def pay_systems_get(currency: Currency):
    systems = [
        {
            'name': system.name,
            'description': system.description,
            'data': loads(system.data),
        } for system in System.select().where(System.currency == currency)
    ]

    return data_output(
        status=ResponseStatus.successful,
        systems=systems,
    )
