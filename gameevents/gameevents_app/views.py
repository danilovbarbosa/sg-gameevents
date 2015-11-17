'''
Defines the methods/endpoints (the views) of the gameevents service.
This defines the interaction points, but the actual logic is treated
by the :mod:`controller`.
'''

#Flask and modules
from flask import Blueprint, jsonify, request, abort, make_response
from flask.json import dumps
from flask.ext.api import status 
#from flask.helpers import make_response

#Exceptions and errors
from flask.ext.api.exceptions import AuthenticationFailed, ParseError
import json
from simplejson.decoder import JSONDecodeError
from gameevents_app.errors import *

#Python modules
#import datetime
#import json
#import time

#Import controller
from gameevents_app import controller

#Extensions
from .extensions import LOG
from sqlalchemy.orm.exc import NoResultFound
from flask_api.exceptions import NotAcceptable
from sys import exc_info
from werkzeug.exceptions import BadRequest

#Gamevents blueprint
gameevents = Blueprint('gameevents', __name__, url_prefix='/gameevents/api/v1.0')

#Admin blueprint
admin = Blueprint('admin', __name__, url_prefix='/gameevents/api/v1.0/admin')



######################################################
# Authentication
######################################################

@gameevents.route('/token', methods = ['POST'])
def get_token():
    """The client can request an authentication token that will be used to 
    interact with the service. The POST request must be sent as JSON and include
    a valid "clientid" and "apikey" (unique for each game). An admin client can request
    a token without a valid "sessionid" and will be given access to all running sessions.
    A non-admin client needs to provide a valid sessionid to get a token. 
    The sessionid will be validated by the user profile service.       
    """

    #Check if request is json and contains all the required fields
    required_fields = ["clientid", "apikey"]
    if not request.json or not (set(required_fields).issubset(request.json)): 
        return jsonify({'message': 'Invalid request. Please try again.'}), status.HTTP_400_BAD_REQUEST      
    else:
        clientid = request.json['clientid']
        apikey = request.json['apikey']
        
        try:
            sessionid = request.json['sessionid']
        except KeyError:
            sessionid = False
            
      
        try:
            client = controller.client_authenticate(clientid, apikey)
            token = client.generate_auth_token(sessionid)
            return jsonify({ 'token': token.decode('ascii') })
        except AuthenticationFailed as e:
            return jsonify({'message': 'Could not authenticate. Please check your credentials and try again.'}), status.HTTP_401_UNAUTHORIZED 
        except TokenExpiredException as e:
            return jsonify({'message': 'Your token expired. Please generate another one.'}), status.HTTP_401_UNAUTHORIZED
        except InvalidGamingSessionException as e:
            return jsonify({'message': 'Invalid gaming session. Did the player authorize the use of their data?'}), status.HTTP_401_UNAUTHORIZED
        except Exception as e:
            LOG.error(e, exc_info=True)
            return jsonify({'message': 'Unexpected error'}), status.HTTP_500_INTERNAL_SERVER_ERROR

        
######################################################
# Admin
######################################################

@admin.route('/clients', methods = ['POST'])
def new_client():
    """An admin can add a new client by posting a request with a valid admin token, 
    the clientid to be created, the apikey and the optional role (admin or normal). 
    The token must be passed as a X-AUTH-TOKEN header.
    """
    #Check if request sent authentication token as header
    auth_token = request.headers.get('X-AUTH-TOKEN', None)
    if not auth_token:
        return jsonify({'errors':[{'userMessage':"Missing header ['X-AUTH-TOKEN']."}]}), status.HTTP_400_BAD_REQUEST
     
    #Check if request is json and contains all the required fields
    required_fields = ["clientid", "apikey"]
    if not request.json or not (set(required_fields).issubset(request.json)): 
        return jsonify({'message': 'Invalid request. Please try again.'}), status.HTTP_400_BAD_REQUEST      
    else:            
        newclientid = request.json.get('clientid')
        newapikey = request.json.get('apikey')
        
        try:
            role = request.json.get('role')
        except Exception:
            role = "normal"
        
        try:
            current_client = controller.token_authenticate(auth_token)
            is_current_client_admin = current_client.is_admin()
            if (current_client and is_current_client_admin):
                client = controller.new_client(newclientid, newapikey, role)
                return jsonify({'message': 'Client ID created, id %s ' % client.clientid}), status.HTTP_201_CREATED
            else:
                return jsonify({'message': 'Sorry, you are not allowed to do this action.'}), status.HTTP_401_UNAUTHORIZED
        except ParseError as e:
            return jsonify({'message': 'Invalid request.'}), status.HTTP_400_BAD_REQUEST
        except NoResultFound as e:
            return jsonify({'message': 'Non authenticated.'}), status.HTTP_401_UNAUTHORIZED
        except AuthenticationFailed as e:
            return jsonify({'message': 'You are not allowed to do this action. Do you have a valid token?'}), status.HTTP_401_UNAUTHORIZED
            #abort(status.HTTP_400_BAD_REQUEST) # missing arguments
        except ClientExistsException as e:
            #LOG.error(e, exc_info=False)
            return jsonify({'message': 'Client already exists in the database.'}), status.HTTP_409_CONFLICT
            #abort(status.HTTP_409_CONFLICT) # missing arguments
        except Exception as e:
            LOG.error(e, exc_info=True)
            abort(status.HTTP_500_INTERNAL_SERVER_ERROR) # missing arguments


