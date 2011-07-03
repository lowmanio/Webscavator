"""
    visualController
    ----------------
    
    Contains the class for the visualisation AJAX endpoints and the add filter form, as 
    well as some helper functions.
"""

# python imports
from datetime import datetime, timedelta, time as t
from os import path
# library imports
import simplejson as json
from werkzeug import Response, redirect
from mako.lookup import TemplateLookup
# local imports
from webscavator.utils.utils import session, config, ROOT_DIR, getLists
from webscavator.controllers.baseController import BaseController, lookup, jsonify
from webscavator.model.models import *
from webscavator.model.filters import FilterQuery
from webscavator.forms.forms import add_filter_form

class VisualController(BaseController):
    """
        Controller for filter pages and AJAX visualisation calls  
    """
        
    #    Filters
    # ======================
    
    def addFilter(self):
        """
            Endpoint for the add filter pop-up page. 
        """
        options = json.dumps({"Browser": self.processOptions(Browser.getFilterOptions()),
                              "URL Parts": self.processOptions(URL.getFilterOptions()),
                              "Web Files": self.processOptions(Group.getFilterOptions()),
                              "Entry": self.processOptions(Entry.getFilterOptions()),
                              'Search Terms':self.processOptions(SearchTerms.getFilterOptions())
                              })
        list_files = getLists()
        return self.returnResponse('filters', 'add.html', 
                                   options=options, 
                                   list_files = list_files)  
    
    @jsonify
    def jsonAddFilter(self):
        """
            Endpoint for the AJAX request to validate and add a new filter. If valid, the filter
            is added and a new hash is created and appended to the database file with the current 
            date and time, returning `True`. Otherwise `self.form_error` is returned.
        """
        if self.validate_form(add_filter_form()):
            text = self.form_result['name']
            label = "".join(self.form_result['name'].split(' ')).lower()

            fq = FilterQuery()
            fil = Filter(label, text)
            for f in self.form_result['filter']:
                cls = f['cls']
                attr = f['attribute']
                func = f['function']
                val = f['value']
                
                if f['value_list'] is not None:
                    val_list = f['value_list']
                else:
                    val_list = None
                
                fq.add_element(cls, attr, func, val, val_list)
                
            fil.query = fq
            session.add(fil)
            session.commit()
            
            self.write_log(self.dbfile, 'Added a filter called ' + text)
            
            return True
        else:
            return self.form_error  
        
    @staticmethod
    def processOptions(opts):
        """
            Process the options for each filterable table in :doc:`models`. 
            Returns a dictionary with the table attribute as keys and the operations, 
            values and value type as the value tuple. 
        """
        d = {}
        for k, v in opts.iteritems():
            label, op, callback, value_type = v
            vals = [getattr(obj, k) for obj in callback().group_by(k).all() \
                    if getattr(obj, k) is not None and getattr(obj, k) != ''] if callback else None
            d[label] = (op, vals, value_type)
        return d
     
     
    #    Word Cloud
    # ======================
       
    @jsonify
    def jsonGetWordClouds(self):
        """
            Endpoint for the AJAX request to get the search terms in the word cloud.
            Calls `Filter.onlineSearches()` in :doc:`filters` for each search engine in the config file.
            Returns a dictionary of terms.
        """
        highlight_funcs, remove_funcs = convertFilters(self.request.args)            
        amount = self.request.args.get('amount', 20)
        
        search_results = {}
        opts = config.options('search_engines')
        for opt in opts:
            cloud, terms, unique, small = Filter.onlineSearches(opt, highlight_funcs, remove_funcs,
                                                                amount)
            search_results[opt] = (cloud, terms, opt, config.get('search', opt), unique, small)
        return search_results

    #
    #    Domains
    # ======================
    
    @jsonify
    def jsonGetDomains(self):
        """
            Endpoint for the AJAX request to get the domain names.
            Calls `URL.getTop()` in :doc:`models` which returns a list of domain name tuples 
            in ascending order of number of visits.
        """
        highlight_funcs, remove_funcs = convertFilters(self.request.args)
        amount = self.request.args.get('amount', 20)
        return URL.getTop(num=amount, highlight_funcs=highlight_funcs, remove_funcs=remove_funcs)
    

    #    Timegraph
    # ======================
    
    @jsonify
    def jsonGetEntries(self):
        """
            Endpoint for the AJAX request to get the timegraph. Calls `Case.getTimeGraph()`
            in :doc:`models` with the date, time and filter options and returns a list of 
            dictionaries that Flot can understand to plot. 
            The dictionaries are those points to be highlighted, removed and visible. 
        """
        
        # Used incase of bad dates given, defaults to the latest month
        latest = Case.getNewestEntry(self.case).access_date
        min, max = Case.getMinMax(latest)
        
        # self.request.args is an immutable dict, convert to normal dict  
        req_args = {}  
        for k, v in self.request.args.iteritems():
            req_args[k] = v
        
        # get the x,y viewing co-ordinates of the time graph
        x1 = float(req_args.pop('xmin', min))
        x2 = float(req_args.pop('xmax', max))
        y1 = float(req_args.pop('ymin', 0.0))
        y2 = float(req_args.pop('ymax', 23.999))
        duplicate_time = int(req_args.pop('dup_remove', 0))

        # validate the x,y co-ordinates
        if x1 > x2 or y1 > y2 or y1 < 0.0 or y2 >= 24.0 or x2 > max:
            x1, x2 = min, max
            y1, y2 = 0.0, 23.999        
            
        # get which filters to highlight and which to remove
        highlight_funcs, remove_funcs = convertFilters(req_args)

        # convert the x,y co-ordinates into dates and times 
        dates = convertDates([x1, x2])
        startdate = datetime(dates[0].year, dates[0].month, dates[0].day, 0, 0, 0)
        enddate = datetime(dates[1].year, dates[1].month, dates[1].day, 0, 0, 0) + timedelta(days = 1) - timedelta(milliseconds=1)
        starttime, endtime = convertTimes([y1, y2])

        # duplicate removal
        if duplicate_time > 0:            
            remove_duplicates = True
        else:
            remove_duplicates = False
        
        # get the two lists of data to be plotted: normal and highlighted.
        # removed data is just not shown.
        highlighted, not_highlighted,removed = Case.getTimeGraph(startdate, enddate, starttime, endtime,
                                                   remove_funcs, highlight_funcs,
                                                   remove_duplicates=remove_duplicates,
                                                   duplicate_time=duplicate_time)   
        
        return [{   
                'label': 'removed',
                'data': removed,
                'points': {'show': True, 'fill': '0'},
                'color': '#E8E8E8'
        },
        {   
                'label': 'non-highlighted',
                'data': not_highlighted,
                'points': {'show': True, 'fill': '0'},
                'color': '#1874CD'
        },                
        {   
                'label': 'highlighted',
                'data': highlighted,
                'points': {'show': True, 'fill': '0'},
                'color': '#FF6103'
        }]
    
    
