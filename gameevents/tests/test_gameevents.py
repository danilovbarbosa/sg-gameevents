
import unittest
import time
import datetime
import json
import sys
#import base64
#from werkzeug.wrappers import Response
sys.path.append("..") 

#from flask import current_app

#from werkzeug.datastructures import Headers

from gameevents_app import create_app

#Extensions
from gameevents_app.extensions import db, LOG


from gameevents_app.models.gamingsession import GamingSession
from gameevents_app.models.client import Client
from gameevents_app.models.gameevent import GameEvent

#from gameevents_app.errors import InvalidGamingSession
#from sqlalchemy.orm.exc import NoResultFound
#from flask.ext.api.exceptions import AuthenticationFailed



class TestGameEvents(unittest.TestCase):
    """TODO: Create some tests trying to add duplicate data
    """
    @classmethod
    def setUpClass(self):
        
        self.app = create_app(testing=True)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        
        LOG.info("Initializing tests.")
        
        #Create a brand new test db
        db.create_all()
        
        #Add a clientid and apikey
        new_client = Client("myclientid", "myapikey")
        new_admin_client = Client("dashboard", "dashboardapikey")        
        
        #Adding one gaming session 
        new_gamingsession = GamingSession("aaaa")
        
        #Generating tokens        
        self.mytoken = new_client.generate_auth_token("aaaa")
        self.myexpiredtoken = new_client.generate_auth_token("aaaa", expiration=1)
        
        self.myadmintoken = new_admin_client.generate_auth_token()
        self.myexpiredadmintoken = new_admin_client.generate_auth_token(expiration=1)
        
        self.mybadtoken = "badlogin" + self.mytoken.decode()[8:]
        self.mybadtoken = self.mybadtoken.encode("ascii")
        
        time.sleep(3) #expire the token
        
        
        
        new_gamingsession2 = GamingSession('bbbb')
        #new_gamingsession2.status = False
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
        new_gameevent = GameEvent(new_gamingsession.id,gameevent)
        
        db.session.add(new_gamingsession)
        db.session.add(new_gamingsession2)
        db.session.add(new_gameevent)
        db.session.add(new_client)
        db.session.add(new_admin_client)
        try:
            db.session.commit()
        except Exception as e:
            LOG.error(e, exc_info=True)

    
    @classmethod
    def tearDownClass(self):
        LOG.info("======================Finished tests====================")
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    #@unittest.skip
    def test_token_existing_sessionid(self):
        """Make a test request for a login with valid credentials and existing sessionid.
        """
        requestdata = json.dumps(dict(clientid="myclientid", apikey="myapikey", sessionid = "aaaa"))
        response = self.client.post('/gameevents/api/v1.0/token', 
                                 data=requestdata, 
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        # Assert response is 200 OK.                                           
        self.assertEquals(response.status, "200 OK")
    

    def test_token_nonexisting_but_valid_sessionid(self):
        """Make a test request for a login with valid credentials and a valid - but still not in the db - sessionid.
        """
        requestdata = json.dumps(dict(clientid="myclientid", apikey="myapikey", sessionid="xxxx"))
        response = self.client.post('/gameevents/api/v1.0/token', 
                                 data=requestdata, 
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        # Assert response is 200 OK.                                           
        self.assertEquals(response.status, "200 OK")
        

    def test_token_invalid_sessionid(self):
        """Make a test request for a login with valid credentials but invalid sessionid.
        """
        requestdata = json.dumps(dict(clientid="myclientid", apikey="myapikey", sessionid="zzzz"))
        response = self.client.post('/gameevents/api/v1.0/token', 
                                 data=requestdata, 
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        # Assert response is 200 OK.                                           
        self.assertEquals(response.status, "401 UNAUTHORIZED")
        
    def test_get_admin_token(self):
        """Make a test request for a login with valid credentials and existing sessionid.
        """
        requestdata = json.dumps(dict(clientid="dashboard", apikey="dashboardapikey"))
        response = self.client.post('/gameevents/api/v1.0/token', 
                                 data=requestdata, 
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        # Assert response is 200 OK.                                           
        self.assertEquals(response.status, "200 OK")
    

    def test_token_badparams(self):
        """Make a test request with invalid/missing parameters.
        """
        requestdata = json.dumps(dict(clientid="myclientid"))
        response = self.client.post('/gameevents/api/v1.0/token', 
                                 data=requestdata, 
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        # Assert response is 400 BAD REQUEST.                                           
        self.assertEquals(response.status, "400 BAD REQUEST")
        

    def test_token_invalid_apikey(self):
        """Make a test request for a token with valid client id, invalid apikey and valid sessionid.
        """
        requestdata = json.dumps(dict(clientid="myclientidaaaaa", apikey="myapikeyaaaa", sessionid="aaaa"))
        response = self.client.post('/gameevents/api/v1.0/token', 
                                 data=requestdata, 
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        # Assert response is 200 OK.                                           
        self.assertEquals(response.status, "401 UNAUTHORIZED")
 

    def test_token_invalid_clientid(self):
        """Make a test request for a login with invalid client id and valid sessionid.
        """
        requestdata = json.dumps(dict(clientid="myclientid", apikey="myapikeyaaaa", sessionid="aaaa"))
        response = self.client.post('/gameevents/api/v1.0/token', 
                                 data=requestdata, 
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        # Assert response is 200 OK.                                           
        self.assertEquals(response.status, "401 UNAUTHORIZED")       
        
    
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
        response = self.client.post('/gameevents/api/v1.0/commitevent', 
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
        response = self.client.post('/gameevents/api/v1.0/commitevent', 
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
        response = self.client.post('/gameevents/api/v1.0/commitevent', 
                                 data=requestdata, 
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        self.assertEquals(response.status, "401 UNAUTHORIZED")
      
     
    def test_getgameevents(self):
        token = self.mytoken.decode()
        sessionid = "aaaa"
        requestdata = json.dumps(dict(token=token, sessionid = sessionid))
        response = self.client.post('/gameevents/api/v1.0/events', 
                                 data=requestdata, 
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        self.assertEquals(response.status, "200 OK")
     
      
    def test_getgameevents_badtoken(self):
        token = self.mybadtoken.decode()
        sessionid = "aaaa"
        requestdata = json.dumps(dict(token=token, sessionid = sessionid))
        response = self.client.post('/gameevents/api/v1.0/events', 
                                 data=requestdata, 
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        self.assertEquals(response.status, "401 UNAUTHORIZED")


    def test_newclient_admintoken(self):
        token = self.myadmintoken.decode()
        requestdata = json.dumps(dict(token=token, clientid="testclientid", apikey="testapikey"))
        response = self.client.post('/gameevents/api/v1.0/admin/client', 
                                 data=requestdata, 
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        self.assertEquals(response.status, "201 CREATED")

        
    def test_newexistingclient(self):
        token = self.myadmintoken.decode()
        requestdata = json.dumps(dict(token=token, clientid="myclientid", apikey="testapikey"))
        response = self.client.post('/gameevents/api/v1.0/admin/client',
                                 data=requestdata, 
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        self.assertEquals(response.status, "409 CONFLICT")
        
    def test_newclient_nonadmintoken(self):
        token = self.mytoken.decode()
        requestdata = json.dumps(dict(token=token, clientid="testclientid", apikey="testapikey"))
        response = self.client.post('/gameevents/api/v1.0/admin/client', 
                                 data=requestdata, 
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        self.assertEquals(response.status, "401 UNAUTHORIZED")
        
    def test_newclient_expiredadmintoken(self):
        token = self.myexpiredadmintoken.decode()
        requestdata = json.dumps(dict(token=token, clientid="testclientid", apikey="testapikey"))
        response = self.client.post('/gameevents/api/v1.0/admin/client', 
                                 data=requestdata, 
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        self.assertEquals(response.status, "401 UNAUTHORIZED")
                
    def test_newclient_badtoken(self):
        token = self.mybadtoken.decode()
        requestdata = json.dumps(dict(token=token, clientid="testclientid", apikey="testapikey"))
        response = self.client.post('/gameevents/api/v1.0/admin/client', 
                                 data=requestdata, 
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        self.assertEquals(response.status, "401 UNAUTHORIZED")
        
        
    def test_getsessions_validtoken(self):
        token = self.myadmintoken.decode()   
        
        requestdata = json.dumps(dict(token=token))
        response = self.client.post('/gameevents/api/v1.0/sessions', 
                                 data=requestdata, 
                                 content_type = 'application/json', 
                                 follow_redirects=True)
       
        json_results = json.loads(response.get_data().decode())
        self.assertEquals(response.status, "200 OK")
        self.assertEquals(json_results["count"], 2)
        
if __name__ == '__main__':
    unittest.main()