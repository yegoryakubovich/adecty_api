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


from flask import Blueprint

from app.database.pay.models import Currency
from app.functions.data_input import data_input
from app.functions.data_output import data_output, ResponseStatus


blueprint_pay_currencies = Blueprint('blueprint_pay_currencies', __name__, url_prefix='/currencies')


@blueprint_pay_currencies.route('/get', endpoint='pay_currencies_get', methods=('GET',))
@data_input(schema={})
def pay_currencies_get():
    currencies = [
        {
            'name': currency.name,
            'description': currency.description,
            'icon': currency.icon,
            'places_decimal': currency.places_decimal,
        } for currency in Currency.select()
    ]

    return data_output(
        status=ResponseStatus.successful,
        currencies=currencies,
    )