@gameevents.route('/sessions')
def get_sessions():
    """An admin client can request a list of all active sessions. 
    The token must be passed as a X-AUTH-TOKEN header.
    """  

    try:
        auth_token = request.headers.get('X-AUTH-TOKEN', None)
        if not auth_token:
            return jsonify({'errors':[{'userMessage':"Missing header ['X-AUTH-TOKEN']."}]}), status.HTTP_400_BAD_REQUEST
            
        client = controller.token_authenticate(auth_token)
            
        if (not client or not client.is_admin()):
            return jsonify({'errors':[{'userMessage':"You are not authorized to see all sessions."}]}), status.HTTP_401_UNAUTHORIZED
        else:
            sessions = controller.get_sessions()
            num_results = len(sessions)
            results = [ session.as_dict() for session in sessions ]
            response = make_response(dumps(results), status.HTTP_200_OK)
            response.headers["X-Total-Count"] = num_results
            return response
        
    except AuthenticationFailed as e:
        abort(status.HTTP_401_UNAUTHORIZED, {'message': 'Could not authenticate. Please check your credentials and try again.'})
    except NoResultFound as e:
        abort(status.HTTP_401_UNAUTHORIZED, {'message': 'Could not authenticate. Please check your credentials and try again.'})
    except TokenExpiredException as e:
        abort(status.HTTP_401_UNAUTHORIZED, {'message': 'Your token expired. Please generate another one.'})
    except InvalidGamingSessionException as e:
        abort(status.HTTP_401_UNAUTHORIZED, {'message': 'Invalid gaming session. Did the player authorize the use of their data?'})
    except Exception as e:
        LOG.error(e, exc_info=True)
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR)
            
######################################################
# Game events
######################################################

@gameevents.route('/sessions/<sessionid>/events', methods=['POST'])
def commit_event(sessionid):
    """Receives a json request with a token, timestamp, and game event.
    The authentication token must be passed as a X-AUTH-TOKEN header.
    The user must be authorized to read/write the session.
    """
 
    try:
        json_results = request.json
        #json = request.json    

        auth_token = request.headers.get('X-AUTH-TOKEN', None)
    
        if not auth_token:
            return jsonify({'errors':[{'userMessage':"Missing header ['X-AUTH-TOKEN']."}]}), status.HTTP_400_BAD_REQUEST         
    
        #Check if request is json and contains all the required fields
        required_fields = ["gameevent", "timestamp"] 
        if (not json_results) or (not set(required_fields).issubset(json_results)):
            return jsonify({'message': 'Invalid request. Please try again.'}), status.HTTP_400_BAD_REQUEST    
        else:            
            success = controller.record_gameevent(sessionid, auth_token, json_results['timestamp'], json_results['gameevent']) 
            if success:
                return jsonify({'message': "Game event recorded successfully."}), status.HTTP_201_CREATED
            else:
                return jsonify({'message': "Could not record game event."}), status.HTTP_500_INTERNAL_SERVER_ERROR
    except JSONDecodeError as e:
        return jsonify({'message': 'Invalid request, not valid JSON. Please try again.'}), status.HTTP_400_BAD_REQUEST
    except AuthenticationFailed as e:
        LOG.warning("Authentication failure when trying to record game event.")   
        return jsonify({'message': e.args}), status.HTTP_401_UNAUTHORIZED    
    except NotAcceptable as e:
        LOG.warning(e.args)   
        return jsonify({'message': e.args}), status.HTTP_400_BAD_REQUEST  
    except Exception as e:
        LOG.error("Undefined exception when trying to record a game event.")
        LOG.error(e.args, exc_info=True)
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR) 
    
            
@gameevents.route('/sessions/<sessionid>/events')
def get_events(sessionid):
    """Lists all game events associated to a gaming session.
    The authentication token must be passed as a X-AUTH-TOKEN header.
    The user must be authorized to read the session.
    """
    
    auth_token = request.headers.get('X-AUTH-TOKEN', None)
    if not auth_token:
        return jsonify({'errors':[{'userMessage':"Missing header ['X-AUTH-TOKEN']."}]}), status.HTTP_400_BAD_REQUEST
            
    try:
        client = controller.token_authenticate(auth_token)
        if client.is_session_authorized(sessionid):
            gameevents = controller.get_gameevents(auth_token, sessionid)
            num_results = len(gameevents)
            #LOG.debug("number of results: %s" % num_results)
            results = [ gameevent.as_dict() for gameevent in gameevents ]
            #LOG.debug(results)
            response = make_response(dumps(results), status.HTTP_200_OK)
            response.headers["X-Total-Count"] = num_results
            return response
        else:
            return jsonify({'message': "Not authorized to see events for this session."}), status.HTTP_401_UNAUTHORIZED
      
    except AuthenticationFailed as e:
        return jsonify({'message': "Authentication failure when trying to read game events for a token."}), status.HTTP_401_UNAUTHORIZED  
      
    except Exception as e:
        LOG.error("Undefined exception when trying to read game events for a token.")
        LOG.error(e, exc_info=True)
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR) 


    