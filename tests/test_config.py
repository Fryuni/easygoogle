import os

import easygoogle.config


def test_api_configuration():
    configurate = easygoogle.config.setapiinfo(
        ('First test API', 'api_name_1', 'api_name_1.v1'), 'https://googlescopes/api_name_1.scope.exemple')
    assert 'apis' in configurate
    assert 'scope' in configurate

    assert isinstance(configurate['apis'], list)
    assert len(configurate['apis']) == 1
    assert configurate['apis'][0]['name'] == 'api_name_1'
    assert configurate['apis'][0]['version'] == 'api_name_1.v1'

    assert configurate['scope'] == "https://googlescopes/api_name_1.scope.exemple"


def test_multiple_api_configuration():
    for i in range(1, 4):
        configurate = easygoogle.config.setapiinfo(
            ('%s# test API' % i, 'api_name_%s' % i, 'api_name_%s.v1' % i), 'https://googlescopes/apis.scope.exemple')
        assert 'apis' in configurate
        assert 'scope' in configurate

        assert isinstance(configurate['apis'], list)
        assert len(configurate['apis']) == i
        assert configurate['apis'][-1]['name'] == 'api_name_%s' % i
        assert configurate['apis'][-1]['version'] == 'api_name_%s.v1' % i

        assert configurate['scope'] == "https://googlescopes/apis.scope.exemple"


def test_full_apis_configuration():
    apis = easygoogle.config.config(test_mode=True)

    for k, v in apis.items():
        assert 'apis' in v
        assert 'scope' in v
        assert isinstance(v['apis'], list)
        assert len(v['apis']) > 0
        for api in v['apis']:
            assert 'name' in api
            assert 'version' in api

        assert bool(v['scope'])
