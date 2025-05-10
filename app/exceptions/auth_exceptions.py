class DuplicateEmailError(Exception):
    pass

class NoAccountError(Exception):
    pass

class WrongPasswordError(Exception):
    pass

class BadJWTError(Exception):
    pass

class ExpiredJWTError(Exception):
    pass