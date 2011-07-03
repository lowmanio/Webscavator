"""
    This file stores the WSGI application class which takes in the URL requested, 
    and responds with an html page. 
"""

# python imports
from os import path
import sys, traceback
# library imports
from werkzeug import ClosingIterator, Request, SharedDataMiddleware, DebuggedApplication, Response
from werkzeug.exceptions import HTTPException, NotFound, InternalServerError
from werkzeug.routing import Map, Rule
from werkzeug.contrib.sessions import FilesystemSessionStore
# local imports
from controllers import controller_lookup
from controllers.baseController import BaseController
from utils.utils import ROOT_DIR, local_manager, local, session, config

## Hack to fix bug in werkzeug 0.6.2
import werkzeug.posixemulation
werkzeug.posixemulation.sys = sys

sys.path.append('webscavator')

staticLocations = {
    '/css': path.join(ROOT_DIR, 'static', 'css'),
    '/images': path.join(ROOT_DIR, 'static', 'images'),
    '/js': path.join(ROOT_DIR, 'static', 'javascript'),
    '/docs': path.join(ROOT_DIR, 'docs', '_build', 'html')
}

def make_app():
    """
        Make the WGSI application. If `debug` is set to True in the configuration file, 
        then an interactive debugger will be 
        displayed in the web browser when there are errors. Otherwise a page 500 will be 
        displayed. 
    """
    application = Application()
    application = SharedDataMiddleware(application, staticLocations)    
    application = local_manager.make_middleware(application)
    
    if config.getboolean('debugging', 'debug') == True:
        application = DebuggedApplication(application, evalex=True)
    return application


class Application(object):    
    """
        WSGI Application class. See the 
        `WerkZeug <http://werkzeug.pocoo.org/documentation/dev/tutorial.html>`_ 
        documentation for more details on how this works.
    """
    
    def __init__(self):
        self.session_store = FilesystemSessionStore()
        self.url_map = self.make_url_map()

    def __call__(self, environ, start_response):
        """
            Given a WGSI environment, finds the correct 'endpoint' to map the URL to and dispatches
            it accordingly. An endpoint is a controller class method defined in 
            webscavator/controllers/__init__.py
            
            If there are exceptions, a 404 or 500 page is returned instead of the normal page response.
        """
        local.application = self
        request = Request(environ)
        self.load_session(request)
        response = None
        try:    
            adapter = self.url_map.bind_to_environ(environ)
            endpoint, vars = adapter.match()
            response = self.dispatch(request, adapter, endpoint, vars)
        except NotFound, e:
            b = BaseController(request, adapter)
            response = b.return404()
        except InternalServerError, e:
            request.environ['wsgi.errors'].write(traceback.format_exc())
            b = BaseController(request, adapter)
            response = b.return500()
        except HTTPException, e:
            request.environ['wsgi.errors'].write(traceback.format_exc())
            response = e
        finally:
            session.expunge_all()
            session.remove()
            if response:
                self.save_session(request, response)
        return ClosingIterator(response(environ, start_response),[local_manager.cleanup])

    def load_session(self, request):
        """
            Load cookies from `session_store` and puts them into `request.session`.  
        """
        sid = request.cookies.get('webscavator')
        if sid is None:
            request.session = self.session_store.new()
        else:
            request.session = self.session_store.get(sid)
        
            
    def save_session(self, request, response):
        """ 
            Save cookies in `session_store` and `response`.
        """
        if request.session.should_save:
            self.session_store.save(request.session)
            response.set_cookie('webscavator', request.session.sid)
        
        
    def dispatch(self, request, adapter, endpoint, vars):
        """ 
            Dispatch the request to the correct endpoint, i.e. the controller method found in
            one of :doc:`controllers`
        """
        ctrl_str, act_str = endpoint.split('.')
        
        controller = controller_lookup[ctrl_str](request, adapter)
        method_to_call = getattr(controller, act_str)

        try:
            response = method_to_call(**vars)
        except:
            session.rollback()
            raise
        else:            
            session.commit()
            return response

    @staticmethod
    def make_url_map():
        """ 
            Map that defines all the valid URLs and what endpoint they should be dispatched to. 
            For example the index page, (which is just `<http://localhost:5000/>`_) points to
            `generalController.index()` in :doc:`generalController`. The map uses 
            `controller_lookup` dictionary in :doc:`controllers`.
        """
        
        map = Map()
        # index page
        map.add(Rule('/', endpoint='general.index'))
        
        # general pages 
        map.add(Rule('/about/', endpoint='general.about'))
        map.add(Rule('/help/', endpoint='general.help'))
        
        # pages to add a new case
        map.add(Rule('/wizard/', endpoint='case.wizard'))
        map.add(Rule('/case/add/namecase/', endpoint='case.wizard1'))
        map.add(Rule('/case/add/addfiles/', endpoint='case.wizard2'))
        map.add(Rule('/case/add/checkdata/', endpoint='case.wizard3'))
        map.add(Rule('/case/add/complete/', endpoint='case.wizard4'))
        
        # pages to edit current case
        map.add(Rule('/case/edit/renamecase/', endpoint='case.edit1'))
        map.add(Rule('/case/edit/editfiles/', endpoint='case.edit2'))
        map.add(Rule('/case/edit/checkdata/', endpoint='case.edit3'))
        map.add(Rule('/case/edit/complete/', endpoint='case.edit4'))
        
        # pages to load a case
        map.add(Rule('/case/load/', endpoint='case.load'))
        map.add(Rule('/case/load/complete/', endpoint='case.loaded'))
        
        # ajax pages for the wizards to add/edit cases
        map.add(Rule('/json/addwizard1', endpoint='case.jsonAddCase'))
        map.add(Rule('/json/addwizard2', endpoint='case.jsonAddEntries'))
        map.add(Rule('/json/editwizard1', endpoint='case.jsonEditCase'))
        map.add(Rule('/json/editwizard2', endpoint='case.jsonEditEntries'))
        
        # ajax visualisation calls
        map.add(Rule('/vis/getEntries/', endpoint='visual.jsonGetEntries'))
        map.add(Rule('/vis/getWordCloud/', endpoint='visual.jsonGetWordClouds'))
        map.add(Rule('/vis/getDomains/', endpoint='visual.jsonGetDomains'))
        
        # pages to add/delete filters
        map.add(Rule('/filter/add/', endpoint='visual.addFilter'))
        map.add(Rule('/filter/add/complete', endpoint='visual.jsonAddFilter'))
        
        # help pages
        map.add(Rule('/help/userguide/', endpoint='general.userguide'))  
        map.add(Rule('/help/userguide/addingdata/', endpoint='general.userguide_part1'))  
        map.add(Rule('/help/userguide/visualisations/', endpoint='general.userguide_part2'))      
        map.add(Rule('/help/addprograms/', endpoint='general.help_addfiles'))    
        map.add(Rule('/help/guidelines/', endpoint='general.guidelines'))  
        
        # Static rules -- these never match, they're only used for building.
        for k in staticLocations:
            map.add(Rule('%s/<file>' % k, endpoint=k.strip('/'), build_only=True))

        return map
