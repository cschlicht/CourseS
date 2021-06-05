"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""
import datetime
import json
import os
import traceback
import uuid

from nqgcs import NQGCS
from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_user_email
from .settings import APP_FOLDER
from .gcs_url import gcs_url

url_signer = URLSigner(session)

BUCKET = '/coursesource-files'
# GCS keys.  You have to create them for this to work.  See README.md
GCS_KEY_PATH = os.path.join(APP_FOLDER, 'private/gcs_keys.json')
with open(GCS_KEY_PATH) as gcs_key_f:
    GCS_KEYS = json.load(gcs_key_f)

# I create a handle to gcs, to perform the various operations.
gcs = NQGCS(json_key_path=GCS_KEY_PATH)

JSON_FILE = os.path.join(APP_FOLDER, "data", "classes.json")

@action('index')
@action.uses(url_signer, auth.user, 'index.html')
def index():

    # print(JSON_FILE)
    # Inserting JSON to db
    '''r
    with open(JSON_FILE,'r', encoding='utf-8') as j:
         data = json.load(j)
         for d in data:

    #         # print(d["ClassSymbol"])
    #         # print(d["Class Name"])
             db.classes.insert(
                 number=d['ClassSymbol'],
                 name=d['Class Name'],
                 favorite=0,
             )
    '''         
    #db(db.classes).delete()  # Deletes classes database
    #load_classes()
    rows = db(db.classes).select()
    #print(rows)
    return dict(
        # This is the signed URL for the callback.
        star_url = URL('star', signer = url_signer),
        load_classes_url = URL('load_classes', signer=url_signer),
        load_contacts_url = URL('load_contacts', signer=url_signer),
        file_info_url = URL('file_info', signer=url_signer),
    )

@action('star', method="POST")
@action.uses(url_signer.verify(), db)
def star():
    id = request.json.get("id")
    field = request.json.get("field")
    value = request.json.get("value")
    prev = request.json.get("prev")

    test = db(db.user.email == get_user_email()).select().as_list()

  #THIS IS WHERE WE .update(favorite = value) the .select for the specific user
  # with class_id == id and db.user.email == get_user_email()

    db.user.update_or_insert(
        ((db.user.class_id == id) & (db.user.email == get_user_email())),
        class_id = id,
        email = get_user_email(),
        favorite = value
    )
  
    '''r
    if value == 1:  # changing to starred
        if prev == 0:  # if we are currently not starred
            
            #db(db.classes.id == id).update(favorite=value)
            if test:
                db(db.user.class_id == id).update(favorite=value)
            else:
                db.user.insert(email = get_user_email(), class_id = id, favorite = value)

    if value == 0:  # changing to not starred
        if prev == 1:  # if we are currently starred
            
           # db(db.classes.id == id).update(favorite=value)
            if test:
                db(db.user.class_id == id).update(favorite=value)
            else:
                db.user.insert(class_id = id, favorite = value)
    '''
@action('load_classes')
@action.uses(url_signer.verify(), db)
def load_classes():
    rows = db(db.classes).select().as_list()
    users = db(db.user.email == get_user_email()).select().as_list()
    #print(users)
    flag = 0
    for r in rows:
        #print(r['id'])
        for u in users:
            if u['class_id'] == r['id'] and u['email'] == get_user_email():
                flag = 1
            
        if(flag == 0):
            db.user.insert(
            class_id = r['id'],
            email = get_user_email(),
            favorite = 0,
            )
        flag = 0
    '''r
    use = db(db.user.class_id == 645).select().as_list()
    print(use)
    x = 0
    for r in rows:
        use = db(db.user.class_id == r['id']).select().as_list()
        for u in use:
            x += 1
            if x > 1:
                db(db.user.id == u['id']).delete()
        x = 0

    use = db(db.user.class_id == 645).select().as_list()
    '''
   # print(use)
    #print(users)
    users = db(db.user.email == get_user_email()).select().as_list()

    for u in users:
        if u['favorite'] == 1:
            db(db.classes.id == u['class_id']).update(favorite = 1)
        if u['favorite'] == 0:
            db(db.classes.id == u['class_id']).update(favorite = 0)

    #print(users)
    #rows = sorted(rows, key = lambda i: (i['favorite']), reverse = True)
    '''r
    likedList = [] 
    likedDic = {}
    for u in users:
        if u['favorite'] == 1:
            cl = db(db.classes.id == u['class_id']).select().as_list()
            #print(cl)
            for c in cl:

                likedDic['number'] = c['number']
                likedDic['name'] = c['name']
                likedList.append(likedDic)
                likedDic = {}

   # print(likedList)
    for u in likedList:

        print(u['number'])
        print(u['name'])
'''
    rows = db(db.classes).select().as_list()
    rows = sorted(rows, key = lambda i: (i['favorite']), reverse = True)
    return dict(class_rows = rows)

