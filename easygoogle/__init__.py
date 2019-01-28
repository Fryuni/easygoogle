# -*- coding: utf-8 -*-

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
import logging
import os
from argparse import Namespace

import google.auth.transport.requests
import google.oauth2.credentials
import google.oauth2.service_account
import googleapiclient
import googleapiclient.discovery
import six
from google_auth_oauthlib.flow import InstalledAppFlow

from ._patch_resources import applyPatch
from .config import config as updateApiCache

# Try to import appengine memcache as the default cache option
try:
    from google.appengine.api import memcache as DEFAULT_CACHE
except ImportError:
    from cachetools import LFUCache as DEFAULT_CACHE

    DEFAULT_CACHE = DEFAULT_CACHE(20)

logger = logging.getLogger(__name__)

registeredApis = {}


# Load APIs versions, identifiers and scopes relations
# from json file
def loadApiDict():
    global registeredApis
    with open(os.path.join(os.path.dirname(__file__), 'apis.json'), 'r') as fl:
        registeredApis = json.load(fl)


if not os.environ.get("EASYGOOGLE_NO_AUTO_PATCH_RESOURCES"):
    applyPatch()

if os.path.isfile(os.path.join(os.path.dirname(__file__), 'apis.json')):
    loadApiDict()

AUTH = Namespace(
    CONSOLE='auth-opt-1',
    BROWSER='auth-opt-2',
    SILENT='auth-opt-3',
)
AUTH_OPTS = tuple(AUTH.__dict__.values())


class _CONSTS(object):

    def __setattr__(self, arg, val):
        raise TypeError

    def __delattr__(self, arg):
        raise TypeError

    @property
    def DEFAULT_AUTH_OPT(self):
        return getattr(
            AUTH,
            os.environ.get(
                'EASYGOOGLE_DEFAULT_MODE',
                'BROWSER'
            )
        )

    @property
    def DEFAULT_APP_DIR(self):
        return os.environ.get(
            'EASYGOOGLE_DEFAULT_APP_DIR',
            '.'
        )

    @property
    def DEFAULT_APP_NAME(self):
        return os.environ.get(
            'EASYGOOGLE_DEFAULT_APP_NAME',
            'Google Client Library - Python'
        )

    @property
    def DEFAULT_HOSTNAME(self):
        return os.environ.get(
            'EASYGOOGLE_DEFAULT_HOSTNAME',
            'localhost'
        )

    @property
    def DEFAULT_PORT(self):
        return os.environ.get(
            'EASYGOOGLE_DEFAULT_PORT',
            None
        )

    @property
    def ENFORCE_DEFAULT_OPT(self):
        return os.environ.get('EASYGOOGLE_ENFORCE_AUTH_MODE') == 'ENFORCE'


_CONSTS = _CONSTS()


