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

from app.blueprints.pay.currencies import blueprint_pay_currencies
from app.blueprints.pay.systems import blueprint_pay_systems
from app.blueprints.pay.wallet import blueprint_pay_wallet
from app.blueprints.pay.wallet_offer import blueprint_pay_wallet_offer


blueprint_pay = Blueprint('blueprint_pay', __name__, url_prefix='/pay')
blueprints_pay = (blueprint_pay_wallet_offer, blueprint_pay_wallet, blueprint_pay_systems, blueprint_pay_currencies)


[blueprint_pay.register_blueprint(blueprint) for blueprint in blueprints_pay]
