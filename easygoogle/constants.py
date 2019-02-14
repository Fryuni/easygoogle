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

# -*- coding: utf-8 -*-
import os
from argparse import Namespace

AUTH = Namespace(
    CONSOLE='auth-opt-1',
    BROWSER='auth-opt-2',
    SILENT='auth-opt-3',
)
AUTH_OPTS = tuple(AUTH.__dict__.values())


class _CONSTS(object):

    def __setattr__(self, arg, val):
        raise NotImplementedError("Cannot package constants.")

    def __delattr__(self, arg):
        raise NotImplementedError("Cannot package constants.")

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
