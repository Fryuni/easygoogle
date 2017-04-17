from setuptools import setup
setup(
        name = "easygoogle",
        packages = ["easygoogle"],
        license = "https://github.com/Fryuni/easy_google/blob/master/LICENSE",
        version = '0.1b1',
        description = "Easy to use wrapper to google APIs",
        author = "Luiz Augusto Ferraz",
        author_email = "adm.fryuni@gmail.com",
        install_requires = ["google-api-python-client (>=1.6.2)",
            "setuptools"],
        url = "https://github.com/Fryuni/easy_google/archive/0.1b1.tar.gz",
        keywords = ['google', 'apis', 'google-apis'],
        classifiers = []
        )
