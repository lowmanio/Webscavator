"""
    Each class validates a certain field or group of fields within a form. 
    
    If the field(s) have errors, the validator will throw an `Invalid` exception and add the 
    name of the form field and the error message to a dictionary, which is passed back to the 
    web page for the user to correct. 
    
    If the field is valid, the validator will return the value. 
    The validators may also process the value
    and return the processed value, e.g. the value is a Case id, and the processor returns the 
    Case object.  
    
    .. note::
        Most of these forms were created before it was realised that files other than CSV were needed
        (such as XML). 
        Therefore a lot of form field names are 'csv_file' rather than just generic 'file'. Also, since
        XML (and any other added convertor) files are allowed, the uploaded file is no longer checked
        to see if it ends with CSV. This should be fixed to check against the type of file it expects.
        
        **ToDo**: Change any field names that refer to csv data to be more generic. Applies to Mako
        templates too.  
        
        **ToDo**: Validate the uploaded data against what it should be. E.g Webscavator = XML and 
        Net Analysis = CSV. PErhaps add a column to `program_lookup` or `program_info` in 
        :doc:`converters`. 
        
        **ToDo**: Add more checks for duplication, e.g. not allowing groups or filters with same name.
"""

# python imports
import operator
from os import path
import datetime
# library imports
from formencode import validators as v, Invalid
from formencode.compound import CompoundValidator
# local imports
from webscavator.model.models import *
from webscavator.utils.utils import ROOT_DIR, CASE_FILE_DIR, getCases
from webscavator.converters import get_names, convert_file, get_program



# Validators over lists of entries
# ===================================
class NoDuplicates(v.FancyValidator):
    """ 
        Checks there are no duplicates in the inputed list.
    """
    messages = {
        'invalid': 'You selected the same value more than once.'
    }
    key = None
    def _to_python(self, value, state):
        errors = []
        seen = set()
        seen_error = False
        for val in value:
            # Are we dealing with a dictionary value that should be indexed?
            if self.key is not None:
                val = val[self.key]

            if val in seen:
                seen_error = True
                if self.key is None:
                    errors.append(Invalid(self.message('invalid', state), value, state))
                else:
                    # If value is a dictionary, add the error to the dictionary field rather than
                    # the whole list item.
                    errors.append(Invalid('', value, state, error_dict={self.key: self.message('invalid', state)}))
            else:
                errors.append(None)
                seen.add(val)
        
        if seen_error:
            raise Invalid('', value, state, error_list=errors)
        return value

class RemoveEmpties(v.FancyValidator):
    """ 
        Removes empty items from a list.
    """
    key = None
    def _to_python(self, value, state):
        if self.key is None:
            return [item for item in value if item]
        else:
            # If item is a dictionary, check the required dictionary key.
            return [item for item in value if item[self.key]]
    
class CheckHasItems(v.FancyValidator):
    """ 
        Checks the value is not empty / `None` / `false` etc. 
    """
    messages = {
                'invalid': 'Please select an item.'
    }
    def _to_python(self, value, state):
        if value:
            return value
        else:
            raise Invalid(self.message('invalid', state), value, state)

# for chained validators over the whole form or partial form
# ===========================================================
  
class RequireIfCondition(v.FormValidator):
    """ 
        `RequireIfCondition` requires 'requireds' fields if 'field' [condition] 'value'. [condition] is 
        defined by `RequireIfCondition`'s children as can be equals or not equals.
        
        
        E.g. if a user selects the option 'other' in a select box, then it is required that they
        fill in a value in a text input called 'Other'.
    """
    __unpackargs__ = ('field', 'value')
    requireds = None
    validate_partial_form = True
    condition = None
    allow_null = True    
    error_message = 'Please enter a value'
    
    def validate_partial(self, vals, state):
        self.validate_python(vals, state)
    
    def validate_python(self, vals, state):
        if self.condition(vals.get(self.field), self.value):
            errors = {}
            for f_name in self.requireds:
                if vals.get(f_name) in ('', None, []) or (not self.allow_null and vals.get(f_name) == 'null'):
                    errors[f_name] = self.error_message
            if errors:
                raise Invalid('', vals, state, error_dict=errors)

class RequireIfEquals(RequireIfCondition):
    """
        Child of `RequireIfCondition`, the condition is `==`
    """
    condition = operator.eq

class RequireIfNotEquals(RequireIfCondition):
    """
        Child of `RequireIfCondition`, the condition is `!=`
    """
    condition = operator.ne

