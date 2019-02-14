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

import easygoogle.controllers.base
import easygoogle.controllers.service_account

__local__ = os.path.dirname(os.path.abspath(__file__))

MOCKED_APIS = json.load(open(os.path.join(__local__, 'data', 'apis.json')))

SCOPES = ['scope.unique', 'scope.multiple']
RESULT_SCOPES = ["https://testscopes.exemple.org/auth/scope.multiple",
                 "https://testscopes.exemple.org/auth/scope.unique"]


def test_inheritance():
    assert issubclass(easygoogle.controllers.service_account.service_acc, easygoogle.controllers.base._api_builder)
    assert issubclass(easygoogle.controllers.service_account._delegated, easygoogle.controllers.base._api_builder)


def test_creation_call(mocker):
    mocker.patch.dict('easygoogle.controllers.base.registeredApis', values=MOCKED_APIS)
    mocked_google_credentials = mocker.patch('easygoogle.controllers.service_account.Credentials', autospec=True)
    mocked_six = mocker.patch('easygoogle.controllers.service_account.six', autospec=True)
    mocked_six.string_types = (type(mocker.sentinel.json_file),)

    test_target = mocked_google_credentials.from_service_account_file

    credentials_mock = mocker.MagicMock()
    test_target.return_value = credentials_mock

    service = easygoogle.controllers.service_account.service_acc(mocker.sentinel.json_file, [])

    test_target.assert_called_once_with(mocker.sentinel.json_file, scopes=[])

    assert service.credentials is credentials_mock

    mocker.stopall()


def test_scoped_creation_call(mocker):
    mocker.patch.dict('easygoogle.controllers.base.registeredApis', values=MOCKED_APIS)
    mocked_google_credentials = mocker.patch('easygoogle.controllers.service_account.Credentials', autospec=True)

    service = easygoogle.controllers.service_account.service_acc(
        'test_secret.json',
        [
            'scope.unique', 'scope.multiple', 'scope.invalid'
        ],
    )

    assert service.domain_wide == True

    test_target = mocked_google_credentials.from_service_account_file

    assert test_target.called
    assert test_target.call_count == 1
    assert test_target.call_args[0][0] is 'test_secret.json'
    assert sorted(test_target.call_args[1]['scopes']) == ["https://testscopes.exemple.org/auth/scope.multiple",
                                                          "https://testscopes.exemple.org/auth/scope.unique"]


def test_delegation(mocker):
    mocker.patch.dict('easygoogle.controllers.base.registeredApis', values=MOCKED_APIS)
    mocked_google_credentials = mocker.patch('easygoogle.controllers.service_account.Credentials', autospec=True)

    mocked_six = mocker.patch('easygoogle.controllers.service_account.six')
    mocked_six.string_types = (type(mocker.sentinel.json_file),)

    credentials_mock = mocker.MagicMock()

    mocked_google_credentials.from_service_account_file.return_value = credentials_mock

    service = easygoogle.controllers.service_account.service_acc(
        mocker.sentinel.json_file,
        scopes=['scope.unique'],
    )

    assert service.domain_wide is True

    delegated = service.delegate(mocker.sentinel.delegated_user)

    credentials_mock.with_subject.assert_called_once_with(
        mocker.sentinel.delegated_user)
    assert delegated.valid_apis == {
        'unique_api': ('unique_api', ['v1'])
    }


def test_delegation_failure(mocker):
    mocker.patch.dict('easygoogle.controllers.base.registeredApis', values=MOCKED_APIS)
    mocked_google_credentials = mocker.patch('easygoogle.controllers.service_account.Credentials', autospec=True)

    # Create mock for credentials
    credentials_mock = mocker.MagicMock()
    mocked_google_credentials.from_service_account_file.return_value = credentials_mock

    service = easygoogle.controllers.service_account.service_acc(
        mocker.sentinel.json_file,
        scopes=[],
        domainWide=False,
    )

    assert service.domain_wide is False

    delegated = service.delegate(mocker.sentinel.delegated_user)
    credentials_mock.with_subject.assert_not_called()
    assert delegated is service
