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


from app.database.account import models_account
from app.database.account.models import database_account
from app.database.pay import models_pay
from app.database.pay.models import database_pay


databases = [
    database_account,
    database_pay,
]

models = [
    models_account,
    models_pay,
]


def before_request():
    for db in databases:
        if db.is_closed():
            db.connect()


def teardown_request(arg=None):
    for db in databases:
        if not db.is_closed():
            db.close()


def tables_create():
    before_request()
    for model in models:
        for num, m in enumerate(model):
            model[num].create_table()
    teardown_request()
