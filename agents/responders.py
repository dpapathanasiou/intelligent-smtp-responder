#!/usr/bin/python

"""

This file contains references to the threaded classes which instantiated and invoked 
when specific action inboxes (as defined in config.py) are sent email.

Each responder class __init__ function must accept this prototype/signature:

def __init__ (self, email_dict, sender, subject, text, html=None):

    where email_dict is the dict returned by server/email_parser.parse()
    and sender, subject, text, and html are all strings, representing
    the sender's email address, subject line, body plain text,
    and body html text (if any)

and contain a run() function which executes the specific request, 
sending the results back to the sender.

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
