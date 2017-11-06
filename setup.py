#!/usr/bin/env python
from os import environ

from setuptools import setup

VERSION = environ.get('CIRCLE_TAG', '0.0.0.dev1')
DOWNLOAD_URL = None

if 'CIRCLE_TAG' in environ:
    if VERSION[:8] != 'release-':
        exit("Invalid CIRCLE_TAG environment")
    else:
        import re
        match = re.match(r'^([0-9]+)\.([0-9]+)\.([0-9]+)$', VERSION[8:])
        if match:
            VERSION = '.'.join(str(int(p)) for p in match.groups())
        else:
            exit("Invalid CIRCLE_TAG environment")
    DOWNLOAD_URL = 'https://github.com/Fryuni/easygoogle/archive/%s.tar.gz' % VERSION

print("Running for version:", VERSION)
print()

setup(
    name="easygoogle",
    packages=["easygoogle"],
    license="Apache License 2.0",
    version=VERSION,
    description="Easy to use wrapper to google APIs client library",
    package_data={
        'easygoogle': ['apis.pk']
    },
    author="Luiz Augusto Ferraz",
    author_email="adm.fryuni@gmail.com",
    install_requires=["google-api-python-client (~=1.6.4)",
                      'google-auth (~=1.2.0)',
                      'google-auth-httplib2 (~=0.0.2)',
                      'google-auth-oauthlib (~=0.1.1)'],
    url="https://github.com/Fryuni/easygoogle",
    download_url=DOWNLOAD_URL,
    keywords="google apis google-apis",
    classifiers=["Development Status :: 5 - Production/Stable",
                 "Intended Audience :: Developers",
                 "Intended Audience :: Education",
                 "Intended Audience :: Information Technology",
                 "License :: OSI Approved :: Apache Software License",
                 "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
                 "Topic :: Utilities"]
)
