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


class EasygoogleError(Exception):
    pass


class UnknownPreferredVersion(EasygoogleError):
    def __init__(self, api):
        super(UnknownPreferredVersion, self).__init__(api)
        self.api = api

    def __str__(self):
        return f'Could not determine preferred version for api "{self.api}"'


class UncertainPreferredVersion(UnknownPreferredVersion):
    def __str__(self):
        return (
            f'The api "{self.api}" has multiple preferred versions, probably it an api macro group. '
            'In this situation it is mandatory to specify a version.'
        )
