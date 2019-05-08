'''
Defines the methods/endpoints of the gameevents service.
This defines the interaction points, but the actual logic is treated
by the :mod:`gameevents_app.controller`.
'''

#Flask and modules
from flask import Blueprint, jsonify, request, abort, make_response, current_app
from flask.ext.api import status 
import simplejson

#Extensions
from .extensions import LOG

#Exceptions and errors
from flask.ext.api.exceptions import AuthenticationFailed, ParseError, NotAuthenticated
from sqlalchemy.orm.exc import NoResultFound
from flask_api.exceptions import NotAcceptable, NotFound
from simplejson.scanner import JSONDecodeError
from gameevents_app.errors import * # @UnusedWildImport

#Controller
from gameevents_app import controller

#Gamevents blueprint
gameevents = Blueprint('gameevents', __name__, url_prefix='/v1')

#Admin blueprint
admin = Blueprint('admin', __name__, url_prefix='/v1/admin')


######################################################
# Handshake & help
######################################################

@gameevents.route('/')
def index():
    return "Olá, você está acessando o app Gameevents.", status.HTTP_200_OK


@gameevents.route('/version')
def get_version():
    '''
    Returns the current version of the API.
    '''
#     error = {}
#     error["code"] = "400"
#     error["message"] = "Invalid request. Please try again."
    #payload["data"] = [] 
    #return jsonify(error = error), status.HTTP_400_BAD_REQUEST   
    return jsonify(version='v1'), status.HTTP_200_OK


######################################################
# Authentication
######################################################

@gameevents.route('/token', methods = ['POST'])
def get_token():
    '''
    Returns an authentication token to interact with the service. 
    A non-admin client needs to provide a valid sessionid to get a token. 
    An admin client can request a token without a valid "sessionid" 
    and will be given access to all running sessions.
    
    :<json string clientid: human-readable id of the client
    :<json string apikey: client's apikey
    :<json string sessionid: UUID of the session. Optional for admins 
    :status 200: Successful request, returns the token
    :status 400: Not JSON object or missing parameters
    :status 401: Wrong credentials
    '''

    #Check if request is json and contains all the required fields
    required_fields = ["clientid", "apikey"]
    error = {}
            
    if not request.json or not (set(required_fields).issubset(request.json)):
        error["message"] = "Invalid request. Please try again."
        error["code"] = 400 
        return jsonify(error = error), status.HTTP_400_BAD_REQUEST
    
    else:
        clientid = request.json['clientid']
        apikey = request.json['apikey']
        
        try:
            sessionid = request.json['sessionid']            
        except KeyError:
            sessionid = False
      
        if ( sessionid and ( not controller.is_uuid_valid(sessionid) ) ):
            error["message"] = "Invalid sessionid"
            error["code"] = 400 
            return jsonify(error=error), status.HTTP_400_BAD_REQUEST
            
        try:
            #######################################
            # Success
            #######################################
            
            token = controller.client_authenticate(clientid, apikey, sessionid)
            
            return jsonify(token=token.decode('ascii')), status.HTTP_200_OK


        except (AuthenticationFailed, NotAuthenticated) as e:
            error["message"] = "Could not authenticate. Please check your credentials and try again" 
            error["code"] = 401 
            return jsonify(error=error), status.HTTP_401_UNAUTHORIZED 
        
        except TokenExpiredException as e:
            error["message"] = "Your token expired. Please generate another one." 
            error["code"] = 401 
            return jsonify(error=error), status.HTTP_401_UNAUTHORIZED
        
        except InvalidGamingSessionException as e:
            error["message"] = "Invalid gaming session. Did the player authorize the use of their data?" 
            error["code"] = 401 
            return jsonify(error=error), status.HTTP_401_UNAUTHORIZED
        
        except Exception as e:
            LOG.error(e, exc_info=True)
            error["message"] = "Unexpected error. The developers have been informed." 
            error["code"] = 500
            return jsonify(error=error), status.HTTP_500_INTERNAL_SERVER_ERROR

        
######################################################
# Clients
######################################################

