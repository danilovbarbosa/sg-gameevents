import os
import unittest

from config import basedir
from app import app, db
from app import models, controller, errors

from app.errors import SessionNotActive
from sqlalchemy.orm.exc import NoResultFound

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
        new_gamingsession2 = models.GamingSession()
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
        db.session.commit()


    
    @classmethod
    def tearDownClass(self):
        db.session.remove()
        db.drop_all()
        
        
    def test_startgamingsession(self):
        # There are already two sessions, the third should have ID 3
        newsessionid = controller.startgamingsession()
        self.assertEqual(newsessionid, 3)
                
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
        
    def test_recordgameeventinactivesession(self):
        sessionid = 2
        gameevent = '''<event name="INF_STEALTH_LOST">
                           <choice>
                              <text>Lose the Stealth ship.</text>
                                <event>
                                    <ship load="INF_SHIP_STEALTH" hostile="false"/>
                                </event>
                           </choice>
                        </event>'''
        with self.assertRaises(SessionNotActive):
            controller.recordgameevent(sessionid, gameevent)

    def test_recordgameeventinexistentsession(self):
        sessionid = 10000
        gameevent = '''<event name="INF_STEALTH_LOST">
                           <choice>
                              <text>Lose the Stealth ship.</text>
                                <event>
                                    <ship load="INF_SHIP_STEALTH" hostile="false"/>
                                </event>
                           </choice>
                        </event>'''
        
        with self.assertRaises(NoResultFound):
            controller.recordgameevent(sessionid, gameevent)

        
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
        
if __name__ == '__main__':
    unittest.main()