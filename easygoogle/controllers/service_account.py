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
import warnings
from typing import List, Optional, Union

import google.auth
from google.oauth2.service_account import Credentials

from .base import _ApiBuilder
from ..config.scope_scrap import get_scopes_short_map

logger = logging.getLogger(__name__)
_deprecation_dummy = object()


class ServiceAccount(_ApiBuilder):
    """Handler for service account authentication."""

    # noinspection PyPep8Naming
    def __init__(self,
                 service_file: Optional[Union[str, dict]],
                 scopes: List[str],
                 domainWide: bool = _deprecation_dummy,
                 *args,
                 **kwargs):
        super(ServiceAccount, self).__init__(*args, **kwargs)

        if domainWide is not _deprecation_dummy:
            warnings.warn(
                message=(
                    'The parameter "domainWide" is deprecated and not enforced when '
                    'creating delegated credentials controllers. APIs calls may fail '
                    'to authenticate depending on domain-wide configuration on GCP Console'
                ),
                category=DeprecationWarning,
            )

        # Save all scopes results
        self.SCOPES = list({
            get_scopes_short_map().get(scope, scope)
            for scope in scopes
        })

        # Acquire credentials from JSON key file
        if service_file is not None:
            if isinstance(service_file, dict):
                self._credentials = Credentials.from_service_account_info(
                    service_file,
                    scopes=self.SCOPES,
                )
            else:
                self._credentials = Credentials.from_service_account_file(
                    service_file,
                    scopes=self.SCOPES,
                )
            self.projectId = self._credentials.project_id
        else:
            self._credentials, self.projectId = google.auth.default()
            self._credentials = self._credentials.with_scopes(self.SCOPES)
        logger.debug("Credentials acquired")

    @property
    def credentials(self) -> Credentials:
        return self._credentials

    @classmethod
    def default(cls, scopes=('cloud-platform',), **kwargs):
        return cls(None, scopes, **kwargs)

    def delegate(self, user):
        """Delegate authorization using application impersonation of authority."""
        # Instantiate delegated handler
        res = _delegated(
            self.credentials.with_subject(user), self.valid_apis)
        logger.info("Created delegated credentials")
        return res


class _delegated(_ApiBuilder):
    # Delegated class, created from service account application impersonation
    def __init__(self, dCredentials, apis):
        self.valid_apis = apis
        self._credentials = dCredentials

    @property
    def credentials(self):
        return self._credentials
