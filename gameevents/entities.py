'''
Created on 14 Oct 2015

@author: mbrandaoca
'''

from sqlalchemy import *

from sqlalchemy.orm import relationship

from base import Base

########################################################################
class GamingSession(Base):
    """"""
    __tablename__ = "gamingsession"
 
    id = Column(Integer, primary_key=True)
    status = Column(Boolean)
 
    #----------------------------------------------------------------------
    def __init__(self):
        """"""
        #self.id = name
        self.status = 1