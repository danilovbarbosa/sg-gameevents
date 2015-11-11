'''
Controller of the application, which defines the behaviour
of the application when called by the views.
'''

from flask import current_app

# Exceptions and errors
from flask.ext.api.exceptions import AuthenticationFailed, ParseError
from sqlalchemy.orm.exc import NoResultFound 
from gameevents_app.errors import ClientExistsException
#from itsdangerous import BadSignature, SignatureExpired

# Models
from gameevents_app.models.gamingsession import GamingSession
from gameevents_app.models.client import Client
from gameevents_app.models.gameevent import GameEvent

#Extensions
from .extensions import db, LOG
from werkzeug.exceptions import Unauthorized
from flask_api.exceptions import NotFound

###################################################
#    Client functions
###################################################

def newclient(clientid, apikey):
    """ Adds a new client to the database.
    TODO: Protect this function so that only admins have access.
    """
    if clientid is None or apikey is None:
        raise ParseError('Invalid parameters')
    if db.session.query(Client).filter_by(clientid = clientid).first() is not None:
        raise ClientExistsException('Client exists')
    client = Client(clientid, apikey)
    db.session.add(client)
    try:
        db.session.commit()
        #print(client)
        return client
    except Exception as e:
        LOG.warning(e)
        db.session.rollback()
        db.session.flush() # for resetting non-commited .add()
        return False
    
###################################################
#    Session functions
###################################################

def getsessions():
    query = db.session.query(GamingSession)
    res_sessions = query.all()
    return res_sessions
    


###################################################
#    Game events functions
###################################################

def recordgameevent(token, timestamp, gameevent):
    try:
        #Is this a valid token?
        LOG.debug("Verifying token...")
        gamingsession = GamingSession.verify_auth_token(token)
        if gamingsession and ("sessionid" in gamingsession) and ("clientid" in gamingsession):
            sessionid = gamingsession["sessionid"]
            clientid = gamingsession["clientid"]
            LOG.debug("sessionid: " + sessionid)
            query_sessionid = db.session.query(GamingSession).filter(GamingSession.sessionid == sessionid)
            res_sessionid = query_sessionid.one()
            if (res_sessionid):
                LOG.debug("sessionid_id: " + res_sessionid.id)
                LOG.debug("Trying to record the game event.")
                new_gameevent = GameEvent(sessionid, gameevent)
                db.session.add(new_gameevent)
                try:
                    db.session.commit()
                    return True
                except Exception as e:
                    LOG.warning(e)
                    db.session.rollback()
                    db.session.flush() # for resetting non-commited .add()
                    LOG.error(e, exc_info=True)
                    raise e                
        else:
            LOG.warning("User tried to use an invalid token.")
            raise AuthenticationFailed('Unauthorized token.') 
    except Exception as e:
        LOG.error(e, exc_info=True)
        raise e
    
    
def getgameevents(token, sessionid):
    try:
        #Is Client authorized to see this session id?
        if is_client_authorized(token, sessionid):
            query_events = db.session.query(GameEvent).filter(GameEvent.gamingsession_id == sessionid)
            res_events = query_events.all()
            LOG.debug("Found %s results." % len(res_events))
            return res_events
        else:
            LOG.warning("User tried to use an invalid token.")
            raise AuthenticationFailed('Unauthorized token.') 
    except Exception as e:
        LOG.error(e, exc_info=True)
        raise e
    
###################################################
#    Clients
###################################################

def getclient(clientid):
    try:
        client = db.session.query(Client).filter_by(clientid = clientid).one()
        return client
    except NoResultFound:
        return False
    
    
###################################################
#    Token
###################################################

def gettoken(clientid, apikey, sessionid=False):
    go_on = False
    #Check if client is in the database
    client = db.session.query(Client).filter_by(clientid = clientid).first()
    if not client:
        #LOG.debug("Client not in database.")
        raise Unauthorized("Client not in database.")
    else:
        if (not client.verify_apikey(apikey)):
            #LOG.debug("Wrong credentials.")
            raise Unauthorized("Wrong credentials.")
        else:
            #LOG.debug("Good credentials, continuing...")
            if (sessionid and is_session_authorized(sessionid, clientid)):
                #LOG.debug("Client provided valid session id...")
                go_on = True
            else:
                #LOG.debug("No session id. Is client an admin?)
                if (client.is_admin()):
                    go_on = True
                else:
                    raise Unauthorized("Non-admin trying to access admin-only functions.")
                
        if go_on:
            token = client.generate_auth_token()
            return token            
            

