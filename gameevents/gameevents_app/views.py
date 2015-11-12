'''
Defines the methods/endpoints (the views) of the gameevents service.
This defines the interaction points, but the actual logic is treated
by the :mod:`controller`.
'''

#Flask and modules
from flask import Blueprint, jsonify, request, abort, g
from flask.ext.api import status 
#from flask.helpers import make_response

#Exceptions and errors
from flask.ext.api.exceptions import AuthenticationFailed, ParseError
from gameevents_app.errors import ClientExistsException, TokenExpiredException, InvalidGamingSessionException

#Python modules
#import datetime
#import json
#import time

#Import controller
from gameevents_app import controller

#Extensions
from .extensions import LOG
from sqlalchemy.orm.exc import NoResultFound

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
    a valid "clientid" and "apikey" (unique for each game) and a valid "sessionid".
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
            LOG.warning(e.args)
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

@admin.route('/client', methods = ['POST'])
def new_client():
    """An admin can add a new client by posting a request with a valid admin token, 
    the clientid to be created and the apikey. 
    """
    token = request.json.get('token')
    newclientid = request.json.get('clientid')
    newapikey = request.json.get('apikey')
    
    try:
        current_client = controller.token_authenticate(token)
        is_current_client_admin = current_client.is_admin()
        if (current_client and is_current_client_admin):
            LOG.debug("Current client %s is admin? %s" % (current_client.clientid, is_current_client_admin))
            client = controller.newclient(newclientid, newapikey)
            return jsonify({'message': 'Client ID created, id %s ' % client.clientid}), status.HTTP_201_CREATED
        else:
            return jsonify({'message': 'Sorry, you are not allowed to do this action.'}), status.HTTP_401_UNAUTHORIZED
    except ParseError as e:
        LOG.error(e, exc_info=False)
        return jsonify({'message': 'Invalid request.'}), status.HTTP_400_BAD_REQUEST
        #abort(status.HTTP_400_BAD_REQUEST) # missing arguments
    except NoResultFound as e:
        LOG.error(e, exc_info=False)
        return jsonify({'message': 'Non authenticated.'}), status.HTTP_401_UNAUTHORIZED
    except AuthenticationFailed as e:
        LOG.error(e, exc_info=False)
        return jsonify({'message': 'You are not allowed to do this action. Do you have a valid token?'}), status.HTTP_401_UNAUTHORIZED
        #abort(status.HTTP_400_BAD_REQUEST) # missing arguments
    except ClientExistsException as e:
        LOG.error(e, exc_info=False)
        return jsonify({'message': 'Client already exists in the database.'}), status.HTTP_409_CONFLICT
        #abort(status.HTTP_409_CONFLICT) # missing arguments
    except Exception as e:
        LOG.error(e, exc_info=True)
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR) # missing arguments
        #return jsonify({ 'clientid': client.clientid }), 201, {'Location': url_for('token', clientid = client.clientid, apikey = client.apikey, _external = True)}



@gameevents.route('/sessions', methods = ['POST'])
def get_sessions():
    """The client can request a list of active sessions. The POST request must be sent as JSON 
    and include a valid "token".    
    """  

    #Check if request is json and contains all the required fields
    required_fields = ["token"]
    if not request.json or not (set(required_fields).issubset(request.json)): 
        return jsonify({'message': 'Invalid request. Please try again.'}), status.HTTP_400_BAD_REQUEST
    else:
        #check if client submitted a valid token
        try:
            token = request.json['token']
            client = controller.token_authenticate(token)
                
            if (not client or not client.is_admin()):
                return jsonify({'message': 'You are not authorized to see all sessions.'}), status.HTTP_401_UNAUTHORIZED
            else:
                sessions = controller.getsessions()
                num_results = len(sessions)
                LOG.debug("number of results: %s" % num_results)
                results = [ session.as_dict() for session in sessions ]
                LOG.debug(results)
                return jsonify({'count': num_results, 'results': results}), status.HTTP_200_OK
            
        except KeyError:
            return jsonify({'message': 'Bad request. You need to provide a valid token.'}), status.HTTP_400_BAD_REQUEST
        except AuthenticationFailed as e:
            LOG.warning(e.args)
            abort(status.HTTP_401_UNAUTHORIZED, {'message': 'Could not authenticate. Please check your credentials and try again.'})
        except NoResultFound as e:
            LOG.warning(e.args)
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

@gameevents.route('/commitevent', methods=['POST'])
def commit_event():
    """Receives a json request with a token, timestamp, and game event.
    """
    #Check if request is json and contains all the required fields
    required_fields = ["token", "gameevent", "timestamp"]
    if not request.json or not (set(required_fields).issubset(request.json)):  
        return jsonify({'message': 'Invalid request. Please try again.'}), status.HTTP_400_BAD_REQUEST    
    else:
        LOG.debug("Request is valid. continuing...")
        try:
            LOG.debug(request.json)
            success = controller.recordgameevent(request.json['token'], request.json['timestamp'], request.json['gameevent']) 
            if success:
                LOG.info("Successfully recorded a game event.")
                return jsonify({'message': "Game event recorded successfully."}), status.HTTP_201_CREATED
            else:
                LOG.warning("Could not record game event.")
                abort(status.HTTP_500_INTERNAL_SERVER_ERROR)
        except AuthenticationFailed as e:
            LOG.warning("Authentication failure when trying to record game event.")   
            return jsonify({'message': e.args}), status.HTTP_401_UNAUTHORIZED    
        except Exception as e:
            LOG.error("Undefined exception when trying to record a game event.")
            LOG.error(e, exc_info=False)
            abort(status.HTTP_500_INTERNAL_SERVER_ERROR) 
            
@gameevents.route('/events', methods=['POST'])
def get_events():
    """Lists all game events associated to a gaming session. Requires a valid token and a sessionid.
    """
    #Check if request is json and contains all the required fields
    required_fields = ["token", "sessionid"]
    if not request.json or not (set(required_fields).issubset(request.json)): 
        return jsonify({'message': 'Invalid request. Please try again.'}), status.HTTP_400_BAD_REQUEST  
    else:
        token =  request.json['token']
        sessionid =  request.json['sessionid']
        try:
            client = controller.token_authenticate(token)
            if client.is_session_authorized(sessionid):
                gameevents = controller.getgameevents(token, sessionid)
                num_results = len(gameevents)
                LOG.debug("number of results: %s" % num_results)
                results = [ gameevent.as_dict() for gameevent in gameevents ]
                LOG.debug(results)
                return jsonify({'count': num_results, 'results': results}), status.HTTP_200_OK
            else:
                return jsonify({'message': "Not authorized to see events for this session."}), status.HTTP_401_UNAUTHORIZED
            
        except AuthenticationFailed as e:
            return jsonify({'message': "Authentication failure when trying to read game events for a token."}), status.HTTP_401_UNAUTHORIZED  
        
        except Exception as e:
            LOG.error("Undefined exception when trying to read game events for a token.")
            LOG.error(e, exc_info=True)
            abort(status.HTTP_500_INTERNAL_SERVER_ERROR) 
  

    