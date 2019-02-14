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

import json
import logging
import os

import google.auth
import google.oauth2
import six
from google_auth_oauthlib.flow import InstalledAppFlow

from .base import _api_builder
from ..constants import AUTH, AUTH_OPTS, _CONSTS

logger = logging.getLogger(__name__)


class oauth2(_api_builder):
    # OAuth2 class
    # Handles API connector building, configuration of avaiable API and OAuth2 authentication flow

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
            logger.warning('Auth mode is enforced by environment, ignoring argument\n')

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
