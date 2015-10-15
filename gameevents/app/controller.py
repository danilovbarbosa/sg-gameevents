'''
Created on 15 Oct 2015

@author: mbrandaoca
'''

from app import db, models

from app.errors import SessionNotActive
from sqlalchemy.orm.exc import NoResultFound 


def startgamingsession():
    new_gamingsession = models.GamingSession()
    db.session.add(new_gamingsession)
    db.session.commit()

    try:
        db.session.commit()
        return new_gamingsession.id
    except Exception as e:
        app.logger.warning(e)
        db.session.rollback()
        db.session.flush() # for resetting non-commited .add()
        return False


def getgamingsessionstatus(sessionid):
    try:
        query = db.session.query(models.GamingSession).filter(models.GamingSession.id == sessionid)
        res = query.one()
        return res.status
    except NoResultFound as e:
        raise NoResultFound('This gaming session ID does not exist.') 
        

    
def isexistinggamingsession(sessionid):
    query = db.session.query(models.GamingSession).filter(models.GamingSession.id == sessionid)
    res = query.count()
    if res >= 1:
        return True
    else:
        return False
    
def finishgamingsession(sessionid):
    return False

def getgameevents(sessionid):
    if isexistinggamingsession(sessionid):
        query = db.session.query(models.GameEvent).filter(models.GameEvent.gamingsession_id == sessionid)
        res = query.all()
        return res
    else:
        raise NoResultFound('This gaming session ID does not exist.')
    
def recordgameevent(sessionid, gameevent):
    if not isexistinggamingsession(sessionid):
        raise NoResultFound('This gaming session ID does not exist.')
    else:
        if not getgamingsessionstatus(sessionid):
            raise SessionNotActive('This gaming session is no longer active.')
        else:
            new_gameevent = models.GameEvent(sessionid, gameevent)
            db.session.add(new_gameevent)
            successful = False
            try:
                db.session.commit()
                successful = True
            except Exception as e:
                app.logger.warning(e)
                db.session.rollback()
                db.session.flush() # for resetting non-commited .add()
                successful = False
            return successful
    
def __inactivategamingsession(sessionid):
    return False
    
def __getlastgamingsessionid():
    return False