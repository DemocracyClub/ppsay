import sys
from datetime import datetime
from flask import request
from flask.ext.login import current_user

from db import db_action_log

def log(action, url, extra_data):
    doc = {'time_now': datetime.now(),
           'client_ip': request.remote_addr,
           'action': action,
           'url': url,
           'extra': extra_data}

    if current_user.is_authenticated():
        doc['user'] = current_user['user_name']

    doc_id = db_action_log.save(doc)

    return doc_id

