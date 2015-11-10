'''
Models that extend the Model class provided by 
Flask's SQLAlchemy extension (flask.ext.sqlalchemy).
'''

import uuid
import OpenSSL
#from passlib.apps import custom_app_context as pwd_context

from app import db
#from app import app
#from app.errors import TokenExpired

#from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
#from flask.ext.api.exceptions import AuthenticationFailed

#from config import DEFAULT_TOKEN_DURATION



    
    
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