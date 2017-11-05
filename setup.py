#!/usr/bin/env python
from os import environ

from setuptools import setup

setup(
    name="easygoogle",
    packages=["easygoogle"],
    license="Apache License 2.0",
    version=environ.get('CIRCLE_TAG', '0.0.0dev1'),
    description="Easy to use wrapper to google APIs client library",
    package_data={
        'easygoogle': ['apis.pk']
    },
    author="Luiz Augusto Ferraz",
    author_email="adm.fryuni@gmail.com",
    install_requires=["google-api-python-client (~=1.6.4)",
                      'google-auth (~=1.2.0)',
                      'google-auth-oauthlib (~=0.1.1)'],
    url="https://github.com/Fryuni/easygoogle",
    download_url='https://github.com/Fryuni/easygoogle/archive/%s.tar.gz' % environ.get('CIRCLE_TAG', '0.0.0dev1'),
    keywords="google apis google-apis",
    classifiers=["Development Status :: 5 - Production/Stable",
                 "Intended Audience :: Developers",
                 "Intended Audience :: Education",
                 "Intended Audience :: Information Technology",
                 "License :: OSI Approved :: Apache Software License",
                 "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
                 "Topic :: Utilities"]
)
