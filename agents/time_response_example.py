#!/usr/bin/python

"""

This is an example of a threaded responder class which replies with the current time, 
using data from the US Naval Observatory Master Clock.

Notice that its __init__ function accepts this prototype/signature:

def __init__ (self, email_dict, sender, subject, text, html=None):

    where email_dict is the dict returned by server/email_parser.parse()
    and sender, subject, text, and html are all strings, representing
    the sender's email address, subject line, body plain text,
    and body html text (if any)

and it contains a run() function which executes the specific request,
which in this case is the current time, sending the results back to the sender.

"""

import threading

from emailer import send
from email_utils import get_text_from_html
from config import server_auto_email
from network import get_url

class reply_time (threading.Thread):
    """In reply to email sent to current-time@ -> lookup the current time and return it to the sender of this email"""

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
        # get the time as an html page result from the US Naval Observatory Master Clock
        time_html = get_url('http://tycho.usno.navy.mil/cgi-bin/timer.pl')

        if time_html is None:
            # there was an error gettting the time data
            send('The Current Time', 'Sorry, this service is temporarily unavailable', recipient_list=[self.sender], sender=server_auto_email)
        else:
            # auto-reply with both the text and html versions of the time report
            time_txt = get_text_from_html(time_html.replace('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final"//EN>', ''))
            send('The Current Time', time_txt, recipient_list=[self.sender], html=time_html, sender=server_auto_email)
