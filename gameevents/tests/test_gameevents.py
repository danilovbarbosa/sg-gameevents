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
        
        #Adding one gaming session and one game event
        new_gamingsession = models.GamingSession()
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
        db.session.add(new_gameevent)
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
        
    def test_recordgameevent(self):
        sessionid = 1
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
        result = controller.recordgameevent(sessionid, gameevent)
        
        self.assertTrue(result)
        
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
    
    def test_getgamesessionstatus(self):
        sessionid = 1
        self.assertEqual(controller.getgamingsessionstatus(sessionid), True, "Session status is True (active)")
        
    def test_getnonexistentgamesessionstatus(self):
        sessionid = 100000
        self.assertEqual(controller.getgamingsessionstatus(sessionid), False, "Session status is False (active)")
        
if __name__ == '__main__':
    unittest.main()