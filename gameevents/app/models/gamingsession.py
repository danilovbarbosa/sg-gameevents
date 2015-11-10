'''
Created on 10 Nov 2015

@author: mbrandaoca
'''

import uuid, OpenSSL

from itsdangerous import (TimedJSONWebSignatureSerializer
                           as Serializer, BadSignature, SignatureExpired)

from app import db
from app import app

from config import DEFAULT_TOKEN_DURATION


class GamingSession(db.Model):
    """Models 'gamingsession' table in the database. Has columns id (UUID), sessionid (string) and a
    clientid (referencing the client database). It has a back reference to the list of game events
    associated to this gaming session.
     """
    __tablename__ = "gamingsession"
 
    #id = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String, primary_key=True)
    sessionid = db.Column(db.String)
    #status = db.Column(db.Boolean)
    clientid = db.Column(db.Integer, db.ForeignKey('client.id'))
    gameevents = db.relationship("GameEvent", backref="gamingsession")
 
    #----------------------------------------------------------------------
    
    def __init__(self, sessionid, clientid):
        """"""
        self.id = uuid.UUID(bytes = OpenSSL.rand.bytes(16)).hex
        #self.status = True
        self.sessionid = sessionid
        self.clientid = clientid
        
    def __eq__(self, other):
        return (self.id == other.id and 
                #self.status == other.status and 
                self.sessionid == other.sessionid and 
                self.clientid == other.clientid)
    
    def as_dict(self):
        obj_d = {
            'id': self.id,
            'sessionid': self.sessionid,
        }
        return obj_d
    
    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
            app.logger.debug("Got data: %s " % data)
            return dict(sessionid=data['sessionid'], clientid=data['clientid'], id=data['id'])
        except SignatureExpired as e:
            app.logger.debug("Expired token, returning false")
            app.logger.debug(e, exc_info=False)
            #raise e
            return False # valid token, but expired
        except BadSignature as e:
            app.logger.debug("Invalid token, returning false.")
            app.logger.debug(e, exc_info=False)
            #raise e
            return False # invalid token
        except Exception as e:
            app.logger.error(e, exc_info=False)
            raise e
        
    
    def generate_auth_token(self, expiration = DEFAULT_TOKEN_DURATION):        
        s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
        app.logger.debug("Generating token with expiration: %s" % expiration)
        return s.dumps({ 'id': self.id, 'sessionid': self.sessionid, 'clientid' : self.clientid  })