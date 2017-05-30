from oauth2client import client, tools
from oauth2client.file import Storage
from oauth2client.service_account import ServiceAccountCredentials
from httplib2 import Http
from apiclient.discovery import build
import os, logging
from sys import argv
from pickle import load
from argparse import ArgumentParser

logger = logging.getLogger(__name__)
argparser = ArgumentParser(parents=[tools.argparser], add_help=False)
if not os.path.isfile(os.path.join(os.path.dirname(__file__), 'apis.pk')):
    import easygoogle.config as cfg
    cfg.config()
with open(os.path.join(os.path.dirname(__file__), 'apis.pk'), 'rb') as fl:
    apisDict = load(fl)

class oauth2:
    def __init__(self, appname, secret_json, scopes, user="", app_dir='.', flags=None, manualScopes=[], *args, **kwargs):
        self._loadApiNames(scopes)
        
        home_dir = os.path.abspath(app_dir)
        self.credential_dir = os.path.join(home_dir, '.credentials')
        os.makedirs(self.credential_dir, exist_ok=True)
        
        self.name = appname
        self.filename = ''.join(map(chr, (x for x in self.name.encode() if x < 128))).lower().replace(' ', '_') + user + ".json"
        self.credential_path = os.path.join(self.credential_dir, self.filename)
        
        store = Storage(self.credential_path)
        credentials = store.locked_get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(secret_json, list(set([x['scope'] for x in self.apis.values()]+manualScopes)))
            flow.user_agent = self.name
            if flags==None:
                flags = argparser.parse_args()
            credentials = tools.run_flow(flow, store, flags)
            logger.info("Storing credentials to %s" % self.credential_path)
        logger.info("Credentials acquired")
        self.credentials = credentials
                
        self.http_auth = self.credentials.authorize(Http())
        logger.info("Authorization acquired")

    def _loadApiNames(self, scopes):
        apiset = dict()
        for x in list(set(scopes)):
            try:
                apiset[x] = apisDict[x]
            except KeyError:
                logger.warning("[!] API %s not registered" % x)
            except Exception as e:
                logger.error(e)
                raise e
            else:
                logger.debug("Loaded auth: %s --> api: %s" % (x, ', '.join(("%s, %s" % (a['name'], a['version']) for a in apiset[x]['apis']))))
        logger.info("Apis imported")

        self.apis = apiset
        self.valid_apis = dict()
        for a in self.apis.values():
            for b in a['apis']:
                suffix = b['version'].split('_v')
                suffix = "_"+suffix[0] if len(suffix) > 1 else ""
                self.valid_apis[b['name']+suffix] = (b['name'], b['version'])
    
    def get_api(self, api):
        if api in self.valid_apis:
            res = build(self.valid_apis[api][0], self.valid_apis[api][1], http=self.http_auth, cache_discovery=False)
            logger.info("%s API Generated" % api)
            return res
        else:
            logger.warning("%s is not a valid API" % api)


class service_acc(oauth2):
    def __init__(self, jsonfile, scopes, domainWide=False, *args, **kwargs):

        self._loadApiNames(scopes)
        self.domWide = domainWide
        
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(jsonfile, scopes=list(set([x['scope'] for x in self.apis.values()])))
        logger.info("Credentials acquired")
        
        self.http_auth = self.credentials.authorize(Http())
        logger.info("Authorization acquired")

    def delegate(self, user):
        if self.domWide:
            res = delegated(self.credentials.create_delegated(user), self.apis)
            logger.info("Created delegated credentials")
            return res
        else:
            logger.warning("Domain Wide Delegation disabled")
            return self


class delegated(service_acc):
    def __init__(self, dCredentials, apis):
        self.apis = apis
        self.dowWide = False
        self.credentials = dCredentials
        self.http_auth = self.credentials.authorize(Http())
