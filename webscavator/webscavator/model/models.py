"""
    Models
    ------
    
    This is where all the database models are defined. 
    Each database table is represented by a class, and each object in that class is a table row. 
    SQLAlchemy converts the objects into rows and any manipulation on them as SQL queries 
    to abstract the model from the actual database implementation used. 
    
"""

# python imports
import urlparse
from datetime import datetime, timedelta, time as t
import time, calendar
from os import path
import urllib
# library imports
from sqlalchemy import Table, Column, Integer, Boolean, Float, Unicode, MetaData, Time 
from sqlalchemy import ForeignKey, DateTime, CheckConstraint, asc, desc, func, PickleType
from sqlalchemy.sql import or_, not_, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relation, contains_eager, aliased
# local imports
from webscavator.utils.utils import connect, bind, init_database, session, ROOT_DIR, CASE_FILE_DIR, FILE_TYPES
from webscavator.converters import get_name, get_program_info



Base = declarative_base()

__all__ = ['Browser', 'Case', 'Group', 'Entry', 'URL', 'Filter', 'SearchTerms', 'get_plotable', 'getFilter']

entry_terms = Table('entry_terms', Base.metadata,
                      Column('entry_id', Integer, ForeignKey('entry.id'), primary_key = True),
                      Column('search_id', Integer, ForeignKey('search_terms.id'), primary_key = True)
                      )

# Useful functions
# ===================
def get_plotable(d, t, u, bn, bv, bs, p, ti):
    """
        Returns (date, time, URL, browser name, browser version, browser source, program name, title)
        in a format Flot (the JavaScript timeline library) will understand. 
        Only (date, time) needs to be sent in order
        for the graph to be displayed properly. The others are used for hover over and clickable text.
        
        .. note:: 
            Currently this function uses a hack to get British Summer Time dates to be displayed
            properly as GMT in Flot by adding an hour on to any dates after March 28th 2010.
            
            **ToDo**: Fix this urgently!!
    """
    
    # Hack to get British Summer Time to convert to GMT for flot to display this properly
    if d >= datetime(2010, 3, 28):
        d = d + timedelta(hours=1)
    
    # date at midnight in milliseconds since Unix Epoch
    d = time.mktime(d.timetuple()) * 1000
    # time in a faction e.g. 5:30pm --> 17.5
    t = float(t.hour) + t.minute/60.0 + t.second/3600.00
    return (d, t, u, bn, bv, bs, get_name(p), ti if ti else '--')

def getFilter(highlight_funcs=[], remove_funcs=[]):
    """
        Get the right filter. This is used to filter domain names and search terms correctly.
        `Case.filter_queries` is called, and if `highlight_funcs` != [] then return
        the highlighted query, otherwise return the non-highlighted query. 
    """
    filter_q = session.query(Entry.id)\
                .join(Entry.parsedurl, Entry.browser, Entry.group)\
                .outerjoin(Entry.search_terms)                    

    q_removed, q_highlighted, q_not_highlighted = \
        Case.filter_queries(filter_q, remove_funcs, highlight_funcs)        
        
    if highlight_funcs:
        filter_q = q_highlighted 
    else:
        filter_q = q_not_highlighted
        
    return filter_q.group_by(Entry.id).subquery()


# Model Classes
# ======================

class Model(object):
    """
        Abstract class with some useful functions for all the model classes.
    """
    @classmethod
    def get(cls, id):
        """
            Return the object with the given id.
        """
        return session.query(cls).get(id)
    
    @classmethod
    def getFilterBy(cls, **vars):
        """
            Return a list of objects which satisfy the conditions in **vars
            E.g. `Case.getFilterBy(name="Foo")`
        """
        return session.query(cls).filter_by(**vars)

    @classmethod
    def getAll(cls):
        """ 
            Return all the objects.
        """
        try:
            q = session.query(cls).order_by(asc(cls.id))
        except AttributeError:
            q = session.query(cls).order_by(asc(cls.entry_id))
        return q
    
    @classmethod
    def getAmount(cls):
        """
            Return the number of objects.
        """
        return session.query(cls).count()
    
    @classmethod
    def getFilterOptions(cls):
        """
            Returns the classes `filter_options`.
        """
        opt = cls.filter_options
        return opt

