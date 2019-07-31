#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

from os import environ

from setuptools import setup

VERSION = environ.get('CIRCLE_TAG', '0.0.0.dev1')
DOWNLOAD_URL = None
VALID_DIST_TYPES = ("release", "beta", "alpha", "bugfix", "hotfix")
DIST_TYPE = 'development'

if 'CIRCLE_TAG' in environ:
    import re

    DOWNLOAD_URL = 'https://github.com/Fryuni/easygoogle/archive/%s.tar.gz' % VERSION

    match = re.match(
        r'^([a-z]+)-([0-9]+)\.([0-9]+)\.([0-9]+[ab]?[0-9]*)$', VERSION
    )
    if match:
        VERSION = '.'.join(str(int(p)) for p in match.groups()[1:])
        DIST_TYPE = match.group(1)
    else:
        exit("Invalid CIRCLE_TAG environment variable")

    if DIST_TYPE not in VALID_DIST_TYPES:
        exit("Invalid tag prefix")

setup(
    name="easygoogle",
    packages=["easygoogle", "easygoogle.controllers"],
    license="Apache License 2.0",
    version=VERSION,
    description="Easy to use wrapper to google APIs client library",
    package_data={
        'easygoogle': ['apis.json']
    },
    author="Luiz Augusto Ferraz",
    author_email="luiz@lferraz.com",
    install_requires=[
        "google-api-python-client (~=1.7.10)",
        'google-auth (~=1.6.3)',
        'google-auth-oauthlib (~=0.4.0)',
    ],
    url="https://github.com/Fryuni/easygoogle",
    download_url=DOWNLOAD_URL,
    keywords="google apis google-apis",
    entry_points={
        'console_scripts': [
            'easygoogle_refreshapis=easygoogle.config:main',
        ],
    },
    classifiers=["Development Status :: 5 - Production/Stable",
                 "Intended Audience :: Developers",
                 "Intended Audience :: Education",
                 "Intended Audience :: Information Technology",
                 "License :: OSI Approved :: Apache Software License",
                 "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
                 "Topic :: Utilities"]
)
