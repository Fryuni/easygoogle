# -*- coding: utf-8 -*-
import functools

import googleapiclient.discovery
import six


def applyPatch():
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
