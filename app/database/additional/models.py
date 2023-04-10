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
    database='adecty_additional',
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    charset='utf8mb4',
    autoconnect=False,
)


class DataType:
    account_create = 'account_create'
    account_token_create = 'account_token_create'
    pay_wallet_create = 'pay_wallet_create'
    pay_wallet_delete = 'pay_wallet_delete'


class BaseModel(Model):
    class Meta:
        database = database_account


class DataTemplate(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=64, unique=True)
    description = CharField(max_length=512)
    type = CharField(max_length=32)

    class Meta:
        db_table = 'data_templates'


class DataTemplateParameter(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=64, unique=True)
    description = CharField(max_length=512)
    type = CharField(max_length=32)

    class Meta:
        db_table = 'data_templates_parameters'
