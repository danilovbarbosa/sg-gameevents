''''''
from uuid import UUID
import OpenSSL
from passlib.apps import custom_app_context as pwd_context

from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from flask.ext.api.exceptions import AuthenticationFailed

from flask import current_app
from ..extensions import db, LOG

from config import DEFAULT_TOKEN_DURATION




class Client(db.Model):
    '''
    Model "clients" table in the database. Each game/application 
    using the service (i.e. a client) must have an entry in this 
    table to be able to request an authentication token.
    Initialization generates the internal ID and stores apikey hashed.
    
    :param str clientid: human readable identifier of the client application
    :param str apikey: desired apikey
    :param str role: admin/normal
    
    '''
    
    __tablename__ = "client"  
    #: (uuid) internal ID of the client  
    id = db.Column(db.String(36), primary_key=True) # Referenced in Sessionid
    #: human readable identifier of the client application
    clientid = db.Column(db.String(255), unique=True)
    #: (str) hashed apikey
    apikey_hash = db.Column(db.String(255))
    #: (str) admin/normal
    role = db.Column(db.String(6))
    #: (relationship) back reference to list the sessions connected to this client
    sessions = db.relationship("Session", backref="client")


    def __init__(self, clientid, apikey, role):
        ''''''
        self.id = UUID(bytes = OpenSSL.rand.bytes(16)).hex
        self.clientid = clientid
        self.apikey_hash = pwd_context.encrypt(apikey)
        self.role = role
        #self.token = None
        
    def as_dict(self):
        '''
        Represents client as dictionary.  
              
        :rtype: dict
        '''
        obj_d = {
            'id': self.id,
            'clientid': self.clientid,
            'role': self.role,
        }
        return obj_d
    
    def is_session_authorized(self, sessionid):
        '''
        Checks if the client is authorized to access this sessionid.
        
        TODO: Check authorized sessions in UserProfile service. 
        
        :param sessionid: Sessionid to be checked        
        :rtype: boolean
        
        '''
        if (sessionid != "zzzz" and sessionid != False or self.is_admin()): 
            return True
        else:
            return False
        
    def is_admin(self):
        '''
        Checks if the client is admin.
        
        :rtype: boolean
        '''
        if (self.role == "admin"):
            return True
        else: 
            return False

    def verify_apikey(self, apikey):
        '''
        Checks if the provided apikey matches the client's stored apikey hashed.
        
        :param apikey: Apikey to be verified against the client's
        :rtype: boolean
        '''
        #LOG.debug("Checking apikey... clientid %s, apikey %s" % (self.clientid, apikey))
        verified = pwd_context.verify(apikey, self.apikey_hash)
        if verified:
            #LOG.debug("Good credentials, continue.")
            #g.clientid = self.clientid
            return True
        else:
            return False
        
    @staticmethod
    def verify_auth_token(token):
        '''
        Receives a token and returns the data stored in the token (id, clientid, sessionid). 
                
        :param token: The token to be verified
        :rtype: dict
        :raise: :exc:`AuthenticationFailed` when the token is invalid or has expired. 
        '''
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
        '''
        Generates an authentication token, which contains client data and the sessionid.
        A token with no associated sessionid is only allowed to admins.
        
        :param sessionid: Optional sessionid to be included in the token
        :param expiration: Optional custom expiration time for token, in seconds
        ''' 
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

        
    