#!/usr/bin/python

"""

Utilities for processing the parsed email output of messages sent through the smtp server

"""

import re
from lxml import html as lxml_html

from config import pass_through_mailboxes, action_mailboxes, default_mailbox
from rfc_822_email_address_validator import is_valid_email_address

def valid_email_address (email_address):
    """Confirm that the email address provided is of a valid format"""
    result = False
    if email_address:
        if is_valid_email_address(email_address.strip('<>')):
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
        if domain_recipients[0] in action_mailboxes.keys() \
           or domain_recipients[0] in pass_through_mailboxes \
           or default_mailbox is not None:
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
