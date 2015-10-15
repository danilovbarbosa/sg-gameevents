'''
Created on 15 Oct 2015

@author: mbrandaoca
'''
from flask import render_template, flash, redirect
from flask import Flask, jsonify, request, abort
from flask import current_app, Blueprint, render_template
from flask.ext.api import status 
from flask.helpers import make_response
from app import app
import datetime
import json

from app import controller

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
    return jsonify({'gamingsession': gamingsession}), status.HTTP_200_OK

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
    