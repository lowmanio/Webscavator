from csv_converter import CSVConverter
from datetime import datetime

class ChromecacheviewerConverter(CSVConverter):
    """
        Converts Chrome Cache Viewer CSV output to normalised format.
        
        To obtain CSV data from Chrome Cache Viewer, select all the entries, and go to `File >
        Save Selected Items`. Save as a *Tab-delimited Text File*, and then change the extension to 
        `csv`. Make sure the file is in UTF-8 encoding, otherwise the CSV converter will throw
        an exception. 
    """
    skip = 0
    delimiter = '\t'

    def process_row(self, row):        
        """
            `process_row` takes in a row from the CSV file, and returns a normalised dictionary as output.
            
            
            One row of Chrome Cache Viewer's CSV data looks like so:
            
        
            filename, url, content_type, file_size, access_time, server_time, modified_time, expired_time, 
            server_name, http_headers, content_encoding, cache_name, cache_control, e_tag, _ 
            
        """
        filename, url, content_type, file_size, access_time, \
        server_time, modified_time, expired_time, server_name, http_headers,\
        content_encoding, cache_name, cache_control, e_tag, _ = row

        if modified_time: 
            modified_time = datetime.strptime(modified_time,"%d/%m/%Y %H:%M:%S")
        else:
            modified_time = None

        if access_time:
            access_time = datetime.strptime(access_time,"%d/%m/%Y %H:%M:%S")
        else:
            access_time = None

        return {
            'type': None, 
            'url': unicode(url, 'utf-8'), 
            'modified_time': modified_time,
            'access_time': access_time,
            'filename': unicode(filename, 'utf-8'), 
            'directory': None,
            'http_headers': unicode(http_headers, 'utf-8'),
            'title': None,
            'deleted': None,
            'content_type': unicode(content_type, 'utf-8'),
            'browser_name': u"Chrome",
            'browser_version': None,
            'source_file': None
        }