"""
    Forms and Validators
    --------------------
    
    Forms and Validators use the `FormEncode library <http://formencode.org/>`_.
    
    
    Every HTML form in Webscavator is validated using :doc:`forms` and :doc:`validators`. Form
    data is kept in `self.request.form`, e.g.:
    
    ::
    
        request.form['date'] = '1/1/2010'
    
    
    Each endpoint that wants to validate a form 
    calls `self.validate_form(schema)` defined in :doc:`baseController`, where `schema` is one of the 
    classes in :doc:`forms`. 
    
    
    The data is validated according to the schemas validators, most
    of which come from FormEncode, but others are defined in :doc:`validators`. If there is an error,
    the validator will raise an exception which gets stored in `self.form_errors`, a dictionary
    of form names and their error messages, e.g.:
    
    ::
        
        form_errors['date'] = "The date must be in dd/mm/yyyy format."
        
    
    If there are no errors, `self.form_result` gets populated with the validated results, e.g.:
    
    ::
    
        form_result['date'] = datetime(2010, 1, 1)
"""