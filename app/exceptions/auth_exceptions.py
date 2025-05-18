"""No modules needed"""
class DuplicateEmailError(Exception):
    """Duplicate Email Error Wrapper"""

class NoAccountError(Exception):
    """No Account Wrapper"""

class WrongPasswordError(Exception):
    """Wrong Password Wrapper"""

class BadJWTError(Exception):
    """Bad JWT Wrapper"""

class ExpiredJWTError(Exception):
    """Expired JWT Wrapper"""
