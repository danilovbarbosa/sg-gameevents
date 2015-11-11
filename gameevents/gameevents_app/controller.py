'''
Controller of the application, which defines the behaviour
of the application when called by the views.
'''

from flask import current_app

# Exceptions and errors
from flask.ext.api.exceptions import AuthenticationFailed
from sqlalchemy.orm.exc import NoResultFound 
#from gameevents_app.errors import InvalidGamingSession, TokenExpired
#from itsdangerous import BadSignature, SignatureExpired

# Models
from gameevents_app.models.gamingsession import GamingSession
from gameevents_app.models.client import Client
from gameevents_app.models.gameevent import GameEvent

#Logging
from logging import getLogger
LOG = getLogger(__name__)


def authenticate(clientid_or_token, apikey=False, sessionid=False):
    """Takes a client_id + apikey + sessionid and checks if it is a valid combination OR
    a token. Returns the token.
    """
    
    clientid = False
    
    #First try with the token
    token = clientid_or_token
    try:
        gamingsession = GamingSession.verify_auth_token(token)
        LOG.debug(gamingsession)
        if gamingsession:
            LOG.debug("Got a valid token. Now I know the clientid.")
            LOG.debug(gamingsession)
            sessionid = gamingsession["sessionid"]
            clientid = gamingsession["clientid"]
            LOG.debug("Sessionid '%s'; clientid '%s'. Checking if this is a valid pair..." % (sessionid, clientid))
            if (current_app.db.session.query(GamingSession).filter_by(clientid = clientid, sessionid=sessionid).first()):
                LOG.debug("Valid combination of sessionid/clientid, return true.")
                return token
            else:
                LOG.debug("This combination is not in the db. Bad token!")
                return False
        else:
            LOG.debug("NOT a valid token.")
            if (apikey):
                LOG.debug("Apikey provided, trying to authenticate client...")
                clientid = clientid_or_token
                #client = models.Client(clientid, apikey)
                
                #Check if client is in the database
                client = current_app.db.session.query(Client).filter_by(clientid = clientid).first()
                if not client:
                    LOG.debug("Client not in database.")
                    return False
                else:
                    if (not client.verify_apikey(apikey)):
                        LOG.debug("Wrong credentials.")
                        return False
                    else:
                        LOG.debug("Good credentials, continuing...")
            else:
                LOG.debug("Apikey not provided, returning false...")
                return False
    except Exception as e:
        LOG.error("Unexpected failure when trying to authenticate token and/or clientid+apikey+sessionid")
        LOG.error(e.args, exc_info=True)
        raise e

    
    #Is client an admin?
    is_client_admin = is_admin(clientid) 
    if (is_client_admin and sessionid == False):
        try:
            client = current_app.db.session.query(Client).filter_by(clientid = clientid).first()
            LOG.debug("Client is admin. Generate a token...")
            token = client.generate_auth_token()
            return token
            
        except Exception as e:
            LOG.error("Unexpected failure when generating token for admin.")
            LOG.error(e.args, exc_info=True)
            raise e
    elif (is_client_admin==False and sessionid != False):
        # Now I should have sessionid and clientid. I can see if they are valid
        LOG.debug("I have sessionid (%s) and clientid (%s). I need to check if this sessionid is valid." % (sessionid, clientid))
        #gamingsession = GamingSession(sessionid, clientid)
        gamingsession = GamingSession(sessionid)
        try:
            if (check_sessionid(sessionid, clientid)):
                LOG.debug("Sessionid is valid. Generate a token...")
                token = gamingsession.generate_auth_token(clientid)
                return token
            else:
                LOG.debug("Session ID not valid. Returning false.")
                return False
        except Exception as e:
            LOG.error("Unexpected failure when checking the sessionid/clientid.")
            LOG.error(e.args, exc_info=True)
            raise e
    else:
        LOG.debug("Not an admin trying to get token without specific sessionid, returning false")
        return False

def newclient(clientid, apikey):
    """ Adds a new client to the database.
    TODO: Protect this function so that only admins have access.
    """
    if clientid is None or apikey is None:
        raise Exception('Invalid parameters')
    if current_app.db.session.query(Client).filter_by(clientid = clientid).first() is not None:
        raise Exception('Client exists')
    client = Client(clientid, apikey)
    current_app.db.session.add(client)
    try:
        current_app.db.session.commit()
        #print(client)
        return client
    except Exception as e:
        LOG.warning(e)
        current_app.db.session.rollback()
        current_app.db.session.flush() # for resetting non-commited .add()
        return False
    
    

