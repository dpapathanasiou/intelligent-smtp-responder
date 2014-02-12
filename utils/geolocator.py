#!/usr/bin/python

"""

Functions to physically locate email messages based on the
sender's IP address using the hostip.info API.

"""

from network import get_url

def _generate_url (ip_address, get_latlong=True):
    """Generate and return the url used to call the geolocation API"""

    url_parts = ['http://api.hostip.info/get_html.php?']

    if get_latlong:
        url_parts.append('position=true&')

    url_parts.append('ip=')
    url_parts.append(ip_address)

    return ''.join(url_parts)

def get_location (ip_address):
    """Call the geolocation API and return a dict of the results, if any,
    including the latitude and longitude"""

    location = {}

    query = get_url(_generate_url(ip_address))
    if query is not None:
        for line in query.splitlines():
            data = line.split(': ')
            if len(data) == 2 and len(data[1]) > 0:
                location[data[0]] = data[1]

    return location
