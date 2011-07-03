"""
    generalController
    -----------------
    
    Contains the class for the endpoints of general pages that do not need much complex processing
    (apart form the index page). 
    
"""
#python imports
from os import path, rename, mkdir
from datetime import datetime
import time
from os import path
# library imports
from werkzeug import Response, redirect
from mako.lookup import TemplateLookup
from werkzeug.exceptions import NotFound
# local imports
from webscavator.controllers.baseController import BaseController, lookup
from webscavator.model.models import Case, Filter, Entry, Browser
from webscavator.converters import get_program_infos, get_programs_files, get_names
from webscavator.utils.utils import ROOT_DIR


class GeneralController(BaseController):
    """
        Controller for general pages, e.g. the index page, about page and help pages. 
    """
    
    def index(self): 
        """ 
            Endpoint for index page of webscavator. If a case has been loaded, this will 
            show information about the case and lead onto the visualisations. 
            Otherwise, the index page will display a choice
            to either load a case or create a new case. 
        """    
        if self.done_wizard: # wizard completed
            if self.case: # just to check cookie set correctly
                self.loaded_case = None
                
                # dates and times for the limits and end points of the timegraph
                latest = Case.getNewestEntry(self.case).access_date
                oldest = Case.getOldestEntry(self.case).access_date
                start, end = Case.getMinMax(latest)
                backward_limit = time.mktime(datetime(oldest.year, oldest.month, 1).timetuple())*1000
                forward_limit = end
                
                # get all the filters
                allfilters = Filter.getAll().all()
                
                # for the overview statistics and heatmap
                browser_stats = Browser.getPercentages()
                average_pages = Entry.averagePages()
                peak_time = Entry.peakTime()
                heatmap_headers, heatmap_rows, high, low = Entry.generateHeatMap()
                
                # for the local file access tab
                files_accessed, file_amount = Entry.filesAccessed()
                    
                return self.returnResponse('pages', 'index.html', ticksize = 61, start = start, 
                                           end = end, allfilters = allfilters, 
                                           forward_limit = forward_limit,
                                           backward_limit = backward_limit,
                                           heatmap_headers=heatmap_headers, peak_time=peak_time,
                                           heatmap_rows=heatmap_rows, high=high, low=low,
                                           browser_stats=browser_stats, average_pages=average_pages,
                                           files_accessed=files_accessed, file_amount=file_amount
                                           )
            else:
                return redirect(self.urls.build('case.wizard', {}))
        else:   # do wizard
            return redirect(self.urls.build('case.wizard', {}))
    
    def about(self):     
        """ 
            Endpoint for the about page. 
        """
        return self.returnResponse('pages', 'about.html')
    
    def help(self): 
        """ 
            Endpoint for the index help page.
        """    
        return self.returnResponse('help', 'help.html')
    
    def help_addfiles(self): 
        """ 
            Endpoint for the help page on how to add new web history program file convertors  
        """    
        programs = get_programs_files()
        folder = path.abspath(path.join(ROOT_DIR, 'webscavator','converters'))
        folder_icons = path.abspath(path.join(ROOT_DIR,'static','images','programs'))
        return self.returnResponse('help', 'addfiles.html',programs=programs, folder=folder, folder_icons=folder_icons)
    
    def userguide(self): 
        """ 
            Endpoint for the user documentation.
        """    
        return self.returnResponse('help', 'userguide.html')

    def userguide_part1(self): 
        """ 
            Endpoint for the user documentation on how to extract web history files and add/load/edit a case.
        """    
        return self.returnResponse('help', 'userguide_part1.html', 
                                   programs = get_programs_files(),
                                   program_explanations = get_program_infos())
        
    def userguide_part2(self): 
        """ 
            Endpoint for the user documentation on how to sue the visualisations.
        """    
        return self.returnResponse('help', 'userguide_part2.html')    
    def guidelines(self): 
        """ 
            Endpoint for guidelines on what data to add to cases.
        """    
        program_explanations = get_program_infos()
        return self.returnResponse('help', 'guidelines.html', program_explanations=program_explanations)