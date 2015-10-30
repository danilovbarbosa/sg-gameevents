'''
Created on 14 Oct 2015

@author: mbrandaoca
'''
# config2/test.py
import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'gamingsession.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

TMPDIR = os.path.join(basedir, 'tmp')

DEFAULT_TOKEN_DURATION = 600 #IN SECONDS

WTF_CSRF_ENABLED = True
SECRET_KEY = 'heytheredonottrytomesswithmemister'
