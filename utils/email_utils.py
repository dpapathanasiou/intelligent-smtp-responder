#!/usr/bin/python

"""

Utilities for processing the parsed email output of messages sent through the smtp server

"""

import re
from lxml import html as lxml_html

from email_parser import parse
from config import pass_through_mailboxes, pass_through_target, action_mailboxes
import responders

valid_email_pattern = re.compile("^[\w-]+(\.[\w-]+)*@([\w-]+\.)+[a-zA-Z]{2,7}$")

def valid_email_address (email_address):
    """Confirm that the email address provided is of a valid format"""
    result = False
    if email_address:
        if valid_email_pattern.match(email_address.strip('<>')):
            result = True
    return result

def get_email_address (s):
    """Parse out the first email address found in the string and return it"""
    for token in s.split():
        if token.find('@') > -1:
            # token will be in the form:
            # 'FROM:<bob@example.org>' or 'TO:<alice@example.org>'
            # and with or without the <>
            for email_part in token.split(':'): 
                if email_part.find('@') > -1:
                    return email_part.strip('<>')

def domain_recipients_valid (domain_recipients=[]):
    """Confirm that the first email recipient @smtp_server_domain could correspond to a valid project (i.e., it a new project or an int) and return it"""
    result = None
    try:
        if domain_recipients[0] in action_mailboxes.keys() or domain_recipients[0] in pass_through_mailboxes:
            result = domain_recipients[0]
    except IndexError:
        pass
    return result

subject_prefix_pattern = re.compile('^(Fwd?|Re)(\[?[0-9]*\]?):', re.IGNORECASE) # matches Fwd:/Fw:/Re:/Re[4]: prefixes

def get_base_subject (subject_string):
    """Strip all forward/reply prefixes from the subject and return the base string"""

    if not subject_prefix_pattern.search(subject_string):
        # there are no Fwd:/Fw:/Re:/Re[4]: prefixes so just return the string as-is
        return subject_string
    else:
        # Strip off the first layer of Fwd:/Fw:/Re:/Re[4]: prefixes, and pass it through again,
        # to handle cases such as 'Re: Re[4]: Re:'
        return get_base_subject(subject_prefix_pattern.sub('', subject_string).lstrip())

def get_text_from_html (html_string):
    """Return the text from an html string -- needed for cases where there is no 'body' returned from parse(), only 'html'"""
    document = lxml_html.document_fromstring(html_string)
    return document.text_content()

def process_email (email_data):
    """Take the data dict returned by the smtp server for this email message and process it according to the rules defined in config.py"""

    eml = parse(email_data['contents'])
    if email_data.has_key('inbox'):

        inbox = email_data['inbox']

        if email_data.has_key('subject'):
            subject = email_data['subject']
        else:
            subject = 'Your email'

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
            responders.pass_through(eml, email_data['sender'], pass_through_target, subject, body_text, body_html)
        
        elif inbox in action_mailboxes.keys():
            # this email represents a command that requires a specific function invoked
            # use the string representation of the function name -- defined by action_mailboxes[inbox] in config.py -- to call it
            getattr(responders, action_mailboxes[inbox])(eml, email_data['sender'], subject, body_text, body_html)
