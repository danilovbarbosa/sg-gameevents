'''
Defines the views of the dashboard.
This defines the interaction points, but the actual logic is treated
by the :mod:`controller`.
'''
from flask import render_template, flash, redirect, url_for
from flask import Flask, jsonify, request, abort
from flask import current_app, Blueprint
from flask.ext.api import status 
from flask.helpers import make_response
from app import app, auth
import datetime
import json
import time
from lxml import objectify
from requests import ConnectionError

from app import controller

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html",
                           title='Home')
    
@app.route('/error')
def error():
    return render_template("error.html",
                           title='Error')


@app.route('/events', methods = ['GET'])
def eventswrapper():
    return render_template('eventswrapper.html')

@app.route('/events/<sessionid>', methods = ['GET'])
def events(sessionid):
    return render_template('events.html', sessionid = sessionid)


@app.route('/get_events/<sessionid>', methods = ['GET'])
def get_events(sessionid):
    """The index page makes a request to the gameevents service and
    provides a live feed of the game events for a determined session      
    """
    ajax_response = {}
    try:
        events_controller = controller.EventsController()
        events_result = events_controller.get_events(sessionid)   
        if events_result:
            app.logger.debug(events_result)
            if "count" in events_result:
                count = events_result["count"]
            if "results" in events_result:
                events_xml = events_result["results"]
            events = []
            for event_xml in events_xml:
                formatted_event = {}
                
                #app.logger.debug(event_xml["gameevent"])
                myevent = objectify.fromstring(event_xml["gameevent"])
                
                app.logger.debug(myevent)
                
                try:
                    formatted_event["level"] = '%s' % myevent.level
                except AttributeError:
                    formatted_event["level"] = "==Not in a level=="
            
                try:
                    timestamp = datetime.datetime.fromtimestamp(myevent.timestamp)
                    formatted_event["timestamp"] = '%s' % timestamp.strftime( "%Y-%m-%d %H:%M:%S %Z")
                except AttributeError:
                    formatted_event["timestamp"] = "==No timestamp=="
                    
                try:
                    formatted_event["action"] = '%s' % myevent.action
                except AttributeError:
                    formatted_event["action"] = "==No action=="
                
                app.logger.debug(formatted_event)
                events.append(formatted_event)
            
            #app.logger.debug(events)
            #Invert the response
            events.reverse()
            #app.logger.debug(events)
            ajax_response["status"] = "success"
            ajax_response["data"] = events

        
        else:
            ajax_response["status"] = "error"

    except ConnectionError as e:
        #return render_template("error.html",
        #                   title='Error',
        #                   error='Connection error. Is the game events service up?')
        ajax_response["status"] = "error"

    return jsonify(ajax_response)    
    