class Browser(Base, Model):
    """
        Class that stores browser types.
        
        `id`
            browser id
        
        `name`
            browser name
        
        `version`
            browser version
        
        `source`
            browser source. this is either a profile for Firefox/Chrome 
            or the file location for IE, e.g. history or cache
        
        `entries`
            list of entry items that were made using this browser
    """
    __tablename__ = 'browser'
    
    id = Column(Integer, primary_key = True)
    name = Column(Unicode)
    version = Column(Unicode) 
    source = Column(Unicode)
    
    def __init__(self, name, version, source):
        self.name = name
        self.version = version
        self.source = source

    def __repr__(self):
        return "[%s]" % self.name
    
    @staticmethod
    def getPercentages():
        """
            Used in the overview statistics. Returns a list of `(browser object, percent)` tuples 
            for each browser where percent is the percentage this browser is used in all the entries.
        """
        q = session.query(Browser.name, func.count(1)).join('entries').group_by(Browser.name).all()
        total = 0.0
        for browser, count in q:
            total = total + count
        return [(browser, count/total) for browser, count in q]
    
Browser.filter_options = {'name': ('Name', ['Is','Is not'], Browser.getAll, 'select'),
                      'version': ('Version', ['Is','Is not'], Browser.getAll, 'select'),
                      'source': ('Profile/IE Type', ['Is','Is not'], Browser.getAll, 'select'),
                      }

class Case(Base, Model):
    """
        Class that stores the case. Each database will only have one case. 
        
        `id`    
            case id
        
        `name`
            case name
        
        `date`
            date this case was created
        
        `groups`
            A list of group objects that belong to this case
    """
    __tablename__ = 'case'
    
    id = Column(Integer, primary_key = True)
    name = Column(Unicode)
    date = Column(DateTime)
    
    def __init__(self, name):
        self.name = name
        self.date = datetime.now()

    def __repr__(self):
        return "[%s, %s]" % (self.name, self.date.strftime("%H:%M %b %d %Y"))  
    
    @staticmethod
    def create_database(dbfile):
        """
            Creates the database file, initialises all the models in this file and binds the 
            database to webscavator's session. 
        """
        db = connect(path.join(CASE_FILE_DIR, dbfile))
        init_database(db)
        bind(db)
      
    @staticmethod  
    def load_database(dbfile):
        """
            Given a database file, connects to the database and binds it to webscavator's session.
        """
        db = connect(path.join(CASE_FILE_DIR, dbfile))
        bind(db)        
        
    @staticmethod
    def get_case():
        """
            Get the current case.
        """
        return session.query(Case).first()
    
    def dblocation(self, dbfile):
        """
            Return the absolute location of a given database file.
        """
        return path.abspath(path.join(CASE_FILE_DIR, dbfile))
    
    def _formatDate(self):
        """
            A property for formatted_date. Returns the date in a normalised format.
        """
        return self.date.strftime("%I:%M%p %d %b %Y")
    formatted_date = property(_formatDate)
    
    @staticmethod
    def getNewestEntry(case):
        """
            Returns the latest Entry for this case.
        """
        q = Case.getAllEntries(case).order_by(desc(Entry.access_date), desc(Entry.access_time)).first()
        return q

    @staticmethod
    def getOldestEntry(case):
        """
            Returns the oldest Entry for this case.
        """
        q = Case.getAllEntries(case).order_by(asc(Entry.access_date), asc(Entry.access_time)).first()
        return q
        
    @staticmethod
    def getAllEntries(case):
        """
            Returns all the entries for this case where the access time and date are not `None`.
        """
        q = session.query(Entry).filter(Entry.access_time!=None).filter(Entry.access_date!=None).\
            join('group').filter_by(case_id=case.id)
        return q                        
    
    @staticmethod
    def getMinMax(latest):
        """
            Return the minimum and maximum dates for Flot. Given a date, returns minimum which is
            1 month prior on the 1st of the month, to the last day of the month for the given date.
            E.g. given 12th May, returns (1st April, 31st May). This is returned in JavaScript 
            milliseconds since the Epoch. 
        """
        start_month = latest.month - 1 if latest.month != 1 else 12        
        start_year = latest.year if latest.month != 1 else latest.year - 1

        start = datetime(start_year, start_month, 1)
        end = start + timedelta(days=62)
                
        return time.mktime(start.timetuple()) * 1000, time.mktime(end.timetuple()) * 1000
    
    @staticmethod
    def filter_queries(q, remove_funcs, highlight_funcs):
        """
            This expects `q` to have entry, browser, url, group and search_terms available 
            for filtering. Returns three queries with the correct entries put in each according
            to the filters:
            `q_removed`, `q_highlighted` and `q_not_highlighted`.
        """
        # do the filtering query
        # ---------------------        
        filtered_ors = []
        for f in remove_funcs:
            ands = f.query()
            filtered_ors.append(ands)

        q_filtered = q        
        if filtered_ors:
            q_removed = q_filtered.filter((or_(*filtered_ors)))
            q_filtered = q_filtered.filter(not_(or_(*filtered_ors)))
        else:
            q_removed = q_filtered.filter('0')

        highlighted_ors = []
        for f in highlight_funcs:
            ands = f.query()
            highlighted_ors.append(ands)
            
        q_highlighted = q_filtered
        if highlighted_ors:
            q_highlighted = q_highlighted.filter(or_(*highlighted_ors))
        else:
            q_highlighted = q_highlighted.filter('0')

        q_not_highlighted = q_filtered
        if highlighted_ors:
            q_not_highlighted.filter(not_(and_(*highlighted_ors)))       
        
        return q_removed, q_highlighted, q_not_highlighted
        
    @staticmethod
    def getTimeGraph(startdate, enddate, starttime, endtime, remove_funcs, highlight_funcs,
               remove_duplicates=False, duplicate_time=0):
        """
            Given a start and end date and time and filters, returns three lists of entry points:
            `highlighted`, `not_highlighted` and `removed` by calling `filter_queries()`
            Each entry will be in one of those lists for Flot to draw.  
        """
        
        # make the queries
        # ----------------
        q = session.query(Entry.access_date, Entry.access_time, Entry.url, Browser.name,
                          Browser.version, Browser.source, Group.program, Entry.title)
        
        # join onto all the other tables
        q = q.join('browser').join('parsedurl').join('group').outerjoin(Entry.search_terms)
        
        # filter by the start and end dates and times
        q = q.filter(Entry.access_date >= startdate).filter(Entry.access_date <= enddate)
        
        q_removed, q_highlighted, q_not_highlighted = Case.filter_queries(q, remove_funcs, highlight_funcs)

        removed = (q_removed.order_by(asc(Entry.access_date), asc(Entry.access_time)), [])
        highlighted = (q_highlighted.order_by(asc(Entry.access_date), asc(Entry.access_time)), []) 
        not_highlighted = (q_not_highlighted.order_by(asc(Entry.access_date), asc(Entry.access_time)), [])

        # put the results in the format Flot wants it
        # -------------------------------------------
        for (q, entries) in [removed, highlighted, not_highlighted]:
            seen = set()
            for cols in q:   
                plot = get_plotable(*cols)

                if remove_duplicates == True: # remove duplicates                
                    if plot not in seen:
                        if len(entries) == 0:
                            entries.append(plot)   # add first entry regardless
                            seen.add(plot)
                        else:
                            if (entries[-1][0] == plot[0] and \
                            (plot[1] - entries[-1][1]) >= float(duplicate_time)/float(60)) \
                            or (entries[-1][0] < plot[0]): 
                                # only add entries <duplicate_time> minutes apart
                                entries.append(plot)
                                seen.add(plot)
                else: # else add everything
                    entries.append(plot)
                
        return highlighted[1], not_highlighted[1], removed[1]

