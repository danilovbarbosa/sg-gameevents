'''
Defines the methods/endpoints (the views) of the gameevents service.
This defines the interaction points, but the actual logic is treated
by the :mod:`controller`.
'''
from flask import render_template, flash, redirect
from flask import Flask, jsonify, request, abort
from flask import current_app, Blueprint, render_template
from flask.ext.api import status 
from flask.helpers import make_response
from app import app, auth
import datetime
import json
import time

from app.errors import TokenExpired


from app import controller
from app.models import Client

from flask.ext.api.exceptions import AuthenticationFailed

'''TODO: check if request contains clientid, apikey and **valid** sessionid (will need to call the userprof svc)'''
@app.route('/gameevents/api/v1.0/token', methods = ['POST'])
def get_auth_token():
    if not request.json or not 'clientid' or not 'sessionid' in request.json:
        abort(status.HTTP_400_BAD_REQUEST)
    else:
        clientid = request.json['clientid']
        sessionid = request.json['sessionid']
        if "apikey" in request.json:
            apikey = request.json['apikey']
        else:
            apikey = False
        try:
            #TODO: check if sessionid exists in db
            
            #if does not exist, ask the user profile service to confirm that session id exists and that user 
            # authorized the game to use it and the game events service to receive data. if everything is fine,
            # add session id to db and proceed to create a token for the game.
            #controller.startgamingsession(sessionid) 
            token = controller.authenticate(clientid, apikey, sessionid)
        except AuthenticationFailed as e:
            app.logger.warning(e.args)
            abort(status.HTTP_401_UNAUTHORIZED, {'message': 'Could not authenticate. Please try again.'})
        except TokenExpired as e:
            abort(status.HTTP_401_UNAUTHORIZED, {'message': 'Your token expired. Please generate another one.'})
        except Exception as e:
            app.logger.error(e, exc_info=False)
            abort(status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            if token:
                return jsonify({ 'token': token.decode('ascii') })
            else:
                app.logger.warning("User could not authenticate.")
                abort(status.HTTP_401_UNAUTHORIZED, {'message': 'Could not authenticate. Please try again.'})
        

@auth.verify_password
def verify_password(clientid_or_token, apikey=False):
    try:
        return controller.authenticate(clientid_or_token, apikey)
    except Exception as e:
        app.logger.error(e, exc_info=False)
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR) # missing arguments
           
    


@app.route('/gameevents/api/v1.0/client', methods = ['POST'])
def new_client():
    clientid = request.json.get('clientid')
    apikey = request.json.get('apikey')
    try:
        client = controller.newclient(clientid, apikey)
    except Exception as e:
        abort(400, {'message': e.args}) # missing arguments
    #return jsonify({ 'clientid': client.clientid }), 201, {'Location': url_for('token', clientid = client.clientid, apikey = client.apikey, _external = True)}
    return jsonify({'message': 'Client ID created'}), status.HTTP_201_CREATED

@app.route('/gameevents/api/v1.0/initsession', methods=['POST'])
def initsession():
    if not request.json or not 'id' in request.json:
        abort(status.HTTP_400_BAD_REQUEST)
    gamingsession = {
        'id': request.json['id'],
        'timestamp': str(datetime.datetime.now()),
        'status':'active'
    }
    controller.startgamingsession()
    return jsonify({'token': gamingsession}), status.HTTP_200_OK

@app.route('/gameevents/api/v1.0/endsession', methods=['POST'])
def endsession():
    if not request.json or not 'id' in request.json:
        abort(status.HTTP_400_BAD_REQUEST)
    if controller.finishgamingsession(request.json['id']):
        return jsonify({'message': 'Session terminated'}), status.HTTP_200_OK
    else:
        resp = make_response(json.dumps({'error': 'No such session.'}), status.HTTP_405_METHOD_NOT_ALLOWED)
        h = resp.headers
        h['Access-Control-Allow-Methods'] = 'initsession'        
        return resp

'''
    Receives a json request with an auth token, timestamp, and game event.
    token:
'''
@app.route('/gameevents/api/v1.0/commitevent', methods=['POST'])
def commitevent():
    if not request.json:
        app.logger.warning("Received an empty request, aborting...")
        abort(status.HTTP_400_BAD_REQUEST, {'message': "Bad request. Please format as json."})
        
    if not ( ('token' in request.json) and ('gameevent' in request.json) and ('timestamp' in request.json) ):
        app.logger.warning("Received a request missing required values, aborting...")
        abort(status.HTTP_400_BAD_REQUEST, {'message': "Your request needs to provide values 'token','timestamp' and a 'gameevent'."})
    else:
        app.logger.debug("Good request, continuing...")
        
    
    try:
        #app.logger.debug("trying to expire the token.")
        #time.sleep(5) #expire the token
        success = controller.recordgameevent(request.json['token'], request.json['timestamp'], request.json['gameevent']) 
        if success:
            app.logger.info("Successfully recorded a game event.")
            return jsonify({'message': "Game event recorded successfully."}), status.HTTP_201_CREATED
        else:
            app.logger.warning("Could not record game event.")       
        #    return jsonify({'message': 'Sorry, could not process your request.'}), status.HTTP_500_INTERNAL_SERVER_ERROR
    except AuthenticationFailed as e:
        app.logger.warning("Authentication failure when trying to record game event.")          
        abort(status.HTTP_401_UNAUTHORIZED, {'message': e.args}) # missing arguments   
    except Exception as e:
        app.logger.error("Undefined exception when trying to record a game event.")
        app.logger.error(e, exc_info=False)
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR) # missing arguments 