"""
    CSV Converters
    --------------
    
    
    Module contains abstract class that all web history programs that output CSV data must inherit from.
    
    All children must return in `process_row(row)`:
        
    ::
        
        return {
            'type': type of entry, 
            'url': URL entry, 
            'modified_time': modified time of entry,
            'access_time': access time of entry,
            'filename': entry file name, 
            'directory': entry directory,
            'http_headers': HTTP headers of entry,
            'title': entry page title,
            'deleted': if entry is deleted,
            'content_type': entry content type,
            'browser_name': browser used, one of 'Firefox', 'Internet Explorer', 'Safari', 'Chrome', 'Opera',
            'browser_version': browser version,
            'source_file': profile or location/name of file
        }  
        
    All entries in the dictionary may be `None` apart from `url` and `access_time`.
"""
import csv

class CSVConverter(object):
    """
    
    Children classes must override delimiter and skip:
    
    `delimiter`
        the CSV file delimiter.
    
    `skip`
        how many lines to skip at the top of the CSV file (including header lines).
    """
    
    delimiter = None
    skip = 0
    
    def __init__(self, csv_file):
        """
            Constructor takes in a CSV file. 
        """
        self.csv_file = csv_file
    
    def process(self):
        """
            Reads in the CSV file, skips `skip` number of lines and then for each line in the CSV file calls
            `self.process_row()` in the child class.
            
            Returns a generator which can be looped over to get the normalised row.
        """
        self.csv_file.seek(0) # rewind to beginning
        csvreader = csv.reader(self.csv_file, delimiter=self.delimiter)
        
        
        for _ in xrange(self.skip):
            csvreader.next()

        for row in csvreader:
            try:
                yield self.process_row(row)
            except Exception, e:
                yield e

        