class Group(Base, Model):
    """
        Class that stores information about a particular uploaded file.
        
        `id`    
            group id
            
        `name`
            group name
            
        `description`
            group description
            
        `csv_name`
            the filename of the uploaded file
            
        `program`
            the program used to make the file
            
        `case`
            the case object this group belongs to
            
        `entries`
            list of entry objects for this group
        
    .. note::
        Most of these forms were created before it was realised that files other than CSV were needed
        (such as XML). 

        **ToDo**: change `csv_name` to `file_name`.  
    """
    __tablename__ = 'groups'
    
    id = Column(Integer, primary_key = True)
    name = Column(Unicode)
    description = Column(Unicode)
    csv_name = Column(Unicode)
    program = Column(Unicode)
    case_id = Column(Integer, ForeignKey('case.id'))
    
    case = relation(Case, backref=backref('groups', order_by=desc(name)))
    
    def __init__(self, name, desc, case, program):
        self.name = name
        self.description = desc
        self.case = case
        self.program = program          

    def __repr__(self):
        return "[%s, %s]" % (self.name, self.case.name)
    
    def getNumEntries(self):
        """
            Get amount of entries for this group.
        """
        return session.query(Entry).filter_by(group_id=self.id).count()
    
    def getStartDate(self):
        """
            Get the starting date of all the group's entries.
        """
        return self._formatDate(session.query(Entry).filter_by(group_id=self.id).\
                                filter(Entry.access_date!=None).filter(Entry.access_time!=None).\
                                order_by(asc(Entry.access_date), asc(Entry.access_time)).\
                                first().access_date)
    
    def getEndDate(self):
        """
            Get the ending date of all the group's entries.
        """
        return self._formatDate(session.query(Entry).filter_by(group_id=self.id).\
                                filter(Entry.access_date!=None).filter(Entry.access_time!=None).\
                                order_by(desc(Entry.access_date), desc(Entry.access_time)).\
                                first().access_date)
    
    def _formatDate(self, date):
        """
            Given a date, return it in a normalised format.
        """
        return date.strftime("%I:%M%p %d %b %Y")
        
    def _getProgramName(self):
        """
            Return the full name of the web history program used to create the file. See 
            vizzieweb/convertors/__init__.py for details. 
        """
        return get_name(self.program)
    program_name = property(_getProgramName)
    
    def _getProgramIcon(self):
        """
            Return the icon of the web history program used to create the file. See 
            vizzieweb/convertors/__init__.py for details. 
        """
        return get_program_info(self.program_name)['image']
    program_icon = property(_getProgramIcon)