@action('resources/<c>')
@action.uses(url_signer, auth.user, 'resources.html')
def resources(c = None):
    assert c is not None
    
    #user = get_user_email()
    rows = db(db.resources.sym == c).select().as_list()
    
    #print(rows)
    #for r in rows:
        #print(r['description'])
        #for d in r['description']:
            #print(d)
    '''r
    for r in rows:
        print(r['title'], r['likes'])
    rows = sorted(rows, key = lambda i: (i['likes']))
    print("Sorted: \n")
    for r in rows:
        print(r['title'], r['likes'])
    #print("Sorted: \n")
    #print(sorted(rows, key = lambda i: (i['likes'])))
    '''
    return dict(
        course = c,
        # This is the signed URL for the callback.
        load_classes_url = URL('load_classes', signer=url_signer),
        load_contacts_url = URL('load_contacts', signer=url_signer),
        add_contact_url = URL('add_contact', signer=url_signer),
        delete_contact_url = URL('delete_contact', signer=url_signer),
        like_url = URL('like', signer = url_signer),
        file_info_url = URL('file_info', signer=url_signer),
        obtain_gcs_url = URL('obtain_gcs', signer=url_signer),
        notify_url = URL('notify_upload', signer=url_signer),
        delete_url = URL('notify_delete', signer=url_signer),
    )


@action('load_contacts')
@action.uses(url_signer.verify(), db)
def load_contacts():
    user = get_user_email()
    #print(user)
   # rows = db(db.contact).select().as_list()
    db(db.resources.likes == None).delete()
    rows = db(db.resources).select().as_list()
    #print(rows)
    #for r in rows:
       # print(r['sym'], r['title'], r['likes'])
    #rows = sorted(rows, key = lambda i: (i['likes']))
    #print(type(rows))
    #rows.sort(key=testFunc)
    #print(rows)
    users = db(db.user.email == get_user_email()).select().as_list()
    #print(users)
    flag = 0
    for r in rows:
        #print(r['id'])
        for u in users:
            if u['item_id'] == r['id'] and u['email'] == get_user_email():
                flag = 1
            
        if(flag == 0):
            db.user.insert(
            item_id = r['id'],
            email = get_user_email(),
            status = 0
            )
        flag = 0

    #print(rows)
    users = db(db.user.email == get_user_email()).select().as_list()
    #print(users)

    #print(rows)
    #u = db(db.user.email == get) .select().as_list()
   # print(users)
    '''r
    for r in rows:
        print(r['id'])
    for u in users:
        print(u['item_id'])
    '''

    #ups = db(db.upload.owner == get_user_email()).select()
    #print(ups)
    #upss = db(db.upload).select()
    #print(ups)
   # for u in ups:
        #fileP = u['file_path']
        #tes = db(db.resources.id == u['resource_id']).select()
        #for x in tes:
            #print(x['title'])

        #download_url=gcs_url(GCS_KEYS, fileP, verb='GET')
        #print("NEW URL: ", download_url)


    rows = sorted(rows, key = lambda i: (i['likes']))
    
    return dict(rows=rows, user = user, users = users)



