'''
Models that extend the Model class provided by 
Flask's SQLAlchemy extension (flask.ext.sqlalchemy).
'''

import uuid, OpenSSL
from passlib.apps import custom_app_context as pwd_context

from app import db
from app import app
from app.errors import TokenExpired

from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from flask.ext.api.exceptions import AuthenticationFailed

from config import DEFAULT_TOKEN_DURATION

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
    
    
class GameEvent(db.Model):
    """Models 'gameevent' table in the database. Has columns id (UUID), gameevent (string) and 
    gamingsessionid (a foreign key).
    """
    __tablename__ = "gameevent"
 
    id = db.Column(db.String, primary_key=True)
    gameevent = db.Column(db.String)
    gamingsession_id = db.Column(db.Integer, db.ForeignKey('gamingsession.id'))
 
    #----------------------------------------------------------------------
    def __init__(self, gamingsessionid, gameevent):
        """"""
        self.id = uuid.UUID(bytes = OpenSSL.rand.bytes(16)).hex
        self.gamingsession_id = gamingsessionid
        self.gameevent = gameevent
        
    def __repr__(self):
        return '<GameEvent. id: %s; gamingsession_id: %s; gameevent: %s [...]>' % (self.id, self.gamingsession_id, self.gameevent[:100])
    
    def __eq__(self, other):
        return self.id == other.id and self.gameevent == other.gameevent and self.gamingsession_id == other.gamingsession_id
    
    def as_dict(self):
        obj_d = {
            'id': self.id,
            'gamingsession_id': self.gamingsession_id,
            'gameevent': self.gameevent
        }
        return obj_d