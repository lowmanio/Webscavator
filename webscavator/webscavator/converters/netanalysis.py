from csv_converter import CSVConverter
from datetime import datetime

class NetanalysisConverter(CSVConverter):
    """
        Converts Net Analysis CSV output to normalised format.
        
        
        To obtain CSV data from Net Analysis, click on `File > Export History As > Tab Delimited Text`.
        Rename the extension to `csv` instead of `txt`.
    """
    skip = 0
    delimiter = '\t'

    def process_row(self, row): 
        """
            `process_row` takes in a row from the CSV file, and returns a normalised dictionary as output.
            
            
            Net Analysis produces the same output regardless of what type of browser was used, 
            producing *a lot* of columns to process. One row of Fox Analysis CSV data looks like so:
            
            
           type, tag, last_visited_utc, access_time, hits, user, url, host, title, abs_path, query, 
           fragment, port, url_category, username, password, redirect_url, feed_url, referral_url, 
           favicon_url, cache_folder, cache_file, extension, length, exists, http_response, 
           cache_entry_type_flag, content_type, content_length, content_encoding, active_bias, 
           date_first_visited, date_expiration, modified_time, date_index_created, date_added, 
           date_last_sync, source_file, source_offset, index_type, browser_version, ie_type, status, 
           bookmark, urn
           
           .. Note::
               Net Analysis allows users to move columns around and export the data in it's new format.
               Currently this convertor assumes the columns are in the correct format and does not
               work when they are moved / there are less columns.
               
               **ToDo**: See if there is a work around for this.
        """   
         
        type, tag, last_visited_utc, access_time, hits, user, url, host, title, abs_path, query,\
        fragment, port, url_category, username, password, redirect_url, feed_url, referral_url,\
        favicon_url, cache_folder, cache_file, extension, length, exists, http_response, cache_entry_type_flag,\
        content_type, content_length, content_encoding, active_bias, date_first_visited, date_expiration,\
        modified_time, date_index_created, date_added, date_last_sync, source_file, source_offset,\
        index_type, browser_version, ie_type, status, bookmark, urn = row
        
        if modified_time:
            modified_time = datetime.strptime(modified_time,"%d/%m/%Y %H:%M:%S %a")
        else:
            modified_time = None
            
        if access_time: 
            access_time = datetime.strptime(access_time,"%d/%m/%Y %H:%M:%S %a")
        else:
            access_time = None

        if exists == "True":
            deleted = False
        elif exists == "False":
            deleted = True
        else:
            deleted = None
        
        browser = browser_version.split(' ')[0]
        if browser == "MSIE":
            browser = "Internet Explorer"
        
        return {
            'type': unicode(type, 'utf-8'), 
            'url': unicode(url, 'utf-8'), 
            'modified_time': modified_time,
            'access_time': access_time,
            'filename': unicode(abs_path, 'utf-8'), 
            'directory': None,
            'http_headers': unicode(http_response, 'utf-8'),
            'title': unicode(title, 'utf-8'),
            'deleted': deleted,
            'content_type': unicode(content_type, 'utf-8'),
            'browser_name': unicode(browser, 'utf-8'),
            'browser_version': None,
            'source_file': unicode(source_file, 'utf-8')
        }       
        
