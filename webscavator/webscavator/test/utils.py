"""
    Some utilities for testing. 
"""

from webscavator.application import Application

urls = Application.make_url_map().bind('localhost')
 
class FakeFileUpload(object): 
    """
        A fake File Upload to mimic uploading an actual file.
    """
    def __init__(self, filename, content_type, location):
        self.filename = filename
        self.content_type = content_type
        self.content = open(location, "r")
        
    def save(self, new):
        pass