Group.filter_options = {'name': ('Group Name', ['Is','Is not'], Group.getAll, 'select'),
                        'program': ('Program Used', ['Is','Is not'], Group.getAll, 'select'),
                      }
              
class Entry(Base, Model):
    """
        Class that stores a particular row in the file. 
        
        `id`
            entry id
            
        `type`
            entry type e.g. URL
            
        `access_date`
            entry access date
            
        `access_time`
            entry access time
            
        `modified_date`
            entry modified date
            
        `modified_time`
            entry modified time
            
        `url`
            entry url
            
        `filename`
            entry filename on disk
            
        `directory`
            entry folder on disk
            
        `http_headers`
            entry url http headers
            
        `title`
            entry url title
            
        `deleted`
            whether entry was originally deleted or not
            
        `content_type`
            type of content, usually only index.dat files store this
            
        `group`
            group object this entry belongs to
            
        `parsedurl`
            url object this entry has
            
        `browser`
            browser object this entry belong to
        
    """
    __tablename__ = 'entry'
    
    id = Column(Integer, primary_key = True)
    type = Column(Unicode) 
    access_date = Column(DateTime, index=True)
    access_time = Column(Time, index=True)
    modified_date = Column(DateTime)
    modified_time = Column(Time)
    url = Column(Unicode)
    filename = Column(Unicode)
    directory = Column(Unicode)
    http_headers = Column(Unicode)
    title = Column(Unicode)
    deleted = Column(Boolean)
    content_type = Column(Unicode)
    
    browser_id = Column(Integer, ForeignKey('browser.id'))
    group_id = Column(Integer, ForeignKey('groups.id'))
    
    group = relation(Group, backref=backref('entries'))
    browser = relation(Browser, backref=backref('entries', order_by=desc(id)))
    
    HEADERS = [('browsername','Browser'), ('access_time_str', 'Access Time'), ('type', 'Type'),('url', 'URL')]
    
    def __init__(self, **vars):    
        for k, v in vars.iteritems():  
            if k == "access_time" :
                self.access_date = datetime(v.year, v.month, v.day, 0, 0, 0, 0)
                self.access_time = t(v.hour, v.minute, v.second, v.microsecond)
            elif k == "modified_time" :
                self.modified_date = datetime(v.year, v.month, v.day, 0, 0, 0, 0)
                self.modified_time = t(v.hour, v.minute, v.second, v.microsecond)
            else:
                setattr(self, k, v)
            
        self.parsedurl = URL(self.url)
        
    def __repr__(self):
        return "[entry %s]" % (self.url)   
    
    def _formatAccessTime(self):
        """
            A property for access_time_str. Returns the date in a normalised format.
        """
        return self.access_time.strftime("%H:%M") + " " + self.access_date.strftime("%d/%m/%Y")
    access_time_str = property(_formatAccessTime)
                              
    def _formatModifiedTime(self):
        """
            A property for modified_time_str. Returns the date in a normalised format.
        """
        return self.modified_time.strftime("%H:%M") + " " + self.modified_date.strftime("%d/%m/%Y")
    modified_time_str = property(_formatModifiedTime) 
    
    def _timeline_date(self):
        """
            A property for timeline_date. Returns the date in a normalised format for Flot.
        """
        if self.access_time and self.access_date:
            # Fri Jul 02 2010 18:00:00
            return self.access_date.strftime("%a %b %d %Y") + " " + self.access_time.strftime("%H:%M:%S")
        else: 
            return None
    timeline_date = property(_timeline_date)

    def _browsername(self):
        """
            A property for browsername.
        """
        return self.browser.name
    browsername = property(_browsername) 
    
    @staticmethod
    def generateHeatMap():
        """
            Returns heatmap things for the overview: the table headers, the heatmap
            table and the highest and lowest values (used to calculate heatmap colour).
        """
        headers = ['Mon', 'Tue','Wed','Thu','Fri','Sat','Sun']
        rows = []
        step = 1 # number of hours each row in table represents
        
        init = datetime(1, 1, 1)
        start_time = init.time()
        until_time = None
        
        highest = 0
        lowest = 0
        
        while(start_time < t((24-step),0,0)):
            start_time = init.time()
            until_time = (init + timedelta(hours=step) - timedelta(milliseconds=1)).time()
            
            title = start_time.strftime('%H:%M - ') + until_time.strftime('%H:%M')
            
            values = []
            for weekday in [1,2,3,4,5,6,0]: # '%w' gives weekdays starting on sunday
                q = session.query(Entry)\
                    .filter(func.strftime('%w', Entry.access_date) == str(weekday))\
                    .filter(Entry.access_time >= start_time)\
                    .filter(Entry.access_time <= until_time).count()

                if q > highest:
                    highest = q
                if q < lowest:
                    lowest = q
                
                values.append(q)
                
            rows.append((title, values))
            init = init + timedelta(hours=step)

        return headers, rows, highest, lowest   
    
    @staticmethod
    def averagePages():
        """
            Returns the average number of websites visited in one day, i.e. only http
            and http entries. 
        """
        q = session.query(Entry.access_date, func.count(1)).join('parsedurl')\
            .filter(or_(URL.scheme=="http", URL.scheme=="https")).group_by(Entry.access_date)
        total = q.count()
        sums = [row1 for row0, row1 in q]
        if total != 0:
            return int(sum(sums)/float(total))
        else:
            return 0  
    
    @staticmethod
    def peakTime():  
        """
            Returns the peak time of web browser usage. Similar to the heatmap, although doesn't 
            do for each day of the week - sums up each hour and returns the highest.
        """     
        step = 1
        
        init = datetime(1, 1, 1)
        start_time = init.time()
        until_time = None
        
        highest = 0
        timeperiod = None
        while(start_time < t(24-step,0,0)):
            start_time = init.time()
            until_time = (init + timedelta(hours=step) - timedelta(milliseconds=1)).time()
        
            q = session.query(Entry).filter(Entry.access_time >= start_time)\
                    .filter(Entry.access_time <= until_time).count()

            if q > highest:
                highest = q
                timeperiod = start_time.strftime('%H:%M - ') + until_time.strftime('%H:%M')
                
            init = init + timedelta(hours=step)
        return timeperiod  
    
    @staticmethod
    def _buildTree(tree, element):
        """
            Used to build the file directory tree for the File tab.
        """
        path, count, dates = element               
        current = tree
        
        parts = path.split('/')
        for part in parts[:-1]:
            current = current.setdefault(part, {})
        current[parts[-1]] = (count, dates)
    
    @staticmethod
    def filesAccessed():
        """
            Returns a file directory tree and the total amount of files accessed. The tree
            is a dictionary of drives, each drive letter is the key and the value is another dictionary 
            with the keys being file types. For each file type, the value is a tree structure with the
            end point being a file name, the number of times the file was accessed and a list of 
            access dates.
                    
            .. note::
                This does not allow for Linux etc drives, only Windows one letter drives.
                
                **ToDo**: re-optimise this query, more things were done making it slow again for 
                larger datasets. 
            
                **ToDo**: Allow other operating systems file systems. 
        """
        q = session.query(URL, func.count(1)).filter(URL.scheme == "file").order_by(func.count(1))
        q = q.group_by(URL.path)
        
        total = q.count()
         
        drives = {}
        
        for file, count in q:
            path = urllib.unquote(file.path[1:])
            
            # hack to get dates working: needs to be made into above query ^
            dates = session.query(Entry.access_date, Entry.access_time).join(URL)\
                .filter(URL.path==file.path)\
                .order_by(desc(Entry.access_date), desc(Entry.access_time))
            
            if path[1] == ":":
                drive = path[0]
            else:
                continue #don't deal with Linux yet
            
            ending = path.rsplit('.',1)
            type = FILE_TYPES.get(ending[-1].strip().lower(),'other file')


            if drive not in drives:           
                drives[drive] = ({}, 0)
            
            if type not in drives[drive][0]:
                drives[drive][0][type] = ({}, 0)
                
            drives[drive] = (drives[drive][0], drives[drive][1] + count)
            drives[drive][0][type] = (drives[drive][0][type][0], drives[drive][0][type][1] + count)
     
            Entry._buildTree(drives[drive][0][type][0], (path, count, dates))
                            
        return drives, total    
                