# Base class, loads API information and build the connectors with the credentials
class _api_builder:

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
            res = googleapiclient.discovery.build(
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


# OAuth2 class
# Handles API connector building, configuration of avaiable API and OAuth2 authentication flow
class oauth2(_api_builder):

    # Main constructor function
    def __init__(self,
                 client_secrets,
                 scopes,
                 appname=_CONSTS.DEFAULT_APP_NAME,
                 user="",
                 app_dir=_CONSTS.DEFAULT_APP_DIR,
                 manualScopes=[],
                 hostname=_CONSTS.DEFAULT_HOSTNAME,
                 port=_CONSTS.DEFAULT_PORT,
                 auth_mode=_CONSTS.DEFAULT_AUTH_OPT):
        assert auth_mode in AUTH_OPTS
        if _CONSTS.ENFORCE_DEFAULT_OPT and auth_mode != _CONSTS.DEFAULT_AUTH_OPT:  # pragma: no cover
            sys.stderr.write('Auth mode is enforced by environment, ignoring argument\n')

        # Load valid APIs unlocked with the scopes
        self._loadApiNames(scopes)

        # Save all scopes results
        self.SCOPES = list(
            set([x['scope'] for x in self.apis.values()] + manualScopes))

        # App information
        home_dir = os.path.abspath(os.path.expanduser(app_dir))

        self.__auth_hostname = hostname
        self.__auth_port = port
        self.__auth_mode = auth_mode

        if client_secrets == None:
            self._credentials, self.projectId = google.auth.default()
        else:
            self.__acquireCredentials(client_secrets, home_dir, appname, user)

    def __acquireCredentials(self, client_secrets, home_dir, appname, user):
        # Path to credentials files directory
        self.credential_dir = os.path.join(home_dir, '.credentials')
        # Create credentials directory if not exists
        if not os.path.isdir(self.credential_dir):
            os.makedirs(self.credential_dir)

        # Save app name
        self.name = appname

        # Construct file name
        self.filename = ''.join(
            e for e in self.name if e.isalnum() or e in ' _-'
        ).lower().replace(
            ' ', '_'
        ) + '#' + user + ".json"

        # Assemble full credential file path
        self.credential_path = os.path.join(self.credential_dir,
                                            self.filename)

        # Load saved credentials if the file exists
        if os.path.isfile(self.credential_path):
            saved_state = self.__loadStateFromFile(self.credential_path)
        else:
            saved_state = None

        if saved_state is None:
            credentials = self.__runAuthenticationFlow(client_secrets)
        else:
            credentials = self.__credentialsFromSavedState(saved_state)
        self._credentials = credentials

    def __loadStateFromFile(self, credential_path):
        saved_state = json.load(open(credential_path))
        saved_scopes = set(saved_state['scopes'])
        cur_scopes = set(self.SCOPES)
        if len(cur_scopes.difference(saved_scopes)) > 0:
            self.scopes = list(saved_scopes.union(cur_scopes))
            saved_state = None
        return saved_state

    def __credentialsFromSavedState(self, saved_state):
        credentials = google.oauth2 \
            .credentials.Credentials(None, **saved_state)
        credentials.refresh(
            google.auth.transport.requests.Request(),
        )
        return credentials

    def __runAuthenticationFlow(self, client_secrets):
        # No valid credentials found
        # Instantiate authrization flow
        if isinstance(client_secrets, six.string_types):
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secrets, scopes=self.SCOPES
            )
        else:
            flow = InstalledAppFlow.from_client_config(
                client_secrets, scopes=self.SCOPES,
            )

        # Start web server to authorize application
        if self.__auth_port is None:
            import socket
            tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp.bind(('', 0))
            _, self.__auth_port = tcp.getsockname()
            tcp.close()

        if self.__auth_mode == AUTH.CONSOLE:
            credentials = flow.run_console()
        else:
            credentials = flow.run_local_server(
                host=self.__auth_hostname,
                port=self.__auth_port,
                open_browser=self.__auth_mode == AUTH.BROWSER,
            )
        credentials.refresh(
            google.auth.transport.requests.Request(
                session=flow.authorized_session(),
            ),
        )

        saved_state = {
            'refresh_token': credentials.refresh_token,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'token_uri': credentials.token_uri,
            'id_token': credentials.id_token,
            'scopes': list(credentials.scopes),
        }

        json.dump(saved_state, open(self.credential_path, 'w'))
        return credentials

    @property
    def credentials(self):
        return self._credentials

    @classmethod
    def default(cls):
        return cls(None, ['cloud-platform'])


# Handler for service account authentication
class service_acc(_api_builder):

    # Instantiate handler
    def __init__(self,
                 service_file,
                 scopes,
                 manualScopes=[],
                 domainWide=True,
                 *args,
                 **kwargs):

        # Load valid APIs unlocked with the scopes
        self._loadApiNames(scopes)

        # Save all scopes results
        self.SCOPES = list(
            set([x['scope'] for x in self.apis.values()] + manualScopes))

        # Set domain wide delegation flag
        self.__domWide = domainWide

        # Acquire credentials from JSON keyfile
        if service_file is not None:
            if isinstance(service_file, six.string_types):
                self._credentials = google.oauth2.service_account.Credentials.from_service_account_file(
                    service_file,
                    scopes=self.SCOPES,
                )
            else:
                self._credentials = google.oauth2.service_account.Credentials.from_service_account_info(
                    service_file,
                    scopes=self.SCOPES,
                )
            self.projectId = self._credentials.project_id
        else:
            self._credentials, self.projectId = google.auth.default()
            self._credentials = self._credentials.with_scopes(self.SCOPES)
        logger.debug("Credentials acquired")

    @property
    def credentials(self):
        return self._credentials

    @credentials.setter
    def credentials(self, newCredentials):
        self._credentials = newCredentials

    @classmethod
    def default(cls, scopes=['cloud-platform'], **kwargs):
        return cls(None, scopes, **kwargs)

    # Delegate authorization using application impersonation of authority
    def delegate(self, user):
        # Proceed only if domain wide delegation flag was setted to True
        if self.__domWide:
            # Instantiate delegated handler
            res = _delegated(
                self.credentials.with_subject(user), self.valid_apis)
            logger.info("Created delegated credentials")
            return res
        else:
            logger.warning("Domain Wide Delegation disabled")
            return self

    @property
    def domain_wide(self):
        return self.__domWide


# Delegated class, created from service account application impersonation
class _delegated(_api_builder):
    def __init__(self, dCredentials, apis):
        self.valid_apis = apis
        self._credentials = dCredentials

    @property
    def credentials(self):
        return self._credentials
