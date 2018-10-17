''''''


from flask import url_for
from ..extensions import db

import datetime


#Logging
# from logging import getLogger
# LOG = getLogger(__name__)

class Session(db.Model):
    '''
    Models 'session' table in the database. 
    
    :param sessionid: uuid coming from the userprofile service
    :param client_id: internal id of the client to which this session belongs.

    '''
    __tablename__ = "session"
 
    #: (uuid) ID of the session
    id = db.Column(db.String(36), unique=True, primary_key=True)
    #: Foreign key to client table (internal id of the client)
    client_id = db.Column(db.String(36), db.ForeignKey('client.id'))
    #: (datetime) when the session was registered internally (to manage expiration times)
    timestamp = db.Column(db.DateTime(True))
    #: relationship to gameevents under this session
    gameevents = db.relationship("GameEvent", backref="session")
    _URLFor = "/session"
 
    #----------------------------------------------------------------------
    
    def __init__(self, sessionid, client_id):
        self.id = sessionid
        self.client_id = client_id
        self.timestamp = datetime.datetime.utcnow() 
        
    def __eq__(self, other):
        return (self.id == other.id 
                and self.client_id == other.client_id
                )
    
    def as_dict(self):
        '''
        Returns a dictionary version of the session.
        
        :rtype: dict
        '''
        obj_d = {
            'id': self.id,
            'client_id': self.client_id,
            'timestamp':str(self.timestamp)
        }
        return obj_d
    
    def as_hateoas(self):
        '''
        Returns dict representation of the session that follows hateoas representation.        
        '''
       
        _links = []
        _self = {
            "rel" : "self",
            "href" : url_for("gameevents.get_session", sessionid=self.id)
        }
        _client = {
            "rel" : "client",
            "href" : url_for("gameevents.get_client", clientid= self.client_id)
        }
        _links.append(_self)
        _links.append(_client)
        obj_d = {
            'id': self.id,
            #'client_id': self.client_id,
            'created':str(self.timestamp),
            '_links':_links
        }
        return obj_d
