#!/usr/bin/env python
import requests
from base64 import b64encode as b64encode


class Token:
    """A simple helper to make working with the CloudPassage API Easier"""


    baseurl = "https://api.cloudpassage.com/" #URL to access the cloudpassage API
    _auth = None

    def __init__(self, keyid, secret_key):
        """
        Create the object, and load the credentials for login

        :param keyid: The public keyid credential
        :param secret_key: The private secret_key "password" credential
        """
        self._auth = b64encode('%s:%s' % (keyid, secret_key))
        self.login()

    def __get(self, endpoint, data=None, headers=None):
        json = requests.get(self.baseurl + endpoint, data=data, headers=headers).json()
        if u'error' in json:
            if json[u'error'] == u'invalid_client':
                raise InvalidClientError(json['error_description'])
            else:
                raise CloudPassageError(json['error'], json['error_description'])
        return json

    def __post(self, endpoint, data=None, headers=None):
        json = requests.post(self.baseurl + endpoint, data=data, headers=headers).json()
        if u'error' in json:
            if json[u'error'] == u'invalid_client':
                raise InvalidClientError(json['error_description'])
            else:
                raise CloudPassageError(json['error'], json['error_description'])
        return json

    def login(self):
        """
        Authenticate to the Cloudpassage Endpoint

        NOTE: This does not yet handle the token timing out!
        """
        endpoint = 'oauth/access_token?grant_type=client_credentials'
        headers = dict()
        headers['Authorization'] = 'Basic %s' % self._auth
        self.json = self.__post(endpoint, None, headers)
        # And store the data
        # TODO: Move this all into a token object that expires / auto refreshes
        self._access_token = json['access_token']
        self.token_type = json['token_type']
        self.expires_in = json['expires_in']
        self.scope = json['scope']


if __name__ == "__main__":
    #Print documentation
    import os

    os.environ['TERM'] = 'dumb'
    help(Token)
