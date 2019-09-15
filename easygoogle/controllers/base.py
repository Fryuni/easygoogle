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
import warnings
from typing import Dict

from cachetools import LFUCache
from google.auth.credentials import Credentials
from googleapiclient.discovery import build

from easygoogle.config.full_api_dict import load_api_dict
from ..errors import UnknownPreferredVersion, UncertainPreferredVersion

logger = logging.getLogger(__name__)

DEFAULT_CACHE = LFUCache(20)


class _ApiBuilder(metaclass=abc.ABCMeta):
    # Base class, loads API information and build the connectors with the credentials

    _preferred_version_cache: Dict[str, str] = {}
    _discovery = None
    _credentials: Credentials

    # Internal function to load all avaiable APIs based on the scopes
    def _loadApiNames(self, scopes):

        warnings.warn(
            message="The api loading method is deprecated and will not work in future versions of easygoogle.",
            category=DeprecationWarning,
        )

        # Create a new dictionary to hold the information
        apiset = dict()

        # Iterates through every unique scopes
        for x in list(set(scopes)):
            try:
                # Load scope relations descriptor
                apiset[x] = _get_registered_apis()[x]
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

        if version is None:
            version = self.get_preferred_version(api)
        res = build(
            api,
            version,
            credentials=self._credentials,
            cache_discovery=cache is not None,
            cache=cache,
        )
        logger.info("%s API Generated" % api)
        return res

    @classmethod
    def get_preferred_version(cls, api):
        if api not in cls._preferred_version_cache:
            discovery = cls.get_discovery()
            apis_res = discovery.apis()
            res = apis_res.list(name=api, preferred=True).execute()
            items = res.get('items', [])
            if len(items) == 0:
                raise UnknownPreferredVersion(api)
            if len(items) > 1:
                raise UncertainPreferredVersion(api)
            cls._preferred_version_cache[api] = items[0]['version']
        return cls._preferred_version_cache[api]

    @classmethod
    def get_discovery(cls):
        if cls._discovery is None:
            cls._discovery = build('discovery', 'v1', cache=DEFAULT_CACHE)
        return cls._discovery


def _get_registered_apis():
    global __registered_apis
    if __registered_apis is None:
        if os.path.isfile(os.path.join(os.path.dirname(__file__), 'apis.json')):
            __registered_apis = load_api_dict()
        else:
            __registered_apis = {}
    return __registered_apis


__registered_apis = None