def getgameevents(token, sessionid):
    try:
        #Is Client authorized to see this session id?
        if is_client_authorized(token, sessionid):
            query_events = current_app.db.session.query(GameEvent).filter(GameEvent.gamingsession_id == sessionid)
            res_events = query_events.all()
            LOG.debug("Found %s results." % len(res_events))
            return res_events
        else:
            LOG.warning("User tried to use an invalid token.")
            raise AuthenticationFailed('Unauthorized token.') 
    except Exception as e:
        LOG.error(e, exc_info=True)
        raise e
    
def recordgameevent(token, timestamp, gameevent):
    try:
        #Is this a valid token?
        LOG.debug("Verifying token...")
        gamingsession = GamingSession.verify_auth_token(token)
        if gamingsession and ("sessionid" in gamingsession) and ("clientid" in gamingsession):
            sessionid = gamingsession["sessionid"]
            clientid = gamingsession["clientid"]
            LOG.debug("sessionid: " + sessionid)
            query_sessionid = current_app.db.session.query(GamingSession).filter(GamingSession.sessionid == sessionid)
            res_sessionid = query_sessionid.one()
            if (res_sessionid):
                LOG.debug("sessionid_id: " + res_sessionid.id)
                LOG.debug("Trying to record the game event.")
                new_gameevent = GameEvent(sessionid, gameevent)
                current_app.db.session.add(new_gameevent)
                try:
                    current_app.db.session.commit()
                    return True
                except Exception as e:
                    LOG.warning(e)
                    current_app.db.session.rollback()
                    current_app.db.session.flush() # for resetting non-commited .add()
                    LOG.error(e, exc_info=True)
                    raise e                
        else:
            LOG.warning("User tried to use an invalid token.")
            raise AuthenticationFailed('Unauthorized token.') 
    except Exception as e:
        LOG.error(e, exc_info=True)
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
    if (sessionid and clientid):
        try:
            gamingsession = current_app.db.session.query(GamingSession).filter(GamingSession.sessionid == sessionid).one()
            client = current_app.db.session.query(Client).filter(Client.clientid == clientid).one()
    
            #Session and client exist. Now, is this clientid authorized to read the session?
                     
            res = current_app.db.session.query.filter(GamingSession.clients.any(clientid=clientid)).all()
            #res = query.count()
            if len(res) >= 1:
                LOG.debug("Sessionid exists and client is authorized, returning true.")
                return True
            else:
                # Ask the profiling service if this client is authorized to read this sessionid.
                # If yes, add it to database with an expiration time
                if (True): #This will be the service replying yes
                    gamingsession.clients.append(client) 
                    return True
                else:
                    raise AuthenticationFailed("Client not authorized.")
                
        except NoResultFound as e:
            LOG.debug("Sessionid is not in db. Let's ask the user profiling service...")
            if (_is_valid_sessionid(sessionid, clientid)):
                LOG.debug("User profiling service says it's a good session id! Let's add it to the current_app.db.")
                gamingsession = GamingSession(sessionid)
                current_app.db.session.add(gamingsession)
                try:
                    current_app.db.session.commit()
                    LOG.debug("Added sessionid to db.")
                    return True
                except Exception as e:
                    LOG.error("Unable to add session id to db. " + e.args)
                    current_app.db.session.rollback()
                    current_app.db.session.flush() # for resetting non-commited .add()
                    raise e
        except Exception as e:
            LOG.error(e, exc_info=True)
            raise e
    else:
        return False
    
def _is_valid_sessionid(sessionid, clientid):
    """Asks the userprofile service if the sessionid is valid.
    TODO: write the implementation!
    """
    if (sessionid != "zzzz" and sessionid != False): 
        return True
    else:
        return False
    
def getsessions():
    try:
        query = current_app.db.session.query(GamingSession)
        res_sessions = query.all()
        return res_sessions
    except Exception as e:
        LOG.error(e, exc_info=True)
        raise e
    
def is_admin(clientid):
    if (clientid == "dashboard"):
        return True
    else: 
        return False
        
def is_client_authorized(token, sessionid):
    #TODO: Implement this function!!! 
    return True