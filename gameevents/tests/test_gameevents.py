import os
import unittest

from config import basedir
from app import app, db
from app import models, controller

#engine = None

class TestGameEvents(unittest.TestCase):
    
    @classmethod
    def setUpClass(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'gamingevents_test.db')
        self.app = app.test_client()
        db.create_all()
        
        #Adding one record
        new_gamingsession = models.GamingSession()
        db.session.add(new_gamingsession)
        db.session.commit()

    
    @classmethod
    def tearDownClass(self):
        db.session.remove()
        db.drop_all()
        
        
    def test_startgamingsession(self):
        newsessionid = controller.startgamingsession()
        self.assertEqual(newsessionid, 2)
                
    @unittest.expectedFailure
    def test_finishgamingsession(self):
        self.fail("Not implemented")
        
    @unittest.expectedFailure
    def test_recordgameevent(self):
        self.fail("Not implemented")
        
    @unittest.expectedFailure
    def test_getgameevents(self):
        self.fail("Not implemented")
    
    def test_getgamesessionstatus(self):
        sessionid = 1
        self.assertEqual(controller.getgamingsessionstatus(sessionid), True, "Session status is True (active)")
        
    def test_getnonexistentgamesessionstatus(self):
        sessionid = 100000
        self.assertEqual(controller.getgamingsessionstatus(sessionid), False, "Session status is False (active)")
        
if __name__ == '__main__':
    unittest.main()