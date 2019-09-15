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
import gzip

from google.oauth2.credentials import Credentials


def credentials_to_bytes(credentials: Credentials, store_token=True) -> bytes:
    raw = '\x10'.join((
        credentials.token if store_token else '',
        credentials.refresh_token if credentials.refresh_token else '',
        credentials.id_token if credentials.id_token else '',
        credentials.client_id, credentials.client_secret,
        '~'.join(credentials.scopes), credentials.token_uri,
    )).encode('ascii')
    return gzip.compress(raw)


def credentials_from_bytes(data: bytes, load_token=True) -> Credentials:
    raw = gzip.decompress(data).decode('ascii')
    (token, refresh_token, id_token, client_id,
     client_secret, scopes, token_uri) = raw.split('\x10')
    return Credentials(
        token=token if token and load_token else None,
        refresh_token=refresh_token or None,
        id_token=id_token or None,
        client_id=client_id,
        client_secret=client_secret,
        scopes=scopes.split('~'),
        token_uri=token_uri,
    )


def credentials_to_dict(credentials: Credentials, store_token=True) -> dict:
    return {
        'token': credentials.token if store_token else None,
        'refresh_token': credentials.refresh_token,
        'id_token': credentials.id_token,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': list(credentials.scopes),
        'token_uri': credentials.token_uri,
    }


def credentials_from_dict(data: dict, load_token=True) -> Credentials:
    return Credentials(
        token=data['token'] if load_token else None,
        refresh_token=data['refresh_token'],
        id_token=data['id_token'],
        client_id=data['client_id'],
        client_secret=data['client_secret'],
        scopes=data['scopes'],
        token_uri=data['token_uri'],
    )
