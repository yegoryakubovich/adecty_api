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


from flask import request

from app.web.functions.data_output import data_output, ResponseStatus


def data_input(schema: dict):
    def wrapper(function):

        def validator(*args):
            data = {}
            for key, value in request.json.items():
                if key not in schema.keys():
                    continue

                requirements = schema[key]

                # Validation data
                for requirement_type, requirement_value in requirements.items():
                    if requirement_type == 'string':
                        return data_output(
                            status=ResponseStatus.error,
                            message='Key key must match the type key_type'.format(
                                key=key,
                                key_type=requirement_value,
                            )
                        )
                    if requirement_type == 'length_min':
                        if len(value) < requirement_value:
                            return data_output(
                                status=ResponseStatus.error,
                                message='Key length {key} be at least {requirement_value} characters'.format(
                                    key=key,
                                    requirement_value=requirement_value,
                                )
                            )
                    if requirement_type == 'length_max':
                        if len(value) > requirement_value:
                            return data_output(
                                status=ResponseStatus.error,
                                message='Key length {key} must be no more than {requirement_value} characters'.format(
                                    key=key,
                                    requirement_value=requirement_value,
                                )
                            )
                    if requirement_type == 'characters_allowed':
                        for character in value:
                            if character not in requirement_value:
                                return data_output(
                                    status=ResponseStatus.error,
                                    message=
                                    '{key} must contain only characters {requirement_value}. '
                                    'Forbidden symbol used: {character}'.format(
                                        key=key,
                                        requirement_value=requirement_value,
                                        character=character,
                                    )
                                )

                data[key] = value
            return function(*args, **data)

        return validator
    return wrapper
