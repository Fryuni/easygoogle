from setuptools import setup

setup(
    name="easygoogle",
    packages=["easygoogle"],
    license="GNU General Public License v3.0",
    version='1.0.2',
    description="Easy to use wrapper to google APIs client library",
    package_data={
        'easygoogle': ['apis.pk']
    },
    author="Luiz Augusto Ferraz",
    author_email="adm.fryuni@gmail.com",
    install_requires=["google-api-python-client (>=1.6.4)"],
    url="https://github.com/Fryuni/easy_google",
    download_url='https://github.com/Fryuni/easy_google/archive/1.0.1.tar.gz',
    keywords="google apis google-apis",
    classifiers=["Development Status :: 5 - Production/Stable",
                 "Intended Audience :: Developers",
                 "Intended Audience :: Education",
                 "Intended Audience :: Information Technology",
                 "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
                 "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
                 "Topic :: Utilities"]
)
