"""
    baseController
    --------------
    Contains the `BaseController` which all other controllers inherit from and a couple of other useful
    functions for JSON-ifying responses.
"""

# python imports
from os import path, chmod
import stat
import simplejson as json
import cgi
from datetime import datetime, time
from functools import wraps
# library imports
from werkzeug import Response, redirect
from mako.lookup import TemplateLookup
from formencode import Invalid
from formencode.variabledecode import variable_decode
# local imports
from webscavator.utils.utils import session, CASE_FILE_DIR, ROOT_DIR, multidict_to_dict
from webscavator.model.models import *
from webscavator.model.filters import FilterQuery

lookup = TemplateLookup(directories=[path.join(ROOT_DIR, 'templates')], output_encoding='utf-8')

# Functions to turn Python into JSON
# ===================================
def jsonify(func):
    """ 
        Wrap a function so the return value is 'JSON-ified' and wrapped in a Werkzeug response object. 
        This essentially returns something an AJAX request will understand.
    """
    @wraps(func)
    def _wrapper(*args, **kwds):
        r = func(*args, **kwds)
        if isinstance(r, Response):
            return r
        else:
            return Response(json.dumps(r), mimetype='application/json')
    return _wrapper

def jsonifyfile(func):
    """
        Similar to `jsonify(func)`, but used for file uploads. 
        They have to be put in textareas to work properly.
    """
    @wraps(func)
    def _wrapper(*args, **kwds):
        r = func(*args, **kwds)
        if isinstance(r, Response):
            return r
        else:
            result = cgi.escape(json.dumps(r))
            return Response("<textarea>%s</textarea>" % result, mimetype='text/html')
    return _wrapper

# Needed to give stateful information to the validators
# =====================================================
class FormState(object):
    """
        Sometimes the validators in :doc:`validators` need to know stateful information, such as
        the current case being edited to compare values with. 
        This object is passed to the validators as `state`.
    """
    def __init__(self, obj, case, urls):
        self.obj = obj
        self.case = case
        self.urls = urls
        
        
