'''
Created on 13 Oct 2015

@author: mbrandaoca
'''
from flask import Flask, jsonify, request, abort
from flask.ext.api import status 
from flask.helpers import make_response
import datetime
import json

import gameevents

app = Flask(__name__)



@app.route('/gameevents/api/v1.0/initsession', methods=['POST'])
def initsession():
    if not request.json or not 'id' in request.json:
        abort(status.HTTP_400_BAD_REQUEST)
    gamingsession = {
        'id': request.json['id'],
        'timestamp': str(datetime.datetime.now()),
        'status':'active'
    }
    GameEvents.startrecording(gamingsession)
    return jsonify({'gamingsession': gamingsession}), status.HTTP_200_OK

@app.route('/gameevents/api/v1.0/endsession', methods=['POST'])
def endsession():
    if not request.json or not 'id' in request.json:
        abort(status.HTTP_400_BAD_REQUEST)
    #gamingsession = (item for item in sessions if item["id"] == request.json['id']).next()
    gamingsession = next((item for item in sessions if item["id"] == request.json['id']), None)
    if GameEvents.finishrecording(gamingsession):
        return jsonify({'gamingsession': gamingsession}), status.HTTP_200_OK
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
    if GameEvents.recordgameevent(gamevent):
        return jsonify({'gamevent': gamevent}), status.HTTP_201_CREATED



if __name__ == '__main__':
    app.run(debug=True)
    