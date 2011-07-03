"""
    XML Convertors
    --------------
    
    Module contains abstract class that all web history programs that output XML data must inherit from.
    
    All children must return in `process_element(row)`:
        
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

from xml.etree import ElementTree

class XMLConverter(object):
    """
    """

    def __init__(self, xml_file):
        """
            Constructor takes in a XML file.
        """
        self.xml_file = xml_file
    
    def process(self):
        """
            Reads in the XML file. Finds all the top level web history elements and 
            returns a generator which can be looped over to get the normalised element entries.
        """
        self.xml_file.seek(0)
        xmlreader = ElementTree.parse(self.xml_file)
        for row in xmlreader.findall(self.topelement):
            try:
                yield self.process_element(row)
            except Exception, e:
                yield e
                    
                

        