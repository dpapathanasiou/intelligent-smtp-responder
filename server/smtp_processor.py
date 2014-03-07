#!/usr/bin/python

"""

The actual processing logic for incoming email, once the smtp server has
determined that the message is valid, and corresponds to an active
mailbox and defined function (which gets invoked here).

"""

import time
from email_parser import parse
from config import pass_through_mailboxes, pass_through_target, action_mailboxes
from utils.email_utils import get_text_from_html
import responders

def process_email (email_data):
    """Take the data dict returned by the smtp server for this email message and process it according to the rules defined in config.py"""

    eml = parse(email_data['contents'])
    if email_data.has_key('inbox'):

        inbox = email_data['inbox']

        if email_data.has_key('subject'):
            subject = email_data['subject']
        else:
            subject = '(no subject)'

        body_text = ""
        if eml['body'] is not None and len(eml['body']) > 0:
            body_text = eml['body']

        body_html = None
        if eml['html'] is not None and len(eml['html']) > 0:
            if len(body_text) == 0:
                body_text = get_text_from_html(eml['html'])
            body_html = eml['html']

        if inbox in pass_through_mailboxes:
            # treat this email as a regular incoming message and pass it along to the intended inbox
            responders.pass_through(eml, email_data['sender'], pass_through_target, '['+inbox+'@] '+subject, body_text, body_html)
        
        elif inbox in action_mailboxes.keys():
            # this email represents a command that requires a specific threaded class instantiated and invoked
            # use the string representation of the class name -- defined by action_mailboxes[inbox] in config.py -- to call it
            try:
                response_class = getattr(responders, action_mailboxes[inbox])
                obj = response_class(eml, email_data['sender'], subject, body_text, body_html)
                obj.start() # kick off the request processor as a child thread so that the smtp server can close the connection immediately
            except AttributeError, e:
                print 'Exception:', time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()), e
