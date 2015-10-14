'''
Created on 14 Oct 2015

@author: mbrandaoca
'''

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from base import Base

engine = None
mysessionmaker = sessionmaker()
mydb = scoped_session(sessionmaker)

def configure_engine(uri, **kwargs):
    global mysessionmaker, engine, mydb

    engine = create_engine(uri, **kwargs, echo=True)
    mydb.remove()
    mysessionmaker.configure(bind=engine)

def init_engine(uri, **kwargs):
    global engine
    engine = create_engine(uri, **kwargs, echo=True)
    return engine

def get_session():
    db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
    return db_session

def init_db():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    from entities import GamingSession
    Base.metadata.create_all(bind=engine)



