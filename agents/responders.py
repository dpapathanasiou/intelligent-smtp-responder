#!/usr/bin/python

"""
These are the functions invoked when specific action inboxes (as defined in config.py) are sent email.

Each responder function must accept this prototype/signature:

def action_fn (email_dict, sender, subject, text, html=None):

    where email_dict is the dict returned by server/email_parser.parse()
    and sender, subject, text, and html are all strings, representing the sender's email address, subject line, body plain text, and body html text (if any)

"""

import os
import urllib

from emailer import send

def clean_attachment_name (filename):
    """URL decode the parsed attachment filename and strip the extraneous quotes which can appear there"""
    return urllib.unquote(filename).replace('"','')

def save_attachments (attachments, attachments_folder='/tmp'):
    """Save the attachment data to the filesystem and return a list of their fully qualified path filenames"""

    saved_files = []
    for attachment in attachments:
        # attachment['name'] contains the filename
        # attachment['data'] is a cStringIO object -- use .getvalue() to retrieve its contents
        filename = os.path.join(attachments_folder, clean_attachment_name(attachment['name']))
        try:
            f = open(filename, 'wb')
            f.write(attachment['data'].getvalue())
            f.close()
            saved_files.append(filename)
        except IOError:
            # TO-DO: indicate that this attachment couldn't be saved
            pass
    return saved_files

def delete_attachments (filenames):
    """Take the list of fully-qualified path filenames and delete each one from the filesystem"""

    deleted_files = []
    for filename in filenames:
        try:
            os.remove(filename)
            deleted_files.append(filename)
        except OSError:
            pass
    return deleted_files

def pass_through (email_dict, sender, target, subject, text, html=None):
    """Treat this email as a regular incoming message and pass it along to the intended inbox (target email address)"""

    # save the attached files (if any)
    attached_files = save_attachments(email_dict['attachments'])

    # send the message to its intended mailbox
    send(subject, text, recipient_list=[target], html=html, files=attached_files, sender=sender)

    # remove the attached files (they've been sent with the message in the line above)
    delete_attachments(attached_files) # TO-DO: check that all were actually removed and cleanup, if necessary


#
# Auto-Reply Examples
#

# These methods corresponding to the values in the action_mailboxes dict defined in config.py
# For convenience they are all implemented here, but for larger or more complex cases, they can call upon classes or functions defined elsewhere

from config import server_auto_email
from email_utils import get_text_from_html
from network import load_url

def reply_time (email_dict, sender, subject, text, html=None):
    """In reply to email sent to current-time@ -> lookup the current time and return it to the sender of this email"""

    # get the time as an html page result from the US Naval Observatory Master Clock
    time_html = load_url('http://tycho.usno.navy.mil/cgi-bin/timer.pl')

    if time_html is None:
        # there was an error gettting the time data
        send('The Current Time', 'Sorry, this service is temporarily unavailable', recipient_list=[sender], sender=server_auto_email)
    else:
        # auto-reply with both the text and html versions of the time report
        time_txt = get_text_from_html(time_html.replace('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final"//EN>', ''))
        send('The Current Time', time_txt, recipient_list=[sender], html=time_html, sender=server_auto_email)


from lxml import etree

def reply_nyc_weather (email_dict, sender, subject, text, html=None):
    """In reply to email sent to nyc-weather@ -> lookup the current weather conditions and return it to the sender of this email"""

    # get the current weather for NYC from the National Weather Service feed
    weather_xml = network.load_url('http://forecast.weather.gov/MapClick.php?lat=40.71980&lon=-73.99300&FcstType=dwml')

    if weather_xml is None:
        # there was an error gettting the weather data
        send('NYC Weather', 'Sorry, this service is temporarily unavailable', recipient_list=[sender], sender=server_auto_email)
    else:
        # parse the report from the xml and auto-reply with it as the message body
        doc = etree.fromstring(d)

        # find the human-readable text report in the xml
        report = []
        for elem in doc.xpath('//wordedForecast'):
            for subelem in elem.getchildren():
                if subelem.tag == 'text':
                    report.append(subelem.text)

        # send it back to the sender
        send('NYC Weather', '\n'.join(report), recipient_list=[sender], sender=server_auto_email)
    
