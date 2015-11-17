'''
Controller of the application, which defines the behaviour
of the application when called by the views.
'''

#from flask import current_app

# Exceptions and errors
from flask.ext.api.exceptions import AuthenticationFailed, ParseError
from sqlalchemy.orm.exc import NoResultFound 
from gameevents_app.errors import *
#from itsdangerous import BadSignature, SignatureExpired
#from werkzeug.exceptions import Unauthorized
#from flask_api.exceptions import NotFound

# Models
from gameevents_app.models.session import Session
from gameevents_app.models.client import Client
from gameevents_app.models.gameevent import GameEvent

#Extensions
from .extensions import db, LOG
from flask_api.exceptions import NotAuthenticated, NotAcceptable


###################################################
#    Client functions
###################################################

def new_client(clientid, apikey, role="normal"):
    """ Adds a new client to the database.
    TODO: Protect this function so that only admins have access.
    """
    if role != "admin":
        role = "normal"
        
    if clientid is None or apikey is None:
        raise ParseError('Invalid parameters')
    if db.session.query(Client).filter_by(clientid = clientid).first() is not None:
        raise ClientExistsException('Client exists')
    client = Client(clientid, apikey, role)
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

def get_sessions():
    """"""
    query = db.session.query(Session)
    res_sessions = query.all()
    return res_sessions
    
def new_session(sessionid, client_id):
    session = Session(sessionid, client_id)
    try:
        db.session.add(session)
        db.session.commit()
        return session
    except Exception as e:
        LOG.warning(e)
        db.session.rollback()
        db.session.flush() # for resetting non-commited .add()
        LOG.error(e, exc_info=True)
        raise e  
    
def is_session_authorized(sessionid):
    """TODO: Implement this function to check using timestamp and/or 
    with user profile service if the pair is valid."""
    return True
    

###################################################
#    Game events functions
###################################################

def record_gameevent(sessionid, token, timestamp, gameevent):
    """Checks if the token is valid and records the game event in the database."""

    client = Client.verify_auth_token(token)
    
    if client and ("sessionid" in client):
        if sessionid != client["sessionid"]:
            raise NotAcceptable("Requested sessionID and token sessionid do not match.")
        
        query_sessionid = db.session.query(Session).filter(Session.id == sessionid)
        try:
            res_sessionid = query_sessionid.one()
        except NoResultFound:
            # SessionID is not in the db. Ask the userprofile service and if authorized, 
            # add it in the local db with a timestamp to be able to expire it.
            
            
            try:
                #fetch client object
                client_obj = get_client(client["clientid"])
                if (is_session_authorized(sessionid)):
                    res_session = new_session(sessionid, client_obj.id)
                    res_sessionid = res_session.id
                else:
                    raise SessionNotAuthorizedException("You are not authorized to use this sessionid.")
            except NoResultFound:
                raise NotAuthenticated("This clientid is not valid.")
                #This is strange, and should not happen that a token has a valid clientid for a client not in db
            
            
            
        if (res_sessionid):
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
        raise AuthenticationFailed('Unauthorized token.') 

    
def get_gameevents(token, sessionid):
    """Receives token and an optional sessionid to retrieve existing game events."""
    #Is Client authorized to see this session id?
    client = token_authenticate(token)
    if client.is_session_authorized(sessionid):
        query_events = db.session.query(GameEvent).filter(GameEvent.session_id == sessionid)
        res_events = query_events.all()
        #LOG.debug("Found %s results." % len(res_events))
        return res_events
    else:
        #LOG.warning("User tried to use an invalid token.")
        raise AuthenticationFailed('Unauthorized token.') 
    
    
###################################################
#    Clients
###################################################

def get_client(clientid):
    """Auxiliary function for the view, to retrieve a Client object from a clientid."""
    client = db.session.query(Client).filter_by(clientid = clientid).one()
    return client
    
    

###################################################
#    Authentication functions
###################################################

def client_authenticate(clientid, apikey):
    """Tries to authenticate a client by checking a clientid/apikey pair."""
    try:
        client = db.session.query(Client).filter_by(clientid = clientid).one()
        if (not client.verify_apikey(apikey)):
            raise AuthenticationFailed("Wrong credentials.")
        else:
            return client
    except NoResultFound:
        raise AuthenticationFailed("Clientid does not exist.")

def token_authenticate(token):
    """Tries to authenticate a client checking the token."""
    try:
        token_client = Client.verify_auth_token(token)
        clientid_from_token = token_client["clientid"]
        client = db.session.query(Client).filter_by(clientid = clientid_from_token).one()
        return client
    except NoResultFound:
        # Temporary fix to be able to create the first admin user
        if clientid_from_token == "masteroftheuniverse":
            client = Client(clientid_from_token, "easkdajskda")
            return client
        else:
            raise AuthenticationFailed("Clientid does not exist.")

    