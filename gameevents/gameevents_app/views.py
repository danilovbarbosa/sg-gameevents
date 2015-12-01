'''
Defines the methods/endpoints of the gameevents service.
This defines the interaction points, but the actual logic is treated
by the :mod:`gameevents_app.controller`.
'''

#Flask and modules
from flask import Blueprint, jsonify, request, abort, make_response, current_app
#from flask.json import dumps
from flask.ext.api import status 
#from flask.helpers import make_response
import simplejson
#import json


#Python modules
#import datetime
#import json
#import time

#Import controller
from gameevents_app import controller

#Extensions
from .extensions import LOG

#Exceptions and errors
from flask.ext.api.exceptions import AuthenticationFailed, ParseError, NotAuthenticated
from sqlalchemy.orm.exc import NoResultFound
from flask_api.exceptions import NotAcceptable, NotFound
#from sys import exc_info
#from werkzeug.exceptions import BadRequest
from simplejson.scanner import JSONDecodeError
from gameevents_app.errors import * # @UnusedWildImport

#Gamevents blueprint
gameevents = Blueprint('gameevents', __name__, url_prefix='/gameevents/api/v1.0')

#Admin blueprint
admin = Blueprint('admin', __name__, url_prefix='/gameevents/api/v1.0/admin')


######################################################
# Handshake
######################################################

@gameevents.route('/version')
def get_version():
    '''
    
    '''
    return jsonify({'data': [{'version':'v1.0'}] }), status.HTTP_200_OK


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
      
        if ( sessionid and ( not controller.is_uuid_valid(sessionid) ) ):
            return jsonify({'message': 'Invalid sessionid'}), status.HTTP_400_BAD_REQUEST
            
        try:
            token = controller.client_authenticate(clientid, apikey, sessionid)
            #token = client.generate_auth_token(sessionid)
            return jsonify({ 'token': token.decode('ascii') }), status.HTTP_200_OK
        except (AuthenticationFailed, NotAuthenticated) as e:
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
            #LOG.debug(sessions)
            num_results = len(sessions)
            results = [ session.as_dict() for session in sessions ]
            response = make_response(simplejson.dumps(results), status.HTTP_200_OK)
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
 
    json_package = False
    try:
        json_package = request.json
    except JSONDecodeError as e:
        return jsonify({'message': 'Invalid request, not valid JSON. Please try again.'}), status.HTTP_400_BAD_REQUEST

    
    auth_token = request.headers.get('X-AUTH-TOKEN', None)

    if not auth_token:
        return jsonify({'errors':[{'userMessage':"Missing header ['X-AUTH-TOKEN']."}]}), status.HTTP_400_BAD_REQUEST         

    #Check if request is json and contains all the required fields
    required_fields = ["events", "timestamp"] 
    if (not json_package) or (not set(required_fields).issubset(json_package)):
        return jsonify({'message': 'Invalid request. Please try again.'}), status.HTTP_400_BAD_REQUEST    
    else:
        #Check if events is valid json or xml
#         LOG.debug(type(json_package))
#         LOG.debug(json_package)
#         LOG.debug(json_package["events"])
        is_json = controller.is_json(json_package["events"])
        
        if (not is_json):
            return jsonify({'message': 'Please format your gameevent as json.'}), status.HTTP_400_BAD_REQUEST
        
        if (not controller.is_uuid_valid(sessionid)):
            return jsonify({'message': 'Invalid sessionid'}), status.HTTP_400_BAD_REQUEST
            
        try:
            #Record the event         
            count = controller.record_gameevent(sessionid, auth_token, json_package['timestamp'], json_package["events"])
            return jsonify({'message': "Created %s new item(s)." % count}), status.HTTP_201_CREATED    
        except AuthenticationFailed as e:
            #LOG.warning("Authentication failure when trying to record game event.")   
            return jsonify({'message': e.args}), status.HTTP_401_UNAUTHORIZED
        except (NotFound) as e:
            return jsonify({'message': 'SessionID not in the database. Did you ask for a token first?'}), status.HTTP_404_NOT_FOUND
        except NotAcceptable as e:
            LOG.warning(e.args)   
            return jsonify({'message': e.args}), status.HTTP_400_BAD_REQUEST  
        except Exception as e:
            LOG.error("Undefined exception when trying to record a game event.")
            LOG.error(e.args, exc_info=True)
            return jsonify({'message': 'Internal error. Please try again.'}), status.HTTP_500_INTERNAL_SERVER_ERROR
    
            
@gameevents.route('/sessions/<sessionid>/events')
def get_events(sessionid):
    '''
    Lists all game events associated to a gaming session.
    The authentication token must be passed as a X-AUTH-TOKEN header.
    The user must be authorized to read the session.
    
    :param sessionid: The desired sessionid
    :type sessionid: uuid (string)
    :reqheader X-AUTH-TOKEN: A valid token
    :status 200: Successful request, returns the events
    :responseheader: Content-type: application/json
    :responseheader: X-Total-Count: the total number of results 
    
    **Example request**:
        
        .. sourcecode:: http
        
            GET sessions/2bdff61dfa6df36f2e72ef8b2f3da92f/events
            X-AUTH-TOKEN:<yourtoken>
        
    **Example response**:
        
        .. sourcecode:: http        
            
            HTTP/1.0 200 OK
            Content-Type: application/json
            Content-Length: 227
            X-Total-Count: 1
            Server: Werkzeug/0.10.4 Python/3.4.3
            Date: Tue, 01 Dec 2015 16:34:23 GMT
            
            [{
                "session_id": "2bdff61dfa6df36f2e72ef8b2f3da92f",
                "gameevent": {
                    "action": "STARTGAME",
                    "level": "",
                    "result": [],
                    "which_lix": "",
                    "update": "",
                    "timestamp": "2015-12-01T16:33:26Z"
                },
                "id": "de2f06d139d0c940f7dde8d5ec3db4f5"
            }]
    '''
    
    auth_token = request.headers.get('X-AUTH-TOKEN', None)
    if not auth_token:
        return jsonify({'errors':[{'userMessage':"Missing header ['X-AUTH-TOKEN']."}]}), status.HTTP_400_BAD_REQUEST
            
    try:
        client = controller.token_authenticate(auth_token)
        if client.is_session_authorized(sessionid):
            gameevents = controller.get_gameevents(auth_token, sessionid)
            num_results = len(gameevents)
            #LOG.debug("number of results: %s" % num_results)
            #results = [ gameevent.as_dict() for gameevent in gameevents ]
            results = simplejson.dumps([ gameevent.as_dict() for gameevent in gameevents ])
            #LOG.debug(results)
            response = make_response(results, status.HTTP_200_OK)
            response.headers["X-Total-Count"] = num_results
            response.headers["Content-Type"] = "application/json"
            return response
        else:
            return jsonify({'message': "Not authorized to see events for this session."}), status.HTTP_401_UNAUTHORIZED
      
    except AuthenticationFailed as e:
        return jsonify({'message': "Authentication failure when trying to read game events for a token."}), status.HTTP_401_UNAUTHORIZED  
      
    except Exception as e:
        LOG.error("Undefined exception when trying to read game events for a token.")
        LOG.error(e, exc_info=True)
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR) 

######################################################
# Game events
######################################################

@gameevents.route('/help', methods = ['GET'])
def apihelp():
    '''
    Print available functions.
    '''
    func_list = {}
    for rule in current_app.url_map.iter_rules():
        if rule.endpoint != 'static':
            func_list[rule.rule] = current_app.view_functions[rule.endpoint].__doc__
        #print(func_list)
    return jsonify(func_list)
    