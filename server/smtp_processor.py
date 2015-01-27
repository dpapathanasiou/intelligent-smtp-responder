#!/usr/bin/python

"""

The actual processing logic for incoming email, once the smtp server has
determined that the message is valid, and corresponds to an active
mailbox and defined function (which gets invoked here).

"""

import time
from email_parser import parse
from config import pass_through_mailboxes, pass_through_target, action_mailboxes, default_mailbox
from utils.email_utils import get_text_from_html
import responders
import importlib

def _invoke_action (inbox_action, eml, sender, subject, body_text, body_html):
    try:
        (resp_mod, resp_cl) = inbox_action.split('.')
        # convert the string representation of the module.class to the corresponding objects
        response_module = importlib.import_module(resp_mod)
        response_class  = getattr(response_module, resp_cl)
        obj = response_class(eml, sender, subject, body_text, body_html)
        obj.start() # kick off the request processor as a child thread so that the smtp server can close the connection immediately
    except Exception as e:
        print 'Exception:', time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()), e
        
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
            # use the string representation of the module.class name -- defined by action_mailboxes[inbox] in config.py -- to call it
            _invoke_action(action_mailboxes[inbox], eml, email_data['sender'], subject, body_text, body_html)
        elif default_mailbox is not None:
            # use the default response action, if it is defined
            _invoke_action(default_mailbox, eml, email_data['sender'], subject, body_text, body_html)