# base controller all other controllers inherit from
# ==================================================
class BaseController(object):
    """
        `BaseController` contains useful methods for all the controllers, 
        contains the return functions and cookie setters/getters. 
    """

    currentObj = None

    def __init__(self, request, urls):
        self.request = request
        self.urls = urls
      
    #    Responses
    # ========================
    def defaultResponse(self, statuscode, *location, **vars):
        """ 
            Return the rendered template with variables with the given `statuscode`.
        """
        if self.done_wizard:
            vars['not_in_wizard'] = True
        else:
            vars['not_in_wizard'] = False
            
        html = self.renderTemplate(*location, **vars)

        return Response(html, mimetype='text/html', status=statuscode)

    def renderTemplate(self, *location, **vars):
        """
            Returns a rendered Mako HTML template.
        """
        template = lookup.get_template(path.join(*location))
        return template.render(urls=self.urls, 
                               case = self.case, 
                               dbfile = self.dbfile,
                               **vars)

        
    def return404(self):
        """ 
            Calls `defaultResponse` with a 404 page. This method is called by 
            `application()` when none of
            the entries in the URL map match with any controller endpoints.
        """
        return self.defaultResponse(404, 'base', '404.html')

    def return500(self):
        """ 
            Calls `defaultResponse` with a 500 page. This method is called by 
            `application()` when the endpoint
            has raised an exception or an error has happened. 
        """
        return self.defaultResponse(500, 'base', '500.html')
    
    def returnResponse(self, *location, **vars):
        """ 
            Calls `defaultResponse` with the expected page for the controller endpoint, with
            a 200 status code. 
        """
        return self.defaultResponse(200, *location, **vars)
    
    #    Forms
    # ========================
    
    def validate_form(self, schema):
        """ 
            Validates a form post against schema in :doc:`forms`. 
            
            
            If no form was posted, returns `False`. 
            If the form was posted and it is invalid, returns `False` 
            and sets `self.form_error`, a dictionary with input names and 
            their corresponding error messages. 
            If the form validated correctly, returns `True` and sets `self.form_result` to the
            validated results.
        """
    
        if self.request.method != 'POST':
            return False
        try:
            # Convert fields with more than one value into lists
            form_vars = multidict_to_dict(self.request.form)
            form_vars.update(multidict_to_dict(self.request.files))
            
            state = FormState(self.currentObj, self.case, self.urls)
            self.form_result = schema.to_python(variable_decode(form_vars), state)

            return True
        except Invalid, e:
            self.form_error = e.unpack_errors(encode_variables=True)
            return False
        
    #     MD5 Hashes and security things
    # =====================================
    
    def _computeHash(self, file, block_size=2**20):
        """ 
            Returns the MD5 hash of the file.
        """
        import hashlib
        md5 = hashlib.md5()
        while True:
            data = file.read(block_size)
            if not data:
                break
            md5.update(data)
        return md5.hexdigest()
    
    def _storeHash(self, hash, dbfile, msg):
        """ 
            Writes the hash, filename, message and current date to a list of hashes for that 
            database file.
        """
        f = open(path.join(ROOT_DIR, '..', 'case file hashes', dbfile[:-3] + '_hashes.txt'), 'a')
        now = datetime.today().strftime("%I:%M%p %d %b %Y")
        f.write("\n" + dbfile + "\t\t" + hash + "\t\t" + now + "\t\t" + msg)
        f.close()
        
    def write_log(self, dbfile, msg):
        """ 
             Computes a MD5 hash of the dbfile by calling `_computeHash(file)` and then appends 
             the hash in a file for that dbfile by calling `_storeHash(hash, dbfile, msg)`.
             Returns the hash and the path to the folder where the hash file is kept.
        """
        
        database = open(path.join(CASE_FILE_DIR, dbfile), 'r')
        hash = self._computeHash(database)  # create hash
        hashfolder = path.abspath(path.join(ROOT_DIR, '..', 'case file hashes'))
        self._storeHash(hash, dbfile, msg)  # store hash in text file
        
        return hash, hashfolder
    
        
    #     Cookies
    # ===========================
    
    def _setWizard(self, wizard):
        self.request.session['done_wizard'] = wizard
      
    def _getWizard(self):
        return self.request.session.get('done_wizard')
    done_wizard = property(_getWizard, _setWizard)

    def _setLoad(self, load):
        self.request.session['loaded_case'] = load
      
    def _getLoad(self):
        return self.request.session.get('loaded_case')
    loaded_case = property(_getLoad, _setLoad)        
    
    def _getCase(self):
        if session.bind is None:
            return None
        return Case.get_case()        
    case = property(_getCase)

    def _setDB(self, dbfile):
        self.request.session['dbfile'] = dbfile
      
    def _getDB(self):
        return self.request.session.get('dbfile')
    dbfile = property(_getDB, _setDB)
    
    
    def addDefaultFilters(self):
        """
            Adds the default filters for the timegraph such as filtering by browser type,
            group, work hours, Google searches and local files. Gets called when a new case
            is being set up in `finish_wizard()` in :doc:`caseController`. 
        """
        
        # Add filters for the browsers available, unless only one browser, then a filter on 
        # everything is pointless
        browsers = Browser.getAll().group_by(Browser.name).all()
        if len(browsers) > 1:
            for browser in browsers:
                f = Filter(u''.join(browser.name.lower().split(' ')), browser.name)
                fq = FilterQuery()
                cls = u'Browser'
                attr = u'name'
                func = u'Is'
                val = browser.name
                fq.add_element(cls, attr, func, val, None)
                    
                f.query = fq
                session.add(f)
                session.flush()
        
        # filters for Google searches
        f = Filter(u'googlesearch', u'Google searches')
        fq = FilterQuery()
        
        params = [(u'URL Parts', u'query', u'Is not', None, None),
                  (u'URL Parts', u'netloc', u'Is not', None, None),
                  (u'URL Parts', u'path', u'Is not', None, None),
                  (u'URL Parts', u'netloc', u'Contains', u'google', None),
                  (u'URL Parts', u'path', u'Contains', u'search', None),
                  ]
        for entry in params:
            fq.add_element(*entry)
            
        f.query = fq
        session.add(f)
        session.flush()

        # filters for local files accessed
        files = URL.getFilterBy(scheme="file").all()
        if files is not None:
            f = Filter(u'files', u'Local Files')
            fq = FilterQuery()
            cls = u'URL Parts'
            attr = u'scheme'
            func = u'Is'
            val = u'file'
            fq.add_element(cls, attr, func, val, None)  
            f.query = fq
            session.add(f)
            session.flush() 
        
        # filters for different groups      
        groups = Group.getAll().all()
        if len(groups) > 1:
            for group in groups:
                f = Filter(u''.join(group.name.lower().split(' ')), group.name)
                fq = FilterQuery()
                cls = u'Group'
                attr = u'name'
                func = u'Is'
                val = group.name
                fq.add_element(cls, attr, func, val, None)  
                f.query = fq
                session.add(f)
                session.flush()
                
        # filters for work hours 
        f = Filter(u'workhours', u'Work hours')
        fq = FilterQuery()
        
        five = time(17, 00, 01)
        nine = time(8, 59, 59)
        params = [(u'Entry', u'access_time', u'Less than', five, None),
                  (u'Entry', u'access_time', u'Greater than', nine, None),
                  ]
        for entry in params:
            fq.add_element(*entry)
              
        f.query = fq
        session.add(f)
        session.flush()
        
        # filters for adverts 
        f = Filter(u'adverts', u'Advert URLs')
        fq = FilterQuery()
        fq.add_element(u'URL Parts',u'domain',u'Is not', None, None) 
        fq.add_element(u'URL Parts',u'domain',u'Is in list', None, 'advert_domainnames.txt') 
        f.query = fq
        session.add(f)
        session.flush()
        
        # filters for Facebook, MySpace, Bebo, twitter, hi5
        f = Filter(u'social', u'Social Networking URLs')
        fq = FilterQuery()
        fq.add_element(u'URL Parts',u'domain',u'Is not', None, None) 
        fq.add_element(u'URL Parts',u'domain',u'Is in list', None, 'socialmedia.txt') 
        f.query = fq
        session.add(f)
        session.flush()
        
        # filters for email
        f = Filter(u'email', u'Web Email')
        fq = FilterQuery()
        five = time(17, 00, 01)
        nine = time(8, 59, 59)
        params = [(u'Entry', u'url', u'Contains', 'mail', None),
                  (u'URL Parts', u'scheme', u'Is Not', 'file', None),
                  ]
        for entry in params:
            fq.add_element(*entry)
              
        f.query = fq
        session.add(f)
        session.flush()
        
        # filters for news
        f = Filter(u'news', u'News URLs')
        fq = FilterQuery()
        fq.add_element(u'URL Parts',u'hostname',u'Is not', None, None) 
        fq.add_element(u'URL Parts',u'hostname',u'Is in list', None, 'news.txt') 
        f.query = fq
        session.add(f)
        session.flush()