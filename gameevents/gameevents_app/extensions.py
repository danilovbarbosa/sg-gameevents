'''
Flask and other extensions instantiated here.

To avoid circular imports with views and create_app(), extensions are instantiated here. They will be initialized
(calling init_app()) in __init__.py.
'''
from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy()

#Logging
from logging import getLogger
LOG = getLogger(__name__) 