# Copyright (C) 2015  Custodia Project Contributors - see LICENSE file

import socket

import requests

from requests.adapters import HTTPAdapter
from requests.compat import unquote, urlparse

from requests.packages.urllib3.connection import HTTPConnection
from requests.packages.urllib3.connectionpool import HTTPConnectionPool


class HTTPUnixConnection(HTTPConnection):

    def __init__(self, host, timeout=60, **kwargs):
        super(HTTPConnection, self).__init__('localhost')
        self.unix_socket = host
        self.timeout = timeout

    def connect(self):
        s = socket.socket(family=socket.AF_UNIX)
        s.settimeout(self.timeout)
        s.connect(self.unix_socket)
        self.sock = s


class HTTPUnixConnectionPool(HTTPConnectionPool):

    scheme = 'http+unix'
    ConnectionCls = HTTPUnixConnection


class HTTPUnixAdapter(HTTPAdapter):

    def get_connection(self, url, proxies=None):
        # proxies, silently ignored
        path = unquote(urlparse(url).netloc)
        return HTTPUnixConnectionPool(path)


DEFAULT_HEADERS = {'Content-Type': 'application/json'}


class CustodiaHTTPClient(object):

    def __init__(self, url):
        self.session = requests.Session()
        self.session.mount('http+unix://', HTTPUnixAdapter())
        self.headers = dict(DEFAULT_HEADERS)
        self.url = url

    def set_simple_auth_keys(self, name, key,
                             name_header='CUSTODIA_AUTH_ID',
                             key_header='CUSTODIA_AUTH_KEY'):
        self.headers[name_header] = name
        self.headers[key_header] = key

    def _join_url(self, path):
        return self.url.rstrip('/') + '/' + path.lstrip('/')

    def _add_headers(self, **kwargs):
        headers = kwargs.get('headers', None)
        if headers is None:
            headers = dict()
        headers.update(self.headers)
        return headers

    def _request(self, cmd, path, **kwargs):
        url = self._join_url(path)
        kwargs['headers'] = self._add_headers(**kwargs)
        return cmd(url, **kwargs)

    def delete(self, path, **kwargs):
        return self._request(self.session.delete, path, **kwargs)

    def get(self, path, **kwargs):
        return self._request(self.session.get, path, **kwargs)

    def head(self, path, **kwargs):
        return self._request(self.session.head, path, **kwargs)

    def patch(self, path, **kwargs):
        return self._request(self.session.patch, path, **kwargs)

    def post(self, path, **kwargs):
        return self._request(self.session.post, path, **kwargs)

    def put(self, path, **kwargs):
        return self._request(self.session.put, path, **kwargs)


class CustodiaClient(CustodiaHTTPClient):

    def create_container(self, name):
        r = self.post(name if name.endswith('/') else name + '/')
        r.raise_for_status()
        return r

    def delete_container(self, name):
        r = self.delete(name if name.endswith('/') else name + '/')
        r.raise_for_status()
        return r

    def list_container(self, name):
        r = self.get(name if name.endswith('/') else name + '/')
        r.raise_for_status()
        return r

    def get_key(self, name):
        r = self.get(name)
        r.raise_for_status()
        return r

    def set_key(self, name, data_to_json):
        r = self.put(name, json=data_to_json)
        r.raise_for_status()
        return r

    def del_key(self, name):
        r = self.delete(name)
        r.raise_for_status()
        return r

    def get_simple_key(self, name):
        simple = self.get_key(name).json()
        ktype = simple.get("type", None)
        if ktype != "simple":
            raise TypeError("Invalid key type: %s" % ktype)
        return simple["value"]

    def set_simple_key(self, name, value):
        self.set_key(name, {"type": "simple", "value": value})