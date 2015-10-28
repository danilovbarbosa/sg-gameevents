'''
Main module for starting the gameevents service. Imports required 
modules from Flask (including DB and auth modules, 
and sets up logging.
'''

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

from flask.ext.httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

# Logging when in production:
import os
import sys
from config import TMPDIR
import logging
from logging.handlers import RotatingFileHandler
#from logging import StreamHandler

if not app.debug:
    file_handler = RotatingFileHandler(os.path.join(TMPDIR, 'gameevents.log.txt'), 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    #app.logger = logging.getLogger(__name__)
    #app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('Game Events Service Start Up')
else:
    file_handler = RotatingFileHandler(os.path.join(TMPDIR, 'gameevents-debug.log.txt'), 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(file_handler)
    app.logger.debug('Game Events Service Start Up - Debugging!')
    
from app import apiviews, controller
