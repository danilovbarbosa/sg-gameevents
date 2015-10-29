'''
Controller of the application, which defines the behaviour
of the application when called by the views.
'''

import uuid, OpenSSL
from app import app, db, models

from app.errors import InvalidGamingSession, TokenExpired
from flask.ext.api.exceptions import AuthenticationFailed
from sqlalchemy.orm.exc import NoResultFound 

from itsdangerous import BadSignature, SignatureExpired

# def generatesessionid():
#     # from https://stackoverflow.com/questions/817882/unique-session-id-in-python/6092448#6092448
#     sessionid = uuid.UUID(bytes = OpenSSL.rand.bytes(16))
#     #sessionid = uuid.UUID(bytes = M2Crypto.m2.rand_bytes(num_bytes=16))
#     return sessionid

def authenticate(clientid_or_token, apikey=False, sessionid=False):
    """Takes a client_id + apikey + sessionid and checks if it is a valid combination OR
    a token. Returns the token.
    """
    
    clientid = False
    
    #First try with the token
    token = clientid_or_token
    try:
        gamingsession = models.GamingSession.verify_auth_token(token)
        if gamingsession and ("sessionid" in gamingsession):
            app.logger.debug("Got a valid token. Now I know the sessionid and clientid.")
            sessionid = gamingsession["sessionid"]
            clientid = gamingsession["clientid"]
            app.logger.debug("Sessionid '%s'; clientid '%s'. Checking if this is a valid pair..." % (sessionid, clientid))
            if (models.GamingSession.query.filter_by(clientid = clientid, sessionid=sessionid).first()):
                app.logger.debug("Valid combination of sessionid/clientid, return true.")
                return token
            else:
                app.logger.debug("This combination is not in the db. Bad token!")
                return False
        else:
            app.logger.debug("NOT a valid token.")
            if (apikey):
                app.logger.debug("Apikey provided, trying to authenticate client...")
                clientid = clientid_or_token
                client = models.Client(clientid, apikey)         
           
                if (client.verify_apikey(apikey)):
                    app.logger.debug("Clientid and apikey are valid. Continuing...")
                else:
                    return False
            else:
                app.logger.debug("Apikey not provided, returning false...")
                return False
    except Exception as e:
        app.logger.error("Unexpected failure when trying to authenticate token and/or clientid+apikey+sessionid")
        app.logger.error(e.args, exc_info=True)
        raise e

    # Now I should have sessionid and clientid. I can see if they are valid
    app.logger.debug("Now I have sessionid (%s) and clientid (%s). All I need now is to check if this sessionid is valid." % (sessionid, clientid))
    gamingsession = models.GamingSession(sessionid, clientid)
    try:
        if (check_sessionid(sessionid, clientid)):
            app.logger.debug("Sessionid is valid. Generate a token.")
            token = gamingsession.generate_auth_token()
            return token
        else:
            app.logger.debug("Session ID not valid. Returning false.")
            return False
    except Exception as e:
        app.logger.error("Unexpected failure when checking the sessionid/clientid.")
        app.logger.error(e.args, exc_info=True)
        raise e

def newclient(clientid, apikey):
    """ Adds a new client to the database.
    TODO: Protect this function so that only admins have access.
    """
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
    
    
# def startgamingsession(sessionid):
#     new_gamingsession = models.GamingSession(sessionid)
#     db.session.add(new_gamingsession)
#     #db.session.commit()
# 
#     try:
#         db.session.commit()
#         return new_gamingsession.id
#     except Exception as e:
#         app.logger.warning(e)
#         db.session.rollback()
#         db.session.flush() # for resetting non-commited .add()
#         return False


# def getgamingsessionstatus(sessionid):
#     try:
#         query = db.session.query(models.GamingSession).filter(models.GamingSession.id == sessionid)
#         res = query.one()
#         return res.status
#     except NoResultFound as e:
#         raise NoResultFound('This gaming session ID does not exist.') 
        

    
# def isexistinggamingsession(sessionid):
#     query = db.session.query(models.GamingSession).filter(models.GamingSession.id == sessionid)
#     res = query.count()
#     if res >= 1:
#         return True
#     else:
#         return False
    