Entry.filter_options = {
    'access_date': ('Access Date', 
                    ['Is','Is not','Greater than','Less than'], 
                     None, 'date'),
    'access_time': ('Access Time', 
                    ['Is','Is not','Greater than','Less than'],
                    None, 'time'),
    'modified_date': ('Modified Date', 
                      ['Is','Is not','Greater than','Less than'], 
                    None, 'date'),
    'modified_time': ('Modified Time', 
                      ['Is','Is not','Greater than','Less than'], 
                    None, 'time'),
    'url': ('Full URL', 
            ['Is','Is not','Contains','Matches regular expression',\
             'Is in list','Is not in list'], 
            None, 'text'),
    'title': ('Page title', 
              ['Is','Is not','Contains','Matches regular expression',\
               'Is in list','Is not in list'], 
            None, 'text'),
    'type': ('Type', 
            ['Is','Is not'], 
            Entry.getAll, 'select'),
    'filename': ('File Name', 
                ['Is','Is not','Contains','Matches regular expression'], 
                None, 'text'),
    'directory': ('Directory', 
                  ['Is','Is not'], 
                Entry.getAll, 'select'),
    'http_headers': ('HTTP Headers', 
                    ['Is','Is not','Contains','Matches regular expression'], 
                    None, 'text'),
    'deleted': ('Deleted', ['Is','Is not'], 
                Entry.getAll, 'select'),
    'content_type': ('Content Type', 
                    ['Is','Is not'], 
                    Entry.getAll, 'select')
}


