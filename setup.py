from setuptools import setup

setup(
    name="easygoogle",
    packages=["easygoogle"],
    license="GNU General Public License v3.0",
    version='1.0',
    description="Easy to use wrapper to google APIs client library",
    author="Luiz Augusto Ferraz",
    author_email="adm.fryuni@gmail.com",
    install_requires=["google-api-python-client (>=1.6.2)"],
    url="https://github.com/Fryuni/easy_google",
    keywords="google apis google-apis",
    classifiers=["Development Status :: 5 - Production/Stable",
                 "Intended Audience :: Developers",
                 "Intended Audience :: Education",
                 "Intended Audience :: Information Technology",
                 "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
                 "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
                 "Topic :: Utilities"]
)
