#!/usr/bin/env python
from __future__ import absolute_import
import requests
import httplib
import urllib
from json import dumps
from base64 import urlsafe_b64encode as b64encode
from datetime import datetime, timedelta
from cloudpassage.exceptions import InvalidClientError
from cloudpassage.exceptions import CloudPassageError
from cloudpassage.exceptions import ValidationFailedError


class Token(str):
    """Handle automagically refreshing expired tokens"""

    # URL to access the cloudpassage API
    baseurl = "https://api.cloudpassage.com"
    _auth = None

    def __post(self, endpoint, data=None, headers=None):
        url = self.baseurl + endpoint
        if headers is None:
            headers = {}
        headers['Content-Type'] = 'application/json'
        req = requests.post(url, data=data, headers=headers)
        req.raise_for_status()
        json = req.json()
        if u'error' in json:
            if json[u'error'] == u'invalid_client':
                raise InvalidClientError(json['error_description'])
            else:
                raise CloudPassageError(json['error'],
                                        json['error_description'])
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
        if datetime.now() < self.expires:
            return self._access_token
        endpoint = '/oauth/access_token?grant_type=client_credentials'
        headers = dict()
        headers['Authorization'] = 'Basic %s' % self._auth
        json = self.__post(endpoint, None, headers)
        self._access_token = json['access_token']
        self.token_type = json['token_type']
        self.expires = datetime.now() + timedelta(seconds=json['expires_in'])
        self.scope = json['scope']
        return self._access_token

    def __str__(self):
        """Make this object work like a string for easy access"""
        return self.token()

    def __repr__(self):
        """Make this object work like a string for easy access"""
        return repr(self.token())


class CloudPassage:
    """A simple helper to make working with the CloudPassage API Easier"""

    # URL to access the cloudpassage API
    baseurl = "https://api.cloudpassage.com"
    _auth = None

    def __init__(self, keyid, secret_key):
        """
        Create the object, and load the credentials for login

        :param keyid: The public keyid credential
        :param secret_key: The private secret_key "password" credential
        """
        self.token = Token()
        self.token.login(keyid, secret_key)

    def __get(self, endpoint):
        headers = {'Authorization': 'Bearer %s' % self.token}
        url = self.baseurl + endpoint
        req = requests.get(url, headers=headers)
        return self.__parserequest(req)

    def __post(self, endpoint, data=None):
        if data:
            # Convert data to properly-formatted json before posting
            data = dumps(data)
        headers = {'Authorization': 'Bearer %s' % self.token,
                   'Content-Type': 'application/json'}
        url = self.baseurl + endpoint
        req = requests.post(url, data=data, headers=headers)
        return self.__parserequest(req)

    def __parserequest(self, req):
        if httplib.HTTPConnection.debuglevel > 0:
            print 'body:', req.text
        req.raise_for_status()
        json = req.json()
        if u'error' in json:
            if json[u'error'] == u'invalid_client':
                raise InvalidClientError(json['error_description'])
            if json[u'message'] == u'Validation Failed':
                for error in json.errors:
                    raise ValidationFailedError(error['details'])
            else:
                raise CloudPassageError(json['error'],
                                        json['error_description'])
        return json

    def list_users(self):
        """
        Lists all available profile information, including user ID and URL to
        the user resource, for all users in your Halo account.
        """
        return self.__get('/v1/users')

    def get_user(self, uid):
        """
        Lists the profile information for a single user, specified by user ID.
        """
        return self.__get('/v1/users/%s' % uid)

    def list_server_groups(self):
        """
        Returns the names and details, including group ID, of all of your
        currently defined server groups.
        """
        return self.__get('/v1/groups')

    def list_server_group(self, gid):
        """
        Returns information describing a single server group specified by group
        ID.
        """
        return self.__get('/v1/groups/%s' % gid)

    def create_server_group(self, name, tag, **kwargs):
        """
        Creates a new server group with default values that you specify, and
        returns its information, including URL and group ID, in the response
        body.
        """
        body = {"group": {}}
        body['group']['name'] = name
        body['group']['tag'] = tag
        for k, v in kwargs.items():
            body['group'][k] = v

        print body
        return self.__post('/v1/groups', body)

    def update_server_group(self, gid, **kwargs):
        """
        Use this call to update individual attributes of the server group that
        you specify by group ID.
        You need to include only the attributes that you want modified; other
        attributes of the group will remain unchanged.
        """
        body = {"group": {}}
        for k, v in kwargs.items():
            body['group'][k] = v

        return self.__post('/v1/groups/%s' % gid, body)

    def search_server_groups(self, **kwargs):
        return self._get('/v1/groups?' % urllib.urlencode(kwargs))
