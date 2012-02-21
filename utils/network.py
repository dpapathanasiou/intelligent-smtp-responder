#!/usr/bin/python

"""

Functions for network access, including fetching url data

"""

import pycurl
from cStringIO import StringIO
from urlparse import urlparse

# DOMAINS = [tld.lower() for tld in urllib.urlopen('http://data.iana.org/TLD/tlds-alpha-by-domain.txt').read().split('\n') if not (tld.startswith('#') or tld == '')]
# (source: http://h5m.net/2009/04/list-comprehension-for-filtering.html)

DOMAINS = ['ac', 'ad', 'ae', 'aero', 'af', 'ag', 'ai', 'al', 'am', 'an', 'ao', 'aq', 'ar', 'arpa', 'as', 'asia', 'at', 'au', 'aw', 'ax', 'az', 'ba', 'bb', 'bd', 'be', 'bf', 'bg', 'bh', 'bi', 'biz', 'bj', 'bm', 'bn', 'bo', 'br', 'bs', 'bt', 'bv', 'bw', 'by', 'bz', 'ca', 'cat', 'cc', 'cd', 'cf', 'cg', 'ch', 'ci', 'ck', 'cl', 'cm', 'cn', 'co', 'com', 'coop', 'cr', 'cu', 'cv', 'cw', 'cx', 'cy', 'cz', 'de', 'dj', 'dk', 'dm', 'do', 'dz', 'ec', 'edu', 'ee', 'eg', 'er', 'es', 'et', 'eu', 'fi', 'fj', 'fk', 'fm', 'fo', 'fr', 'ga', 'gb', 'gd', 'ge', 'gf', 'gg', 'gh', 'gi', 'gl', 'gm', 'gn', 'gov', 'gp', 'gq', 'gr', 'gs', 'gt', 'gu', 'gw', 'gy', 'hk', 'hm', 'hn', 'hr', 'ht', 'hu', 'id', 'ie', 'il', 'im', 'in', 'info', 'int', 'io', 'iq', 'ir', 'is', 'it', 'je', 'jm', 'jo', 'jobs', 'jp', 'ke', 'kg', 'kh', 'ki', 'km', 'kn', 'kp', 'kr', 'kw', 'ky', 'kz', 'la', 'lb', 'lc', 'li', 'lk', 'lr', 'ls', 'lt', 'lu', 'lv', 'ly', 'ma', 'mc', 'md', 'me', 'mg', 'mh', 'mil', 'mk', 'ml', 'mm', 'mn', 'mo', 'mobi', 'mp', 'mq', 'mr', 'ms', 'mt', 'mu', 'museum', 'mv', 'mw', 'mx', 'my', 'mz', 'na', 'name', 'nc', 'ne', 'net', 'nf', 'ng', 'ni', 'nl', 'no', 'np', 'nr', 'nu', 'nz', 'om', 'org', 'pa', 'pe', 'pf', 'pg', 'ph', 'pk', 'pl', 'pm', 'pn', 'pr', 'pro', 'ps', 'pt', 'pw', 'py', 'qa', 're', 'ro', 'rs', 'ru', 'rw', 'sa', 'sb', 'sc', 'sd', 'se', 'sg', 'sh', 'si', 'sj', 'sk', 'sl', 'sm', 'sn', 'so', 'sr', 'st', 'su', 'sv', 'sx', 'sy', 'sz', 'tc', 'td', 'tel', 'tf', 'tg', 'th', 'tj', 'tk', 'tl', 'tm', 'tn', 'to', 'tp', 'tr', 'travel', 'tt', 'tv', 'tw', 'tz', 'ua', 'ug', 'uk', 'us', 'uy', 'uz', 'va', 'vc', 've', 'vg', 'vi', 'vn', 'vu', 'wf', 'ws', 'xn--0zwm56d', 'xn--11b5bs3a9aj6g', 'xn--3e0b707e', 'xn--45brj9c', 'xn--80akhbyknj4f', 'xn--90a3ac', 'xn--9t4b11yi5a', 'xn--clchc0ea0b2g2a9gcd', 'xn--deba0ad', 'xn--fiqs8s', 'xn--fiqz9s', 'xn--fpcrj9c3d', 'xn--fzc2c9e2c', 'xn--g6w251d', 'xn--gecrj9c', 'xn--h2brj9c', 'xn--hgbk6aj7f53bba', 'xn--hlcj6aya9esc7a', 'xn--j6w193g', 'xn--jxalpdlp', 'xn--kgbechtv', 'xn--kprw13d', 'xn--kpry57d', 'xn--lgbbat1ad8j', 'xn--mgbaam7a8h', 'xn--mgbayh7gpa', 'xn--mgbbh1a71e', 'xn--mgbc0a9azcg', 'xn--mgberp4a5d4ar', 'xn--o3cw4h', 'xn--ogbpf8fl', 'xn--p1ai', 'xn--pgbs0dh', 'xn--s9brj9c', 'xn--wgbh1c', 'xn--wgbl6a', 'xn--xkc2al3hye2a', 'xn--xkc2dl3a5ee0h', 'xn--yfro4i67o', 'xn--ygbi2ammx', 'xn--zckzah', 'xxx', 'ye', 'yt', 'za', 'zm', 'zw']


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


def load_url (url, user_agent=None):
    """Attempt to load the url using pycurl and return the data (which is None if unsuccessful)"""

    databuffer = StringIO()
    curl = pycurl.Curl()
    curl.setopt(pycurl.URL, url)
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
