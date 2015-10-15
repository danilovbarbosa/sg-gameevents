'''
Created on 15 Oct 2015

@author: mbrandaoca
'''

from app import db, models

def startgamingsession():
    new_gamingsession = models.GamingSession()
    db.session.add(new_gamingsession)
    db.session.commit()
    return new_gamingsession.id

def getgamingsessionstatus(sid):
    query = db.session.query(models.GamingSession).filter(models.GamingSession.id == sid)
    res = query.all()
    if res and len(res) >= 1:
        return res[0].status
    else:
        return False
    
def finishgamingsession(sessionid):
    return False
    
def recordgameevent(sessionid, gameevent):
    return False
    
def getgameevents(sessionid):
    return False

def __inactivategamingsession(sessionid):
    return False
    
def __getlastgamingsessionid():
    return False