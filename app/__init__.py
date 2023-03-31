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


from flask import Flask
from app.blueprints import blueprints
from app.database import before_request, teardown_request, tables_create


def app_create():
    tables_create()

    app = Flask(__name__)
    [app.register_blueprint(blueprint) for blueprint in blueprints]
    app.before_request(before_request)
    app.teardown_request(teardown_request)
    return app
