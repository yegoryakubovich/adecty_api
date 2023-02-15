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


from asyncio import iscoroutinefunction
from hashlib import pbkdf2_hmac

from peewee import MySQLDatabase, Model, PrimaryKeyField, CharField, DateTimeField, ForeignKeyField, BooleanField

from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, SALT_PASSWORDS


db = MySQLDatabase(DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, charset='utf8mb4',
                   autoconnect=False)


def db_manager(function):
    async def wrapper(self, *args, **kwargs):
        if self.data:
            return None

        if iscoroutinefunction(function):
            return await function(self, *args, **kwargs)
        else:
            return function(self, *args, **kwargs)

    return wrapper


def password_hash(password: str):
    password = pbkdf2_hmac('sha256', password.encode('utf-8'), SALT_PASSWORDS.encode('utf-8'), 100000)
    return password.hex()


class BaseModel(Model):
    class Meta:
        database = db


class Account(BaseModel):
    id = PrimaryKeyField()
    username = CharField(max_length=32, unique=True)
    password = CharField(max_length=64)
    datetime = DateTimeField()

    def password_check(self, password):
        if password_hash(password) == self.password:
            return True
        else:
            return False

    class Meta:
        db_table = 'accounts'


class Session(BaseModel):
    id = PrimaryKeyField()
    account = ForeignKeyField(Account, to_field='id')
    token = CharField(max_length=256)
    datetime = DateTimeField()
    datetime_closed = DateTimeField(null=True, default=None)
    closed = BooleanField(default=False)

    class Meta:
        db_table = 'sessions'


class Action(BaseModel):
    id = PrimaryKeyField()
    session = ForeignKeyField(Session, to_field='id')
    name = CharField(max_length=256)
    datetime = DateTimeField()
