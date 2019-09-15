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

import re

import requests

__scopes_short_map = None


def get_scopes_short_map():
    global __scopes_short_map
    if __scopes_short_map is None:
        with requests.get("https://developers.google.com/identity/protocols/googlescopes") as res:
            data = res.text
        rgx = re.compile(r"<tr>\s*<td>(https://[\w./\-\d]+?) ?</td")

        scopes = [
            match.group(1)
            for match in rgx.finditer(data)
        ]

        __scopes_short_map = {
            scope.rsplit('/', 1)[-1]: scope
            for scope in scopes
        }
    return __scopes_short_map
