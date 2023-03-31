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
from hashlib import pbkdf2_hmac
from json import dumps
from secrets import token_hex

from peewee import MySQLDatabase, Model, PrimaryKeyField, CharField, DateTimeField, ForeignKeyField, BooleanField

from config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, SALT_PASSWORDS


database_account = MySQLDatabase(
    database='adecty_account',
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    charset='utf8mb4',
    autoconnect=False,
)


def password_hash(password: str):
    password = pbkdf2_hmac(
        hash_name='sha256',
        password=password.encode('utf-8'),
        salt=SALT_PASSWORDS.encode('utf-8'),
        iterations=131072
    ).hex()
    return password


def token_create():
    return token_hex(32)


class AccountActions:
    account_create = 'account_create'
    account_token_create = 'account_token_create'
    pay_wallet_create = 'pay_wallet_create'
    pay_wallet_delete = 'pay_wallet_delete'


class BaseModel(Model):
    class Meta:
        database = database_account


class Account(BaseModel):
    id = PrimaryKeyField()
    username = CharField(max_length=32, unique=True)
    password = CharField(max_length=64)

    def password_check(self, password):
        if password_hash(password) == self.password:
            return True
        else:
            return False

    def action_create(self, action: str, data=None):

        account_session = self.account_session if hasattr(self, 'account_session') else None

        account_action = AccountAction(
            account=self,
            account_session=account_session,
            action=action,
            data=dumps(data if data else {}),
            datetime=datetime.now(timezone.utc)
        )
        account_action.save()

    class Meta:
        db_table = 'accounts'


class AccountSession(BaseModel):
    id = PrimaryKeyField()
    account = ForeignKeyField(Account, to_field='id')
    token = CharField(max_length=256)
    closed = BooleanField(default=False)

    class Meta:
        db_table = 'accounts_sessions'


class AccountSessionDevice(BaseModel):
    id = PrimaryKeyField()
    account_session = ForeignKeyField(AccountSession, to_field='id')
    name = CharField(max_length=256)
    ip_4 = CharField(max_length=15)

    class Meta:
        db_table = 'accounts_sessions_devices'


class AccountAction(BaseModel):
    id = PrimaryKeyField()
    account = ForeignKeyField(Account, to_field='id')
    account_session = ForeignKeyField(AccountSession, to_field='id', null=True, default=None)
    action = CharField(max_length=256)
    data = CharField(max_length=1024)
    datetime = DateTimeField()

    class Meta:
        db_table = 'accounts_actions'
