'''
Models that extend the Model class provided by 
Flask's SQLAlchemy extension (flask.ext.sqlalchemy).
'''

from uuid import UUID
import OpenSSL

from ..extensions import db

    
class GameEvent(db.Model):
    """Models 'gameevent' table in the database. Has columns id (UUID), gameevent (string) and 
    sessionid (a foreign key).
    """
    __tablename__ = "gameevent"
 
    id = db.Column(db.String(36), primary_key=True)
    gameevent = db.Column(db.UnicodeText())
    session_id = db.Column(db.String(36), db.ForeignKey('session.id'))
 
    #----------------------------------------------------------------------
    def __init__(self, sessionid, gameevent):
        """Initializes the game event with a sessionid and the body of the game event."""
        self.id = UUID(bytes = OpenSSL.rand.bytes(16)).hex
        self.session_id = sessionid
        self.gameevent = gameevent
        
    def __repr__(self):
        """"""
        return '<GameEvent. id: %s; session_id: %s; gameevent: %s [...]>' % (self.id, self.session_id, self.gameevent[:100])
    
    def __eq__(self, other):
        """"""
        return self.id == other.id and self.gameevent == other.gameevent and self.session_id == other.session_id
    
    def as_dict(self):
        """Returns a dictionary version of the game event."""
        obj_d = {
            'id': self.id,
            'session_id': self.session_id,
            'gameevent': self.gameevent
        }
        return obj_d
    