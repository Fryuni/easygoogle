#!/usr/bin/env python
from setuptools import setup

setup(
    name="easygoogle",
    packages=["easygoogle"],
    license="Apache License 2.0",
    version='1.1.0',
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
    download_url='https://github.com/Fryuni/easygoogle/archive/1.1.0.tar.gz',
    keywords="google apis google-apis",
    classifiers=["Development Status :: 5 - Production/Stable",
                 "Intended Audience :: Developers",
                 "Intended Audience :: Education",
                 "Intended Audience :: Information Technology",
                 "License :: OSI Approved :: Apache Software License",
                 "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
                 "Topic :: Utilities"]
)
