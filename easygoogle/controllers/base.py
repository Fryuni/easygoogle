# -*- coding: utf-8 -*-

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
import abc
import logging
import os

from googleapiclient.discovery import build
import six

from ..config import load_api_dict

try:
    # Try to import appengine memcache as the default cache option
    from google.appengine.api import memcache as DEFAULT_CACHE
except ImportError:
    from cachetools import LFUCache as DEFAULT_CACHE

    DEFAULT_CACHE = DEFAULT_CACHE(20)

logger = logging.getLogger(__name__)

registeredApis = {}
if os.path.isfile(os.path.join(os.path.dirname(__file__), 'apis.json')):
    registeredApis = load_api_dict()


@six.add_metaclass(abc.ABCMeta)
class _api_builder(object):
    # Base class, loads API information and build the connectors with the credentials

    # Internal function to load all avaiable APIs based on the scopes
    def _loadApiNames(self, scopes):
        # Create a new dictionary to hold the information
        apiset = dict()

        # Iterates through every unique scopes
        for x in list(set(scopes)):
            try:
                # Load scope relations descriptor
                apiset[x] = registeredApis[x]
            except KeyError:
                # Log when scope not found
                logger.warning("[!] SCOPE %s not registered" % x)
            else:
                # On success log the unlocked APIs
                logger.debug("Loaded auth: %s --> api: %s" % (x, ', '.join(
                    ("%s, %s" % (a['name'], a['version'])
                     for a in apiset[x]['apis']))))
        logger.info("Apis imported")

        # Save the raw apiset
        self.apis = apiset
        # Instantiated a new dictionary create usable control
        self.valid_apis = dict()

        # Iterates through every scope descriptor unlocked
        for a in self.apis.values():

            # Iterates through all APIs described in the scope relations descriptor
            for b in a['apis']:
                # Process suffix when there are subidentifier in version
                suffix = b['version'].split('_v')
                suffix = "_" + suffix[0] if len(suffix) > 1 else ""
                api_tag = b['name'] + suffix
                if api_tag in self.valid_apis:
                    if b['preferred']:
                        self.valid_apis[api_tag][1].insert(0, b['version'])
                    else:
                        self.valid_apis[api_tag][1].append(b['version'])
                else:
                    self.valid_apis[api_tag] = (b['name'], [b['version']])

    def __call__(self, api, version=None, cache=None):
        return self.get_api(api, version)

    # Function to build connector based on API identifiers
    def get_api(self, api, version=None, cache=None):

        if cache is None:
            cache = DEFAULT_CACHE

        # Build connector if API identifier is valid
        if api in self.valid_apis:
            if version is None:
                version = self.valid_apis[api][1][-1]
            res = build(
                self.valid_apis[api][0],
                version,
                credentials=self._credentials,
                cache_discovery=cache is not None,
                cache=cache,
            )
            logger.info("%s API Generated" % api)
            return res
        else:
            logger.warning("%s is not a valid API" % api)
            raise ValueError("Invalid API identifier")