@gameevents.route('/clients', methods = ['POST'])
def new_client():
    '''
    Admin only. Adds a new client.
    
    :reqheader X-AUTH-TOKEN: A valid admin token obtained from :http:get:`/token`
    :<json string clientid: human-readable id of the client to be created
    :<json string api: Plaintext version of the apikey
    :<json string role: Optional role (admin/normal). If not informed, a normal client will be created
    :status 201: Client created successfully
    :status 400: Not JSON object or missing parameters
    :status 401: Token not authorized
    :responseheader Content-Type: application/json
    :responseheader X-Total-Count: the total number of results created
    :>jsonarr string id: Internal id of the created client
    :>jsonarr string clientid: Human-readable id of the client
    :>jsonarr string role: Role of the created client
    :>jsonarr string _links: Link to the resource and related entities (if any)
    
    '''

    #Check if request sent authentication token as header
    auth_token = request.headers.get('X-AUTH-TOKEN', None)
    
    error = {}
    if not auth_token:
        error["message"] = "Missing header ['X-AUTH-TOKEN']" 
        error["code"] = 400
        return jsonify(error=error), status.HTTP_400_BAD_REQUEST
     
    #Check if request is json and contains all the required fields
    required_fields = ["clientid", "apikey"]
    
    if not request.json or not (set(required_fields).issubset(request.json)): 
        error["message"] = "Invalid request. Check your parameters and try again." 
        error["code"] = 400
        return jsonify(error=error), status.HTTP_400_BAD_REQUEST      
    
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
                
                #############################
                # Success
                #############################
                
                client = controller.new_client(newclientid, newapikey, role)
                
                client_response= simplejson.dumps(client.as_hateoas(), indent=2)
                
                response = make_response(client_response, status.HTTP_201_CREATED)
                response.headers["X-Total-Count"] = 1
                response.headers["Content-Type"] = "application/json"
                
                return response
                
            
            else:
                error["message"] = "You are not allowed to do this action." 
                error["code"] = 401
                return jsonify(error=error), status.HTTP_401_UNAUTHORIZED
            
        except ParseError as e:
            error["message"] = "Invalid request." 
            error["code"] = 400
            return jsonify(error=error), status.HTTP_400_BAD_REQUEST
        
        except NoResultFound as e:
            error["message"] = "Could not authenticate your token." 
            error["code"] = 401
            return jsonify(error=error), status.HTTP_401_UNAUTHORIZED
        
        except AuthenticationFailed as e:
            error["message"] = "You are not allowed to do this action. Do you have a valid token?" 
            error["code"] = 401
            return jsonify(error=error), status.HTTP_401_UNAUTHORIZED
        
        except ClientExistsException as e:
            error["message"] = "Client already exists in the database." 
            error["code"] = 409
            return jsonify(error=error), status.HTTP_409_CONFLICT
        
        except Exception as e:
            LOG.error(e, exc_info=True)
            abort(status.HTTP_500_INTERNAL_SERVER_ERROR) # missing arguments
            

@gameevents.route('/clients/<clientid>')
def get_client(clientid): 
    error={}
    error["message"] = "Forbidden" 
    error["code"] = 403
    return jsonify(error=error), status.HTTP_403_FORBIDDEN

######################################################
# Sessions
######################################################

@gameevents.route('/sessions/<sessionid>')
def get_session(sessionid): 
    error={}
    error["message"] = "Forbidden" 
    error["code"] = 403
    return jsonify(error=error), status.HTTP_403_FORBIDDEN



