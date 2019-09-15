#  Copyright 2017-2019 Luiz Augusto Alves Ferraz
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
import logging
import os

logger = logging.getLogger(__name__)


def get_all_apis(discovery_api):
    apis_res = discovery_api.apis()
    get_page = apis_res.list(
        fields='items(name,title,version,preferred)',
    )

    if not hasattr(apis_res, 'list_next'):
        return get_page.execute()['items']

    # If Google decides to paginate the global discovery endpoint
    result = []
    while get_page:
        page = get_page.execute()
        result.extend(page.get('items', tuple()))
        get_page = apis_res.list_next(
            previous_request=get_page,
            previous_response=page,
        )
    return result


def build_api_dict(discovery, api_list):
    def parse_rest_definition(api):
        def parser(idp, response, exception):
            if exception:
                logger.warning(
                    "Could not acquire openapi document for api '%s' version '%s'",
                    api['name'], api['version']
                )
                return
            if 'auth' not in response:
                return

            for scope in response['auth']['oauth2']['scopes'].keys():
                name = scope.strip('/').split('/')[-1]

                logger.info("Configuring scope \"%s\" for \"%s\"...",
                            name, api['title'])

                # If scope already registered, link to new API
                if name in apis:
                    apis[name]['apis'].append(api)

                # Else, register scope and link to API
                else:
                    apis[name] = {'apis': [api], 'scope': scope}

        return parser

    apis = {}

    apis_res = discovery.apis()

    for cut in range(0, len(api_list), 50):
        batch = discovery.new_batch_http_request()
        for api_item in api_list[cut:cut + 50]:
            batch.add(
                apis_res.getRest(
                    api=api_item['name'],
                    version=api_item['version'],
                    fields='auth',
                ),
                callback=parse_rest_definition(api_item)
            )
            batch.execute()

    return apis


def load_api_dict():
    file_path = os.path.join(os.path.dirname(__file__), 'apis.json')
    if os.path.isfile(file_path):
        with open(file_path, 'r') as fl:
            return json.load(fl)
    else:
        return {}
