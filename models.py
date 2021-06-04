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
    Field('name'), # CSE 
    Field('number'), # 183
    Field('favorite', 'boolean', default=False),
    Field('created_by', default=get_user_email),
    Field('creation_date', 'datetime', default=get_time),
)
db.define_table('contact',
                Field('comment'),
                Field('author'), 
                Field('email', default = get_user_email),
                Field('status', 'integer', default = 0))

db.define_table('user',
                Field('item_id', 'integer'),
                
                Field('email'), 
                Field('status', 'integer', default = 0))

db.define_table(
    'resources',
    Field('classes_id', 'reference classes'),
    Field('sym'),
    Field('title', requires=IS_NOT_EMPTY()),
    Field('link'),
    Field('image'),
    Field('likes', 'integer', default = 0),
    Field('dislikes', 'integer', default = 0),
    Field('description', requires=IS_NOT_EMPTY()),
    Field('created_by', default=get_user_email),
    Field('creation_date', 'datetime', default=get_time),
)

db.define_table(
    'upload',
    Field('owner', default=get_user_email),
    Field('resource_id', 'reference resources'),
    Field('file_name'),
    Field('file_type'),
    Field('file_date'),
    Field('file_path'),
    Field('file_size', 'integer'),
    Field('download_url'),
    Field('confirmed', 'boolean', default=False), # Was the upload to GCS confirmed?
)

db.classes.id.readable = db.classes.id.writable = False
db.classes.created_by.readable = db.classes.created_by.writable = False
db.classes.creation_date.readable = db.classes.creation_date.writable = False

db.resources.classes_id.readable = db.resources.classes_id.writable = False
db.resources.id.readable = db.resources.id.writable = False
db.resources.created_by.readable = db.resources.created_by.writable = False
db.resources.creation_date.readable = db.resources.creation_date.writable = False


### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later

db.commit()