@action('add_contact', method="POST")
@action.uses(url_signer.verify(), db)
def add_contact():

    u = get_user_email()
    '''r
    id2 = db.contact.insert(
        comment=request.json.get('comment'),
        author=request.json.get('author'),
        email = get_user_email,
        status = 0,
    )
    '''
    link = request.json.get('link')
    
    
    if 'www.youtube.com/watch?v' in link: #is our link a youtube link?
        code = link.split("=", 1)[1]
        newLink = "https://www.youtube.com/embed/"
        newLink = newLink + code
        #print(newLink)
        link = newLink
    if link == '':

            link = None
    image_bool = request.json.get("image_bool")
    if image_bool: #if user added an image

        rows = db(db.upload.owner == get_user_email()).select()
        for r in rows:
            up_id = r['id'] #will get the most recent id
            image = r['download_url'] #get the most recent download_url
            #print(r['download_url'])
        #print(up_id)
    id = db.resources.insert(
        sym = request.json.get('author'), 
        title = request.json.get('title'), 
        description = request.json.get('comment'),
        image = None if image_bool is False else image,
        likes = 0, 
        dislikes = 0, 
        link = link)
    db.user.insert(
        item_id = id,
        email = get_user_email,
        status = 0,
    )

    if image_bool:
        db(db.upload.id == up_id).update(resource_id = id) #connect upload to specific resource

    #print("resource database added")
    
    return dict(id=id, u = u)

@action('delete_contact')
@action.uses(url_signer.verify(), db)
def delete_contact():
    id = request.params.get('id')
    assert id is not None
    db(db.upload.resource_id == id).delete()
    db(db.resources.id == id).delete()
    return "ok"


@action('like', method="POST")
@action.uses(url_signer.verify(), db)
def like():
    id = request.json.get("id")
    field = request.json.get("field")
    value = request.json.get("value")
    prev = request.json.get("prev")
    #print(prev)
   # db(db.resources.id == id).update(**{field: value})
    rows = db(db.resources.id == id).select().as_list()
    for r in rows:

        #print(r['likes'])
        likeVal = r['likes']
        disVal = r['dislikes']
    
    
    
    if value == 1:
        if prev == 0: #if we are currently unliked
            likeVal += 1
        
        if prev == 2: #if we are currently disliked
            likeVal += 1
            disVal -=1
        
        db(db.resources.id == id).update(likes = likeVal)
        db(db.resources.id == id).update(dislikes = disVal)

    if value == 0: #we are going from some stage to unliked 
        if prev == 1: #if we are currently liked
            likeVal -= 1
        if prev == 2: #if we are currently disliked
            disVal -= 1

        db(db.resources.id == id).update(likes = likeVal)
        db(db.resources.id == id).update(dislikes = disVal)
    if value == 2:
        if prev == 0: #if we are currently unliked
            disVal += 1
        
        if prev == 1: #if we are currently liked
            likeVal -= 1
            disVal +=1
        
        db(db.resources.id == id).update(likes = likeVal)
        db(db.resources.id == id).update(dislikes = disVal)
    
    
    rows = db(db.resources.id == id).select().as_list()
    #for r in rows:

        #print("likes: ", r['likes'])
        #print("dislikes: ", r['dislikes'])
    #db(db.user.item_id == id).update(**{field: value})
    db.user.update_or_insert(
        ((db.user.item_id == id) & (db.user.email == get_user_email())),
        item_id = id,
        email = get_user_email(),
        status = value
    )

@action('file_info')
@action.uses(url_signer.verify(), db)
def file_info():
    """Returns to the web app the information about the file currently
    uploaded, if any, so that the user can download it or replace it with
    another file if desired."""
    row = db(db.upload.owner == get_user_email()).select().first()
    # The file is present if the row is not None, and if the upload was
    # confirmed.  Otherwise, the file has not been confirmed as uploaded,
    # and should be deleted.
    if row is not None and not row.confirmed:
        # We need to try to delete the old file content.
        delete_path(row.file_path)
        row.delete_record()
        row = {}
    if row is None:
        # There is no file.
        row = {}
    file_path = row.get('file_path')
    return dict(
        file_name=row.get('file_name'),
        file_type=row.get('file_type'),
        file_date=row.get('file_date'),
        file_size=row.get('file_size'),
        file_path=file_path,
        download_url=None if file_path is None else gcs_url(GCS_KEYS, file_path),
        # These two could be controlled to get other things done.
        
        upload_enabled=True,
        download_enabled=True,
    )

