# Easy Google APIs
[![CircleCI](https://circleci.com/gh/Fryuni/easygoogle/tree/master.svg?style=shield)](https://circleci.com/gh/Fryuni/easygoogle/tree/master)
[![PyPiStatus](https://img.shields.io/pypi/status/easygoogle.svg)](https://pypi.org/project/easygoogle/)

[![PyPi](https://img.shields.io/pypi/v/easygoogle.svg)](https://pypi.org/project/easygoogle/)
[![PyPiVersions](https://img.shields.io/pypi/pyversions/google-cloud.svg)](https://pypi.org/project/easygoogle/)

_Google APIs python library wrapepr_

Python package to make Google APIs more practical and easy to use

Supports OAuth authentication and [service accounts](https://developers.google.com/identity/protocols/OAuth2ServiceAccount) (directly and with [domain wide delegation](https://developers.google.com/identity/protocols/OAuth2ServiceAccount#delegatingauthority))

## Installation

    pip install -U easygoogle

## Prerequisites

To use Google APIs you'll need an credentials _json_ file from Google Cloud Platform.
To generate it, follow this steps:
1. Ensure you have a [GCP _(Google Cloud Platform)_ Project](https://cloud.google.com/resource-manager/docs/creating-managing-projects)
1. Go to the [GCP Console](https://console.cloud.google.com) and select the project that you want to use on the top-left corner on the right of the title and the three dots
1. Go to the [API Library](https://console.cloud.google.com/apis/library) and enable the APIs you intend to use
1. On the APIs & services Dashboard, where you should arrive, click on Credentials on the left menu

###### To use OAuth2 authentication:

1. Click on the blue button **_Create credentials_** and select **_OAuth Client ID_**
1. Select your application type, name it and click _Create_ (if you are running utilities scripts, you probably want the _Other_ type)
1. Click OK on the popup, find the name you just used and click the download button at the right end of the line

###### To use a Service Account authentication:

1. Click on the blue button **_Create credentials_** and select **_Service account key_**
1. Select the service account you want to use or create a new one
  - If you are going to use _Domain wide Delegatio_, you need to ensure the service account has the role **Project > Service Account Actor** as well as the requirements on the [official documentation](https://developers.google.com/identity/protocols/OAuth2ServiceAccount#delegatingauthority)
1. Select the keyfile type **JSON**
1. Save the file


## Usage

###### OAuth2 authentication:

```Python
user = easygoogle.oauth2(
    json_file, # Path to the JSON file
    scopes, # List of scopes identifiers
    appname='Google Client Library - Python', # Optional. Used to identify the credentials file saved
    user='', # Optional. Used to identify the credentials file saved
    app_dir='.', # Path to create subdir '.credentials' and store credentials files. Defaults to current working directory
    manualScopes=[], # Manually defined scopes for authorization. Used in Single Sign-On with servers that support OAuth authentication
    hostname='localhost', # Where to open authentication flow server
    port=8080, # Which port to open authentication flow server in
)

# Build API as the authenticated user
api = user.get_api(
    apiname # API identifier
)
```

_Example:_
```Python
import easygoogle

account_controller = easygoogle.oauth2('oauth_secret.json', ['drive'])

drive = account_controller.get_api('drive')

print(drive.files().list().execute())
```

###### Service Account authentication:

```Python
service = easygoogle.service_acc(
    json_file, # Path to the JSON file
    scopes, # List of scopes identifiers,
    domainWide=False, # Set true to enable the .delegate option
    manualScopes=[] # Manually defined scopes for authorization. Used in Single Sign-On with servers that support OAuth authentication
)

# Build API as the service account
api = service.get_api(
    apiname # API identifier
)


# Build user OAuth2 credentials with user impersonation
user = service.delegate(
    user_email # Email or alias of the impersonating user
)

# Build API as the impersonated user
api = user.get_api(
    apiname # API identifier
)
```

_Example:_
```Python
import easygoogle

service = easygoogle.service_acc('service_secret.json', ['drive'])

# Building Drive API as the service account
serviceDrive = servie.get_api('drive')

print(serviceDrive.files().list().execute())
# List files on the service account individual Drive


# Acquiring credentials for user
user = service.delegate('user@example.org')

# Building Drive API as the impersonated user
userDrive = user.get_api('drive')

print(userDrive.files().list().execute())
# List files on the user individual Drive
```
