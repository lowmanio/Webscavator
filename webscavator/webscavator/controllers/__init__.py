"""
    Controllers
    -----------
    
    Controllers control the data between the database model and the html pages. Each controller
    inherits from :doc:`baseController` and consist of endpoints that requests
    are dispatched to and helper functions. 
"""

from generalController import GeneralController
from caseController import CaseController
from visualController import VisualController

controller_lookup = {
               'general': GeneralController,
               'case': CaseController,
               'visual': VisualController
               }
"""
    `controller_lookup` is a dictionary used by `make_url_map()`  in :doc:`application` to 
    find the correct endpoints to dispatch the requests to. 
    Any new controllers should have a line added to this dictionary.
"""