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


from configparser import ConfigParser


config = ConfigParser()
config.read('config.ini')

config_db = config['database']
config_cryptography = config['cryptography']

DB_HOST = config_db.get('host')
DB_PORT = config_db.getint('port')
DB_USER = config_db.get('user')
DB_PASSWORD = config_db.get('password')
SALT_PASSWORDS = config_cryptography.get('salt_passwords')
SALT_TOKENS = config_cryptography.get('salt_tokens')
