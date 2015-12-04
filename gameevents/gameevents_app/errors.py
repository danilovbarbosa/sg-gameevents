'''
Creates a few custom exceptions used throughout the application.
'''

class InvalidGamingSessionException(Exception):
    '''
    Session is invalid or does not exist.
    '''
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
class SessionNotAuthorizedException(Exception):
    '''
    Client is not authorized to access this session.
    '''
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
class TokenExpiredException(Exception):
    '''
    The token has expired.
    '''
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
class ClientExistsException(Exception):
    '''
    Client already exists in database.
    '''
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
class MissingHeadersException(Exception):
    '''
    Request is incomplete, with missing headers.
    '''
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)