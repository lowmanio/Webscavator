from csv_converter import CSVConverter
from datetime import datetime

class FoxanalysisConverter(CSVConverter):
    """
        Converts Fox Analysis CSV output to normalised format.
        
        
        To obtain CSV data from Fox Analysis click on `File > Export to > CSV File`. Please load in 
        the `Website.csv` file produced. 
        
        
        This is comma delimited by default and has 1 line at the top for titles and headers.
    """
    skip = 1
    delimiter = ','

    def process_row(self, row):        
        """
            `process_row` takes in a row from the CSV file, and returns a normalised dictionary as output.
            
            
            One row of Fox Analysis CSV data looks like so:
            
            
            id, fromvisit, datevisited, url, host, totalvisitcount, type, frecency, title
            
        """
        
        # id, fromvisit, datevisited, url, host, totalvisitcount, type, frecency, title = row
        
        datevisited = row[2]
        url = row[3]
        type = row[6]
        title = "".join(row[8:]) # needs to be done like this because occasionally you will get titles that
                                 # contain "'s in them and ,'s which will not parse correctly, making it
                                 # look like there are more fields in the row than there actually are. 
                                 # This recombines any fields which have been separated because of this. 
        
        if datevisited:
            access_time = datetime.strptime(datevisited,"%d/%m/%Y %H:%M:%S")
        else:
            access_time = None

        return {
            'type': unicode(type, 'utf-8'), 
            'url': unicode(url, 'utf-8'), 
            'modified_time': None,
            'access_time': access_time,
            'filename': None, 
            'directory': None,
            'http_headers': None,
            'title': unicode(title, 'utf-8'),
            'deleted': None,
            'content_type': None,
            'browser_name': u"Firefox",
            'browser_version': None,
            'source_file': None            
        }
        