"""
    Converters
    ----------
    
    All the modules in this package represent a particular web history program which gives an output such 
    as a CSV file, XML file or text file. 
    
    
    Each module takes in a row from the output and returns a particular dictionary which is used to add 
    that row to the webscavator database. see :doc:`csvConverter` for details of adding CSV data
    and :doc:`xmlConverter` for details of adding XML data.
    
    
    Variables
    ---------
    
    `program_lookup` is a dictionary of all the currently supported programs: key = Program long name 
    and value is name the short name stored in the database. `program_lookup` is accessed through the 
    methods below. 
    
    
    `program_info` is a dictionary of useful information for each of the programs supported.
    The minimum entries for each dictionary should be `image` - what icon is associated with
    the program (default is application.png) and `description` - how to produce a valid 
    file form the program (use HTML). Other entries can be added and used when needed. 
    `program_info` is also accessed through the methods below.
    
    
    Add to these two dictionaries when adding a new program converter.
    
    
    Functions
    ---------
    
"""
import sys


program_lookup = {'Pasco': ['pasco', 'csv'],
                  'Web Historian': ['webhistorian', 'xml'],
                  'Net Analysis': ['netanalysis','csv'],
                  'Chrome Cache Viewer': ['chromecacheviewer','csv'],
                  'Fox Analysis': ['foxanalysis','csv']
                  }


program_info = {'Pasco': {
                          'image': 'application.png',
                          'description': """
                                <p>To obtain CSV data from Pasco run:</p>
                                <p><pre class="command_line">> pasco index.dat > output.csv</pre></p>
                          """,
                          },
                'Web Historian': {
                                  'image': 'webhistorian.png',
                                  'description': """
                                      <p>To obtain XML data from Web Historian DO NOT ask it to save as CSV. 
                                      Web Historian currently uses a comma as a delimiter, and cannot be parsed
                                       correctly by any CSV parser when there are commas in the first field 
                                       which is 'title' (very likely to occur). Instead save as an 
                                       XML file. </p>
                                    """,
                                  },
                'Net Analysis': {
                                 'image': 'netanalysis.png',
                                 'description': """
                                 <p>To obtain CSV data from Net Analysis, click on <span class="pre">
                                 File > Export History As > Tab Delimited Text</span>. Rename the extension 
                                 to <span class="pre">.csv</span> instead of <span class="pre">.txt</span>.</p>
                                 <p>Sometimes Net Analysis produces files that do not conform exactly to Tab
                                 Delimted Text, and the converter will reject the file. If it is possible to
                                 locate the line(s) that cause the error, removing these will allow the file
                                 to be accepted.</p>
                                 """,
                                 },
                'Chrome Cache Viewer': {
                                        'image': 'chromecacheviewer.png',
                                        'description': """
                                        <p>To obtain CSV data from Chrome Cache Viewer, select all the 
                                        entries, and go to <span class="pre">File > Save Selected Items</span>. 
                                        Save as a Tab-delimited Text File, and then change the extension from 
                                        <span class="pre">.txt</span> to <span class="pre">.csv</span>. 
                                        Make sure the file is in UTF-8 encoding, otherwise the CSV converter 
                                        will not accept the file. You can do this by opening the CSV file in a 
                                        program such as Notepad++, and choose <span class="pre">Encoding > 
                                        Encode in UTF-8</span>.</p>
                                        """,
                                        },
                'Fox Analysis': {
                                        'image': 'foxanalysis.jpg',
                                        'description': """
                                        <p>To obtain CSV data from Fox Analysis, 
                                        go to <span class="pre">File > Export To > CSV File</span>. 
                                        The will produce several files, please pick the one that ends with 
                                        <span class="pre">Website.csv</span>.</p>
                                        """,
                                        },
                }
                

# Convert file
# =============

def convert_file(type, file):
    """
        Given a file, locates the correct converter and returns a generator which produces 
        a normalised dictionary of data for each row in the file.  
    """
    name = 'webscavator.converters.' + type 
    __import__(name) # import the correct converter
    mod = sys.modules[name]
    cls = getattr(mod, type.capitalize() + 'Converter') # get the converter class
    
    return cls(file).process() # return the converter's row generator


# Helper functions to abstract program_lookup
# ===========================================

def get_name(id):
    """
        Given the name of the python file the converter is stored in, 
        return the full name of the converter.
    """ 
    for k,v in program_lookup.iteritems():
        if id == v[0]:
            return k
    return None

def get_names():
    """ 
        Return a list of all the full names of the converters.
    """
    return program_lookup.keys()
    
def get_program(name):
    """
        Given a full name, return the python file name.
    """
    if name in program_lookup:
        return program_lookup[name][0]
    return None

def get_file(name):
    """
        Given a full name, return the file type.
    """
    if name in program_lookup:
        return program_lookup[name][1]
    return None

def get_programs_files():
    """
        Return a list of (full name, file type) tuples
    """
    out = []
    for name, details in program_lookup.iteritems():
        out.append((name, details[1]))
    return out

# Helper functions to get information about programs and files
# ============================================================

def get_program_info(program):
    """
        Given a program name, return the dictionary of information about it.
    """
    return program_info.get(program)

def get_program_infos():
    """
        Return the dictionary program_info with information about each of the supported programs.
    """
    return program_info