class ValidCSVData(v.FormValidator):
    """
        Checks that the data in a CSV file can be processed correctly
    """
    def validate_partial(self, vals, state):
        self.validate_python(vals, state)
    
    def validate_python(self, vals, state):
        program = vals.get('program')
        file = vals.get('data')
        
        guidelines_url =  state.urls.build('general.guidelines', {})
        
        if program and file:
            for d in convert_file(get_program(program), file): 
                if isinstance(d, Exception):
                    raise Invalid('', vals, state, error_dict={'data': 
                    'There was an error processing the file. Please follow the \
                    <a href="javascript:popUp(\'' + guidelines_url + '\')">guidelines</a> [pop-up]'})
    

# Specific Validators
# ====================
 
class NonAscii(v.FancyValidator):
    """
        Checks value is alpha numeric. 
    """
    messages = {
                'invalid': 'Please remove any spaces and non ASCII characters.'
    }
    def _to_python(self, value, state):
        if not value.isalnum():
            raise Invalid(self.message('invalid', state), value, state)
        return value
    
    
class StringNone(v.FancyValidator):
    """
        Checks to see if value has a string value 'None', if so, convert this to a Python
        `None`.
    """
    messages = {
                'invalid': 'The text you have entered is invalid'
    }
    def _to_python(self, value, state):
        if value == "None":
            return None
        else:
            return value

class NotInDatabase(v.FancyValidator):
    """
        Checks the data supplied is not already in database when adding a new object. 
        If editing an object, then it will already be in the database, so must supply 
        `currentObj` in `state`. If they match then allowed.
        
        
        `state` is a `FormState` object which is populated in `validate_form` in
        :doc:`baseController`.
    """
    messages = {
        'duplication': 'This has already been used',
    }
    strip = True
    not_empty = True
    
    def _to_python(self, value, state):
        obj =  v.UnicodeString().to_python(value, state)
        
        if self.valueNotAllowed(obj):
            raise Invalid(self.message('duplication', state), value, state) 
        
        d = self.checkDuplicates(obj, state)
        if d:
            # entry in database
            if state.obj:
                if state.obj.id != d.id:
                    # entry in database does not match current object we are editing
                    raise Invalid(self.message('duplication', state), value, state) 
                else:
                    # entry in database matches current object we are editing
                    return obj
            else:
                raise Invalid(self.message('duplication', state), value, state) 
        else:
            # no entry, allowed to have value
            return obj
    
    def valueNotAllowed(self, obj):
        """ 
            Override to check if values are not in a list of disallowed values.
        """
        return False  

class CheckCaseDoesntExist(v.FancyValidator):
    """
        Checks that case database files do not already exist on disk.
    """
    messages = {
        'duplication': 'This database file has already been used',
    }
    
    def _to_python(self, value, state):
        if path.exists(path.join(CASE_FILE_DIR, value + ".db")):
            raise Invalid(self.message('duplication', state), value, state)
        else:
            return value + ".db"
        
class CheckCaseExists(v.FancyValidator):
    """
        Checks that case database files does exist.
    """
    messages = {
        'invalid': 'You have chosen a case that does not exist',
    }
    
    def _to_python(self, value, state):    
        cases = getCases()
        if value not in cases:
            raise Invalid(self.message('invalid', state), value, state)
        else:
            return value 
         
        
class GroupInDatabase(v.FancyValidator):
    """
        Checks that when editing a group of data, that the group is the correct one.
    """
    messages = {
        'invalid': 'An invalid id for these web browser files has been given',
    }
    
    def _to_python(self, value, state):    
        if value is None:
            return None
        g = Group.get(value)
        if g and g.case.id == state.case.id:
            return g
        else:
            raise Invalid(self.message('invalid', state), value, state)
           
        
# Only allow set of predefined values
# ===================================
class CheckAllowed(v.FancyValidator):
    """
        Check the value is within a set of predefined values.
    """
    values = []

    def _to_python(self, value, state):   
        if value not in self.values:
            raise Invalid(self.message('invalid', state), value, state)
        else:
            return value

   
class CheckAllowedProgram(CheckAllowed):
    """
        Checks that the web history program selected is within a set of predefined programs.
    """
    messages = {
        'invalid': 'You have chosen an invalid program',
    }
    
    values = get_names()
    
    
class CheckAllowedClass(CheckAllowed):
    """
        Checks to see if the class is one of a predefined set of allowed classes.
    """
    messages = {
        'invalid': 'You have chosen an invalid selection',
    }
    
    values = ['Browser','URL Parts', 'Entry','Web Files','Search Terms'] 
        
