#!/usr/bin/python

"""
Functions for network access, including fetching html and posting to forms

"""

import pycurl
from cStringIO import StringIO
from urllib import urlencode, urlopen
from urlparse import urlparse

# define the current official list of TLDs
# (source: http://h5m.net/2009/04/list-comprehension-for-filtering.html)
DOMAINS = [tld.lower() for tld in urlopen('http://data.iana.org/TLD/tlds-alpha-by-domain.txt').read().split('\n') if not (tld.startswith('#') or tld == '')]

def valid_url (url, allowable_schemes=['http', 'https', 'ftp']):
    """Confirm that the url provided is of a valid format (non-regex version using official list of tlds)
    source: http://h5m.net/2009/04/urlparse-cant-do-everything.html"""
    result = False
    (scheme, netloc, path, params, query, fragment) = urlparse(url)
    try:
        if netloc.split(':')[0].lower() == 'localhost' or netloc.split(':')[0].lower() == '127.0.0.1':
            result = True
        else:
            domain, tld = netloc.rsplit('.', 1)
            if tld.lower() in DOMAINS:
                if scheme.lower() in allowable_schemes:
                    result = True
    except ValueError:
        # an error here signifies a url without a top level domain, e.g. 'google' instead of 'google.com'
        pass
    return result

def get_url (url, user_agent=None):
    """Make a GET request of the the url using pycurl and return the data, or None if unsuccessful"""

    databuffer = StringIO()
    curl = pycurl.Curl()
    curl.setopt(pycurl.URL, url)
    curl.setopt(pycurl.FOLLOWLOCATION, 1)
    curl.setopt(pycurl.WRITEFUNCTION, databuffer.write)
    if user_agent:
        curl.setopt(pycurl.USERAGENT, user_agent)
    try:
        curl.perform()
        data = databuffer.getvalue()
    except:
        data = None
    curl.close()

    return data

def post_url (url, data, user_agent=None):
    """Make a POST to the url with the given data using pycurl and return the reply or None if unsuccessful.
    The data parameter is best as a list of tuples, each representing a form (variable, value) pair, e.g.:

    (('multipleSelectForm', 'value1'), ('multipleSelectForm', 'value2'))

    This is preferable over a dict, since it allows for the posting of multiple variables with
    the same name: http://stackoverflow.com/a/18515489"""

    databuffer = StringIO()
    curl = pycurl.Curl()
    curl.setopt(pycurl.URL, url)
    curl.setopt(pycurl.POST, 1)
    curl.setopt(pycurl.POSTFIELDS, urlencode(data))
    curl.setopt(pycurl.WRITEFUNCTION, databuffer.write)
    if user_agent:
        curl.setopt(pycurl.USERAGENT, user_agent)
    try:
        curl.perform()
        data = databuffer.getvalue()
    except:
        data = None
    curl.close()

    return data


