'''
Created on 10 Nov 2015

@author: mbrandaoca
'''


#from flask import current_app
from ..extensions import db

#Logging
# from logging import getLogger
# LOG = getLogger(__name__)


# sessions_clients = db.Table('sessions_clients',
#     db.Column('session_id', db.String(36), db.ForeignKey('session.id')),
#     db.Column('client_id', db.String(36), db.ForeignKey('client.id'))
# )


class Session(db.Model):
    """Models 'ession' table in the database. Has column id (UUID) and a 
    back reference to the list of game events
    associated to this gaming session.
     """
    __tablename__ = "session"
 
    #id = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.String(36), unique=True, primary_key=True)
    #sessionid = db.Column(db.String(36))
    #status = db.Column(db.Boolean)
    #clients = db.relationship("Client", secondary=sessions_clients)
    client_id = db.Column(db.String(36), db.ForeignKey('client.id'))
    gameevents = db.relationship("GameEvent", backref="session")
 
    #----------------------------------------------------------------------
    
    def __init__(self, sessionid, client_id):
        """"""
        #self.id = UUID(bytes = OpenSSL.rand.bytes(16)).hex
        #self.status = True
        self.id = sessionid
        self.client_id = client_id
        
    def __eq__(self, other):
        """"""
        return (self.id == other.id 
                and self.client_id == other.client_id
                )
    
    def as_dict(self):
        """Returns a dictionary version of the session."""
#         myclients = []
#         for client in self.clients:
#             myclients.append(client.as_dict())
        obj_d = {
            'id': self.id,
            'client_id': self.client_id,
        }
        #gameevents_LOG.debug(obj_d)
        return obj_d
    