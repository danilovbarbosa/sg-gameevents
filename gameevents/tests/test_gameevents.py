import os
import unittest
import time
import datetime

from config import basedir
from app import app, db
from app import models, controller, errors

from app.errors import SessionNotActive
from sqlalchemy.orm.exc import NoResultFound
#from flask.ext.api.exceptions import AuthenticationFailed

import json

#engine = None

class TestGameEvents(unittest.TestCase):
    
    @classmethod
    def setUpClass(self):
        app.logger.debug("Initializing tests.")
        app.config['TESTING'] = True
        app.debug = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'gamingevents_test.db')
        
        # Use Flask's test client for our test.
        self.app = app.test_client()
        
        #Create a brand new test db
        db.create_all()
        
        #Add a clientid and apikey
        new_client = models.Client("myclientid", "myapikey")        
        self.mytoken = new_client.generate_auth_token()
        
        self.myexpiredtoken = new_client.generate_auth_token(1)
        
        time.sleep(3) #expire the token
        
        #Adding one gaming session and one game event
        new_gamingsession = models.GamingSession("aaaa")
        new_gamingsession2 = models.GamingSession('bbbb')
        new_gamingsession2.status = False
        gameevent = '''<event name="INF_STEALTH_FOUND">
                           <text>With the adjustment made to your sensors, you pick up a signal! You attempt to hail them, but get no response.</text>
                           <ship load="INF_SHIP_STEALTH" hostile="false"/>
                           <choice>
                              <text>Attack the Stealth ship.</text>
                                <event>
                                    <ship load="INF_SHIP_STEALTH" hostile="true"/>
                                </event>
                           </choice>
                        </event>'''
        new_gameevent = models.GameEvent(1,gameevent)
        
        db.session.add(new_gamingsession)
        db.session.add(new_gamingsession2)
        db.session.add(new_gameevent)
        db.session.add(new_client)
        db.session.commit()
        
        


    
    @classmethod
    def tearDownClass(self):
        db.session.remove()
        db.drop_all()
        
        
    def test_startgamingsession(self):
        # There are already two sessions, the third should have ID 3
        sessionid = "cccc"
        newsessionid = controller.startgamingsession(sessionid)
        self.assertEqual(newsessionid, 3)
                
    @unittest.expectedFailure
    def test_finishgamingsession(self):
        self.fail("Not implemented")
        
    def test_recordgameevent(self):
        token = self.mytoken
        timestamp = str(datetime.datetime.now())
        gameevent = '''<event name="INF_STEALTH_FOUND">
                           <text>With the adjustment made to your sensors, you pick up a signal! You attempt to hail them, but get no response.</text>
                           <ship load="INF_SHIP_STEALTH" hostile="false"/>
                           <choice>
                              <text>Attack the Stealth ship.</text>
                                <event>
                                    <ship load="INF_SHIP_STEALTH" hostile="true"/>
                                </event>
                           </choice>
                        </event>'''
        result = controller.recordgameevent(token, timestamp, gameevent)
        
        self.assertTrue(result)
        
    '''def test_recordgameeventinactivesession(self):
        token = self.myexpiredtoken
        timestamp = str(datetime.datetime.now())
        gameevent = ''<event name="INF_STEALTH_LOST">
                           <choice>
                              <text>Lose the Stealth ship.</text>
                                <event>
                                    <ship load="INF_SHIP_STEALTH" hostile="false"/>
                                </event>
                           </choice>
                        </event>''
        
        with self.assertRaises(SessionNotActive):
            controller.recordgameevent(token, timestamp, gameevent)'''

    '''
    def test_recordgameeventinexistentsession(self):
        sessionid = "abcde"
        timestamp = str(datetime.datetime.now())
        gameevent = ''<event name="INF_STEALTH_LOST">
                           <choice>
                              <text>Lose the Stealth ship.</text>
                                <event>
                                    <ship load="INF_SHIP_STEALTH" hostile="false"/>
                                </event>
                           </choice>
                        </event>''
        
        with self.assertRaises(NoResultFound):
            controller.recordgameevent(sessionid,timestamp, gameevent)'''

        
    def test_getgameevents(self):
        sessionid = 1
        result = controller.getgameevents(sessionid)
        self.maxDiff = None
        
        #Manually create the game event as it should appear in the database after adding it via controller
        gameevent = '''<event name="INF_STEALTH_FOUND">
                           <text>With the adjustment made to your sensors, you pick up a signal! You attempt to hail them, but get no response.</text>
                           <ship load="INF_SHIP_STEALTH" hostile="false"/>
                           <choice>
                              <text>Attack the Stealth ship.</text>
                                <event>
                                    <ship load="INF_SHIP_STEALTH" hostile="true"/>
                                </event>
                           </choice>
                        </event>'''
        new_gameevent = models.GameEvent(1,gameevent)
        new_gameevent.id = 1
        
        expected = [new_gameevent]
        self.assertEqual(expected, result)
        
    def test_getgameeventsemptylist(self):
        #Session id exists, but no game events, should return empty list
        sessionid = 2 
        result = controller.getgameevents(sessionid)
        expected = [] # Empty list
        self.assertEqual(expected, result)
        
    def test_getgameeventsnonexistent(self):
        #Session id does not exist, should raise exception
        sessionid = 10000
        with self.assertRaises(NoResultFound):
            result = controller.getgameevents(sessionid)
    
    def test_getgamesessionstatus(self):
        sessionid = 1
        self.assertEqual(controller.getgamingsessionstatus(sessionid), True, "Session status is True (active)")
        
    def test_getnonexistentgamesessionstatus(self):
        sessionid = 100000
        with self.assertRaises(NoResultFound):
            controller.getgamingsessionstatus(sessionid)
            
        
    def test_credentialslogin(self):
        # Make a test request for a token
        requestdata = json.dumps(dict(clientid="myclientid", apikey="myapikey", sessionid = "aaaa"))
        response = self.app.post('/gameevents/api/v1.0/token', 
                                 data=requestdata, 
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        # Assert response is 200 OK.                                           
        self.assertEquals(response.status, "200 OK")
        
    def test_tokenlogin(self):
        # Make a test request for a token
        requestdata = json.dumps(dict(clientid=self.mytoken.decode(), sessionid="aaaa"))
        response = self.app.post('/gameevents/api/v1.0/token', 
                                 data=requestdata, 
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        # Assert response is 200 OK.                                           
        self.assertEquals(response.status, "200 OK")
        
    def test_badtokenlogin(self):
        # Make a test request for a token
        badtoken = "badlogin" + self.mytoken.decode()[8:]
        #badtoken = badtoken.encode("ascii")
        requestdata = json.dumps(dict(clientid=badtoken, sessionid="aaaa"))
        response = self.app.post('/gameevents/api/v1.0/token', 
                                 data=requestdata, 
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        # Assert response is 200 OK.                                           
        self.assertEquals(response.status, "401 UNAUTHORIZED")
        
    def test_expiredtokenlogin(self):
        # Make a test request with an expired token
        token = self.myexpiredtoken.decode()
        
        requestdata = json.dumps(dict(clientid=token, sessionid="aaaa"))
        response = self.app.post('/gameevents/api/v1.0/token', 
                                 data=requestdata, 
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        # Assert response is 200 OK.                                           
        self.assertEquals(response.status, "401 UNAUTHORIZED")
        
    def test_badcredentialslogin(self):
        # Make a test request for a token
        requestdata = json.dumps(dict(clientid="myclientid2", apikey="myapikey2", sessionid="aaaa"))
        response = self.app.post('/gameevents/api/v1.0/token', 
                                 data=requestdata, 
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        # Assert response is Unauthorized.                                           
        self.assertEquals(response.status, "401 UNAUTHORIZED")
        
if __name__ == '__main__':
    unittest.main()