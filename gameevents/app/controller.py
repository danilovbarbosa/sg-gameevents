'''
Created on 15 Oct 2015

@author: mbrandaoca
'''

from app import db, models

def startgamingsession():
    new_gamingsession = models.GamingSession()
    db.session.add(new_gamingsession)
    db.session.commit()

    try:
        db.session.commit()
        return new_gamingsession.id
    except Exception as e:
        app.logger.warning(e)
        db_session.rollback()
        db_session.flush() # for resetting non-commited .add()
        return False


def getgamingsessionstatus(sessionid):
    query = db.session.query(models.GamingSession).filter(models.GamingSession.id == sessionid)
    res = query.all()
    if res and len(res) >= 1:
        return res[0].status
    else:
        return False
    
def finishgamingsession(sessionid):
    return False

def getgameevents(sessionid):
    query = db.session.query(models.GameEvent).filter(models.GameEvent.gamingsession_id == sessionid)
    res = query.all()
    return res
    
def recordgameevent(sessionid, gameevent):
    new_gameevent = models.GameEvent(sessionid, gameevent)
    db.session.add(new_gameevent)
    successful = False
    try:
        db.session.commit()
        successful = True
    except Exception as e:
        app.logger.warning(e)
        db_session.rollback()
        db_session.flush() # for resetting non-commited .add()
        successful = False
    return successful
    
def __inactivategamingsession(sessionid):
    return False
    
def __getlastgamingsessionid():
    return False