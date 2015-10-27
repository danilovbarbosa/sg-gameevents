'''
Created on 15 Oct 2015

@author: mbrandaoca
'''
import uuid, OpenSSL
from app import app, db, models

from app.errors import SessionNotActive, TokenExpired
from flask.ext.api.exceptions import AuthenticationFailed
from sqlalchemy.orm.exc import NoResultFound 

from itsdangerous import BadSignature, SignatureExpired

# def generatesessionid():
#     # from https://stackoverflow.com/questions/817882/unique-session-id-in-python/6092448#6092448
#     sessionid = uuid.UUID(bytes = OpenSSL.rand.bytes(16))
#     #sessionid = uuid.UUID(bytes = M2Crypto.m2.rand_bytes(num_bytes=16))
#     return sessionid

def authenticate(clientid_or_token, apikey, sessionid):
    #TODO: check if sessionid exists in db. if not, request the user profiling service to
    # verify if sessionid exists and the user authorized its use.
    app.logger.debug("TODO: Check session id!")
    #Try using the token first
    app.logger.debug("Try to verify token...")
    try:
        client = models.Client.verify_auth_token(clientid_or_token)
        if client:
            return client.generate_auth_token()
        else:
            # try to authenticate with clientid and apikey
            credentialscheck = client.verify_apikey(apikey)
            if credentialscheck:
                client.generate_auth_token()
            else:
                return False
    except (BadSignature, SignatureExpired) as e:
        # try to authenticate with clientid and apikey
        client = models.Client.query.filter_by(clientid = clientid_or_token).first()
        if client:
            credentialscheck = client.verify_apikey(apikey)
            if credentialscheck:
                return client.generate_auth_token()
            else:
                return False
        else:
            return False
    except Exception as e:
        app.logger.error("Unexpected failure in authenticate function")
        app.logger.error(e, exc_info=False)
        raise e


def newclient(clientid, apikey):
    if clientid is None or apikey is None:
        raise Exception('Invalid parameters')
    if models.Client.query.filter_by(clientid = clientid).first() is not None:
        raise Exception('Client exists')
    client = models.Client(clientid, apikey)
    db.session.add(client)
    try:
        db.session.commit()
        #print(client)
        return client
    except Exception as e:
        app.logger.warning(e)
        db.session.rollback()
        db.session.flush() # for resetting non-commited .add()
        return False
    
    
def startgamingsession(sessionid):
    new_gamingsession = models.GamingSession(sessionid)
    db.session.add(new_gamingsession)
    #db.session.commit()

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
    
def recordgameevent(token, timestamp, gameevent):
    app.logger.debug("Trying to authenticate token...")
    if not authenticate(token, False):
        app.logger.warning("User tried to use an invalid token.")
        raise AuthenticationFailed('Unauthorized token.')
    else:
        app.logger.debug("Token valid, continuing...")
        if False: #not getgamingsessionstatus(sessionid):
            raise SessionNotActive('This gaming session is no longer active.')
        else:
            app.logger.warning("Trying to record the game event.")
            '''
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
                '''
            successful = True
            return successful
            
    
def __inactivategamingsession(sessionid):
    return False
    
def __getlastgamingsessionid():
    return False