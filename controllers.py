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

from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_user_email

url_signer = URLSigner(session)



@action('index')
@action.uses(url_signer, auth.user, 'index.html')
def index():
    
    #user = get_user_email()
    return dict(
        # This is the signed URL for the callback.
        load_contacts_url = URL('load_contacts', signer=url_signer),
        add_contact_url = URL('add_contact', signer=url_signer),
        delete_contact_url = URL('delete_contact', signer=url_signer),
        like_url = URL('like', signer = url_signer),
    )
@action('resources/<c>')
@action.uses(url_signer, auth.user, 'resources.html')
def resources(c = None):
    assert c is not None
    #user = get_user_email()
    rows = db(db.resources.sym == c).select()
    #print(rows)
    return dict(
        course = c,
        # This is the signed URL for the callback.
        load_contacts_url = URL('load_contacts', signer=url_signer),
        add_contact_url = URL('add_contact', signer=url_signer),
        delete_contact_url = URL('delete_contact', signer=url_signer),
        like_url = URL('like', signer = url_signer),
    )

# This is our very first API function.
@action('load_contacts')
@action.uses(url_signer.verify(), db)
def load_contacts():
    user = get_user_email()
    #print(user)
   # rows = db(db.contact).select().as_list()
    rows = db(db.resources).select().as_list()
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

   
    return dict(rows=rows, user = user, users = users)

@action('add_contact', method="POST")
@action.uses(url_signer.verify(), db)
def add_contact():
    u = get_user_email()
    id2 = db.contact.insert(
        comment=request.json.get('comment'),
        author=request.json.get('author'),
        email = get_user_email,
        status = 0,
    )
    id = db.resources.insert(sym = request.json.get('author'), title = request.json.get('title'), description = request.json.get('comment'), likes = 0, dislikes = 0)
    db.user.insert(
        item_id = id,
        email = get_user_email,
        status = 0,
    )

    
    return dict(id=id, u = u)

@action('delete_contact')
@action.uses(url_signer.verify(), db)
def delete_contact():
    id = request.params.get('id')
    assert id is not None
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

     
    

    
    #print(value)



