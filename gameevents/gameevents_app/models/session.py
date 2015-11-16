'''
Created on 10 Nov 2015

@author: mbrandaoca
'''


#from flask import current_app
from ..extensions import db

import datetime

#Logging
# from logging import getLogger
# LOG = getLogger(__name__)

class Session(db.Model):
    """Models 'session' table in the database. Has column id (UUID) and a 
    back reference to the list of game events
    associated to this gaming session.
     """
    __tablename__ = "session"
 
    id = db.Column(db.String(36), unique=True, primary_key=True)
    client_id = db.Column(db.String(36), db.ForeignKey('client.id'))
    timestamp = db.Column(db.DateTime(True))
    gameevents = db.relationship("GameEvent", backref="session")
 
    #----------------------------------------------------------------------
    
    def __init__(self, sessionid, client_id):
        """"""
        #self.id = UUID(bytes = OpenSSL.rand.bytes(16)).hex
        #self.status = True
        self.id = sessionid
        self.client_id = client_id
        self.timestamp = datetime.datetime.utcnow() 
        
    def __eq__(self, other):
        """"""
        return (self.id == other.id 
                and self.client_id == other.client_id
                )
    
    def as_dict(self):
        """Returns a dictionary version of the session."""
        obj_d = {
            'id': self.id,
            'client_id': self.client_id,
            'timestamp':self.timestamp
        }
        return obj_d
    