@gameevents.route('/sessions')
def get_sessions():
    '''
    Admin only. Requests a list of all active sessions. 
    
    :reqheader X-AUTH-TOKEN: A valid admin token obtained from :http:get:`/token`
    :status 200: Successful request
    :status 400: Missing headers or parameters
    :status 401: Token not authorized to read all sessions
    :responseheader Content-Type: application/json
    :responseheader X-Total-Count: Total number of results
    :>jsonarr string id: Sessionid
    :>jsonarr string created: Timestamp of when the session was added to the local db
    :>jsonarr string _links: Links to the resource and related entities (if any)
    '''

    try:
        error={}
        auth_token = request.headers.get('X-AUTH-TOKEN', None)
        if not auth_token:
            error["message"] = "Missing header ['X-AUTH-TOKEN']" 
            error["code"] = 400
            return jsonify({'errors':[{'userMessage':""}]}), status.HTTP_400_BAD_REQUEST
            
        client = controller.token_authenticate(auth_token)
            
        if (not client or not client.is_admin()):
            error["message"] = "You are not authorized to see all sessions." 
            error["code"] = 401
            return jsonify({'errors':[{'userMessage':"You are not authorized to see all sessions."}]}), status.HTTP_401_UNAUTHORIZED
        
        else:
            #####################
            # Success
            #####################
            
            sessions = controller.get_sessions()
            num_results = len(sessions)
            #sessions_response = [session.as_dict() for session in sessions] 
            sessions_response = simplejson.dumps([session.as_hateoas() for session in sessions], indent=4)
            response = make_response(sessions_response, status.HTTP_200_OK)
            response.headers["X-Total-Count"] = num_results
            response.headers["Content-Type"] = "application/json"
            
            return response
        
    except AuthenticationFailed as e:
        error["message"] = "Could not authenticate. Please check your token and try again." 
        error["code"] = 401
        return jsonify(error=error), status.HTTP_401_UNAUTHORIZED

    except NoResultFound as e:
        error["message"] = "Could not authenticate. Please check your token and try again." 
        error["code"] = 401
        return jsonify(error=error), status.HTTP_401_UNAUTHORIZED
    
    except TokenExpiredException as e:
        error["message"] = "Your token expired. Please generate another one." 
        error["code"] = 401
        return jsonify(error=error), status.HTTP_401_UNAUTHORIZED
    
    except InvalidGamingSessionException as e:
        error["message"] = "Invalid gaming session. Did the player authorize the use of their data?" 
        error["code"] = 401
        return jsonify(error=error), status.HTTP_401_UNAUTHORIZED
    
    except Exception as e:
        LOG.error(e, exc_info=True)
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR)
            
######################################################
# Game events
######################################################

@gameevents.route('/sessions/<sessionid>/events/<eventid>')
def get_event(sessionid, eventid):
    error={}
    error["message"] = "Forbidden" 
    error["code"] = 403
    return jsonify(error=error), status.HTTP_403_FORBIDDEN
    
@gameevents.route('/sessions/<sessionid>/events', methods=['POST'])
def commit_event(sessionid):
    '''
    Submits a new event related to the given sessionid. Client must be authorized
    to write to the session.
    
    :param string sessionid: 
    :reqheader X-AUTH-TOKEN: A valid token obtained from :http:get:`/token`
    :<jsonarr string events: list of JSON game events
    :status 201: Event created successfully
    :status 400: Not JSON object or missing parameters
    :status 401: Token not authorized to write to session
    :status 404: Sessionid not found
    :responseheader Content-Type: application/json
    :responseheader X-Total-Count: the total number of results created
    :>jsonarr string id: Internal id of the created client
    :>jsonarr string gameevent: JSON representation of the event
    :>jsonarr string _links: Link to the resource and related entities (if any)
    '''

 
    json_package = False
    error={}
    try:
        json_package = request.json
    except JSONDecodeError as e:
        error["message"] = "Invalid request, not valid JSON. Please try again." 
        error["code"] = 400
        return jsonify(error=error), status.HTTP_400_BAD_REQUEST
    
    auth_token = request.headers.get('X-AUTH-TOKEN', None)

    if not auth_token:
        error["message"] = "Missing header ['X-AUTH-TOKEN']." 
        error["code"] = 400
        return jsonify(error=error), status.HTTP_400_BAD_REQUEST
    
    #Check if request is json and contains all the required fields
    required_fields = ["events"] 
    if (not json_package) or (not set(required_fields).issubset(json_package)):
        error["message"] = "Invalid request. Please try again." 
        error["code"] = 400
        return jsonify(error=error), status.HTTP_400_BAD_REQUEST   
    else:
        #Check if events is valid json or xml
