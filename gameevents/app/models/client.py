'''
Created on 10 Nov 2015

@author: mbrandaoca
'''
import uuid
import OpenSSL
from passlib.apps import custom_app_context as pwd_context
# 
from app import db
from app import app
# from app.errors import TokenExpired
# 
# from itsdangerous import (TimedJSONWebSignatureSerializer
#                           as Serializer, BadSignature, SignatureExpired)
# from flask.ext.api.exceptions import AuthenticationFailed
# 
# from config import DEFAULT_TOKEN_DURATION

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
        self.id = uuid.UUID(bytes = OpenSSL.rand.bytes(16)).hex
        self.clientid = clientid
        self.apikey_hash = pwd_context.encrypt(apikey)
        #self.token = None

    def verify_apikey(self, apikey):
        app.logger.debug("Checking apikey... clientid %s, apikey %s" % (self.clientid, apikey))
        return pwd_context.verify(apikey, self.apikey_hash)

    '''
    def generate_auth_token(self, expiration = 600):        
        s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
        return s.dumps({ 'id': self.id })
    '''

    """
    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired as e:
            #app.logger.warning(e, exc_info=False)
            raise e
            #return False # valid token, but expired
        except BadSignature as e:
            #app.logger.warning(e, exc_info=False)
            raise e
            #return False # invalid token
        client = Client.query.get(data['id'])        
        return client
    """