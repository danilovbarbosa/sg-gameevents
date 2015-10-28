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
        

        
if __name__ == '__main__':
    unittest.main()