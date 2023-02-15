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


from flask import Blueprint

from app.database.models import db_manager, Account, password_hash
from app.web.functions.data_input import data_input


blueprint_account = Blueprint('blueprint_account', __name__, url_prefix='/account')


password_charset_allowed = '!#$%&()*+,-./:;<=>?@[\]^_`{|}~' \
                           'ABCDEFGHIJKLMNOPQRSTUVWXYZ' \
                           'abcdefghijklmnopqrstuvwxyz' \
                           '0123456789'
username_charset_allowed = '_-.' \
                           'ABCDEFGHIJKLMNOPQRSTUVWXYZ' \
                           'abcdefghijklmnopqrstuvwxyz' \
                           '0123456789'


@db_manager
@blueprint_account.route('/create', methods=('GET', ))
@data_input(schema={
    'username': {'type': 'string', 'length_min': 8, 'length_max': 32, 'characters_allowed': username_charset_allowed},
    'password': {'type': 'string', 'length_min': 8, 'length_max': 64, 'characters_allowed': password_charset_allowed},
})
def account_create(username, password):
    account = Account.get_or_none(Account.username == username)
    if account:
        return 'error, username'

    account = Account(username=username, password=password_hash(password=password))
    account.save()

    return 200


@db_manager
@blueprint_account.route('/session/create', methods=('GET', ))
@data_input(schema={
    'username': {'type': 'string', 'length_min': 8, 'length_max': 32, 'characters_allowed': username_charset_allowed},
    'password': {'type': 'string', 'length_min': 8, 'length_max': 64, 'characters_allowed': password_charset_allowed},
})
def account_session_create():
    return 200
