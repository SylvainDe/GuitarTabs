#! /usr/bin/python3
# vim: set expandtab tabstop=4 shiftwidth=4 :
"""Module with functions wrapping urllib"""

import http.client
import urllib.request
import urllib.parse
import ssl
import gzip
import inspect
import logging
import json
import os
import time
from bs4 import BeautifulSoup

# Avoid flooding the server with requests
DELAY_BEFORE_REQUEST = 1

def log(string):
    """Dirty logging function."""
    # TODO: https://docs.python.org/2/library/logging.html#logrecord-attributes
    # we do not need to retrieve the function name manually
    logging.debug(inspect.stack()[1][3] + " " + string)


def urlopen_wrapper(url, referer=None):
    """Wrapper around urllib.request.urlopen (user-agent, etc).

    url is a string
    referer is an optional string
    Returns a byte object."""
    log('(url : %s)' % url)
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.30 (KHTML, like Gecko) Ubuntu/11.04 Chromium/12.0.742.112 Chrome/12.0.742.112 Safari/534.30'
    try:
        time.sleep(DELAY_BEFORE_REQUEST)
        req = urllib.request.Request(url, headers={'User-Agent': user_agent, 'Accept': '*/*'})
        if referer:
            req.add_header('Referer', referer)
        response = urllib.request.urlopen(req)
        if response.info().get('Content-Encoding') == 'gzip':
            return gzip.GzipFile(fileobj=response)
        return response
    except (urllib.error.HTTPError, http.client.RemoteDisconnected, urllib.error.URLError, ConnectionResetError, ssl.CertificateError) as e:
        print("Exception %s for url %s" % (e, url))
        raise


def get_content(url):
    """Get content at url.

    url is a string
    Returns a string"""
    log('(url : %s)' % url)
    try:
        return urlopen_wrapper(url).read()
    except http.client.IncompleteRead as e:
        print("%s for %s" % (e, url))
        return e.partial


class JsonCache(object):
    def __init__(self, filepath):
        self.filepath = filepath
        self.data = self.get_data_from(self.filepath)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def __contains__(self, item):
        return item in self.data

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        if value is self.data and self.data[key] == value:
            return
        self.data[key] = value
        self.on_update()

    def on_update(self):
        self.save_data_in(self.data, self.filepath)

    @staticmethod
    def get_data_from(json_filepath):
        try:
            with open(json_filepath) as f:
                return json.load(f)
        except IOError:
            return dict()

    @staticmethod
    def save_data_in(data, json_filepath):
        with open(json_filepath, 'w+') as f:
            json.dump(data, f, indent=4, sort_keys=True)


class UrlCache():
    def __init__(self, folder):
        self.folder = folder
        os.makedirs(self.folder, exist_ok=True)
        self.jsonCache = JsonCache(os.path.join(self.folder, "urlCache.json"))

    def get_content(self, url):
        rel_name = self.jsonCache.get(url, None)
        if rel_name is not None:
            with open(os.path.join(self.folder, rel_name), "rb") as f:
                return f.read()
        content = get_content(url)
        rel_name = str(hash(url)) + "_" + "".join(c if c.isalnum() else "-" for c in url)
        with open(os.path.join(self.folder, rel_name), "wb") as f:
                f.write(content)
        self.jsonCache[url] = rel_name
        return content

    def get_soup(self, url):
        content = self.get_content(url)
        return BeautifulSoup(content, "html.parser")


