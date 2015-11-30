'''
Controller of the application, which defines the behaviour
of the application when called by the views.
'''

#from flask import current_app
from uuid import UUID

# Exceptions and errors
from flask.ext.api.exceptions import AuthenticationFailed, ParseError
#from lxml.etree import XMLSyntaxError
from simplejson.scanner import JSONDecodeError

from sqlalchemy.orm.exc import NoResultFound 
from gameevents_app.errors import *  # @UnusedWildImport
#from itsdangerous import BadSignature, SignatureExpired
#from werkzeug.exceptions import Unauthorized
#from flask_api.exceptions import NotFound

import simplejson
#from lxml import etree, objectify

# Models
from gameevents_app.models.session import Session
from gameevents_app.models.client import Client
from gameevents_app.models.gameevent import GameEvent

#Extensions
from .extensions import db, LOG
from flask_api.exceptions import NotAcceptable, NotFound



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
    if (is_uuid_valid(sessionid)):
        if (sessionid == "ac52bb1d811356ab3a8e8711c5f7ac5d"):
            return False
        else:
            return True
    else:
        return False
    

###################################################
#    Game events functions
###################################################

def record_gameevent(sessionid, token, timestamp, events):
    """Checks if the token is valid and records the game event(s) in the database.
    Returns the count of inserted items."""

    client = Client.verify_auth_token(token)
    
   
    if client and ("sessionid" in client):
        if sessionid != client["sessionid"]:
            raise NotAcceptable("Requested sessionID and token sessionid do not match.")
        
        query_sessionid = db.session.query(Session).filter(Session.id == sessionid)
        try:
            res_sessionid = query_sessionid.one()
        except NoResultFound:
            # SessionID is not in the db.
            raise NotFound("This sessionid is not in the database. Did you request a token first?")
            
        #serialized_events = False
        decoded_events = False
        count_new_records = 0
        if (res_sessionid):
            #TODO: Validate the game event against XML schema or JSON-LD context?
            try:
                decoded_events = simplejson.loads(events)
                #serialized_events = simplejson.dumps(decoded_events)
            except JSONDecodeError:
                #LOG.debug("not json")
                pass           
            
            if decoded_events:
                for decoded_event in decoded_events:
                    new_gameevent = GameEvent(sessionid, simplejson.dumps(decoded_event))
                    db.session.add(new_gameevent)
                    try:
                        db.session.commit()
                        count_new_records = count_new_records + 1
                    except Exception as e:
                        LOG.warning(e)
                        db.session.rollback()
                        db.session.flush() # for resetting non-commited .add()
                        LOG.error(e, exc_info=True)
                        raise e
            return count_new_records        
    else:
        raise AuthenticationFailed('Unauthorized token. You need a client token to edit gaming sessions.') 

    
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

def client_authenticate(clientid, apikey, sessionid):
    """Tries to authenticate a client by checking a clientid/apikey pair."""
    client = False
    session = False

    # First, try to see if clientid/apikey is valid
    try:
        client = db.session.query(Client).filter_by(clientid = clientid).one()
        if (not client.verify_apikey(apikey)):
            raise AuthenticationFailed("Wrong credentials.")
    except NoResultFound:
        raise AuthenticationFailed("Clientid does not exist.")
        
    #Is this an admin trying to authenticate without sessionid?
    if (client.is_admin()):
        token = client.generate_auth_token()
    else:
        #Check if sessionid is already in db. If not, ask the UP service
        try:
            session = Session.query.filter_by(id=sessionid, client_id=client.id).one()  # @UndefinedVariable
        except NoResultFound:
            if (is_session_authorized(sessionid)):
                session = new_session(sessionid, client.id)

        if (session):
            token = client.generate_auth_token(session.id)
        else:
            raise AuthenticationFailed("Could not verify session.")
    
    return token
        
    

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
        

        
###################################################
#    Helper functions
###################################################


def is_json(string):
    try:
        json_object = simplejson.loads(string)  # @UnusedVariable
    except ValueError:
        return False
    return True

# def is_xml(string):
#     try:
#         result = objectify.fromstring(string)
#     except XMLSyntaxError:
#         return False
#     return True
    
def is_uuid_valid(sessionid):
    """
    Validate that a UUID string is in
    fact a valid uuid.
    """    

    try:
        val = UUID(sessionid)
    except (ValueError, AttributeError):
        # If it's a value error, then the string 
        # is not a valid hex code for a UUID.
        return False

    return val.hex == sessionid