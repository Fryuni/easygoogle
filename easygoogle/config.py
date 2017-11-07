import logging
from os.path import dirname, join
from pickle import dump, load
from re import compile as rExcompile
from re import findall
from urllib.request import Request as req
from urllib.request import urlopen as uopen

logger = logging.getLogger("easygoogle.configurator")

# Variable to control relations between scopes and APIs
apis = dict()


# Configure valid apis and scopes from Google Documentation
def config():
    global apis
    apis = dict()

    # Read python native API support page
    apiPageData = uopen(req('https://developers.google.com/api-client-library/python/apis/',
                            headers={'User-Agent': 'easyGoogle'}))

    # Search for all APIs identifiers and versions on page
    findings = findall(
        r"<td>(.+?)<\/td>\s+?<td>(.+?)<\/td>\s+?<td><a href=\"https:\/\/developers.google.com\/api-client-library.+?\">(.+?)<\/a><\/td>",
        apiPageData.read().decode())

    # Pair all API indentifiers with the respective versions
    python_confirmed = {(x[0], x[2]): x for x in findings}

    # Read full Google APIs scopes list page
    scopePageData = uopen(req('https://developers.google.com/identity/protocols/googlescopes',
                              headers={'User-Agent': 'easyGoogle'}))

    # Compile regular expressions to identify API block
    rx_header = rExcompile("\\s*<h2.*?<a href=.*?\">(.+? API)</a>, (.+?)</h2>")
    # Compile regular expressions to extract scope
    rx_scope = rExcompile("\\s*<tr>\\s*?<td>(.+?)</td>")

    # Iterates througth all lines of the scopes page source
    while scopePageData.length > 0:
        line = scopePageData.readline().decode()

        # Match each line with the API block header
        match_header = rx_header.match(line)

        # Once found, process API
        if match_header:
            logger.debug("Header found: %s --> %s" % match_header.group(1, 2))

            # Check if API version is supported by Google API client library
            if match_header.group(1, 2) in python_confirmed:
                logger.debug("Header is valid")

                # If supported, extract and process all API scopes
                while True:
                    line = scopePageData.readline().decode()
                    if line == "</table>\n":
                        break

                    match_scope = rx_scope.match(line)
                    if match_scope:
                        setapiinfo(python_confirmed[match_header.group(1, 2)],
                                   match_scope.group(1))

    # Save result configuration to pickle save file
    with open(join(dirname(__file__), 'apis.pk'), 'wb') as fl:
        dump(apis, fl)

    return apis


# Link scope to API
def setapiinfo(info, scope):
    global apis
    # Extract only meaningfull portion the scope link
    name = scope.strip('/').split('/')[-1]

    logger.info("Configuring scope \"%s\" for \"%s\"..." % (name, info[0]))

    # If scope already registered, link to new API
    if name in apis:
        apis[name]['apis'].append({'name': info[1], 'version': info[2]})

    # Else, register scope and link to API
    else:
        apis[name] = {'apis': [{'name': info[1], 'version': info[2]}], 'scope': scope}

    # Also return the working api state
    return apis[name]


if __name__ == "__main__":

    # Instantiate basic logging
    logging.basicConfig(level=logging.INFO, format="[%(name)-20s][%(levelname)-8s]:%(asctime)s: %(message)s")

    # Start configuration
    config()
