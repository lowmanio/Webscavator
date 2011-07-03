from xml_converter import XMLConverter
from datetime import datetime
import urllib

class WebhistorianConverter(XMLConverter):
    """
        Converts Web Historian XML output to normalised format. The toplevel element for a web history
        entry is `UrlHistoryItem`.
    """
    
    topelement = "UrlHistoryItem"

    def process_element(self, data):   
        """
            `process_row` takes in an xml element that contains one web history entry, 
            and returns a normalised dictionary as output.
        """  
         
        url = urllib.unquote(data.findtext('URL'))
        type = data.findtext('VisitType')
        access_time = data.findtext('LastVisitDate')
        browser = data.findtext('BrowserName')
        version = data.findtext('BrowserVersion')
        source_file = data.findtext('Profile')
        
        try:
            title = unicode(data.findtext('PageTitle'), 'utf-8')
        except Exception:
            title = None
        
        if access_time: 
            access_time = datetime.strptime(access_time[:-6],"%Y-%m-%dT%H:%M:%S") 
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
            'title': title,
            'deleted': None,
            'content_type': None,
            'browser_name': unicode(browser, 'utf-8'),
            'browser_version': unicode(version, 'utf-8'),
            'source_file': unicode(source_file, 'utf-8')
        }  
