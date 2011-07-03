from csv_converter import CSVConverter
from datetime import datetime

class PascoConverter(CSVConverter):
    """
        Converts Pasco CSV output to normalised format.
        
        
        To obtain CSV data from Pasco run:
        
        ::
        
            pasco index.dat > output.csv
        
        
        This is tab delimited by default and has 3 lines at the top for titles and headers.
    """
    skip = 3
    delimiter = '\t'

    def process_row(self, row):        
        """
            `process_row` takes in a row from the CSV file, and returns a normalised dictionary as output.
            
            
            One row of Pasco CSV data looks like so:
            
            
            type, url, modified_time, access_time, filename, directory, http_headers
        """
        type, url, modified_time, access_time, filename, directory, http_headers = row

        if modified_time:
            modified_time = datetime.strptime(modified_time,"%m/%d/%Y %H:%M:%S")
        else:
            modified_time = None

        if access_time:
            access_time = datetime.strptime(access_time,"%m/%d/%Y %H:%M:%S")
        else:
            access_time = None

        return {
            'type': unicode(type, 'utf-8'), 
            'url': unicode(url, 'utf-8'), 
            'modified_time': modified_time,
            'access_time': access_time,
            'filename': unicode(filename, 'utf-8'), 
            'directory': unicode(directory, 'utf-8'),
            'http_headers': unicode(http_headers, 'utf-8'),
            'title': None,
            'deleted': None,
            'content_type': None,
            'browser_name': u"Internet Explorer",
            'browser_version': None,
            'source_file': None
        }