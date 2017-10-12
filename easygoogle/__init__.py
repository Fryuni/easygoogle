import logging
import os
from argparse import ArgumentParser
from pickle import load
from sys import argv

from apiclient.discovery import build
from httplib2 import Http
from oauth2client import client, tools
from oauth2client.file import Storage
from oauth2client.service_account import ServiceAccountCredentials

logger = logging.getLogger(__name__)
argparser = ArgumentParser(parents=[tools.argparser], add_help=False)

# Load APIs versions, identifiers and scopes relations
# from pickle file
with open(os.path.join(os.path.dirname(__file__), 'apis.pk'), 'rb') as fl:
    apisDict = load(fl)


# Base class, loads API information and build the connectors with the credentials
class _api_builder:

    # Internal function to load all avaiable APIs based on the scopes
    def _loadApiNames(self, scopes):

        # Create a new dictionary to hold the information
        apiset = dict()

        # Iterates through every unique scopes
        for x in list(set(scopes)):
            try:
                # Load scope relations descriptor
                apiset[x] = apisDict[x]
            except KeyError:
                # Log when scope not found
                logger.warning("[!] SCOPE %s not registered" % x)
            except Exception as e:
                # When unexpected error is cought, log and raise RuntimeError
                logger.error(e)
                raise RuntimeError from e
            else:
                # On success log the unlocked APIs
                logger.debug("Loaded auth: %s --> api: %s" % (
                    x, ', '.join(("%s, %s" % (a['name'], a['version']) for a in apiset[x]['apis']))))
        logger.info("Apis imported")

        # Save the raw apiset
        self.apis = apiset
        # Instantiated a new dictionary create usable control
        self.valid_apis = dict()

        # Iterates through every scope descriptor unlocked
        for a in self.apis.values():

            # Iterates through all APIs described in the scope relations descriptor
            for b in a['apis']:
                # Process suffix when there are subidentifier in version
                suffix = b['version'].split('_v')
                suffix = "_" + suffix[0] if len(suffix) > 1 else ""
                self.valid_apis[b['name'] + suffix] = (b['name'], b['version'])

    # Function to build connector based on API identifiers
    def get_api(self, api):

        # Raises error if object is built ditectly as '_api_builder'
        if type(self) is not _api_builder and isinstance(self, _api_builder):
            # Build connector if API identifier is valid
            if api in self.valid_apis:
                res = build(self.valid_apis[api][0], self.valid_apis[api]
                            [1], http=self.http_auth)
                logger.info("%s API Generated" % api)
                return res
            else:
                logger.warning("%s is not a valid API" % api)
                raise ValueError("Invalid API identifier")
        else:
            raise TypeError(
                "The class '_api_builder' should not be instantiated\nIt should be inherited by other class that implements a valid self.http_auth.")


# OAuth2 class
# Handles API connector building, configuration of avaiable API and OAuth2 authentication flow
class oauth2(_api_builder):

    # Main constructor function
    def __init__(self, secret_json, scopes, appname='Google Client Library - Python', user="",
                 app_dir='.', flags=None, manualScopes=[]):

        # Load valid APIs unlocked with the scopes
        self._loadApiNames(scopes)

        # Save all scopes results
        self.SCOPES = list(set([x['scope']
                                for x in self.apis.values()] + manualScopes))

        # Home directory of the app
        home_dir = os.path.abspath(app_dir)
        # Path to credentials files directory
        self.credential_dir = os.path.join(home_dir, '.credentials')
        # Create credentials directory if not exists
        os.makedirs(self.credential_dir, exist_ok=True)

        # Save app name
        self.name = appname

        # Construct file name
        self.filename = ''.join(
            map(chr, (x for x in self.name.encode() if x < 128))).lower()
        self.filename = self.filename.replace(' ', '_') + user + ".json"

        # Assemble full credential file path
        self.credential_path = os.path.join(self.credential_dir, self.filename)

        # Open credentials store connector to file path
        store = Storage(self.credential_path)
        credentials = store.locked_get()
        # If invalid credentials stored, starts new default authorization flow
        if not credentials or credentials.invalid:
            # Instantiate flow
            flow = client.flow_from_clientsecrets(secret_json, self.SCOPES)
            # Set user agent
            flow.user_agent = self.name
            # Parse default flags
            if flags == None:
                flags = argparser.parse_args([])

            # Get credentials from default flow execution
            credentials = tools.run_flow(flow, store, flags)
            logger.info("Storing credentials to %s" % self.credential_path)

        # Save credentials
        logger.info("Credentials acquired")
        self.credentials = credentials

        # Authorize HTTP requests
        self.http_auth = self.credentials.authorize(Http())
        logger.info("Authorization acquired")