###################################################
#    Authentication functions
###################################################

# def authenticate(clientid_or_token, apikey=False, sessionid=False):
#     """Takes a client_id + apikey + sessionid and checks if it is a valid combination OR
#     a token. Returns the token.
#     """
#     
#     clientid = False    
#     #First try with the token
#     token = clientid_or_token
#     try:
#         gamingsession = GamingSession.verify_auth_token(token)
#         if gamingsession:
#             LOG.debug("Got a valid token. Now I know sessionid.")
#             sessionid = gamingsession['sessionid']
#             
#         else:
#             LOG.debug("NOT a valid token.")
#             if (apikey):
#                 LOG.debug("Apikey provided, trying to authenticate client...")
#                 clientid = clientid_or_token
#                 #client = models.Client(clientid, apikey)
#                 
#                 #Check if client is in the database
#                 client = db.session.query(Client).filter_by(clientid = clientid).first()
#                 if not client:
#                     LOG.debug("Client not in database.")
#                     return False
#                 else:
#                     if (not client.verify_apikey(apikey)):
#                         LOG.debug("Wrong credentials.")
#                         return False
#                     else:
#                         LOG.debug("Good credentials, continuing...")
#             else:
#                 LOG.debug("Apikey not provided, returning false...")
#                 return False
#     except Exception as e:
#         LOG.error("Unexpected failure when trying to authenticate token and/or clientid+apikey+sessionid")
#         LOG.error(e.args, exc_info=True)
#         raise e
# 
#     
#     #Is client an admin?
#     is_client_admin = is_admin(clientid) 
#     if (is_client_admin and sessionid == False):
#         try:
#             client = db.session.query(Client).filter_by(clientid = clientid).first()
#             LOG.debug("Client is admin. Generate a token...")
#             token = client.generate_auth_token()
#             return token
#             
#         except Exception as e:
#             LOG.error("Unexpected failure when generating token for admin.")
#             LOG.error(e.args, exc_info=True)
#             raise e
#     elif (is_client_admin==False and sessionid != False):
#         # Now I should have sessionid and clientid. I can see if they are valid
#         LOG.debug("I have sessionid (%s) and clientid (%s). I need to check if this sessionid is valid." % (sessionid, clientid))
#         #gamingsession = GamingSession(sessionid, clientid)
#         gamingsession = GamingSession(sessionid)
#         try:
#             if (check_sessionid(sessionid, clientid)):
#                 LOG.debug("Sessionid is valid. Generate a token...")
#                 token = gamingsession.generate_auth_token(clientid)
#                 return token
#             else:
#                 LOG.debug("Session ID not valid. Returning false.")
#                 return False
#         except Exception as e:
#             #LOG.error("Unexpected failure when checking the sessionid/clientid.")
#             #LOG.error(e.args, exc_info=True)
#             raise e
#     else:
#         LOG.debug("Not an admin trying to get token without specific sessionid, returning false")
#         return False
    

def client_authenticate(clientid, apikey):
    try:
        client = db.session.query(Client).filter_by(clientid = clientid).one()
        LOG.debug("Found a client.")
        if (not client.verify_apikey(apikey)):
            LOG.debug("Oops, wrong password %s" % apikey)
            raise AuthenticationFailed("Wrong credentials.")
        else:
            return client
    except NoResultFound:
        raise AuthenticationFailed("Clientid does not exist.")
        
    
# def is_admin(client):
#     #LOG.debug("Is it an admin? %s" % client)
#     if type(client) is Client:
#         clientid = client.clientid
#     elif type(client) is str:
#         clientid = client
#     else:
#         LOG.error("Tried to verify if an invalid object or string is admin.")
#         raise ParseError
#     
#     if (clientid == "dashboard" or clientid == "masteroftheuniverse"):
#         return True
#     else: 
#         return False
    
def is_client_authorized(token, sessionid):
    #TODO: Implement this function!!! 
    return True

def is_session_authorized(sessionid, clientid):
    return True
#         
#     #Session and client exist. Now, is this clientid authorized to read the session?
#     res = db.session.query(GamingSession).filter(GamingSession.clients.any(clientid=clientid)).all()
#     #res = query.count()
#     if len(res) >= 1:
#                 
#     else:
#         # Ask the profiling service if this client is authorized to read this sessionid.
#         # If yes, add it to database with an expiration time
#         if (True): #This will be the service replying yes
#             gamingsession.clients.append(client) 
#             return True
#         else:
#             raise AuthenticationFailed("Client not authorized.")