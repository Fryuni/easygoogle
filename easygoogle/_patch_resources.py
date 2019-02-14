# -*- coding: utf-8 -*-
#
#  Copyright 2017-2018 Luiz Augusto Alves Ferraz
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

import functools

import googleapiclient.discovery
import six


def apply_patch():
    original = googleapiclient.discovery.Resource._add_nested_resources

    @functools.wraps(original)
    def _add_nested_resources(self, resourceDesc, rootDesc, schema):
        # Add in nested resources
        if 'resources' in resourceDesc:

            def createResourceMethod(methodName, methodDesc):
                """Create a method on the Resource to access a nested Resource.

                Args:
                methodName: string, name of the method to use.
                methodDesc: object, fragment of deserialized discovery document that
                describes the method.
                """
                methodName = googleapiclient.discovery.fix_method_name(
                    methodName)

                methodResource = googleapiclient.discovery.Resource(
                    http=self._http, baseUrl=self._baseUrl,
                    model=self._model, developerKey=self._developerKey,
                    requestBuilder=self._requestBuilder,
                    resourceDesc=methodDesc, rootDesc=rootDesc,
                    schema=schema,
                )

                # setattr(methodResource, '__doc__', 'A collection resource.')
                setattr(methodResource, '__is_resource__', True)

                return (methodName, methodResource)

            for methodName, methodDesc in six.iteritems(resourceDesc['resources']):
                fixedMethodName, method = createResourceMethod(
                    methodName, methodDesc)
                self._set_dynamic_attr(fixedMethodName, method)

    def call(self):
        return self

    setattr(
        googleapiclient.discovery.Resource,
        '_add_nested_resources', _add_nested_resources
    )
    setattr(
        googleapiclient.discovery.Resource,
        '__call__', call
    )
