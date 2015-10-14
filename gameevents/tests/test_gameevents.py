import unittest
import gameevents
import datetime

class TestGameEvents(unittest.TestCase):
    def test_startrecording(self):
        gamingsession = {
        'id': "00001",
        'timestamp': str(datetime.datetime.now()),
        'status':'active'
        }
        self.assertEqual(gameevents.startrecording(gamingsession), True)
        
if __name__ == '__main__':
    unittest.main()