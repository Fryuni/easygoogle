# Copyright 2017 Luiz Augusto Alves Ferraz
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

import logging
from json import dump
from os.path import dirname, join

import googleapiclient.discovery
import progressbar

progressbar.streams.wrap_stderr()

logger = logging.getLogger(__name__)


# Configure valid apis and scopes from Google Discovery Documentation
def config(progress=False):  # pragma: no cover
    discoveryapi = googleapiclient.discovery.build(
        'discovery',
        'v1',
        cache_discovery=False,
    )
    apisres = discoveryapi.apis()
    allapis = apisres.list(
        fields='items(name,title,version,preferred)'
    ).execute()
    apis = dict()

    if progress:
        iterator = progressbar.progressbar(
            allapis['items'], prefix="Looking up APIs",
            redirect_stdout=True, redirect_stderr=True,
        )
    else:
        iterator = allapis['items']

    for api in iterator:
        try:
            apiinfo = apisres.getRest(api=api['name'], version=api['version'],
                                      fields='auth').execute()
        except Exception as e:
            logger.warning(
                "Could not acquire openapi document for api '%s' version '%s'",
                api['name'], api['version']
            )

        if 'auth' not in apiinfo:
            continue

        for scope in apiinfo['auth']['oauth2']['scopes'].keys():
            name = scope.strip('/').split('/')[-1]

            logger.info("Configuring scope \"%s\" for \"%s\"...",
                        name, api['title'])

            # If scope already registered, link to new API
            if name in apis:
                apis[name]['apis'].append(api)

                # Else, register scope and link to API
            else:
                apis[name] = {'apis': [api], 'scope': scope}

    # Save result configuration to json save file
    with open(join(dirname(__file__), 'apis.json'), 'w') as fl:
        dump(apis, fl)

        return apis


def main():
    # Instantiate basic logging
    logging.basicConfig(
        level=logging.INFO,
        format="[%(name)-20s][%(levelname)-8s]:%(asctime)s: %(message)s",
    )

    # Start configuration
    config(True)


if __name__ == "__main__":
    main()
