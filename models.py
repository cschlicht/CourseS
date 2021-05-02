"""
This file defines the database models
"""

import datetime
from .common import db, Field, auth, T
from pydal.validators import *


def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

def get_time():
    return datetime.datetime.utcnow()


db.define_table(
    'classes', # This table, like all tables, will have an "id"
    Field('number'), # CSE 183
    Field('name'), # Web apps
    Field('description', 'text'),
    Field('created_by', default=get_user_email),
    Field('creation_date', 'datetime', default=get_time),
)

db.classes.id.readable = db.classes.id.writable = False
db.classes.created_by.readable = db.classes.created_by.writable = False
db.classes.creation_date.readable = db.classes.creation_date.writable = False



### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later

db.commit()
