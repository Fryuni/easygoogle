import json
import os

import easygoogle

__local__ = os.path.dirname(os.path.abspath(__file__))

MOCKED_APIS = json.load(open(os.path.join(__local__, 'data', 'apis.json')))

SCOPES = ['scope.unique', 'scope.multiple']
RESULT_SCOPES = [
    "https://testscopes.exemple.org/auth/scope.multiple",
    "https://testscopes.exemple.org/auth/scope.unique"
]


class mock_class(easygoogle._api_builder):
    def __init__(self, scopes):
        self._loadApiNames(scopes)
        self._credentials = None


def test_api_loading(mocker):
    mocker.patch.dict('easygoogle.registeredApis', values=MOCKED_APIS)

    instance = mock_class(['scope.unique', 'scope.multiple', 'scope.invalid'])

    assert instance.valid_apis == {
        'unique_api': ('unique_api', ['v3', 'v1']),
        'shared_api_a': ('shared_api_a', ['v1']),
        'shared_api_b_namedversion': ('shared_api_b', ['namedversion_v1'])
    }


def test_api_generation(mocker):
    mocker.patch.dict('easygoogle.registeredApis', values=MOCKED_APIS)
    mocker.patch('easygoogle.googleapiclient')

    easygoogle.googleapiclient.discovery.build.return_value = mocker.sentinel.api_build_resource

    instance = mock_class(['scope.unique', 'scope.multiple', 'scope.invalid'])
    instance._credentials = mocker.sentinel.api_build_credentials

    built = instance.get_api('unique_api')

    easygoogle.googleapiclient.discovery.build.assert_called_once_with(
        'unique_api',
        'v1',
        credentials=mocker.sentinel.api_build_credentials,
        cache_discovery=False,
    )

    assert built is mocker.sentinel.api_build_resource


def test_api_generation_failure(mocker):
    mocker.patch.dict('easygoogle.registeredApis', values=MOCKED_APIS)
    mocker.patch('easygoogle.googleapiclient')

    easygoogle.googleapiclient.discovery.build.return_value = mocker.sentinel.api_build_resource

    instance = mock_class(['scope.unique', 'scope.multiple', 'scope.invalid'])
    instance.credentials = mocker.sentinel.api_build_credentials

    try:
        built = instance.get_api('no_api')
    except ValueError as e:
        assert e.args == ("Invalid API identifier", )
