"""No modules needed"""
class spaCyDown(Exception):
    """Exception Wrapper for spaCy worker down"""

class GeminiDown(Exception):
    """Exception Wrapper for Gemini worker down"""

class ScraperDown(Exception):
    """Exception Wrapper for Scraper worker down"""

class R2Down(Exception):
    """Exception Wrapper for R2 worker down"""

class CacheFail(Exception):
    """Exception Wrapper for local cache down"""

class NotAddedDetails(Exception):
    """Exception Wrapper for user not adding their preference"""

class NotUploadedResume(Exception):
    """Exception Wrapper for user not uploading their resume"""