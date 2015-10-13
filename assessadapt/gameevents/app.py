'''
Created on 13 Oct 2015

@author: mbrandaoca
'''
from flask import Flask, jsonify, request, abort
from flask.ext.api import status
import logging
import datetime
from flask.helpers import make_response
import json

app = Flask(__name__)

sessions = []

events = [
    {
        'sessionid': 1,
        'title': u'My Title',
        'description': u'My Description',
    }
]

'''
@app.route('/gameevents/api/v1.0/sessions', methods=['GET'])
def get_sessions():
    return jsonify({'sessions': sessions})


@app.route('/gameevents/api/v1.0/events', methods=['GET'])
def get_events():
    return jsonify({'events': events})

    
@app.route('/gameevents/api/v1.0/events', methods=['POST'])
def send_event():
    if not request.json or not 'title' in request.json:
        abort(400)
    event = {
        'sessionid': sessions[-1]['id'] + 1,
        'title': request.json['title'],
        'description': request.json.get('description', "")
    }
    events.append(event)
    return jsonify({'event': event}), 201
    '''

@app.route('/gameevents/api/v1.0/initsession', methods=['POST'])
def initsession():
    if not request.json or not 'id' in request.json:
        abort(status.HTTP_400_BAD_REQUEST)
    gamingsession = {
        'id': request.json['id'],
        'timestamp': str(datetime.datetime.now()),
        'status':'active'
    }
    startrecording(gamingsession)
    return jsonify({'gamingsession': gamingsession}), status.HTTP_200_OK

@app.route('/gameevents/api/v1.0/endsession', methods=['POST'])
def endsession():
    if not request.json or not 'id' in request.json:
        abort(status.HTTP_400_BAD_REQUEST)
    #gamingsession = (item for item in sessions if item["id"] == request.json['id']).next()
    gamingsession = next((item for item in sessions if item["id"] == request.json['id']), None)
    if finishrecording(gamingsession):
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
    recordgameevent(gamevent)
    return jsonify({'gamevent': gamevent}), status.HTTP_201_CREATED

def startrecording(gs):
    logging.info("Started recording a gaming session at %s" % gs['timestamp'])
    sessions.append(gs)

def finishrecording(gs):
    if gs:
        if gs["status"] == "active":
            gs["status"] = "inactive"
            logging.info("Finished recording a gaming session at %s" % gs['timestamp'])
            return True
        else:
            logging.info("No active session found")
            return False
    else:
        logging.info("No such session found")
        return False
    
def recordgameevent(gameevent):
    logging.info("Received game event for sessionid %s" % gameevent['sessionid'])

if __name__ == '__main__':
    app.run(debug=True)
    logging.getLogger(__name__)