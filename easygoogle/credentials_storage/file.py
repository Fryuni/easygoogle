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
from typing import Optional

import pickledb
from google.oauth2.credentials import Credentials

from .base import BaseStorage
from .utils import credentials_to_dict, credentials_from_dict


class FileStore(BaseStorage):
    db: pickledb.PickleDB

    def __init__(self, path: str, store_token: bool = True):
        super(FileStore, self).__init__()
        self.db = pickledb.load(path, False)
        self.store_token = store_token

    def get(self, client_id: str, user: str) -> Optional[Credentials]:
        if not self.has(client_id, user):
            return None
        key = self._unique_key(client_id, user)
        stored = self.db.get(key)
        return credentials_from_dict(stored, load_token=self.store_token)

    def save(self, client_id: str, user: str, credentials: Credentials):
        key = self._unique_key(client_id, user)
        self.db.set(key, credentials_to_dict(credentials, store_token=self.store_token))

    def has(self, client_id: str, user: str) -> bool:
        key = self._unique_key(client_id, user)
        return self.db.exists(key)
