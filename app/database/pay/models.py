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
from json import dumps

from peewee import MySQLDatabase, Model, PrimaryKeyField, CharField, DateTimeField, ForeignKeyField, BooleanField, \
    BigIntegerField, IntegerField

from config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT


database_pay = MySQLDatabase(
    database='adecty_pay',
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    charset='utf8mb4',
)


class WalletActions:
    create = 'create'
    offer_create = 'offer_create'
    balance_frozen = 'balance_frozen'


class OfferActions:
    create = 'create'
    update = 'update'
    delete = 'delete'


class OfferType:
    input = 'input'
    output = 'output'


class BaseModel(Model):
    class Meta:
        database = database_pay


class Currency(BaseModel):
    id = PrimaryKeyField()
    name = CharField(max_length=16)
    description = CharField(max_length=128)
    icon = CharField(max_length=4)
    places_decimal = IntegerField()

    class Meta:
        db_table = 'currencies'


class System(BaseModel):
    id = PrimaryKeyField()
    currency = ForeignKeyField(Currency, to_field='id')
    name = CharField(max_length=16)
    description = CharField(max_length=128)
    data = CharField(max_length=1024)

    class Meta:
        db_table = 'systems'


class Wallet(BaseModel):
    id = PrimaryKeyField()
    account_id = BigIntegerField(null=True)
    company_id = BigIntegerField(null=True)
    balance = BigIntegerField()
    balance_frozen = BigIntegerField()

    def action_create(self, action: str, data=None):
        wallet_action = WalletAction(
            wallet=self,
            account_session_id=self.account_session.id,
            action=action,
            data=dumps(data if data else {}),
            datetime=datetime.now(timezone.utc)
        )
        wallet_action.save()

    class Meta:
        db_table = 'wallets'


class WalletAction(BaseModel):
    id = PrimaryKeyField()
    wallet = ForeignKeyField(Wallet, to_field='id')
    account_session_id = BigIntegerField()
    action = CharField(max_length=256)
    data = CharField(max_length=1024)
    datetime = DateTimeField()

    class Meta:
        db_table = 'wallets_actions'


class Offer(BaseModel):
    id = PrimaryKeyField()
    type = CharField(max_length=16)
    wallet = ForeignKeyField(Wallet, to_field='id')
    system = ForeignKeyField(System, to_field='id')
    system_data = CharField(max_length=1024)
    value_from = BigIntegerField()
    value_to = BigIntegerField()
    rate = BigIntegerField()
    updated_datetime = DateTimeField()
    active = BooleanField(default=False)
    deleted = BooleanField(default=False)

    def action_create(self, action: str, data=None):
        offer_action = OfferAction(
            offer=self,
            account_session_id=self.account_session.id,
            action=action,
            data=dumps(data if data else {}),
            datetime=datetime.now(timezone.utc)
        )
        offer_action.save()

    class Meta:
        db_table = 'offers'


class OfferAction(BaseModel):
    id = PrimaryKeyField()
    offer = ForeignKeyField(Offer, to_field='id')
    account_session_id = BigIntegerField()
    action = CharField(max_length=256)
    data = CharField(max_length=1024)
    datetime = DateTimeField()

    class Meta:
        db_table = 'offers_actions'


class Deal(BaseModel):
    id = PrimaryKeyField()
    wallet = ForeignKeyField(Wallet, to_field='id')
    offer = ForeignKeyField(Offer, to_field='id')
    value = BigIntegerField()
    rate = BigIntegerField()

    class Meta:
        db_table = 'deals_inputs'


class DealAction(BaseModel):
    id = PrimaryKeyField()
    deal = ForeignKeyField(Deal, to_field='id')
    account_session_id = BigIntegerField()
    action = CharField(max_length=256)
    data = CharField(max_length=1024)
    datetime = DateTimeField()

    class Meta:
        db_table = 'deals_actions'
