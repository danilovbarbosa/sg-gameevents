'''
Created on 10 Nov 2015

@author: mbrandaoca
'''
from uuid import UUID
import OpenSSL
from passlib.apps import custom_app_context as pwd_context

from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from flask.ext.api.exceptions import AuthenticationFailed

from flask import current_app
from ..extensions import db, LOG

from config import DEFAULT_TOKEN_DURATION




class Client(db.Model):
    """Model "clients" table in the database. 
    It contains id, a clientid, and hashed apikey. Each game/application
    using the service (i.e. a client) must have an entry in this table to be able
    to request an authentication token.    
    """
    
    __tablename__ = "client"    
    id = db.Column(db.String(36), primary_key=True) # Referenced in Sessionid
    clientid = db.Column(db.String(255), unique=True)
    apikey_hash = db.Column(db.String(255))
    role = db.Column(db.String(6))
    sessions = db.relationship("Session", backref="client")


    def __init__(self, clientid, apikey, role):
        """Initialize client class with the data provided, and encrypting password."""
        self.id = UUID(bytes = OpenSSL.rand.bytes(16)).hex
        self.clientid = clientid
        self.apikey_hash = pwd_context.encrypt(apikey)
        self.role = role
        #self.token = None
        
    def as_dict(self):
        """Returns a representation of the object as dictionary."""
        obj_d = {
            'id': self.id,
            'clientid': self.clientid,
            'role': self.role,
        }
        return obj_d
    
    def is_session_authorized(self, sessionid):
        """Checks if the client is authorized to access this sessionid. Returns boolean."""
        #Check if this client can read/write this sessionid
        if (sessionid != "zzzz" and sessionid != False or self.is_admin()): 
            return True
        else:
            return False
        
    def is_admin(self):
        """Checks if the client is an admin. Returns boolean."""
        if (self.role == "admin"):
            return True
        else: 
            return False

    def verify_apikey(self, apikey):
        """Checks if the client's apikey is valid. Returns boolean."""
        #LOG.debug("Checking apikey... clientid %s, apikey %s" % (self.clientid, apikey))
        verified = pwd_context.verify(apikey, self.apikey_hash)
        if verified:
            #g.clientid = self.clientid
            return True
        else:
            return False
        
    @staticmethod
    def verify_auth_token(token):
        """Receives a token and returns the data in the token (id, clientid, sessionid) as dictionary."""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
            #LOG.debug("Got data: %s " % data)
            try:
                sessionid = data["sessionid"]
            except KeyError:
                sessionid = False
            return dict(clientid=data['clientid'], id=data['id'], sessionid=sessionid)
        except SignatureExpired as e:
            raise AuthenticationFailed("Expired token.")
        except BadSignature as e:
            raise AuthenticationFailed("Bad token.")
        except Exception as e:
            LOG.error(e, exc_info=False)
            raise e



    def generate_auth_token(self, sessionid = False, expiration = DEFAULT_TOKEN_DURATION):
        """Generates an authentication token with the id, clientid, and sessionid (if provided).
            It is possible to provide a custom expiration time in seconds.
        """ 
        if (not sessionid):
            if self.is_admin():       
                s = Serializer(current_app.config['SECRET_KEY'], expires_in = expiration)
                return s.dumps({ 'id': self.id, 'clientid' : self.clientid , 'sessionid' : False })
            else:
                raise AuthenticationFailed("You are not admin. You need to provide a sessionid")
        else:
            if self.is_session_authorized(sessionid):
                s = Serializer(current_app.config['SECRET_KEY'], expires_in = expiration)
                return s.dumps({ 'id': self.id, 'clientid' : self.clientid , 'sessionid' : sessionid })
            else:
                raise AuthenticationFailed("You are not authorized to use this sessionid.")

        
    