import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from base import Base
from entities import *

engine = create_engine('sqlite:///gamingsession_test.db', echo=False)
 
# create a Session
DbSession = sessionmaker(bind=engine)
dbsession = DbSession()


        
########################################################################
class GameEvents(object):
    def __init__ (self):        
        self.sessions = []
    
        self.events = [
                    {
                        'sessionid': 1,
                        'title': u'My Title',
                        'description': u'My Description',
                    }
                ]
        self.logger = logging.getLogger(__name__)
        
        self._lastInsertedId = None

        
        
    def startgamingsession(self):
        new_gamingsession = GamingSession()
        dbsession.add(new_gamingsession)
        dbsession.commit()
        self._lastInsertedId = new_gamingsession.id 
        return self._lastInsertedId 
    
    def finishgamingsession(self, sessionid):
        return False
    
    def recordgameevent(self, sessionid, gameevent):
        return False
    
    def getgameevents(self, sessionid):
        return False
    
    def getgamingsessionstatus(self, sid):
        query = dbsession.query(GamingSession).filter(GamingSession.id == sid)
        res = query.all()
        if res and len(res) >= 1:
            return res[0].status
        else:
            return False
    
    def __inactivategamingsession(self, sessionid):
        return False
    
    def __getlastgamingsessionid(self):
        return self._lastInsertedId
        
if __name__ == '__main__':
    Base.metadata.create_all(engine, checkfirst=True)
    print("I'm in the main!")