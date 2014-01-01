#!/usr/bin/env python
import requests
from base64 import urlsafe_b64encode as b64encode
from datetime import datetime, timedelta


class CloudPassageError(Exception):
    """Exception raised from the API.

    Attributes:
        err_type -- input expression in which the error occurred
        err_desc  -- explanation of the error
    """

    def __init__(self, err_type, err_desc):
        self.expr = err_type
        self.msg = err_desc


class InvalidClientError(Exception):
    """
    Invalid

    Attributes:
        msg  -- explanation of the error
    """

    def __init__(self, msg):
        self.msg = msg


class Token(str):
    """Handle automagically refreshing expired tokens"""


    baseurl = "https://api.cloudpassage.com/" #URL to access the cloudpassage API
    _auth = None

    def __post(self, endpoint, data=None, headers=None):
        json = requests.post(self.baseurl + endpoint, data=data, headers=headers).json()
        if u'error' in json:
            if json[u'error'] == u'invalid_client':
                raise InvalidClientError(json['error_description'])
            else:
                raise CloudPassageError(json['error'], json['error_description'])
        return json

    def login(self, keyid, secretkey):
        """
        Load the credentials for login

        :param keyid: The public keyid credential
        :param secretkey: The private secret_key "password" credential
        """
        self._auth = b64encode('%s:%s' % (keyid, secretkey))
        self.expires = datetime.fromtimestamp(0)
        self.token()

    def token(self):
        """Retrieve the current token, or get a new one"""
        if datetime.now() >= self.expires:
            endpoint = 'oauth/access_token?grant_type=client_credentials'
            headers = dict()
            headers['Authorization'] = 'Basic %s' % self._auth
            json = self.__post(endpoint, None, headers)
            self._access_token = json['access_token']
            self.token_type = json['token_type']
            self.expires = datetime.now() + timedelta(seconds=json['expires_in'])
            self.scope = json['scope']
            return self._access_token
        else:
            return self._access_token


    def __str__(self):
        """Make this object work like a string for easy access"""
        return self.token

    def __repr__(self):
        """Make this object work like a string for easy access"""
        return repr(self.token())


class CloudPassage:
    """A simple helper to make working with the CloudPassage API Easier"""


    baseurl = "https://api.cloudpassage.com/" #URL to access the cloudpassage API
    _auth = None

    def __init__(self, keyid, secret_key):
        """
        Create the object, and load the credentials for login

        :param keyid: The public keyid credential
        :param secret_key: The private secret_key "password" credential
        """
        self.token = Token()
        self.token.login(keyid, secret_key)

    def __get(self, endpoint, data=None, headers=None):
        if not headers:
            headers = {}
        headers['Authorization'] = 'Bearer %s' % self.token
        json = requests.get(self.baseurl + endpoint, data=data, headers=headers).json()
        if u'error' in json:
            if json[u'error'] == u'invalid_client':
                raise InvalidClientError(json['error_description'])
            else:
                raise CloudPassageError(json['error'], json['error_description'])
        return json

    def __post(self, endpoint, data=None, headers=None):
        if not headers:
            headers = {}
        headers['Authorization'] = 'Bearer %s' % self.token
        json = requests.post(self.baseurl + endpoint, data=data, headers=headers).json()
        if u'error' in json:
            if json[u'error'] == u'invalid_client':
                raise InvalidClientError(json['error_description'])
            else:
                raise CloudPassageError(json['error'], json['error_description'])
        return json
