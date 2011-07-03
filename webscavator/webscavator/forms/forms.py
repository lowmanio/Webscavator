"""
    Each class represents the fields present on a particular web form, and how it should be validated.
    Specific validators can be found in :doc:`validators`. All forms inherit from Schema.
    
    
    If the form has an error, the validator will throw an exception and add the name of the 
    form field and the error message to a dictionary `form_error`, which is passed back to the 
    web page for the user to correct. If the form is valid, the endpoint will process the form, 
    and return the successful web page. 
    
    .. note::
        Most of these forms were created before it was realised that files other than CSV were needed
        (such as XML). 
        Therefore a lot of form field names are 'csv_file' rather than just generic 'file'.
        
        **ToDo**: Change any field names that refer to csv data to be more generic. Applies to Mako
        templates too.     
"""

# python imports
import datetime 
# library imports
from formencode import Schema, Invalid, validators as v
from formencode.foreach import ForEach
from formencode.compound import All
# local imports
from webscavator.forms.validators import *



# Step 1 Forms: Adding case and Sqlite DB file
# ============================================
class Case(Schema):
    """
        Case Schema.
    """
    name = v.UnicodeString()
    
class wizard1_form(Case):
    """
        Form to add a new case. Inherits from `Case()`.
        
        
        **Attributes**
        
        
        `name` -- name of case.
        
        
        `dbfile` -- file to save case to. Validator checks this file doesn't already exist.
    """
    dbfile = All(CheckCaseDoesntExist(), NonAscii(not_empty=True)) #check dbfile doesn't already exist
    
class edit1_form(Case):
    """
        Form to edit case. Inherits from `Case()`
        
        
        **Attributes**
        
        
        `name` -- new name of case.
    """
    pass

# Step 2 Forms: Adding data and browsers
# ==========================================
class Data(Schema):
    """
        Data Schema.
    """
    name = v.UnicodeString(not_empty=True)
    desc = v.UnicodeString()
    program = CheckAllowedProgram(not_empty=True) #need to check it's allowed
    
    
class AddData(Data):
    """
        Form to add a new file. Inherits from `Data()`
        
        
        **Attributes**
        
        
        `program` -- web history program used to create file.
        
        
        `name` -- name of this dataset.
        
        
        `desc` -- optional description of dataset.
        
        
        `data` -- the web history file. 
    """
    data = UploadData(not_empty=True)

class EditData(Data):
    """
        Form to edit file. Inherits from `Data()`
        
        
        **Attributes**
    
    
        `group` -- the current data group being edited. Validator checks this exists.
        
        
        `program` -- web history program used to create file.
        
        
        `name` -- name of this data.
        
        
        `desc` -- optional description of data.
        
        
        `keepcsv` -- user chooses to keep the current file or upload another.
        
        
        `data` -- the new file if keepcsv is `False`.
    """
    group = All(GroupInDatabase(), v.Int(if_missing=None)) #check group is valid and of the current case
    data = UploadData()
    keepcsv = v.StringBoolean(if_missing=False)
    
    chained_validators = [
        RequireIfEquals('keepcsv', False, requireds=['data']),  #if not keeping the old data, then must upload new data
    ]

class wizard2_form(Schema):
    """
        Form to add multiple files.
        
        
        **Attributes**
        
        
        `csv_entry` -- list of `AddData` objects.
    """
    csv_entry = ForEach(AddData)

class edit2_form(Schema):
    """
        Form to edit multiple files. 
        
        
        **Attributes**
        
        
        `csv_entry` -- list of `EditData` objects.
    """
    csv_entry = ForEach(EditData)
    
# Form to load Sqlite file
# ========================

class load_form(Schema):
    """
        Form to load a case Sqlite database file.
        
        
        **Attributes**
        
        
        `case` -- the name of a case. Validator checks case exists on disk.
    """
    case = All(CheckCaseExists(not_empty=True)) # check case exists
    x = v.UnicodeString() # button
    y = v.UnicodeString() # button
    
    
# Forms to add new filter
# ========================

class Filter(Schema):
    """
        Represents one filter line. `add_filter_form` can have many filter lines. 
        
        
        **Attributes**
        
        
        `cls` -- The Class the filter applies to.
        
        
        `attribute` -- the Class's attribute the filter applies to.
        
        
        `function` -- the operation to do on the attribute.
        
        
        `value` -- the value the attribute will be compared with.
        
        
        `value_list` -- the file of items to compare the attribute to.
        
        
        Either `value` or `value_list` will be selected, the other will be `None`.
    """
    cls = CheckAllowedClass()
    attribute = v.UnicodeString()
    function = v.UnicodeString()
    value = StringNone()
    value_list = StringNone()
    
    chained_validators = [
        RequireIfEquals('value', None, requireds=['value_list']),
        RequireIfEquals('value_list', None, requireds=['value']),
        CheckAllowedAttributes(),
        CheckAllowedFunctions(),
        CheckAllowedValues()
    ]
    
class add_filter_form(Schema):
    """
        Form to add a filter.
        
        
        **Attributes**
        
        
        `filter` -- list of `Filter()`.
        
        
        `name` -- name of the filter.
    """
    filter = ForEach(Filter)
    name = v.UnicodeString(not_empty=True)
    