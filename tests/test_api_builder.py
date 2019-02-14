#  Copyright 2017-2018 Luiz Augusto Alves Ferraz
#  .
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#  .
#      http://www.apache.org/licenses/LICENSE-2.0
#  .
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import json
import os

import easygoogle
import easygoogle.controllers
import easygoogle.controllers.base

__local__ = os.path.dirname(os.path.abspath(__file__))

MOCKED_APIS = json.load(open(os.path.join(__local__, 'data', 'apis.json')))

SCOPES = ['scope.unique', 'scope.multiple']
RESULT_SCOPES = [
    "https://testscopes.exemple.org/auth/scope.multiple",
    "https://testscopes.exemple.org/auth/scope.unique"
]


class mock_class(easygoogle.controllers.base._api_builder):
    def __init__(self, scopes):
        self._loadApiNames(scopes)
        self._credentials = None


def test_api_loading(mocker):
    mocker.patch.dict('easygoogle.controllers.base.registeredApis', values=MOCKED_APIS)

    instance = mock_class(['scope.unique', 'scope.multiple', 'scope.invalid'])

    assert instance.valid_apis == {
        'unique_api': ('unique_api', ['v3', 'v1']),
        'shared_api_a': ('shared_api_a', ['v1']),
        'shared_api_b_namedversion': ('shared_api_b', ['namedversion_v1'])
    }


def test_api_generation(mocker):
    mocker.patch.dict('easygoogle.controllers.base.registeredApis', values=MOCKED_APIS)
    mocker.patch('easygoogle.controllers.base.build', autospec=True)
    easygoogle.set_default_cache(mocker.sentinel.CACHE_SERVICE)

    easygoogle.controllers.base.build.return_value = mocker.sentinel.api_build_resource

    instance = mock_class(['scope.unique', 'scope.multiple', 'scope.invalid'])
    instance._credentials = mocker.sentinel.api_build_credentials

    built = instance.get_api('unique_api')

    easygoogle.controllers.base.build.assert_called_once_with(
        'unique_api',
        'v1',
        credentials=mocker.sentinel.api_build_credentials,
        cache_discovery=True,
        cache=mocker.sentinel.CACHE_SERVICE,
    )

    assert built is mocker.sentinel.api_build_resource

def test_api_generation_with_custom_cache(mocker):
    mocker.patch.dict('easygoogle.controllers.base.registeredApis', values=MOCKED_APIS)
    mocker.patch('easygoogle.controllers.base.build', autospec=True)
    easygoogle.set_default_cache(mocker.sentinel.CACHE_SERVICE_DEFAULT)

    easygoogle.controllers.base.build.return_value = mocker.sentinel.api_build_resource

    instance = mock_class(['scope.unique', 'scope.multiple', 'scope.invalid'])
    instance._credentials = mocker.sentinel.api_build_credentials

    built = instance.get_api('unique_api', cache=mocker.sentinel.CACHE_SERVICE)

    easygoogle.controllers.base.build.assert_called_once_with(
        'unique_api',
        'v1',
        credentials=mocker.sentinel.api_build_credentials,
        cache_discovery=True,
        cache=mocker.sentinel.CACHE_SERVICE,
    )

    assert built is mocker.sentinel.api_build_resource


def test_api_generation_failure(mocker):
    mocker.patch.dict('easygoogle.controllers.base.registeredApis', values=MOCKED_APIS)
    mocker.patch('easygoogle.controllers.base.build')

    easygoogle.controllers.base.build.return_value = mocker.sentinel.api_build_resource

    instance = mock_class(['scope.unique', 'scope.multiple', 'scope.invalid'])
    instance.credentials = mocker.sentinel.api_build_credentials

    try:
        built = instance.get_api('no_api')
    except ValueError as e:
        assert e.args == ("Invalid API identifier",)
