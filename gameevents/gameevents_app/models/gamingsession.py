'''
Created on 10 Nov 2015

@author: mbrandaoca
'''
from uuid import UUID
import OpenSSL

#from flask import current_app
from ..extensions import db

#Logging
# from logging import getLogger
# LOG = getLogger(__name__)


gamingsessions_clients = db.Table('gamingsessions_clients',
    db.Column('gamingsession_id', db.Integer, db.ForeignKey('gamingsession.id')),
    db.Column('client_id', db.Integer, db.ForeignKey('client.id'))
)


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
    clients = db.relationship("Client", secondary=gamingsessions_clients)
    gameevents = db.relationship("GameEvent", backref="gamingsession")
 
    #----------------------------------------------------------------------
    
    def __init__(self, sessionid):
        """"""
        self.id = UUID(bytes = OpenSSL.rand.bytes(16)).hex
        #self.status = True
        self.sessionid = sessionid
        
    def __eq__(self, other):
        """"""
        return (self.id == other.id 
                and self.sessionid == other.sessionid 
                #and self.clientid == other.clientid
                )
    
    def as_dict(self):
        """Returns a dictionary version of the session."""
        myclients = []
        for client in self.clients:
            myclients.append(client.as_dict())
        obj_d = {
            'id': self.id,
            'sessionid': self.sessionid,
            'clients': myclients,
        }
        #gameevents_LOG.debug(obj_d)
        return obj_d
    