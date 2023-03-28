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
# noinspection PyPackageRequirements
from werkzeug.exceptions import InternalServerError

from app.functions.data_output import ResponseStatus, data_output


blueprint_errors = Blueprint('blueprint_errors', __name__)


@blueprint_errors.app_errorhandler(404)
def errors_404(error: InternalServerError):
    return data_output(
        status=ResponseStatus.error,
        message='Method does not exist',
        error=error.description,
    )


@blueprint_errors.app_errorhandler(500)
def errors_500(error: InternalServerError):
    return data_output(
        status=ResponseStatus.error,
        message='An error has occurred on the server side. We have already found it and are solving it right now',
        error=error.description,
    )
