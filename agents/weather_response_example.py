#!/usr/bin/python

"""
These are two examples of threaded responder classes.

One replies with the current weather for New York City, using data from
the National Weather Service feed.

The other attempts to geolocate the sender's by the ip address, and,
if found, uses that location to get the weather report.

Note that the __init__ function in both classes accepts this
prototype/signature:

def __init__ (self, email_dict, sender, subject, text, html=None):

    where email_dict is the dict returned by server/email_parser.parse()
    and sender, subject, text, and html are all strings, representing
    the sender's email address, subject line, body plain text,
    and body html text (if any)

and they both contain a run() function which executes the specific
request.

"""

import threading
from lxml import etree
import json

import re
ip_pattern = re.compile(r'\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\]')

from emailer import send
from config import server_auto_email, forecast_io_key
from network import get_url
from geolocator import get_location

class reply_nyc_weather (threading.Thread):
    """In reply to email sent to nyc-weather@ -> lookup the current weather
    conditions for New York City and return it to the sender of this email"""

    email_dict = None
    sender = None
    subject = None
    text = None
    html = None

    def __init__ (self, email_dict, sender, subject, text, html=None):
        threading.Thread.__init__(self)
        self.email_dict = email_dict # this particular example doesn't do anything with the email information sent by the sender, but it's available
        self.sender = sender
        self.subject = subject
        self.text = text
        if html is not None:
            self.html = html

    def run(self):
        # get the current weather for NYC from the National Weather Service feed
        weather_xml = get_url('http://forecast.weather.gov/MapClick.php?lat=40.71980&lon=-73.99300&FcstType=dwml')

        if weather_xml is None:
            # there was an error gettting the weather data
            send('NYC Weather', 'Sorry, this service is temporarily unavailable', recipient_list=[self.sender], sender=server_auto_email)
        else:
            # parse the report from the xml and auto-reply with it as the message body
            doc = etree.fromstring(weather_xml)

            # find the human-readable text report in the xml
            report = []
            for elem in doc.xpath('//wordedForecast'):
                for subelem in elem.getchildren():
                    if subelem.tag == 'text':
                        report.append(subelem.text)

            # send it back to the sender
            send('NYC Weather', ' '.join(report), recipient_list=[self.sender], sender=server_auto_email)
 
class reply_weather (threading.Thread):
    """In reply to email sent to weather@ -> lookup the current weather
    conditions based on the location derived from the sender's ip address,
    and return it to the sender of this email"""

    email_dict = None
    sender = None
    subject = None
    text = None
    html = None

    def __init__ (self, email_dict, sender, subject, text, html=None):
        threading.Thread.__init__(self)
        self.email_dict = email_dict
        self.sender = sender
        self.subject = subject
        self.text = text
        if html is not None:
            self.html = html

    def run(self):
        # determine the sender's ip address from the email headers
        ip_address = None
        try:
            headers = self.email_dict['headers']
            for hdr in ['X-Originating-IP', # preferred header order to use
                        'X-Source-IP',
                        'X-Source',
                        'Received']:
                if headers.has_key(hdr):
                    match = ip_pattern.search(headers[hdr])
                    if match is not None:
                       ip_address = match.group().strip().replace('[','').replace(']', '')
                       break

        except KeyError:
            pass

        if ip_address is not None:
            # use the ip address to get the geographic location
            location = get_location(ip_address)

            try:
                lat = location['Latitude']
                lng = location['Longitude']

                # use the latitude and longitude to get the current report from the forecast.io API
                weather_url  = 'https://api.forecast.io/forecast/'+forecast_io_key+'/'+lat+','+lng
                weather_data = get_url(weather_url)
                if weather_data is not None:
                    data = json.loads(weather_data)
                    report = data["currently"]["summary"] + '\n\n' + data["hourly"]["summary"]
                    send('Current Weather', report, recipient_list=[self.sender], sender=server_auto_email)
                    return

            except KeyError:
                pass

        # the default reply, in case the location or weather for that location can't be found
        send('Current Weather',
             'Sorry, this service could not determine the weather for your geographic location',
             recipient_list=[self.sender],
             sender=server_auto_email)
    
