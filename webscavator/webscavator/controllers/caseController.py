"""
    caseController
    --------------
    
    Contains the class that has all the endpoints for loading, adding and editing a case.
"""

#python imports
import sys
from os import path, rename, mkdir
from datetime import datetime, time
import csv
import urllib
# library imports
from werkzeug import Response, redirect
from mako.lookup import TemplateLookup
# local imports
from webscavator.utils.utils import session, ROOT_DIR, CASE_FILE_DIR, getCases, config
from webscavator.controllers.baseController import BaseController, lookup, jsonify, jsonifyfile
from webscavator.model.models import *
from webscavator.forms.forms import wizard1_form, wizard2_form, edit1_form, edit2_form, load_form
from webscavator.converters import get_program, get_names, convert_file

class CaseController(BaseController):
    """
        Controller for the set up and editing of cases. 
    """
    
    # Load cases
    # =======================================
    def load(self, **vars):
        """ 
            Endpoint for the page to load an old case.
        """
        self.loaded_case = True
        cases = getCases()
        return self.returnResponse('wizard', 'load_case.html', cases = cases, **vars)

    def loaded(self):
        """ 
            Endpoint for when user has chosen to load a particular case. 
            Checks whether the case is valid. 
            If so, returns `finish_wizard()`. Otherwise, it returns `self.form_errors()`.   
        """
        if self.validate_form(load_form()):
            # form is validated, so load case
            self.dbfile = self.form_result['case']
            Case.load_database(self.dbfile) 
            
            return self.finish_wizard()
        else:
            return self.load(errors=self.form_error)
        
    # Wizard steps
    # =======================================
    def wizard(self):     
        """ 
            Endpoint for the index page when a case is not yet loaded. 
            Gives the user a choice whether to add
            a new case or load an old case.  
        """
        return self.returnResponse('wizard', 'step0.html')
    
    def case_details(self, edit=False):
        """     
            First step of the wizard: add or edit case details. 
        """
        return self.returnResponse('wizard', 'step1.html', edit=edit)   
    
    def file_details(self, edit=False):
        """ 
            Second step of wizard: add the browser history files.
        """
        return self.returnResponse('wizard', 'step2.html', programs = get_names(), edit=edit) 
    
    def check_details(self, edit=False):
        """ 
            Third step of wizard: user gets to check everything has been added correctly.
        """   
        headers = Entry.HEADERS 
        dblocation = self.case.dblocation(self.dbfile)
        return self.returnResponse('wizard', 'step3.html', headers = headers, 
                                   dblocation = dblocation, edit=edit)    
        
    def finish_wizard(self, edit=False):
        """ 
            Forth step of wizard: The wizard is complete. Creates a hash of the database
            file and adds message to log file by calling `self.write_log(dbfile, msg)`
            found in :doc:`baseController`. 
        """

        self.done_wizard = True # completed the wizard, start page is now the vizualisations
        if self.loaded_case:
            load = True
        else:
            load = False
            if edit == False:
                self.addDefaultFilters()
                    
        session.commit() # before computing hash, commit everything to database
        
        # add what has happened to the db file to log
        if edit == True:
            hash, hashfolder = self.write_log(self.dbfile, 'Edited the data.') 
        elif load == True:
            hash, hashfolder = self.write_log(self.dbfile, 'Loaded the case.') 
        else:
            hash, hashfolder = self.write_log(self.dbfile, 'Added for first time.') 
        
        return self.returnResponse('wizard', 'step4.html', load=load, hash=hash, 
                                   hashfolder=hashfolder, edit=edit)        
                
    
    # Add new case
    # =======================================
        
    def wizard1(self):     
        """
            Endpoint for adding a new case. returns `self.case_details()`.
        """
        self.loaded_case = False
        return self.case_details()
    
    def wizard2(self):   
        """
            Endpoint for adding new CSV files. returns `self.file_details()`.
        """  
        return self.file_details()
    
    def wizard3(self):
        """
            Endpoint for checking details are correct. Returns `self.check_details()`.
        """
        return self.check_details()
    
    def wizard4(self):     
        """
            Endpoint for the end of the wizard. Returns `self.finish_wizard()`.
        """
        return self.finish_wizard()       
    
    #  Edit current case
    #  =======================================
    
    def edit1(self):     
        """
            Endpoint for editing a case. Returns `self.case_details(edit=True)`.
        """        
        return self.case_details(edit=True)
    
    def edit2(self):    
        """
            Endpoint for editing CSV files. Returns `self.file_details(edit=True)`.
        """   
        return self.file_details(edit=True)
    
    def edit3(self):
        """
            Endpoint for checking details are correct. Returns `self.check_details(edit=True)`.
        """
        return self.check_details(edit=True)
    
    def edit4(self):     
        """
            Endpoint for the end of the wizard. Returns `self.finish_wizard(edit=True)`.
        """
        return self.finish_wizard(edit=True)
    
    
    #   Ajax methods
    # =======================================
    
    # ADDING DATA
    # ---------------------------------------
    
    @jsonify
    def jsonAddCase(self):
        """ 
            Endpoint for wizard 1 form (adding case name and dbfile name). This is done via Ajax. 
            If the form has errors, the error dictionary `self.form_errors` is jsonified 
            and passed back to the webpage and the errors displayed to the user. 
            If the form is valid, then the new case is created, the database initialised 
            and data saved to the database. This will then return `True`. 
        """
        if self.validate_form(wizard1_form()):
            # form is validated, so add the case information
            Case.create_database(self.form_result[u'dbfile']) # switch to the new database 
            
            case = Case(self.form_result[u'name'])
            session.add(case)
             
            self.dbfile = self.form_result[u'dbfile'] #set sqlite database location cookie
            
            return True
        else:
            return self.form_error
 
    @jsonifyfile
    def jsonAddEntries(self):
        """
            Endpoint for wizard 2 form (adding CSV/XML data). This is done via Ajax. 
            If the form has errors, the error dictionary `self.form_errors` is jsonified 
            and passed back to the webpage and the errors displayed to the user. 
            If the form is valid, then `self.addData()` is called. 
            If all goes well, this will then return `True`, otherwise if their are errors in 
            the adding of the data in `self.addData()` then self.form_erros is returned. 
        """
        if self.validate_form(wizard2_form()):
            # form is validated, so add group details
            for i, v in enumerate(self.form_result.itervalues()):               
                entry = v[0]
                done = self.addData(entry)
                if done is None:
                    form_error = {}
                    form_error['csv_entry-' + str(i) + '.data'] = \
                    'The data could not be added to the database due to an error.'
                    return form_error
            return True
        else:
            return self.form_error   
        
    # EDITING DATA
    # ---------------------------------------
    
    @jsonify
    def jsonEditCase(self):
        """ 
            Same as `self.jsonAddCase()` apart from the user is not allowed to edit the database name - 
            this can be done manually be renaming the file when not in use. 
        """
        self.currentObj = self.case

        if self.validate_form(edit1_form()):
            # form is validated, so edit the case information
            self.case.name = self.form_result['name']               
            return True
        else:
            return self.form_error  
        
    @jsonifyfile
    def jsonEditEntries(self):
        """
            Same as `self.jsonAddEntries` but allows the editing of old entries and the addition
            of new entries.
        """
        groups = []
        
        if self.validate_form(edit2_form()):
            # form is validated, so edit group details
            for i, v in enumerate(self.form_result.itervalues()):   
                for entry in v:            
                    if entry[u'group'] is None: # new, so add it
                        group = self.addData(entry)
                        
                        if group is None:
                            form_error = {}
                            form_error['csv_entry-' + str(i) + '.data'] = \
                            'The data could not be added to the database due to an error.'
                            return form_error
                
                        groups.append(group)
                    else:                       # already there, edit it
                        group = entry[u'group']
                        groups.append(group)
                        group.name = entry[u'name']
                        group.description = entry[u'desc']
                        group.program = get_program(entry[u'program'])
                        
                        if entry[u'keepcsv'] == False: # add new csv data
                            group.csv_name = entry[u'data'].filename
                            
                            self.addEntry(group.program, entry['data'].stream, group)
                      
                    session.flush()
            
            # some data might be deleted, loop through all groups, if not in 'groups' then can delete it
            for g in self.case.groups:
                if g not in groups:
                    session.delete(g)
            
            return True
        else:
            return self.form_error
       
    # Useful methods
    # ======================================= 

    def addEntry(self, program, file, group):
        """
            Calls the generator `convert_file()` found in :doc:`converters` on each row of the file, 
            and adds the result to the database. If an exception happens during the converting and
            adding of data, then the session is rolled back and `None` is returned. Otherwise
            `True` is returned. 
            
            .. note::
                This had been optimised to make the adding of data as fast as possible, but
                has been slowed down again by adding search terms. 
                
                **ToDo**: Optimise the adding of search terms. 
        """
        session.flush()
        browser_ids = {}        
        
        try:
            entry_ins = Entry.__table__.insert()
            url_ins = URL.__table__.insert()
            for i, d in enumerate(convert_file(program, file)):
                browser_name = d.pop('browser_name')
                browser_version = d.pop('browser_version')
                source = d.pop('source_file')
                                
                key = (browser_name, browser_version, source)                
                browser_id = browser_ids.get(key)
                if browser_id is None:
                    browser = Browser.getFilterBy(name=browser_name, version=browser_version,
                                                  source=source).first()
                    if browser is None:
                        browser = Browser(*key)
                        session.add(browser)
                        session.flush()
                    browser_id = browser_ids[key] = browser.id
                
                # optimised to make adding data as fast as possible - ignores the ORM
                v = d.pop('access_time')
                if v is not None:
                    d['access_date'] = datetime(v.year, v.month, v.day, 0, 0, 0, 0)
                    d['access_time'] = time(v.hour, v.minute, v.second, v.microsecond)
                else:
                    continue # don't add data without an access time
                v = d.pop('modified_time')
                if v is not None:
                    d['modified_date'] = datetime(v.year, v.month, v.day, 0, 0, 0, 0)
                    d['modified_time'] = time(v.hour, v.minute, v.second, v.microsecond)
                else:
                    d['modified_date'] = None
                    d['modified_time'] = None
                
                result = session.execute(entry_ins.values(browser_id=browser_id, 
                                                          group_id=group.id,
                                                           **d))                
                entry_id = result.last_inserted_ids()[0]
                
                # add URLS
                url = URL(d['url'])
                session.execute(url_ins.values(entry_id=entry_id, **url.asDict()))  
                url_id = result.last_inserted_ids()[0]
                
                # add search terms
                # TODO: make this optimised like above!
                entry = Entry.get(entry_id)
                url = URL.get(url_id)
                
                opts = config.options('search_engines')
                if url.query != None and 'search' in url.path:
                    for opt in opts:
                        if opt in url.netloc:
                            query = url.query.split(config.get('search_engines', opt)+'=')\
                                    [-1].split('&')[0]
                            q_string, terms = SearchTerms.getTerms(urllib.unquote(query))
                            url.search = q_string 
                            for term in terms:
                                t = SearchTerms.getFilterBy(term=term, engine=opt).first()
                                if t is None:
                                    t = SearchTerms(term, opt, config.get('search', opt))
                                    session.add(t)
                                else:
                                    t.occurrence = t.occurrence + 1
                                entry.search_terms.append(t)
                                session.flush()                    
        except Exception, e:
            session.rollback()            
            return None
        return True
    
    def addData(self, entry):
        """ 
            Given a validated form called `entry`, adds the group to the database, 
            then calls `self.addEntry()` to convert the data in `entry['data']` to `Entry` objects. 
            Returns the group if the adding of entries was successful, and otherwise
            returns `None`. 
        """        
        group = Group(entry[u'name'], entry[u'desc'], self.case, get_program(entry[u'program']))
        group.csv_name = entry[u'data'].filename
        session.add(group)
        
        # convert the file to entries 
        done = self.addEntry(group.program, entry['data'].stream, group)
        if done == True:
            return group # used in jsonEditEntries
        else:
            return None # exception happened!
