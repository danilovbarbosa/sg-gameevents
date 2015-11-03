'''
Controller of the application, which defines the behaviour
of the application when called by the views.
'''

import uuid, OpenSSL
from app import app, db, models

import requests #Make REST calls
from requests import RequestException

#from app.errors import InvalidGamingSession, TokenExpired
from flask.ext.api.exceptions import AuthenticationFailed
from flask import render_template

from sqlalchemy.orm.exc import NoResultFound 

from itsdangerous import BadSignature, SignatureExpired

from config import GAMEEVENTS_SERVICE_ENDPOINT

class EventsController:
    
    def __init__ (self):
        #start with empty token
        self.token = False

    def get_events(self, sessionid):
        try:
            token = self.get_token(sessionid)
            if token:
                app.logger.debug("Sending request for events...")
                payload = {"token": token}
                url = GAMEEVENTS_SERVICE_ENDPOINT + '/events'
                response = requests.post(url, json=payload)
                myresponse = response.json()
                return(myresponse)
            else:
                return False
        except RequestException as e:
            app.logger.error(e.args, exc_info=False)
            raise e
            #return render_template('error.html', error="Could not process your request, sorry! Reason: %s " % str(e.args))
    
    def get_token(self, sessionid):
        if self.token:
            return self.token
        else:
            payload = {"clientid": "dashboard", "apikey": "dashboardapikey", "sessionid": sessionid}
            url = GAMEEVENTS_SERVICE_ENDPOINT + '/token'
            app.logger.debug("sending request for token...")
            
            try:
                response = requests.post(url, json=payload)
                myresponse = response.json()
                
                if (response.status_code==200):        
                    if "token" in myresponse:
                        token = myresponse["token"]
                        return token
                    else:
                        app.logger.debug("Server response: %s " % myresponse["message"])
                        raise Exception("Unknown error when trying to get token.")
                else:
                    if "message" in myresponse:
                        app.logger.debug("Server response: %s " % myresponse["message"])
                        #response.raise_for_status()
            except RequestException as e:
                app.logger.error("Request exception when trying to get a token. returning false")
                app.logger.error(e.args, exc_info=False)
                return False
            except Exception as e:
                app.logger.error("Unknown exception when trying to get a token")
                app.logger.error(e.args, exc_info=False)
                raise e
    