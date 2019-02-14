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

import logging

import google.auth
from google.oauth2.service_account import Credentials
import six

from .base import _api_builder

logger = logging.getLogger(__name__)


class service_acc(_api_builder):
    # Handler for service account authentication

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
                self._credentials = Credentials.from_service_account_file(
                    service_file,
                    scopes=self.SCOPES,
                )
            else:
                self._credentials = Credentials.from_service_account_info(
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


class _delegated(_api_builder):
    # Delegated class, created from service account application impersonation
    def __init__(self, dCredentials, apis):
        self.valid_apis = apis
        self._credentials = dCredentials

    @property
    def credentials(self):
        return self._credentials