#    Helper functions
# =======================

def convertDates(dates):
    """
        Given a list of dates in JavaScript date format, returns a list of Python dates.
        JavaScript stores dates in milliseconds since the Epoch.
    """
    results = []
    for date in dates:
        unixepoch = float(date)/float(1000)
        results.append(datetime.fromtimestamp(unixepoch))
    return results

def convertTimes(times):
    """
        Given a list of times stored as a fraction e.g. 15.5 is 3:30pm, returns a list
        of Python times. 
    """
    results = []
    for time in times:
        seconds = round((time - int(time)) * 3600)
        results.append(t(int(time),int(seconds/60), int(seconds - int(seconds/60) * 60)))
    return results

def convertFilters(request_args):
    """
        For each request argument, if it is a filter, than put it in the appropriate filter list.
        The request arguments will either be "highlight" or "remove" and will subsequently be put
        in either `highlight_funcs` or `remove_funcs`. Returns those lists.
    """
    remove_funcs = []
    highlight_funcs = [] 
    for label, value in request_args.iteritems():
        f = Filter.getFilterBy(label=label).first()
        if f is not None and value == "highlight":
            q = getattr(f, 'query', None)
            if q is not None:
                highlight_funcs.append(q)
        elif f is not None and value == "remove":
            q = getattr(f, 'query', None)
            if q is not None:
                remove_funcs.append(q)
                
    return highlight_funcs, remove_funcs