class URL(Base, Model):
    """
        Class that stores a URL for an entry divided up into its different parts.
        
        `entry_id`
            url id
            
        `scheme`
            url scheme
            
        `netloc`
            url network location
            
        `path`
            url path
            
        `params`
            url params
            
        `query`
            url query strings
            
        `fragment`
            url fragment
            
        `username`
            url username
            
        `password`
            url password
            
        `hostname`
            url hostname
            
        `port`
            url port
            
        `domain`
            normalised hostname i.e without the www
            
        `search`
            the search engine string (if any)
            
        `entry`
            entry object. one-to-one join. 
    """
    __tablename__ = 'url'
    
    entry_id = Column(Integer, ForeignKey('entry.id'), primary_key = True)
    scheme = Column(Unicode) 
    netloc = Column(Unicode) 
    path = Column(Unicode) 
    params = Column(Unicode) 
    query  = Column(Unicode) 
    fragment = Column(Unicode) 
    username = Column(Unicode) 
    password = Column(Unicode) 
    hostname = Column(Unicode) 
    port = Column(Integer)
    domain = Column(Unicode)
    search = Column(Unicode)
    
    entry = relation(Entry, backref=backref('parsedurl', uselist=False))
    
    def __init__(self, url=None):
        
        if url is not None:
            parsed_url = urlparse.urlparse(self.urlstrip(url))

            self.scheme=parsed_url.scheme
            self.netloc=parsed_url.netloc
            self.path=parsed_url.path
            self.params=parsed_url.params
            self.query=parsed_url.query
            self.fragment=parsed_url.fragment
            self.username=parsed_url.username
            self.password=parsed_url.password
            self.hostname=parsed_url.hostname
            try:
                self.port=parsed_url.port # sometimes throws exception on odd protocols such as res://
            except:
                self.port = None
            self.domain = None
            
            self.setDomain()
    
    def __repr__(self):
        return "[url %s]" % (self.domain)  
            
    def asDict(self):
        """
            Used for optimising adding URLs to database when converting files. 
        """
        return {
            'scheme': self.scheme,
            'netloc': self.netloc,
            'path': self.path,
            'params': self.params,
            'query': self.query,
            'fragment': self.fragment,
            'username': self.username,
            'password': self.password,
            'hostname': self.hostname,
            'port': self.port,
            'domain': self.domain
        }
    
    def urlstrip(self, url):
        """
            Some urls from IE appear like [username]@[url]. urlstrip() gets rid of the 
            [username]@ bit. Returns the shortened URL
        """
        if url.find('@') == -1:
             return url # didn't find an @
        else:
             start, part, end = url.partition('@')
             if start.find('://') == -1:
                 return end # found an @ and no :// before it, so this is user@URL - 
                            # return the shortened URL
             else:
                 return url # found an @, but :// before it, so part of URL - return the URL
             
            
    def setDomain(self):
        """
            Removes www from front of any hostnames to normalise the hostnames and 
            then tries to remove subdomains by working backwards to find the domain.
        """        
        
        toplevel = ['aero', 'arpa', 'asia', 'biz', 'cat', 'com', 'coop', 'edu', 'gov', 'info', 'int', 
                    'jobs', 'mil', 'mobi', 'museum', 'name', 'net', 'org', 'pro', 'tel', 'travel']
        
        if self.hostname and self.scheme not in ['res', 'ms-help']:
            
            if self.hostname.startswith('www.'):
                d = self.hostname[4:]
            else:
                d = self.hostname
                
            parts = d.split('.')
            
            all_int = True  # check to make sure it's a domain name rather than IP address
            for p in parts:
                try:
                    int(p)
                except Exception, e:
                    all_int = False
            
            if all_int == True:
                self.domain = None
            else:
            
                ending = ending1 = ""
                
                if parts[-1] in toplevel or len(parts[-1]) == 2:
                    ending = "." + parts[-1] # ends with toplevel domain name or 
                                             # a 2 letter country code
                    parts = parts[0:-1]
                    if len(parts) > 1 and (len(parts[-1]) == 2 or parts[-1] in toplevel):
                        ending1 = "." + parts[-1]   
                        # second to last part is in toplevel (e.g. org.uk) or 2 letter
                        # code (e.g. co.uk) -- only if url has 2 or more parts left
                        parts = parts[0:-1]         
                    else:
                        ending1 = ""
                        
                domain = parts[-1]
                
                self.domain = domain + ending1 + ending
        else:
            self.domain = None
           
    @staticmethod        
    def setDomain_manual(group):
        """
            Manually set the domain names. Used in the optimised adding of URLs which bypasses 
            creating URL objects using `__init__()`
        """
        q = session.query(URL).join('entry').filter_by(group_id=group.id).all()
        for row in q:
            row.setDomain()
        
    @staticmethod    
    def getTop(num=100, highlight_funcs=[], remove_funcs=[]):
        """
            Get the top [amount] filtered URLS for a case. This has been optimised as one 
            query with a subquery. 
        """        

        filter = getFilter(highlight_funcs, remove_funcs)
        
        url2 = aliased(URL)
        subq = session.query(url2.domain, func.count(url2.domain).label('domain_count'))\
                .join(filter).filter(url2.domain != None)\
                .group_by(url2.domain).order_by(desc(func.count(url2.domain)))

        if num != "all":
            subq = subq.limit(num)           
        subq = subq.subquery()

        q = session.query(URL.netloc, func.count(1), subq.c.domain, subq.c.domain_count)\
            .join((subq, URL.domain == subq.c.domain))\
            .join(filter)\
            .group_by(URL.netloc)\
            .order_by(desc(subq.c.domain_count), asc(subq.c.domain), asc(URL.netloc))

        domains = []
        for netloc, netloc_count, domain, domain_count in q:
            if len(domains) == 0 or domains[-1][0] != domain:
                domains.append((domain, domain_count, []))
                
            domains[-1][2].append((netloc, netloc_count))
          
        return domains 

