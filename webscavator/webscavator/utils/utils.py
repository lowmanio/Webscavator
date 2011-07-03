"""
    Useful variables and methods. Includes all the database connection functions and access to the 
    configuration file.
    
    Variables
    ---------
    
    `ROOT_DIR`
        the root directory of Webscavator.
    
    `CASE_FILE_DIR`
        where case files are kept.
    
    `CONFIG_PATH`
        where the config file is kept.
    
    `FILE_TYPES`
        dictionary of file extensions and what type of file they are. Used in 
        displaying file accesses in the 'files' tab.
    
    `session`
        the sqlite session. Used to access the database. Useful methods include  
        session.add(obj)`, `session.flush()` and `session.commit()`. 
    
    `config`
        the config parser. To get an option do `config[section][option]`
        
    Functions
    ---------
"""

# python imports
from os import path, walk
import csv
from ConfigParser import ConfigParser
# library imports
from werkzeug import Local, LocalManager, MultiDict
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, create_session, sessionmaker

# Useful variables
# ================
ROOT_DIR = path.join(path.dirname(__file__), '..', '..')
CASE_FILE_DIR = path.join(ROOT_DIR, '..', 'case files')
CONFIG_PATH = path.join(ROOT_DIR, 'config')

FILE_TYPES = {'jpg': 'image',
              'jpeg': 'image',
              'png': 'image',
              'gif': 'image',
              'bmp': 'image',
              'tiff': 'image',
              'ico': 'image',
              'doc': 'document',
              'docx': 'document',
              'xls': 'spreadsheet',
              'xlsx': 'spreadsheet',
              'htm': 'web file',
              'html': 'web file',
              'css': 'web file',
              'pdf': 'pdf file',
              'ps': 'pdf file',
              'zip': 'compressed file',
              'gz':'compressed file',
              'csv': 'text file',
              'txt': 'text file',
              'mp3': 'audio file',
              'wav': 'audio file',
              'ogg': 'audio file',
              'wma': 'audio file',
              'avi': 'video file',
              'mpeg':'video file',
              'mp4':'video file',
              'py': 'programming file',
              'pyc': 'programming file',
              'pyw': 'programming file',
              'cpp': 'programming file',
              'c': 'programming file',
              'php': 'programming file',
              'js': 'programming file',
              'sql': 'programming file',
              'java':'programming file'
}

# Local Manager Stuff
# ===================
local = Local()
local_manager = LocalManager([local])

# This creates a custom session class
sessionMaker = sessionmaker(autocommit=False)

# This is a wrapper that will always be the thread-local session
session = scoped_session(sessionMaker, local_manager.get_ident)


# Config Stuff
# ============
config = None

def setup(testing=False):
    """
        This is run when webscavator is started in :doc:`launch`.
        Finds the config file and loads it into the global variable
        config using `ConfigParser()`. Then runs `checkDebugging(testing)`
        with the config option for testing.
    """
    global config
    config_file = path.join(CONFIG_PATH, 'config.ini')
    if not path.exists(config_file):
        raise Exception('Config file "%s" cannot be found' % config_file)
    
    config = ConfigParser()
    config.read(config_file)
    
    checkDebugging(testing)
    
    
def checkDebugging(testing):
    """
        If debug is set to `True` in the config file, a default database is loaded called `debug.db`. 
        This is so that every time webscavator is restarted, there is a database pre-loaded. 
        The Python web server automatically restarts when it detects a change to the code, 
        so when debugging webscavator lots of restarts will happen. 
    """
    if testing == True:
        db = connect(path.join(ROOT_DIR, 'webscavator', 'test', 'test.db'))
        init_database(db)
        bind(db)        
    elif config.getboolean('debugging', 'debug') == True:
        db = connect(path.join(CASE_FILE_DIR, 'debug.db'))
        init_database(db)
        bind(db)
        
# Database Stuff
# ==============

def connect(dbfile):
    """
        Given a database file, create an SQLAlchemy database engine which connects to the database.
    """
    db = create_engine('sqlite:///' + dbfile, echo = False)
    return db

def bind(db):    
    """
        This binds the database to the current session.
    """
    sessionMaker.configure(bind=db, autocommit=False)
    session.remove()

def init_database(db):
    """
        Initialises the database by creating all the tables in webscavator.models.models.py.
    """
    from webscavator.model.models import Base
    Base.metadata.create_all(bind=db)

# Useful Functions
# ================

def getCases():
    """ 
        Gets the case names (.db files) stored in the case file directory.
    """
    files = []
    for subdirs, dirs, f in walk(CASE_FILE_DIR):
        files.append(f)
    return files[0] # only want files, not folders

def getLists():
    """ 
        Gets the list names (.txt files) stored in the case lists directory.
    """
    files = []
    for subdirs, dirs, f in walk(path.join(ROOT_DIR, '..', 'case lists')):
        files.append(f)
    return files[0] # only want files, not folders    

#def get_file_colours():
#
#    f = open(path.join(CONFIG_PATH,'file_access_colours.txt'), 'r')
#    csvreader = csv.reader(f, delimiter=',')
#    
#    file_colours = {}
#    for row in csvreader:
#        try:
#            type, colour = row
#            file_colours[type] = colour
#        except Exception, e:
#            return e
#
#    return file_colours
                
def multidict_to_dict(md):  
    """ 
        Turns a Werkzeug multidict into a dictionary with lists in entries which have 
        more than one value.
    """  
    d = {}
    for k, a in md.iterlists():
        if len(a) == 1:
            d[k] = a[0]
        else:
            d[k] = a
    return d