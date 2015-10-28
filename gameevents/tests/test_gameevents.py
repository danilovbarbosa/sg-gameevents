import os
import unittest
import time
import datetime
import json

from config import basedir, TMPDIR
from app import app, db
from app import models, controller, errors

from app.errors import InvalidGamingSession
from sqlalchemy.orm.exc import NoResultFound
#from flask.ext.api.exceptions import AuthenticationFailed

# Logging:
import logging
from logging.handlers import RotatingFileHandler
 
file_handler_debug = RotatingFileHandler(os.path.join(TMPDIR, 'gameevents-unittests.log.txt'), 'a', 1 * 1024 * 1024, 10)
file_handler_debug.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
#file_handler_debug.setLevel(logging.DEBUG)
file_handler_debug.setLevel(logging.INFO)
app.logger.addHandler(file_handler_debug)
app.logger.info('Game Events Service Start Up - Debugging')



class TestGameEvents(unittest.TestCase):
    """TODO: Create some tests trying to add duplicate data
    """
    @classmethod
    def setUpClass(self):
        app.logger.info("Initializing tests.")
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
        
        #Adding one gaming session 
        new_gamingsession = models.GamingSession("aaaa", "myclientid")
        
        #Generating tokens        
        self.mytoken = new_gamingsession.generate_auth_token()
        self.mybadtoken = "badlogin" + self.mytoken.decode()[8:]
        self.mybadtoken = self.mybadtoken.encode("ascii")
        self.myexpiredtoken = new_gamingsession.generate_auth_token(1)
        time.sleep(3) #expire the token
        
        
        
        new_gamingsession2 = models.GamingSession('bbbb', "myclientid")
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
        new_gameevent = models.GameEvent(new_gamingsession.id,gameevent)
        
        db.session.add(new_gamingsession)
        db.session.add(new_gamingsession2)
        db.session.add(new_gameevent)
        db.session.add(new_client)
        try:
            db.session.commit()
        except Exception as e:
            app.logger.error(e, exc_info=True)

    
    @classmethod
    def tearDownClass(self):
        db.session.remove()
        db.drop_all()
    
    
    def test_login_existing_sid(self):
        """Make a test request for a login with valid credentials and existing sessionid.
        """
        requestdata = json.dumps(dict(clientid="myclientid", apikey="myapikey", sessionid = "aaaa"))
        response = self.app.post('/gameevents/api/v1.0/token', 
                                 data=requestdata, 
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        # Assert response is 200 OK.                                           
        self.assertEquals(response.status, "200 OK")
    
    
    def test_login_nonexisting_but_valid_sid(self):
        """Make a test request for a login with valid credentials and a valid - but still not in the db - sessionid.
        """
        requestdata = json.dumps(dict(clientid="myclientid", apikey="myapikey", sessionid="xxxx"))
        response = self.app.post('/gameevents/api/v1.0/token', 
                                 data=requestdata, 
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        # Assert response is 200 OK.                                           
        self.assertEquals(response.status, "200 OK")
        
    
    def test_login_invalid_sid(self):
        """Make a test request for a login with valid credentials but invalid sessionid.
        """
        requestdata = json.dumps(dict(clientid="myclientid", apikey="myapikey", sessionid="zzzz"))
        response = self.app.post('/gameevents/api/v1.0/token', 
                                 data=requestdata, 
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        # Assert response is 200 OK.                                           
        self.assertEquals(response.status, "401 UNAUTHORIZED")
    
    
    def test_badlogin(self):
        """Make a test request with invalid/missing parameters.
        """
        requestdata = json.dumps(dict(clientid="myclientid", apikey="myapikey"))
        response = self.app.post('/gameevents/api/v1.0/token', 
                                 data=requestdata, 
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        # Assert response is 400 BAD REQUEST.                                           
        self.assertEquals(response.status, "400 BAD REQUEST")
        
    
    def test_commit_gameevent_validtoken(self):
        token = self.mytoken.decode()
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
        timestamp = str(datetime.datetime.now())       
        
        requestdata = json.dumps(dict(token=token, timestamp=timestamp, gameevent=gameevent))
        app.logger.debug(requestdata)
        response = self.app.post('/gameevents/api/v1.0/commitevent', 
                                 data=requestdata, 
                                 content_type = 'application/json', 
                                 follow_redirects=True)

        self.assertEquals(response.status, "201 CREATED")
    
    
    def test_commit_gameevent_expiredtoken(self):
        token = self.myexpiredtoken.decode()
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
        timestamp = str(datetime.datetime.now())       
        
        requestdata = json.dumps(dict(token=token, timestamp=timestamp, gameevent=gameevent))
        app.logger.debug(requestdata)
        response = self.app.post('/gameevents/api/v1.0/commitevent', 
                                 data=requestdata, 
                                 content_type = 'application/json', 
                                 follow_redirects=True)

        self.assertEquals(response.status, "401 UNAUTHORIZED")
    
    
    def test_commit_gameevent_badtoken(self):
        token = self.mybadtoken.decode()
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
        timestamp = str(datetime.datetime.now())       
        
        requestdata = json.dumps(dict(token=token, timestamp=timestamp, gameevent=gameevent))
        app.logger.debug(requestdata)
        response = self.app.post('/gameevents/api/v1.0/commitevent', 
                                 data=requestdata, 
                                 content_type = 'application/json', 
                                 follow_redirects=True)

        self.assertEquals(response.status, "401 UNAUTHORIZED")
        
    def test_getgameevents(self):
        token = self.mytoken.decode()
        sessionid = "aaaa"
        requestdata = json.dumps(dict(token=token, sessionid=sessionid))
        app.logger.debug(requestdata)
        response = self.app.post('/gameevents/api/v1.0/events', 
                                 data=requestdata, 
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        app.logger.warning(response.get_data())
        self.assertEquals(response.status, "200 OK")
        
        
if __name__ == '__main__':
    unittest.main()