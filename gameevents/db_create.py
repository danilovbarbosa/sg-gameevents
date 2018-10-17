'''
Created on 15 Oct 2015

@author: mbrandaoca
'''
from migrate.versioning import api
from configurationProj import SQLALCHEMY_DATABASE_URI
from configurationProj import SQLALCHEMY_MIGRATE_REPO
from gameevents_app import db, create_app
import os.path
import sys

app = create_app()
with app.app_context():
    db.create_all()
    
    
    #Add the admin user
    from gameevents_app.models.client import Client
    #####Added import models because it's necessary for the db_migrate 
    from gameevents_app.models.gameevent import GameEvent
    from gameevents_app.models.session import Session
    
    #Generate random password
    from random import choice
    import string
    chars = string.ascii_letters + string.digits
    length = 16
    randompass = ''.join(choice(chars) for _ in range(length))
    
    admin = Client('administrator', randompass, "admin")
    db.session.add(admin)
    
    try:
        
        db.session.commit()
        sys.stdout.write("Created administrator client: %s, with random apikey %s \n" % (admin.clientid, randompass) )
    except Exception as e:
        sys.stdout.write(e)
        db.session.rollback()
        db.session.flush() # for resetting non-commited .add()
        
    
if not os.path.exists(SQLALCHEMY_MIGRATE_REPO):
    api.create(SQLALCHEMY_MIGRATE_REPO, 'database repository')
    api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
else:
    api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, api.version(SQLALCHEMY_MIGRATE_REPO))