'''
Created on 15 Oct 2015

@author: mbrandaoca
'''
from flask import render_template, flash, redirect
from flask import Flask, jsonify, request, abort
from flask import current_app, Blueprint, render_template
from flask.ext.api import status 
from flask.helpers import make_response
from app import app, auth
import datetime
import json

from app.errors import TokenExpired


from app import controller
from app.models import Client

from flask.ext.api.exceptions import AuthenticationFailed

@app.route('/gameevents/api/v1.0/token', methods = ['POST'])
def get_auth_token():
    if not request.json or not 'clientid' in request.json:
        abort(status.HTTP_400_BAD_REQUEST)
    else:
        clientid = request.json['clientid']
        if "apikey" in request.json:
            apikey = request.json['apikey']
        else:
            apikey = False
        try:
            token = controller.authenticate(clientid, apikey)
        except AuthenticationFailed as e:
            app.logger.warning(e.args)
            abort(status.HTTP_401_UNAUTHORIZED, {'message': 'Could not authenticate. Please try again.'})
        except TokenExpired as e:
            abort(status.HTTP_401_UNAUTHORIZED, {'message': 'Your token expired. Please generate another one.'})
        except Exception as e:
            app.logger.warning(e, exc_info=True)
            abort(status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            if token:
                return jsonify({ 'token': token.decode('ascii') })
            else:
                abort(status.HTTP_401_UNAUTHORIZED, {'message': 'Could not authenticate. Please try again.'})
        

@auth.verify_password
def verify_password(clientid_or_token, apikey=False):
    try:
        return controller.authenticate(clientid_or_token, apikey)
    except Exception as e:
        app.logger.warning(e)
        abort(status.HTTP_500_INTERNAL_SERVER_ERROR) # missing arguments
           
    


# @app.route('/gameevents/api/v1.0/client', methods = ['POST'])
# def new_client():
#     clientid = request.json.get('clientid')
#     apikey = request.json.get('apikey')
#     try:
#         client = controller.newclient(clientid, apikey)
#     except Exception as e:
#         abort(400, {'message': e.args}) # missing arguments
#     #return jsonify({ 'clientid': client.clientid }), 201, {'Location': url_for('token', clientid = client.clientid, apikey = client.apikey, _external = True)}
#     return jsonify({'message': 'Client ID created'}), status.HTTP_201_CREATED

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

@app.route('/gameevents/api/v1.0/commitevent', methods=['POST'])
def commitevent():
    if not request.json or not 'sessionid' in request.json:
        abort(status.HTTP_400_BAD_REQUEST)
    gamevent = {
        'sessionid': request.json['sessionid'],
        'timestamp': str(datetime.datetime.now()),
        'gameevent': request.json['gameevent']
    }
    if controller.recordgameevent(request.json['sessionid'], request.json['gameevent']):
        return jsonify({'gamevent': gamevent}), status.HTTP_201_CREATED
    