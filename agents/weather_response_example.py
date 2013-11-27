#!/usr/bin/python

"""

This is an example of a threaded responder class which replies with the current weather for NYC, 
using data from the National Weather Service feed.

Notice that its __init__ function accepts this prototype/signature:

def __init__ (self, email_dict, sender, subject, text, html=None):

    where email_dict is the dict returned by server/email_parser.parse()
    and sender, subject, text, and html are all strings, representing
    the sender's email address, subject line, body plain text,
    and body html text (if any)

and it contains a run() function which executes the specific request,
which in this case is the current NYC weather, sending the results back to the sender.

"""

import threading
from lxml import etree

from emailer import send
from config import server_auto_email
from network import get_url

class reply_nyc_weather (threading.Thread):
    """In reply to email sent to nyc-weather@ -> lookup the current weather conditions and return it to the sender of this email"""

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
    