URL.filter_options = {'domain': ('Domain name', ['Is','Is not', 'Contains','Matches regular expression',\
                                                 'Is in list','Is not in list'], None, 'text'),
                      'hostname': ('Host name', ['Is','Is not', 'Contains','Matches regular expression',\
                                                 'Is in list','Is not in list'], None, 'text'),
                      'username': ('Username', ['Is','Is not'], URL.getAll, 'select'),
                      'password': ('Password', ['Is','Is not'], URL.getAll, 'select'),
                      'port': ('Port', ['Is','Is not'], URL.getAll, 'select'),
                      'scheme': ('Protocol', ['Is','Is not'], URL.getAll, 'select'),
                      'fragment': ('Fragment', ['Is','Is not'], URL.getAll, 'select'),
                      'query': ('Query', 
                                ['Is','Is not', 'Contains','Matches regular expression'], 
                                None, 'text'),
                      }
     
class Filter(Base, Model):
    """
        Class that stores a filter object. 
        
        `id`
            filter id
            
        `fillcolor`
            the color of flot's markers
            
        `label`
            the name of the filter
            
        `text`
            the long name of the filter, what the user sees
            
        `query`
            pickled Filter object which stores the filter parts see model/filters.py
    """

    __tablename__ = 'filters'
    
    id = Column(Integer, primary_key = True)
    fillColor = Column(Unicode) 
    label = Column(Unicode) 
    text = Column(Unicode)  
    query = Column(PickleType)
    
    def __init__(self, label, text, fillColor='#33A1C9'):
        self.label = label
        self.text = text
        self.fillColor = fillColor   
        
    def __repr__(self):
        return "[filter %s]" % (self.label) 
    
    @staticmethod
    def onlineSearches(engine, highlight_funcs=[], remove_funcs=[], num=20):
        """
            Given a search engine, amount and filters, returns a word cloud dictionary of search terms.
            The keys are the terms and the values are a (ratio, search phrases term was in, 
            length of search phrases) tuple. Also returns total amount of terms, total number of unique 
            terms and the smallest ratio (used to make the sizes of the words relative to smallest).
        """
        
        filter = getFilter(highlight_funcs, remove_funcs)

        searchterms2 = aliased(SearchTerms)
        subq = session.query(searchterms2.id).filter(searchterms2.engine==engine)\
            .join(searchterms2.entries).join((filter, Entry.id == filter.c.id))\
            .group_by(searchterms2.id)\
            .order_by(desc(searchterms2.occurrence))
        
        if num != "all":
            subq = subq.limit(num)
                
        subq = subq.subquery()
        
        q = session.query(SearchTerms)\
            .join((subq, subq.c.id == SearchTerms.id))\
            .join(SearchTerms.entries)\
            .join((filter, Entry.id == filter.c.id))\
            .join(Entry.parsedurl).filter(SearchTerms.engine==engine)\
            .options(contains_eager('entries'), contains_eager('entries.parsedurl'))\
            .order_by(desc(Entry.access_date), desc(Entry.access_time))            
        
        
        terms = q.all()
        total_terms = float(sum(len(t.entries) for t in terms))        
        unique_terms = len(terms)
        cloud = {}
        smallest = 1.0
        for term in terms:
            search_strings = [(entry.parsedurl.search, entry.timeline_date) for entry in term.entries]
            ratio = len(search_strings)/total_terms
            # Hack to stop javascript name-space clash. TODO: Fix this in nicer way.
            cloud['_' + term.term] = (ratio, search_strings, len(search_strings))
            if ratio < smallest:
                smallest = ratio
        return cloud, total_terms, unique_terms, smallest

