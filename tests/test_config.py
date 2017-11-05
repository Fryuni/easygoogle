import json
import os

import easygoogle.config

__path__ = os.path.dirname(os.path.abspath(__file__))

MOCK_API_PAGE = os.path.join(__path__, 'data', 'apipage.html')
MOCK_SCOPE_PAGE = os.path.join(__path__, 'data', 'scopepage.html')
CONFIG_RESULT = os.path.join(__path__, 'data', 'apis.json')


def test_api_configuration():
    configurate = easygoogle.config.setapiinfo(
        ('First test API', 'api_name_1', 'api_name_1.v1'), 'https://googlescopes/api_name_1.scope.exemple')

    assert configurate == {
        'apis': [{
            'name': 'api_name_1',
            'version': 'api_name_1.v1'
        }],
        'scope': "https://googlescopes/api_name_1.scope.exemple"
    }


def test_multiple_api_configuration():
    compare = {
        'scope': "https://googlescopes/apis.scope.exemple",
        'apis': []
    }
    for i in range(1, 4):
        configurate = easygoogle.config.setapiinfo(
            ('%s# test API' % i, 'api_name_%s' % i, 'api_name_%s.v1' % i), 'https://googlescopes/apis.scope.exemple')

        compare['apis'].append({
            'name': 'api_name_%s' % i,
            'version': 'api_name_%s.v1' % i
        })
        assert configurate == compare


def mock_url_request_builder(url, **kwargs):
    if url == "https://developers.google.com/api-client-library/python/apis/":
        return "API"
    elif url == "https://developers.google.com/identity/protocols/googlescopes":
        return "SCOPE"


class mock_url_urlopen:
    def __init__(self, target):
        if target == "API":
            self._src = open(MOCK_API_PAGE, 'rb')
        elif target == "SCOPE":
            self._src = open(MOCK_SCOPE_PAGE, 'rb')
        self._length = len(self._src.read())
        self._src.seek(0)

    @property
    def length(self):
        return self._length

    def read(self, *args, **kwargs):
        res = self._src.read(*args, **kwargs)
        self._length -= len(res)
        return res

    def readline(self, *args, **kwargs):
        res = self._src.readline(*args, **kwargs)
        self._length -= len(res)
        return res


def test_full_apis_configuration(mocker):
    open_mock = mocker.mock_open()
    mocker.patch('easygoogle.config.open', open_mock, create=True)
    pickle_dump = mocker.patch('easygoogle.config.dump')

    mocker.patch('easygoogle.config.req', side_effect=mock_url_request_builder)
    mocker.patch('easygoogle.config.uopen', side_effect=mock_url_urlopen)

    apis = easygoogle.config.config()

    EXPECTED_APIS = json.load(open(CONFIG_RESULT))

    assert apis == EXPECTED_APIS
    pickle_dump.assert_called_once_with(EXPECTED_APIS, open_mock())
