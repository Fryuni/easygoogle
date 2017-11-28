import logging
from json import dump
from os.path import dirname, join

import googleapiclient.discovery

logger = logging.getLogger("easygoogle.configurator")


# Configure valid apis and scopes from Google Discovery Documentation
def config():
    discoveryapi = googleapiclient.discovery.build('discovery', 'v1')
    apisres = discoveryapi.apis()
    allapis = apisres.list(fields='items(name,title,version)').execute()
    apis = dict()

    for api in allapis['items']:
        apiinfo = apisres.getRest(api=api['name'], version=api['version'],
                                  fields='auth').execute()

        if 'auth' not in apiinfo:
            continue

        for scope in apiinfo['auth']['oauth2']['scopes'].keys():
            name = scope.strip('/').split('/')[-1]

            logger.info("Configuring scope \"%s\" for \"%s\"..." % (name, api['title']))

            # If scope already registered, link to new API
            if name in apis:
                apis[name]['apis'].append(api)

                # Else, register scope and link to API
            else:
                apis[name] = {'apis': [api], 'scope': scope}

    # Save result configuration to json save file
    with open(join(dirname(__file__), 'apis.json'), 'w') as fl:
        dump(apis, fl)

        return apis


if __name__ == "__main__":

    # Instantiate basic logging
    logging.basicConfig(level=logging.INFO, format="[%(name)-20s][%(levelname)-8s]:%(asctime)s: %(message)s")

    # Start configuration
    config()
