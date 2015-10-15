import unittest
import datetime

import os

from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import Session

from base import Base
from gameevents import GameEvents

import models

import db
from config.test import *

from app import create_app
from db import *

#engine = None

class TestGameEvents(unittest.TestCase):
    
    @classmethod
    def setUpClass(self):
        #self.app = create_app(SQLALCHEMY_DATABASE_URI)
        print("Setting up test, creating database at %s." % SQLALCHEMY_DATABASE_URI) 
        db.init_engine(SQLALCHEMY_DATABASE_URI)
        db.init_db()
        #Base.metadata.create_all(bind=engine)
        #Base.metadata.create_all(engine)
        session = db.get_session()
        #print(session)
        #print('Created database, now adding one entry.') 
        #Add one record
        new_gamingsession = models.GamingSession()
        session.add(new_gamingsession)
        session.commit()

    
    @classmethod
    def tearDownClass(self):
        print("Tearing down database.") 
        #engine = db.init_engine(SQLALCHEMY_DATABASE_URI)
        #Base.metadata.drop_all(bind=engine)
        
        
    def test_startgamingsession(self):
        print("Testing: add one game session.") 
        #Start a gaming session
        newsessionid = GameEvents().startgamingsession()
        self.assertEqual(newsessionid, 2)
                
    @unittest.expectedFailure
    def test_finishgamingsession(self):
        print("Testing: failed test 1") 
        self.fail("Not implemented")
        
    @unittest.expectedFailure
    def test_recordgameevent(self):
        print("Testing: failed test 2") 
        self.fail("Not implemented")
        
    @unittest.expectedFailure
    def test_getgameevents(self):
        print("Testing: failed test 3") 
        self.fail("Not implemented")
    
    def test_getgamesessionstatus(self):
        print("Testing: get gaming session status") 
        sessionid = 1
        self.assertEqual(GameEvents().getgamingsessionstatus(sessionid), True, "Session status is True (active)")
        
    def test_getnonexistentgamesessionstatus(self):
        print("Testing: get gaming session status from non-existent session") 
        sessionid = 100000
        self.assertEqual(GameEvents().getgamingsessionstatus(sessionid), False, "Session status is False (active)")
        
if __name__ == '__main__':
    unittest.main()