
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


from gameevents_app.models.session import Session
from gameevents_app.models.client import Client
from gameevents_app.models.gameevent import GameEvent

from uuid import UUID
import OpenSSL

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
        new_client = Client("myclientid", "myapikey", "normal")
        new_admin_client = Client("dashboard", "dashboardapikey", "admin")  
        db.session.add(new_client)
        db.session.add(new_admin_client)
        try:
            db.session.commit()
            LOG.info("=== Added clients ===")
        except Exception as e:
            LOG.error(e, exc_info=True)      
        
        #Generating gaming sessions ids
        self.newsessionid = UUID(bytes = OpenSSL.rand.bytes(16)).hex
        self.newsessionid2 = UUID(bytes = OpenSSL.rand.bytes(16)).hex
        self.newsessionid3 = UUID(bytes = OpenSSL.rand.bytes(16)).hex #session not in db
        self.unauthorized_sessionid = "ac52bb1d811356ab3a8e8711c5f7ac5d"
        
        new_session = Session(self.newsessionid, new_client.id)
        new_session2 = Session(self.newsessionid2, new_client.id)
        db.session.add(new_session)
        db.session.add(new_session2)
        try:
            db.session.commit()
            LOG.info("=== Added sessions ===")
            LOG.info("=== Session not in db: %s ===" % self.newsessionid3)
        except Exception as e:
            LOG.error(e, exc_info=True)
        
        #Generating tokens        
        self.mytoken = new_client.generate_auth_token(self.newsessionid)
        self.myexpiredtoken = new_client.generate_auth_token(self.newsessionid, expiration=1)
        
        self.mytokennewsession = new_client.generate_auth_token(self.newsessionid3)
        
        self.myadmintoken = new_admin_client.generate_auth_token()
        self.myexpiredadmintoken = new_admin_client.generate_auth_token(expiration=1)
        
        self.mybadtoken = "badlogin" + self.mytoken.decode()[8:]
        self.mybadtoken = self.mybadtoken.encode("ascii")
        
        self.xml_valid_event = """<event><timestamp>2015-11-29T12:10:57Z</timestamp>
        <action>STARTGAME</action><level></level><update></update><which_lix>
        </which_lix><result></result></event>""";
        self.json_valid_event = """[{
                "timestamp": "2015-11-29T12:10:57Z",
                "action": "STARTGAME",
                "which_lix": ""
              }]"""
        self.xml_invalid_event = """<event>a
         <action>STARTGAME</action>
         <timestamp>2015-11-29T12:10:57Z</timestamp>
         <which_lix />
      </event>"""
        self.json_invalid_event = """
                "timestamp": "2015-11-29T12:10:57Z",
                "action": "STARTGAME",,
                "which_lix": ""
              """
        self.xml_multiple_events = """<event>
         <action>STARTGAME</action>
         <timestamp>2015-11-29T12:10:57Z</timestamp>
         <which_lix />
      </event>
      <event>
         <action>ENDGAME</action>
         <timestamp>2015-11-29T13:10:57Z</timestamp>
         <which_lix />
      </event>"""
        
        self.json_multiple_events = """[{ "timestamp": "2015-11-29T12:10:57Z",
                "action": "STARTGAME",
                "which_lix": ""
              }, {
                "timestamp": "2015-11-29T13:10:57Z",
                "action": "ENDGAME",
                "which_lix": ""
              }]"""
        
        time.sleep(3) #expire the token
     
        new_gameevent = GameEvent(new_session.id,self.xml_valid_event)
        db.session.add(new_gameevent)        
        try:
            db.session.commit()
            LOG.info("=== Added game event. All set up. ===")
        except Exception as e:
            LOG.error(e, exc_info=True)

    
    @classmethod
    def tearDownClass(self):
        LOG.info("======================Finished tests====================")
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    
    def test_token_existing_sessionid(self):
        """Make a test request for a login with valid credentials and existing sessionid.
        """
        requestdata = json.dumps(dict(clientid="myclientid", apikey="myapikey", sessionid = self.newsessionid))
        response = self.client.post('/gameevents/api/v1.0/token', 
                                 data=requestdata, 
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        # Assert response is 200 OK.                                           
        self.assertEquals(response.status, "200 OK")
    

    def test_token_nonexisting_but_valid_sessionid(self):
        """Make a test request for a login with valid credentials and a valid - but still not in the db - sessionid.
        """
        requestdata = json.dumps(dict(clientid="myclientid", apikey="myapikey",  sessionid = self.newsessionid3))
        response = self.client.post('/gameevents/api/v1.0/token', 
                                 data=requestdata, 
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        # Assert response is 200 OK.                                           
        self.assertEquals(response.status, "200 OK")
        

    def test_token_invalid_sessionid(self):
        """Make a test request for a login with valid credentials but invalid sessionid.
        """
        requestdata = json.dumps(dict(clientid="myclientid", apikey="myapikey",  sessionid = "bablablabal"))
        response = self.client.post('/gameevents/api/v1.0/token', 
                                 data=requestdata, 
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        self.assertEquals(response.status, "400 BAD REQUEST")
        
    def test_token_unauthorized_sessionid(self):
        """Make a test request for a login with valid credentials but invalid sessionid.
        """
        requestdata = json.dumps(dict(clientid="myclientid", apikey="myapikey",  sessionid = self.unauthorized_sessionid))
        response = self.client.post('/gameevents/api/v1.0/token', 
                                 data=requestdata, 
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        self.assertEquals(response.status, "401 UNAUTHORIZED")
        
    def test_get_admin_token(self):
        """Make a test request for an admin login with valid credentials.
        """
        requestdata = json.dumps(dict(clientid="dashboard", apikey="dashboardapikey"))
        response = self.client.post('/gameevents/api/v1.0/token', 
                                 data=requestdata, 
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        # Assert response is 200 OK.                                           
        self.assertEquals(response.status, "200 OK")
    
#     def test_get_admin_token_master(self):
#         """Make a test request for a login with superuser (temporary!!!).
#         """
#         requestdata = json.dumps(dict(clientid="masteroftheuniverse", apikey="whatever"))
#         response = self.client.post('/gameevents/api/v1.0/token', 
#                                  data=requestdata, 
#                                  content_type = 'application/json', 
#                                  follow_redirects=True)
#         # Assert response is 200 OK.                                           
#         self.assertEquals(response.status, "401 UNAUTHORIZED")

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
        requestdata = json.dumps(dict(clientid="myclientidaaaaa", apikey="myapikeyaaaa", sessionid=self.newsessionid))
        response = self.client.post('/gameevents/api/v1.0/token', 
                                 data=requestdata, 
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        # Assert response is 200 OK.                                           
        self.assertEquals(response.status, "401 UNAUTHORIZED")
 

    def test_token_invalid_clientid(self):
        """Make a test request for a login with invalid client id and valid sessionid.
        """
        requestdata = json.dumps(dict(clientid="myclientid", apikey="myapikeyaaaa", sessionid=self.newsessionid))
        response = self.client.post('/gameevents/api/v1.0/token', 
                                 data=requestdata, 
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        # Assert response is 200 OK.                                           
        self.assertEquals(response.status, "401 UNAUTHORIZED")       
        
    
    def test_commit_xmlgameevent_validtoken(self):
        token = self.mytoken.decode()
        headers = {}
        sessionid = self.newsessionid
        headers['X-AUTH-TOKEN'] = token
        gameevent = self.xml_valid_event
        timestamp = str(datetime.datetime.now())    
        requestdata = json.dumps(dict(timestamp=timestamp, events=gameevent))
        response = self.client.post('/gameevents/api/v1.0/sessions/%s/events' % sessionid, 
                                 data=requestdata, 
                                 headers=headers,
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        self.assertEquals(response.status, "400 BAD REQUEST")  
        
    def test_commit_gameevent_incompletejsonrequest(self):
        token = self.mytoken.decode()
        headers = {}
        sessionid = self.newsessionid
        headers['X-AUTH-TOKEN'] = token
        requestdata = "{json:\"badlyformed\""
        response = self.client.post('/gameevents/api/v1.0/sessions/%s/events' % sessionid, 
                                 data=requestdata, 
                                 headers=headers,
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        self.assertEquals(response.status, "400 BAD REQUEST")  
        
    def test_commit_jsongameevent_validtoken(self):
        token = self.mytoken.decode()
        headers = {}
        headers['X-AUTH-TOKEN'] = token
        sessionid = self.newsessionid
        gameevent = self.json_valid_event
        timestamp = str(datetime.datetime.now())    
        requestdata = json.dumps(dict(timestamp=timestamp, events=gameevent))
        response = self.client.post('/gameevents/api/v1.0/sessions/%s/events' % sessionid, 
                                 data=requestdata, 
                                 headers=headers,
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        self.assertEquals(response.status, "201 CREATED")
        #self.assertFail()
        
    def test_commit_invalidjsongameevent_validtoken(self):
        token = self.mytoken.decode()
        headers = {}
        sessionid = self.newsessionid
        gameevent = self.json_invalid_event
        headers['X-AUTH-TOKEN'] = token
        timestamp = str(datetime.datetime.now())    
        requestdata = json.dumps(dict(timestamp=timestamp, events=gameevent))
        response = self.client.post('/gameevents/api/v1.0/sessions/%s/events' % sessionid, 
                                 data=requestdata, 
                                 headers=headers,
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        self.assertEquals(response.status, "400 BAD REQUEST")
            
        
    def test_commit_invalidxmlgameevent_validtoken(self):
        token = self.mytoken.decode()
        headers = {}
        sessionid = self.newsessionid
        headers['X-AUTH-TOKEN'] = token
        gameevent = self.xml_invalid_event
        timestamp = str(datetime.datetime.now())    
        requestdata = json.dumps(dict(timestamp=timestamp, events=gameevent))
        response = self.client.post('/gameevents/api/v1.0/sessions/%s/events' % sessionid, 
                                 data=requestdata, 
                                 headers=headers,
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        self.assertEquals(response.status, "400 BAD REQUEST")
           
        
    def test_commit_multiplexmlgameevent_validtoken(self):
        token = self.mytoken.decode()
        headers = {}
        sessionid = self.newsessionid
        headers['X-AUTH-TOKEN'] = token
        gameevent = self.xml_multiple_events
        timestamp = str(datetime.datetime.now())    
        requestdata = json.dumps(dict(timestamp=timestamp, events=gameevent))
        response = self.client.post('/gameevents/api/v1.0/sessions/%s/events' % sessionid, 
                                 data=requestdata, 
                                 headers=headers,
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        self.assertEquals(response.status, "400 BAD REQUEST")
          
        
    def test_commit_multiplejsongameevent_validtoken(self):
        token = self.mytoken.decode()
        headers = {}
        sessionid = self.newsessionid
        headers['X-AUTH-TOKEN'] = token
        gameevent = self.json_multiple_events
        timestamp = str(datetime.datetime.now())    
        requestdata = json.dumps(dict(timestamp=timestamp, events=gameevent))
        response = self.client.post('/gameevents/api/v1.0/sessions/%s/events' % sessionid, 
                                 data=requestdata, 
                                 headers=headers,
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        json_results = json.loads(response.get_data().decode())
        self.assertEquals(json_results["message"], "Created 2 new item(s).")
        self.assertEquals(response.status, "201 CREATED")
        #self.assertFail()  
        
    def test_commit_gameevent_validtoken_newsessionid(self):
        """A session not in the database, allowed in the UP service,
        cannot be used to add a new event. The session needs to be in the database
        when the client asks for a token!"""
        token = self.mytokennewsession.decode()
        sessionid = self.newsessionid3
        gameevent = self.json_valid_event
        timestamp = str(datetime.datetime.now())     
        headers = {}
        headers['X-AUTH-TOKEN'] = token
        
        requestdata = json.dumps(dict(timestamp=timestamp, events=gameevent))
        response = self.client.post('/gameevents/api/v1.0/sessions/%s/events' % sessionid, 
                                 data=requestdata, 
                                 headers=headers,
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        self.assertEquals(response.status, "404 NOT FOUND")
    

    def test_commit_gameevent_expiredtoken(self):
        token = self.myexpiredtoken.decode()
        sessionid = self.newsessionid
        gameevent = self.json_valid_event
        timestamp = str(datetime.datetime.now())
        requestdata = json.dumps(dict(timestamp=timestamp, events=gameevent))
        
        headers = {}
        headers['X-AUTH-TOKEN'] = token
        
        response = self.client.post('/gameevents/api/v1.0/sessions/%s/events' % sessionid, 
                                 data=requestdata, 
                                 headers=headers,
                                 content_type = 'application/json', 
                                 follow_redirects=True)

        self.assertEquals(response.status, "401 UNAUTHORIZED")
    
    
    def test_commit_gameevent_badtoken(self):
        sessionid = self.newsessionid
        token = self.mybadtoken.decode()
        gameevent = self.json_valid_event
        timestamp = str(datetime.datetime.now())       
        
        headers = {}
        headers['X-AUTH-TOKEN'] = token
        
        requestdata = json.dumps(dict(timestamp=timestamp, events=gameevent))
        response = self.client.post('/gameevents/api/v1.0/sessions/%s/events' % sessionid, 
                                 data=requestdata, 
                                 headers=headers,
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        self.assertEquals(response.status, "401 UNAUTHORIZED")
      
     
    def test_getgameevents(self):
        token = self.mytoken.decode()
        sessionid = self.newsessionid
        headers = {}
        headers['X-AUTH-TOKEN'] = token
        response = self.client.get('/gameevents/api/v1.0/sessions/%s/events' % sessionid, 
                                 headers=headers,
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        self.assertEquals(response.status, "200 OK")
     
      
    def test_getgameevents_badtoken(self):
        token = self.mybadtoken.decode()
        headers = {}
        headers['X-AUTH-TOKEN'] = token
        sessionid = self.newsessionid
        response = self.client.get('/gameevents/api/v1.0/sessions/%s/events' % sessionid, 
                                 headers=headers,
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        self.assertEquals(response.status, "401 UNAUTHORIZED")


    def test_newclient_admintoken(self):
        token = self.myadmintoken.decode()
        headers = {}
        headers['X-AUTH-TOKEN'] = token
        requestdata = json.dumps(dict(clientid="testclientid", apikey="testapikey"))
        response = self.client.post('/gameevents/api/v1.0/admin/clients', 
                                 data=requestdata, 
                                 headers=headers,
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        self.assertEquals(response.status, "201 CREATED")
        
    def test_newclient_bad_request_missing_params(self):
        requestdata = json.dumps(dict(clientid="lix", apikey="lixapikey"))
        response = self.client.post('/gameevents/api/v1.0/admin/clients', 
                                 data=requestdata, 
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        self.assertEquals(response.status, "400 BAD REQUEST")
        
        
    def test_newexistingclient(self):
        token = self.myadmintoken.decode()
        headers = {}
        headers['X-AUTH-TOKEN'] = token
        requestdata = json.dumps(dict(clientid="myclientid", apikey="testapikey"))
        response = self.client.post('/gameevents/api/v1.0/admin/clients',
                                 data=requestdata, 
                                 headers=headers,
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        self.assertEquals(response.status, "409 CONFLICT")
        
    def test_newclient_nonadmintoken(self):
        token = self.mytoken.decode()
        headers = {}
        headers['X-AUTH-TOKEN'] = token
        requestdata = json.dumps(dict(clientid="testclientid", apikey="testapikey"))
        response = self.client.post('/gameevents/api/v1.0/admin/clients', 
                                 data=requestdata,
                                 headers=headers, 
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        self.assertEquals(response.status, "401 UNAUTHORIZED")
        
    def test_newclient_expiredadmintoken(self):
        token = self.myexpiredadmintoken.decode()
        headers = {}
        headers['X-AUTH-TOKEN'] = token
        requestdata = json.dumps(dict(clientid="testclientid", apikey="testapikey"))
        response = self.client.post('/gameevents/api/v1.0/admin/clients', 
                                 data=requestdata, 
                                 headers=headers,
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        self.assertEquals(response.status, "401 UNAUTHORIZED")
                
    def test_newclient_badtoken(self):
        token = self.mybadtoken.decode()
        headers = {}
        headers['X-AUTH-TOKEN'] = token
        requestdata = json.dumps(dict(clientid="testclientid", apikey="testapikey"))
        response = self.client.post('/gameevents/api/v1.0/admin/clients', 
                                 data=requestdata, 
                                 headers=headers,
                                 content_type = 'application/json', 
                                 follow_redirects=True)
        self.assertEquals(response.status, "401 UNAUTHORIZED")
        
        
    def test_getsessions_validtoken(self):
        token = self.myadmintoken.decode()   
        headers = {}
        headers['X-AUTH-TOKEN'] = token

        response = self.client.get('/gameevents/api/v1.0/sessions', 
                                   headers=headers, 
                                   follow_redirects=True)
       
        #json_results = json.loads(response.get_data().decode())
        self.assertEquals(response.status, "200 OK")
        #self.assertEquals(response.headers["X-Total-Count"], '3')
        
    def test_getsessions_notoken(self):
        response = self.client.get('/gameevents/api/v1.0/sessions', 
                                   follow_redirects=True)
        self.assertEquals(response.status, "400 BAD REQUEST")
        
        
    def test_getsessions_invalidtoken(self):
        token = self.myexpiredadmintoken.decode()  
        headers = {}
        headers['X-AUTH-TOKEN'] = token
        response = self.client.get('/gameevents/api/v1.0/sessions', 
                                   headers=headers, 
                                   follow_redirects=True)       
        self.assertEquals(response.status, "401 UNAUTHORIZED")
      
        
if __name__ == '__main__':
    unittest.main()