class SearchTerms(Base, Model):
    """
        Class that stores a search term.
        
        `id`
            search term id
            
        `term`
            the term
            
        `occurrence`
            number of times term has appeared in searches
            
        `engine`
            what search engine this term appeared in
            
        `engine_long`
            full name of search engine
            
        `entries`
            list of entries search term belongs to
    """
    
    __tablename__ = 'search_terms'  
    
    id = Column(Integer, primary_key = True)
    term = Column(Unicode)  
    occurrence = Column(Integer)
    engine = Column(Unicode)
    engine_long = Column(Unicode)
    
    entries = relation('Entry', secondary=entry_terms, backref=backref('search_terms'))
    
    STOP_WORDS = ['','of','and','the','to','for','in','a', 'i', 'an', 'are', 'as', 'at', 
              'be', 'by','from','is','on','was','that','this','or','when','where',
              'what','how','was','with', '-', '&','+','b','c','d','e','f','g','h','j',
              'k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
    
    def __init__(self, term, engine, engine_long):
        self.term = term
        self.engine = engine
        self.engine_long = engine_long
        self.occurrence = 1
        
    def __repr__(self):
        return " [%s] " % self.term
    
    @staticmethod
    def getTerms(query):
        """
            Given the query part of a url, extracts the serach terms or phrases (those surrounded
            by quotes). Returns the search string and a list of terms in that string.
        """
        current_terms = []
        terms = query.split('"')
        
        actual_query = u" ".join(query.split('+'))
        
        if len(terms) == 1: # no quotes
            for x in terms[0].split('+'):
                if x not in SearchTerms.STOP_WORDS:
                    current_terms.append(x.strip().lower()) 
        else:
            for t in terms:
                if t != '' and (t[0] == "+" or t[-1] == "+"):
                    for x in t.split('+'):
                        if x not in SearchTerms.STOP_WORDS:
                            current_terms.append(x.strip().lower()) 
                elif t != '':
                    current_terms = current_terms + [' '.join(x for x in t.split('+'))]
        current_terms = [c.lower() for c in current_terms]
        
        return actual_query, current_terms 
SearchTerms.filter_options = {'term': ('Search Term', 
                                       ['Is','Is not', 'Contains',\
                                        'Matches regular expression','Is in list','Is not in list'], 
                                        None, 'text'),
                              'occurrence': ('Term Occurrence', 
                                             ['Is','Is not', 'Greater than','Less than'], 
                                             None, 'number'),
                              'engine_long':('Search Engine',
                                             ['Is','Is not'],SearchTerms.getAll,'select')
                              }
