'''
Controller of the application, which defines the behaviour
of the application when called by the views.
'''

#import uuid, OpenSSL
from app import app, db
from app.models.gamingsession import GamingSession
from app.models.client import Client
from app.models.gameevent import GameEvent

#from app.errors import InvalidGamingSession, TokenExpired
from flask.ext.api.exceptions import AuthenticationFailed
#from sqlalchemy.orm.exc import NoResultFound 
#from flask import jsonify

#from itsdangerous import BadSignature, SignatureExpired


def authenticate(clientid_or_token, apikey=False, sessionid=False):
    """Takes a client_id + apikey + sessionid and checks if it is a valid combination OR
    a token. Returns the token.
    """
    
    clientid = False
    
    #First try with the token
    token = clientid_or_token
    try:
        gamingsession = GamingSession.verify_auth_token(token)
        if gamingsession and ("sessionid" in gamingsession):
            app.logger.debug("Got a valid token. Now I know the sessionid and clientid.")
            sessionid = gamingsession["sessionid"]
            clientid = gamingsession["clientid"]
            app.logger.debug("Sessionid '%s'; clientid '%s'. Checking if this is a valid pair..." % (sessionid, clientid))
            if (GamingSession.query.filter_by(clientid = clientid, sessionid=sessionid).first()):
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
                #client = models.Client(clientid, apikey)
                
                #Check if client is in the database
                client = Client.query.filter_by(clientid = clientid).first()
                if not client:
                    app.logger.debug("Client not in database.")
                    return False
                else:
                    if (not client.verify_apikey(apikey)):
                        app.logger.debug("Wrong credentials.")
                        return False
                    else:
                        app.logger.debug("Good credentials, continuing...")
            else:
                app.logger.debug("Apikey not provided, returning false...")
                return False
    except Exception as e:
        app.logger.error("Unexpected failure when trying to authenticate token and/or clientid+apikey+sessionid")
        app.logger.error(e.args, exc_info=True)
        raise e

    # Now I should have sessionid and clientid. I can see if they are valid
    app.logger.debug("Now I have sessionid (%s) and clientid (%s). All I need now is to check if this sessionid is valid." % (sessionid, clientid))
    gamingsession = GamingSession(sessionid, clientid)
    try:
        if (check_sessionid(sessionid, clientid)):
            app.logger.debug("Sessionid is valid. Generate a token...")
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
    if Client.query.filter_by(clientid = clientid).first() is not None:
        raise Exception('Client exists')
    client = Client(clientid, apikey)
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
    
    

def getgameevents(token):
    try:
        #Is this a valid token?
        gamingsession = GamingSession.verify_auth_token(token)
        if gamingsession and ("sessionid" in gamingsession):
            sessionid = gamingsession["sessionid"]
            query_events = db.session.query(GameEvent).filter(GameEvent.gamingsession_id == sessionid)
            res_events = query_events.all()
            app.logger.debug("Found %s results." % len(res_events))
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
        gamingsession = GamingSession.verify_auth_token(token)
        if gamingsession and ("sessionid" in gamingsession) and ("clientid" in gamingsession):
            sessionid = gamingsession["sessionid"]
            clientid = gamingsession["clientid"]
            app.logger.debug("sessionid: " + sessionid)
            query_sessionid = db.session.query(GamingSession).filter(GamingSession.sessionid == sessionid, GamingSession.clientid == clientid)
            res_sessionid = query_sessionid.one()
            if (res_sessionid):
                app.logger.debug("sessionid_id: " + res_sessionid.id)
                app.logger.debug("Trying to record the game event.")
                new_gameevent = GameEvent(sessionid, gameevent)
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
        query = db.session.query(GamingSession).filter(GamingSession.sessionid == sessionid, 
                                                              GamingSession.clientid == clientid)
        res = query.count()
        if res >= 1:
            app.logger.debug("Sessionid exists, returning true.")
            return True
        else:
            app.logger.debug("Sessionid is not in db. Let's ask the user profiling service...")
            if (_is_valid_sessionid(sessionid)):
                app.logger.debug("User profiling service says it's a good session id! Let's add it to the db.")
                gamingsession = GamingSession(sessionid, clientid)
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
    
def getsessions():
    try:
        query = db.session.query(GamingSession)
        res_sessions = query.all()
        return res_sessions
    except Exception as e:
        app.logger.error(e, exc_info=True)
        raise e
        