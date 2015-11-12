'''
Controller of the application, which defines the behaviour
of the application when called by the views.
'''

#from flask import current_app

# Exceptions and errors
from flask.ext.api.exceptions import AuthenticationFailed, ParseError
from sqlalchemy.orm.exc import NoResultFound 
from gameevents_app.errors import ClientExistsException
#from itsdangerous import BadSignature, SignatureExpired
#from werkzeug.exceptions import Unauthorized
#from flask_api.exceptions import NotFound

# Models
from gameevents_app.models.gamingsession import GamingSession
from gameevents_app.models.client import Client
from gameevents_app.models.gameevent import GameEvent

#Extensions
from .extensions import db, LOG


###################################################
#    Client functions
###################################################

def new_client(clientid, apikey):
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

def get_sessions():
    """"""
    query = db.session.query(GamingSession)
    res_sessions = query.all()
    return res_sessions
    


###################################################
#    Game events functions
###################################################

def record_gameevent(token, timestamp, gameevent):
    """Checks if the token is valid and records the game event in the database."""

    client = Client.verify_auth_token(token)
    if client and ("sessionid" in client):
        sessionid = client["sessionid"]
        query_sessionid = db.session.query(GamingSession).filter(GamingSession.sessionid == sessionid)
        res_sessionid = query_sessionid.one()
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
        query_events = db.session.query(GameEvent).filter(GameEvent.gamingsession_id == sessionid)
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

    