# def finishgamingsession(sessionid):
#     return False

def getgameevents(token):
    try:
        #Is this a valid token?
        gamingsession = models.GamingSession.verify_auth_token(token)
        if gamingsession and ("sessionid" in gamingsession):
            sessionid = gamingsession["sessionid"]
            app.logger.debug("sessionid: " + sessionid)
            query_sessionid = db.session.query(models.GamingSession).filter(models.GamingSession.sessionid == sessionid)
            res_sessionid = query_sessionid.one()
            if (res_sessionid):
                app.logger.debug("sessionid_id: " + res_sessionid.id)
                query_events = db.session.query(models.GameEvent).filter(models.GameEvent.gamingsession_id == res_sessionid.id)
                res_events = query_events.all()
                app.logger.debug(res_events)
            return res_events
        else:
            app.logger.warning("User tried to use an invalid token.")
            raise AuthenticationFailed('Unauthorized token.') 
    except Exception as e:
        app.logger.error(e, exc_info=True)
        raise e
    
def recordgameevent(token, timestamp, gameevent):
    try:
        #Is this a valid token?
        app.logger.debug("Verifying token...")
        gamingsession = models.GamingSession.verify_auth_token(token)
        if gamingsession and ("sessionid" in gamingsession):
            sessionid = gamingsession["sessionid"]
            app.logger.debug("sessionid: " + sessionid)
            query_sessionid = db.session.query(models.GamingSession).filter(models.GamingSession.sessionid == sessionid)
            res_sessionid = query_sessionid.one()
            if (res_sessionid):
                app.logger.debug("sessionid_id: " + res_sessionid.id)
                app.logger.debug("Trying to record the game event.")
                new_gameevent = models.GameEvent(sessionid, gameevent)
                db.session.add(new_gameevent)
                try:
                    db.session.commit()
                    return True
                except Exception as e:
                    app.logger.warning(e)
                    db.session.rollback()
                    db.session.flush() # for resetting non-commited .add()
                    app.logger.error(e, exc_info=True)
                    raise e                
        else:
            app.logger.warning("User tried to use an invalid token.")
            raise AuthenticationFailed('Unauthorized token.') 
    except Exception as e:
        app.logger.error(e, exc_info=True)
        raise e

            
    
# def __inactivategamingsession(sessionid):
#     return False
    
# def __getlastgamingsessionid():
#     return False

def check_sessionid(sessionid, clientid):
    """Checks if sessionid exists in db. If yes, returns true.
    If not, it communicates with the user profile service and checks if
    it is a valid session id. If yes, adds the sessionid to the local db
    and returns true. If not, returns false. 
    """
    try:
        query = db.session.query(models.GamingSession).filter(models.GamingSession.sessionid == sessionid, 
                                                              models.GamingSession.clientid == clientid)
        res = query.count()
        if res >= 1:
            app.logger.debug("Sessionid exists, returning true.")
            return True
        else:
            app.logger.debug("Sessionid is not in db. Let's ask the user profiling service...")
            if (_is_valid_sessionid(sessionid)):
                app.logger.debug("User profiling service says it's a good session id! Let's add it to the db.")
                gamingsession = models.GamingSession(sessionid, clientid)
                db.session.add(gamingsession)
                try:
                    db.session.commit()
                    app.logger.debug("Added sessionid to db.")
                    return True
                except Exception as e:
                    app.logger.error("Unable to add session id to db. " + e.args)
                    db.session.rollback()
                    db.session.flush() # for resetting non-commited .add()
                    raise e
            else:
                app.logger.debug("Sessionid is NOT authorized by user profiling service.")
                return False
    except Exception as e:
        app.logger.error(e, exc_info=True)
        raise e
    
def _is_valid_sessionid(sessionid):
    """Asks the userprofile service if the sessionid is valid.
    TODO: write the implementation!
    """
    if (sessionid != "zzzz"): 
        return True
    else:
        return False