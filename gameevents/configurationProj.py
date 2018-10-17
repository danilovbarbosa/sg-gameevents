import os
basedir = os.path.abspath(os.path.dirname(__file__))

#Flask stuff
# SQLALCHEMY_DATABASE_URI = "mysql://gameevents:gameevents@localhost/gameevents"
SQLALCHEMY_DATABASE_URI = "mysql://root:password@localhost/gameevents"
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
WTF_CSRF_ENABLED = False
SECRET_KEY = 'heytheredonottrytomesswithmemister'

#Other config
SQLALCHEMY_DATABASE_URI_TEST = "mysql://root:password@localhost/gameevents_test"
TMPDIR = os.path.join(basedir, '..', 'tmp')
LOG_FILENAME = "gameevents.log.txt"
LOG_FILENAME_TEST = "gameevents_testing.log.txt"

DEFAULT_TOKEN_DURATION = 600 #IN SECONDS

DEBUB = True

