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
import hashlib
from typing import Optional

from google.oauth2.credentials import Credentials


class StorageError(Exception):
    pass


class BaseStorage(metaclass=abc.ABCMeta):
    store_token: bool = True

    @abc.abstractmethod
    def save(self, client_id: str, user: str, credentials: Credentials):
        raise NotImplementedError()

    @abc.abstractmethod
    def get(self, client_id: str, user: str) -> Optional[Credentials]:
        raise NotImplementedError()

    @abc.abstractmethod
    def has(self, client_id: str, user: str) -> bool:
        raise NotImplementedError()

    @staticmethod
    def _unique_key(client_id: str, user: str) -> str:
        return hashlib.sha256(f"{client_id}-{user}").hexdigest().decode()
