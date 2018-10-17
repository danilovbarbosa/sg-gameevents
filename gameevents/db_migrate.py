'''
Created on 15 Oct 2015

@author: mbrandaoca
'''
import imp
from migrate.versioning import api
from gameevents_app import db
from configurationProj import SQLALCHEMY_DATABASE_URI
from configurationProj import SQLALCHEMY_MIGRATE_REPO

#####Added import models because it's necessary for the db_migrate 
from gameevents_app.models.client import Client
from gameevents_app.models.gameevent import GameEvent
from gameevents_app.models.session import Session

v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
migration = SQLALCHEMY_MIGRATE_REPO + ('/versions/%03d_migration.py' % (v+1))
tmp_module = imp.new_module('old_model')
old_model = api.create_model(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
exec(old_model, tmp_module.__dict__)
script = api.make_update_script_for_model(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, tmp_module.meta, db.metadata)
open(migration, "wt").write(script)
api.upgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
print('New migration saved as ' + migration)
print('Current database version: ' + str(v))