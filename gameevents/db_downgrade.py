#!flask/bin/python
from migrate.versioning import api
from configurationProj import SQLALCHEMY_DATABASE_URI
from configurationProj import SQLALCHEMY_MIGRATE_REPO

#####Added import models because it's necessary for the db_migrate 
from gameevents_app.models.client import Client
from gameevents_app.models.gameevent import GameEvent
from gameevents_app.models.session import Session

v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
api.downgrade(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, v - 1)
v = api.db_version(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
print('Current database version: ' + str(v))
