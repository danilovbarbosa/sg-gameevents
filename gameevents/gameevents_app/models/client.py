'''
Created on 10 Nov 2015

@author: mbrandaoca
'''
from uuid import UUID
import OpenSSL
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

from flask import current_app
from ..extensions import db

from config import DEFAULT_TOKEN_DURATION

#Logging
from logging import getLogger
LOG = getLogger(__name__)

class Client(db.Model):
    """Model "clients" table in the database. 
    It contains id, a clientid, and hashed apikey. Each game/application
    using the service (i.e. a client) must have an entry in this table to be able
    to request an authentication token.    
    """
    
    __tablename__ = "client"    
    id = db.Column(db.String, primary_key=True)
    clientid = db.Column(db.String)
    apikey_hash = db.Column(db.String)


    def __init__(self, clientid, apikey):
        """"""
        self.id = UUID(bytes = OpenSSL.rand.bytes(16)).hex
        self.clientid = clientid
        self.apikey_hash = pwd_context.encrypt(apikey)
        #self.token = None
        
    def as_dict(self):
        obj_d = {
            'id': self.id,
            'clientid': self.clientid,
        }
        return obj_d

    def verify_apikey(self, apikey):
        LOG.debug("Checking apikey... clientid %s, apikey %s" % (self.clientid, apikey))
        return pwd_context.verify(apikey, self.apikey_hash)

    def is_session_authorized(self, sessionid):
        #Check if this client can read/write this sessionid
        if (sessionid != "zzzz" and sessionid != False): 
            return True
        else:
            return False

    def generate_auth_token(self, sessionid = False, expiration = DEFAULT_TOKEN_DURATION):        
        s = Serializer(current_app.config['SECRET_KEY'], expires_in = expiration)
        LOG.debug("Generating token with expiration: %s" % expiration)
        return s.dumps({ 'id': self.id, 'clientid' : self.clientid , 'sessionid' : sessionid })
        
    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
            LOG.debug("Got data: %s " % data)
            return dict(clientid=data['clientid'], id=data['id'])
        except SignatureExpired as e:
            LOG.debug("Expired token, returning false")
            LOG.debug(e, exc_info=False)
            #raise e
            return False # valid token, but expired
        except BadSignature as e:
            LOG.debug("Invalid token, returning false.")
            LOG.debug(e, exc_info=False)
            #raise e
            return False # invalid token
        except Exception as e:
            LOG.error(e, exc_info=False)
            raise e