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
#
# -*- coding: utf-8 -*-
import logging
from json import dump
from os.path import dirname, join

from googleapiclient.discovery import build

from easygoogle.config.full_api_dict import get_all_apis, build_api_dict

logger = logging.getLogger(__name__)


def legacy_config():
    discovery = build(
        'discovery',
        'v1',
        cache_discovery=False,
    )
    api_list = get_all_apis(discovery)

    apis = build_api_dict(discovery, api_list)

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
    legacy_config()


if __name__ == "__main__":
    main()