# OAuth2 class
# Handles API connector building and configuration of avaiable API
# Authorization flow needs to be manually handled
class oauth2_manual(_api_builder):

    def __init__(self, secret_json, scopes, redirectUrl="urn:ietf:wg:oauth:2.0:oob", manualScopes=[], login_hint=None):

        # Load valid APIs unlocked with the scopes
        self._loadApiNames(scopes)

        # Save all scopes results
        self.SCOPES = list(set([x['scope']
                                for x in self.apis.values()] + manualScopes))

        # Instantiated authorization flow
        self._flow = client.flow_from_clientsecrets(secret_json, self.SCOPES, redirect_uri=redirectUrl,
                                                    message="OAuth secret file not found at '{}'".format(
                                                        os.path.abspath(secret_json)),
                                                    login_hint=login_hint)
        logger.info("Instantiated flow")
        self._device_info = None

    # Returns OAuth2 login url
    def get_login_url(self, state=None):
        return self._flow.step1_get_authorize_url(state=state)

    # Returns OAuth2 device authorization info
    def get_device_auth(self):
        if self._device_info is None:
            self._device_info = self._flow.step1_get_device_and_user_codes()

        return self._device_info

    # Acquire credentials using login token
    def apply_login_token(self, token):
        credentials = self._flow.step2_exchange(code=token)
        self._apply_credentials(credentials)

    # Complete device authentication
    def apply_as_device(self):
        credentials = self._flow.step2_exchange(
            device_flow_info=self._device_info)
        self._apply_credentials(credentials)

    # Use credentials to authorize HTTP requests
    def _apply_credentials(self, credentials):
        self.credentials = credentials
        self.http_auth = self.credentials.authorize(Http())
        logger.info("Authorization acquired")


# Handler for service account authentication
class service_acc(_api_builder):

    # Instantiate handler
    def __init__(self, jsonfile, scopes, manualScopes=[], domainWide=False, *args, **kwargs):

        # Load valid APIs unlocked with the scopes
        self._loadApiNames(scopes)

        # Save all scopes results
        self.SCOPES = list(set([x['scope']
                                for x in self.apis.values()] + manualScopes))

        # Set domain wide delegation flag
        self.domWide = domainWide

        # Acquire credentials from JSON keyfile
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(
            jsonfile, scopes=self.SCOPES)
        logger.debug("Credentials acquired")

        # Authorize HTTP requests
        self.http_auth = self.credentials.authorize(Http())
        logger.debug("Authorization acquired")

    # Delegate authorization using application impersonation of authority
    def delegate(self, user):
        # Proceed only if domain wide delegation flag was setted to True
        if self.domWide:
            # Instantiate delegated handler
            res = _delegated(self.credentials.create_delegated(
                user), self.valid_apis)
            logger.info("Created delegated credentials")
            return res
        else:
            logger.warning("Domain Wide Delegation disabled")
            return self


# Delegated class, created from service account application impersonation
class _delegated(_api_builder):
    def __init__(self, dCredentials, apis):
        self.valid_apis = apis
        self.credentials = dCredentials
        self.http_auth = self.credentials.authorize(Http())
