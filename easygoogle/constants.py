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

import enum
import os
import platform


class Auth(enum.Enum):
    CONSOLE = 'auth-opt-1'
    BROWSER = 'auth-opt-2'
    SILENT = 'auth-opt-3'
    MANUAL = 'no-auth-handler'


class _CONSTS(object):

    def __setattr__(self, arg, val):
        raise NotImplementedError("Cannot change constants.")

    def __delattr__(self, arg):
        raise NotImplementedError("Cannot change constants.")

    @property
    def DEFAULT_AUTH_OPT(self) -> Auth:
        return getattr(
            Auth,
            os.environ.get(
                'EASYGOOGLE_DEFAULT_MODE',
                'BROWSER'
            )
        )

    @property
    def DEFAULT_APP_DIR(self) -> str:
        return os.environ.get(
            'EASYGOOGLE_DEFAULT_APP_DIR',
            os.path.expandvars(r"%APPDATA%\easygoogle")
            if platform.system() == "Windows" else
            os.path.expanduser("~/.local/share")
        )

    @property
    def DEFAULT_APP_NAME(self) -> str:
        return os.environ.get(
            'EASYGOOGLE_DEFAULT_APP_NAME',
            'Google Client Library - Python'
        )

    @property
    def DEFAULT_HOSTNAME(self) -> str:
        return os.environ.get(
            'EASYGOOGLE_DEFAULT_HOSTNAME',
            'localhost'
        )

    @property
    def DEFAULT_PORT(self) -> str:
        return os.environ.get(
            'EASYGOOGLE_DEFAULT_PORT',
            None
        )

    @property
    def ENFORCE_DEFAULT_OPT(self) -> str:
        return os.environ.get('EASYGOOGLE_ENFORCE_AUTH_MODE') == 'ENFORCE'


CONSTS = _CONSTS()
del _CONSTS
