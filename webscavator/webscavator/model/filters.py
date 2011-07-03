"""
    Filters
    -------
    
    
    `FilterQuery` objects save the filter details and are stored pickled in the `Filter` class as
    `Filter.query` in :doc:`models`. 
    
"""

from __future__ import with_statement

# python imports
import re
from os import path
# library imports
from sqlalchemy import and_, not_
# local imports
from webscavator.utils.utils import session, ROOT_DIR
from webscavator.model.models import *

def regexp(expr, item):
    """
        Enables regular expressions for filter queries.
    """
    r = re.compile(expr)
    return r.match(item) is not None            

class FilterQuery(object):
    """
        Stores the tables, attributes, operations and values of a query, e.g.
        
        ::
        
            params = (Entry, title, Is, 'Test') 
            
        which equates to `WHERE Entry.title = 'Test'` in SQL.
        
        
        `FilterQuery` objects get stored inside a `Filter` object in :doc:`models`. The
        object stored inside the `Filter` object gets pickled thereby preserving the
        filter information. 
    """
    
    classes = {'Browser': Browser,
               'URL Parts': URL,
               'Entry': Entry,
               'Web Files': Group,
               'Search Terms': SearchTerms 
               }
    
    def __init__(self):
        self.params = []
    
    def __repr__(self):
        return "[filter query object]"
    
    def add_element(self, cls, attr, func, val, val_list):
        """
            Add a new filter line to the `FilterQuery` object `params` list 
            attribute.
        """
        self.params.append((cls, attr, func, val, val_list))
        
    def query(self):
        """
            Called by `Case.filter_queries()` in :doc:`models` to construct the filter
            clause. Returns an ANDed list of filters e.g. `Entry.title = "test" AND
            Entry.url <> "http://example.org"`
        """
        conn = session.bind.connect()
        conn.connection.create_function("regexp", 2, regexp)
        
        ands = []
              
        for cls, attr, func, val, val_list in self.params:            
            table = self.classes[cls]
            opts = table.filter_options            
            column = getattr(table, attr)
            
            if val_list is not None:
                clause = self._operate(column, func, val_list)
            else:
                clause = self._operate(column, func, val)

            ands.append(column != None)
            ands.append(clause)
        return and_(*ands) if ands else None
    
    def _operate(self, col, op, val):
        """
            Returns the correct filter clause given the column to filter on, the value
            and the operator.
            
            .. Note::
            
                **ToDo**: 'Contains fuzzy' and 'Periodical every' are not yet functional and return
                `None`.
                
        """
        if op == "Is":
            return col == val
        elif op == "Is not":
            return col != val
        elif op == "Matches regular expression":
            return col.op('REGEXP')(val)
        elif op == "Contains fuzzy":
            return None
        elif op == "Contains":
            return col.like('%' + val + '%')
        elif op == "Greater than":
            return col > val
        elif op == "Less than":
            return col < val
        elif op == "Periodical every":
            return None
        elif op == "Is in list":
            return col.in_(self._getList(val))
        elif op == "Is not in list":
            return not_(col.in_(self._getList(val)))
        
    def _getList(self, name):
        """
            Given a file called `name`, return a list of the lines in the file. 
            Used when the filter is value IN [list]
        """
        with open(path.join(ROOT_DIR, '..','case lists',name),'r') as file:
            return [unicode(line.strip(), 'utf-8') for line in file.readlines()]
       
