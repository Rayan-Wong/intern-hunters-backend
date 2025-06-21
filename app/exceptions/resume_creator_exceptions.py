"""No modules needed"""
class CacheFail(Exception):
    """Exception Wrapper for local cache down"""

class ResumeCreatorDown(Exception):
    """Exception Wrapper for resume creator down"""

class NotUploadedResume(Exception):
    """Exception Wrapper for user not uploading their resume"""