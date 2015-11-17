'''
Creates a few custom exceptions used throughout the application.
'''

class InvalidGamingSessionException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
class SessionNotAuthorizedException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
class TokenExpiredException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
class ClientExistsException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
class MissingHeadersException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)