#         LOG.debug(type(json_package))
#         LOG.debug(json_package)
#         LOG.debug(json_package["events"])
        is_json = controller.is_json(json_package["events"])
        
        if (not is_json):
            error["message"] = "Invalid request. Please format your gameevent as json." 
            error["code"] = 400
            return jsonify(error=error), status.HTTP_400_BAD_REQUEST
        
        if (not controller.is_uuid_valid(sessionid)):
            error["message"] = "Sessionid not found" 
            error["code"] = 404
            return jsonify(error=error), status.HTTP_404_NOT_FOUND
            
        try:
            ########################
            # Success
            ########################
            
            #Record the event         
            events = controller.record_gameevent(sessionid, auth_token, json_package["events"])
            
            num_results = len(events)
            #sessions_response = [session.as_dict() for session in sessions] 
            events_response = simplejson.dumps([event.as_hateoas() for event in events], indent=2)
                           
            response = make_response(events_response, status.HTTP_201_CREATED)
            response.headers["X-Total-Count"] = num_results
            response.headers["Content-Type"] = "application/json"
            
            return response

           
        except AuthenticationFailed as e:
            error["message"] = "Could not authenticate. Please check your token and try again." 
            error["code"] = 401
            #LOG.warning("Authentication failure when trying to record game event.")
            return jsonify(error=error), status.HTTP_401_UNAUTHORIZED
        
        except (NotFound) as e:
            error["message"] = "SessionID not in the database. If you believe this is an error, contact the developers." 
            error["code"] = 404
            return jsonify(error=error), status.HTTP_404_NOT_FOUND
        
        except NotAcceptable as e:
            error["message"] = e.args 
            error["code"] = 400
            return jsonify(error=error), status.HTTP_400_BAD_REQUEST  
        
        except Exception as e:
            LOG.error(e.args, exc_info=True)
            error["message"] = "Internal error. Please try again."
            error["code"] = 500
            return jsonify(error=error), status.HTTP_500_INTERNAL_SERVER_ERROR
    
            
@gameevents.route('/sessions/<sessionid>/events')
def get_events(sessionid):
    '''
    Lists all game events associated to a gaming session. The user must be authorized to read the session.
    
    :param string sessionid: 
    :reqheader X-AUTH-TOKEN: A valid token obtained from :http:get:`/token`
    :status 200: Successful request, returns the events
    :status 401: Token not authorized to read session
    :status 404: Sessionid not found
    :responseheader Content-Type: application/json
    :responseheader X-Total-Count: the total number of results 
    :>jsonarr string link: Link to the resource
    :>jsonarr string gameevent: JSON representation of the event    
        
    **Example response**:
        
        .. sourcecode:: http        
            
            HTTP/1.0 200 OK
            Content-Type: application/json
            Content-Length: 227
            X-Total-Count: 1
            Server: Werkzeug/0.10.4 Python/3.4.3
            Date: Tue, 01 Dec 2015 16:34:23 GMT

            [
              {
                "gameevent": {
                  "id_questao": "",
                  "nota": "",
                },
                "id": "f9a32e2f23b19d029b8faf0348a02de9",
                "_links": [
                  {
                    "rel": "self",
                    "href": "/v1/sessions/6042b89fcf45c4babd3e0f621713d199/events/f9a32e2f23b19d029b8faf0348a02de9"
                  },
                  {
                    "rel": "session",
                    "href": "/v1/sessions/6042b89fcf45c4babd3e0f621713d199"
                  }
                ]
              }
            ]
    '''
    
    auth_token = request.headers.get('X-AUTH-TOKEN', None)
    error={}
    if not auth_token:
        error["status"]="400"
        error["message"]="Missing header ['X-AUTH-TOKEN']"
        return jsonify(error=error), status.HTTP_400_BAD_REQUEST
            
    try:
        
        client = controller.token_authenticate(auth_token)
        
        if client.is_session_authorized(sessionid):

            gameevents = controller.get_gameevents(auth_token, sessionid)
            
            num_results = len(gameevents)
            
            results = simplejson.dumps([ gameevent.as_dict() for gameevent in gameevents ])
            
            response = make_response(results, status.HTTP_200_OK)
            response.headers["X-Total-Count"] = num_results
            response.headers["Content-Type"] = "application/json"
            
            return response
        
        else:
            error["message"] = "Not authorized to see events for this session." 
            error["code"] = 401
            return jsonify(error=error), status.HTTP_401_UNAUTHORIZED
      
    except AuthenticationFailed as e:
        error["message"] = "Authentication failure when trying to read game events for a token." 
        error["code"] = 401
        return jsonify(error=error), status.HTTP_401_UNAUTHORIZED  
      
    except Exception as e:
        LOG.error(e.args, exc_info=True)
        error["message"] = "Internal error. Please try again."
        error["code"] = 500
        return jsonify(error=error), status.HTTP_500_INTERNAL_SERVER_ERROR




    
    