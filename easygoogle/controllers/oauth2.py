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
from os import PathLike
from pathlib import Path
from typing import List, Optional, Union

from google.auth import default as default_auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from .base import _ApiBuilder
from ..config.scope_scrap import get_scopes_short_map
from ..constants import Auth, CONSTS
from ..credentials_storage.base import BaseStorage

logger = logging.getLogger(__name__)


# noinspection PyPep8Naming,SpellCheckingInspection
class oauth2(_ApiBuilder):
    # OAuth2 class
    # Handles API connector building, configuration of avaiable API and OAuth2 authentication flow

    # Main constructor function
    def __init__(self,
                 client_secrets: Optional[Union[str, PathLike]],
                 scopes: List[str],
                 appname: str = CONSTS.DEFAULT_APP_NAME,
                 user: str = "default_user",
                 credentials_store: BaseStorage = None,
                 hostname: str = CONSTS.DEFAULT_HOSTNAME,
                 port: int = CONSTS.DEFAULT_PORT,
                 auth_mode: Union[Auth, str] = CONSTS.DEFAULT_AUTH_OPT):
        if isinstance(auth_mode, (str, int)):
            auth_mode = Auth(str)
        elif not isinstance(auth_mode, Auth):
            raise ValueError(f'"auth_mode" must be a value from easygoogle.constants.Auth')

        if CONSTS.ENFORCE_DEFAULT_OPT and auth_mode != CONSTS.DEFAULT_AUTH_OPT:  # pragma: no cover
            logger.warning('Auth mode is enforced by environment, ignoring argument\n')
            auth_mode = CONSTS.DEFAULT_AUTH_OPT

        # Save all scopes results
        self.SCOPES = list({
            get_scopes_short_map().get(scope, scope)
            for scope in scopes
        })

        self.credentials_store: BaseStorage = credentials_store
        self.__auth_hostname = hostname
        self.__auth_port = port
        self.__auth_mode = auth_mode
        self._appname = appname
        self._user = user
        self._credentials: Optional[Credentials] = None
        self.projectId: Optional[str] = None

        if auth_mode is Auth.MANUAL:
            return

        if client_secrets is None:
            self._credentials, self.projectId = default_auth()
        else:
            self.__acquireCredentials(client_secrets, user)

    def __acquireCredentials(self, client_secrets: Union[str, PathLike, dict], user: str):
        if not isinstance(client_secrets, dict):
            client_secrets = json.load(Path(client_secrets).open('r'))
        if self.credentials_store:
            self._credentials = self.credentials_store.get(
                client_id=client_secrets['client_id'],
                user=user,
            )

        if (not self._credentials
                or not set(self.SCOPES).issubset(set(self._credentials.scopes))):
            self._credentials = self.__runAuthenticationFlow(client_secrets)
            if self.credentials_store:
                self.credentials_store.save(
                    client_id=client_secrets['client_id'],
                    user=user,
                    credentials=self._credentials,
                )

    def __runAuthenticationFlow(self, client_info) -> Credentials:
        # No valid credentials found
        # Instantiate authrization flow
        flow = InstalledAppFlow.from_client_config(
            client_info, scopes=self.SCOPES,
        )

        # Start web server to authorize application
        if self.__auth_port is None:
            import socket
            tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp.bind(('', 0))
            _, self.__auth_port = tcp.getsockname()
            tcp.close()

        if self.__auth_mode == Auth.CONSOLE:
            credentials = flow.run_console()
        else:
            credentials = flow.run_local_server(
                host=self.__auth_hostname,
                port=self.__auth_port,
                open_browser=self.__auth_mode == Auth.BROWSER,
            )
        credentials.refresh(Request(session=flow.authorized_session()))
        return credentials

    @property
    def credentials(self) -> Optional[Credentials]:
        return self._credentials

    @credentials.setter
    def credentials(self, new_credentials: Credentials):
        self._credentials = new_credentials

    @classmethod
    def default(cls):
        return cls(None, ['cloud-platform'])
