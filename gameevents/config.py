'''
Created on 14 Oct 2015

@author: mbrandaoca
'''
# config2/test.py
import os
basedir = os.path.abspath(os.path.dirname(__file__))

#Flask stuff
SQLITE_DB = 'gamingevents.db'
#SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, SQLITE_DB)
SQLALCHEMY_DATABASE_URI = "mysql://gameevents:gameevents@localhost/gameevents"
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
WTF_CSRF_ENABLED = True
SECRET_KEY = 'heytheredonottrytomesswithmemister'

#Other config
SQLITE_DB_TEST = 'gamingevents_testing.db'
#SQLALCHEMY_DATABASE_URI_TEST = 'sqlite:///' + os.path.join(basedir, SQLITE_DB_TEST)
SQLALCHEMY_DATABASE_URI_TEST = "mysql://gameevents:gameevents@localhost/gameevents_test"
TMPDIR = os.path.join(basedir, 'tmp')
LOG_FILENAME = "gameevents.log.txt"
LOG_FILENAME_TEST = "gameevents_testing.log.txt"

DEFAULT_TOKEN_DURATION = 600 #IN SECONDS
