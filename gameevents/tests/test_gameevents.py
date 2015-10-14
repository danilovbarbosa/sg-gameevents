import unittest
import datetime

from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import Session

from base import Base
from entities import *
from gameevents import *

class TestGameEvents(unittest.TestCase):
    
    @classmethod
    def setUpClass(self):
        print("Setting up test, creating database.") 
        self.engine = create_engine('sqlite:///gamingsession_test.db', echo=False)
        self.session = Session(self.engine)
        Base.metadata.create_all(self.engine)    
        
        #Add one record
        new_gamingsession = GamingSession()
        dbsession.add(new_gamingsession)
        dbsession.commit()

    
    @classmethod
    def tearDownClass(self):
        print("Tearing down database.") 
        Base.metadata.drop_all(self.engine)
        
        
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