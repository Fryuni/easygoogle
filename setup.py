from setuptools import setup
setup(
        name = "easygoogle",
        packages = ["easygoogle"],
        license = "GNU General Public License v3.0",
        version = '0.6.1',
        description = "Easy to use wrapper to google APIs",
        author = "Luiz Augusto Ferraz",
        author_email = "adm.fryuni@gmail.com",
        install_requires = ["google-api-python-client (>=1.6.2)", "coloredLogs"],
        url = "https://github.com/Fryuni/easy_google",
        keywords = "google apis google-apis",
        classifiers = ["Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "Intended Audience :: Education",
            "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
            "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
            "Topic :: Utilities"]
        )