@action('obtain_gcs', method="POST")
@action.uses(url_signer.verify(), db)
def obtain_gcs():
    """Returns the URL to do download / upload / delete for GCS."""
    verb = request.json.get("action")
    if verb == "PUT":
        mimetype = request.json.get("mimetype", "")
        file_name = request.json.get("file_name")
        extension = os.path.splitext(file_name)[1]
        # Use + and not join for Windows, thanks Blayke Larue
        file_path = BUCKET + "/" + str(uuid.uuid1()) + extension
        # Marks that the path may be used to upload a file.
        mark_possible_upload(file_path)
        upload_url = gcs_url(GCS_KEYS, file_path, verb='PUT',
                             content_type=mimetype)
        return dict(
            signed_url=upload_url,
            file_path=file_path
        )
    elif verb in ["GET", "DELETE"]:
        file_path = request.json.get("file_path")
        if file_path is not None:
            # We check that the file_path belongs to the user.
            r = db(db.upload.file_path == file_path).select().first()
            if r is not None and r.owner == get_user_email():
                # Yes, we can let the deletion happen.
                delete_url = gcs_url(GCS_KEYS, file_path, verb='DELETE')
                return dict(signed_url=delete_url)
        # Otherwise, we return no URL, so we don't authorize the deletion.
        return dict(signer_url=None)

@action('notify_upload', method="POST")
@action.uses(url_signer.verify(), db)
def notify_upload():
    """We get the notification that the file has been uploaded."""
    file_type = request.json.get("file_type")
    file_name = request.json.get("file_name")
    file_path = request.json.get("file_path")
    file_size = request.json.get("file_size")
    
    #print("File was uploaded:", file_path, file_name, file_type)
    # Deletes any previous file.
    rows = db(db.upload.owner == get_user_email()).select()
    
    for r in rows:
        if r.file_path != file_path:
            delete_path(r.file_path)
    # Marks the upload as confirmed.
    d = datetime.datetime.utcnow()
    download_url=gcs_url(GCS_KEYS, file_path, verb='GET')
    print("OLD URL: ", download_url)
    db.upload.insert(
        owner=get_user_email(),
        file_path=file_path,
        file_name=file_name,
        file_type=file_type,
        file_date=d,
        file_size=file_size,
        download_url=download_url,
        confirmed=True,
    )
    # Returns the file information.
    #rows = db(db.upload.owner == get_user_email()).select()
    #print(rows)
    #print("URL: ", download_url)
    return dict(
        download_url=download_url,
        file_date=d,
    )

@action('notify_delete', method="POST")
@action.uses(url_signer.verify(), db)
def notify_delete():
    file_path = request.json.get("file_path")
    # We check that the owner matches to prevent DDOS.
    db((db.upload.owner == get_user_email()) &
       (db.upload.file_path == file_path)).delete()
    return dict()

def delete_path(file_path):
    """Deletes a file given the path, without giving error if the file
    is missing."""
    try:
        bucket, id = os.path.split(file_path)
        gcs.delete(bucket[1:], id)
    except:
        # Ignores errors due to missing file.
        pass

def delete_previous_uploads():
    """Deletes all previous uploads for a user, to be ready to upload a new file."""
    previous = db(db.upload.owner == get_user_email()).select()
    for p in previous:
        # There should be only one, but let's delete them all.
        delete_path(p.file_path)
    #db(db.upload.owner == get_user_email()).delete()

def mark_possible_upload(file_path):
    """Marks that a file might be uploaded next."""
    delete_previous_uploads()
    db.upload.insert(
        owner=get_user_email(),
        file_path=file_path,
        confirmed=False,
    )