class CheckAllowedAttributes(v.FormValidator):
    """
        Checks that the attribute belongs to the class in the same filter.
    """
    def validate_partial(self, vals, state):
        self.validate_python(vals, state)
    
    def validate_python(self, vals, state):
        cls = vals.get('cls')
        attr = vals.get('attribute')
        
        classes = {'Browser' :Browser,
                   'URL Parts':URL,
                   'Entry': Entry,
                   'Web Files': Group,
                   'Search Terms': SearchTerms 
                   }
        
        if cls and attr and classes.get(cls) is not None:
            opts = classes.get(cls).filter_options

            found = False
            for name, opt in opts.iteritems():
                if attr == opt[0]:
                    vals['attribute'] = name
                    return            
            raise Invalid('', vals, state, error_dict={'data': 'You have chosen an invalid selection'})
        else:
            raise Invalid('', vals, state, error_dict={'data': 'You have chosen an invalid selection'})
        
        
class CheckAllowedFunctions(v.FormValidator):
    """
        Checks that the operation is allowed on the attribute in the same filter.
    """
    def validate_partial(self, vals, state):
        self.validate_python(vals, state)
    
    def validate_python(self, vals, state):
        cls = vals.get('cls')
        attr = vals.get('attribute')
        func = vals.get('function')

        classes = {'Browser' :Browser,
                   'URL Parts':URL,
                   'Entry': Entry,
                   'Web Files': Group,
                   'Search Terms': SearchTerms  
                   }
        
        if cls and attr and func and classes.get(cls) is not None:
            opts = classes.get(cls).filter_options
            
            if attr in opts:
                if func not in opts[attr][1]:
                    raise Invalid('', vals, state, error_dict={'data': 'You have chosen an invalid selection'})            
        else:
            raise Invalid('', vals, state, error_dict={'data': 'You have chosen an invalid selection'})
 
 
class CheckAllowedValues(v.FormValidator):
    """
        Checks that the value is allowed for the attribute in the same filter. 
    """
    def validate_partial(self, vals, state):
        self.validate_python(vals, state)
    
    def validate_python(self, vals, state):
        cls = vals.get('cls')
        attr = vals.get('attribute')
        func = vals.get('function')
        value = vals.get('value')

        classes = {'Browser' :Browser,
                   'URL Parts':URL,
                   'Entry': Entry,
                   'Web Files': Group,
                   'Search Terms': SearchTerms  
                   }
        
        if value == None:
            return value
        if cls and attr and func and value and classes.get(cls) is not None:
            opts = classes.get(cls).filter_options
            
            if attr in opts:
                opt = opts[attr]
                callback = opt[2]
                type = opt[3]
                        
            if type is None:
                raise Invalid('', vals, state, error_dict={'data': 'You have chosen an invalid selection'})
            else:
                if type == "select":
                    vals = [getattr(obj, attr) for obj in callback().group_by(attr).all() \
                            if getattr(obj, attr) is not None and getattr(obj, attr) != '']
                    if value not in vals:
                        raise Invalid('', vals, state, error_dict={'data': 'You have chosen an invalid selection'})
                elif type == "date":
                    vals['value'] = v.DateConverter(month_style='dd/mm/yyyy').to_python(value, state)
                elif type == "time":
                    vals['value'] = datetime.time(*v.TimeConverter(use_seconds=True).to_python(value, state))
                elif type == "number":
                    vals['value'] = v.Int().to_python(value, state)
                else:
                    vals['value'] = v.UnicodeString().to_python(value, state)
        else:
            raise Invalid('', vals, state, error_dict={'data': 'You have chosen an invalid selection'})
                
# Validators for uploading data
# =================================            

class File(v.FancyValidator):
    """
        Checks whether an uploaded file is empty or not.
    """
    def is_empty(self, value):
        return not bool(getattr(value, 'filename', None))

class Upload(File):
    """
        Upload a file. The value returned is the file stream.
    """
    type = None   # type of file 
    
    def _to_python(self, value, state):
        
        """
        if not (self.type in value.content_type or value.filename.rsplit('.', 1)[-1] == self.type):
            print value, value.content_type, value.filename, "$" * 100
            raise Invalid(self.message('invalid', state), value, state)
        """ 
        return value
    
class UploadData(Upload):
    """ 
        Checks the file uploaded is a CSV file.
    """
    messages = {
        'invalid': 'You did not upload a CSV file'
    } 
    type = 'csv'
