'''
Main module for starting the gameevents service. Imports required 
modules from Flask (including DB and auth modules, 
and sets up logging.
'''
import os
import sys

from flask import Flask

import config

from .extensions import db



def create_app(testing=False):
    # We are using the "Application Factory"-pattern here:
    # http://flask.pocoo.org/docs/patterns/appfactories/

    app = Flask(__name__)
    
    # Our application uses blueprints. Import and register the blueprint:
    from .views import gameevents, admin
    #from .views import auth_blueprint
    app.register_blueprint(gameevents)
    app.register_blueprint(admin)
    #app.register_blueprint(auth_blueprint)  


    # Configure app
    app.config.from_object('config')
    
    if testing:
        app.config['TESTING'] = True
        app.debug = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI_TEST
        app.config['LOG_FILENAME'] = config.LOG_FILENAME_TEST
    
        
    # Init database
    db.init_app(app)

    
    # Logging when in production:
    import logging
    from logging.handlers import RotatingFileHandler
    #from logging import StreamHandler
    
    file_handler = RotatingFileHandler(os.path.join(app.config['TMPDIR'], app.config['LOG_FILENAME']), 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    #app.logger = logging.getLogger(__name__)
    app.logger.setLevel(logging.DEBUG)
    #file_handler.setLevel(logging.DEBUG)
    file_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(file_handler)
    app.logger.info('Game Events Start Up...')   


    return app
