# python modules
import unittest
from datetime import datetime, time as d_time, timedelta
import time
# local models
from webscavator.model.models import *
from webscavator.model.filters import *
from webscavator.utils.utils import session
from webscavator.converters import get_name

class get_plotableTestCase(unittest.TestCase):
    def setUp(self):
        v = datetime.now()
        self.d = datetime(v.year, v.month, v.day, 0, 0, 0, 0) - timedelta(hours=1) 
        self.t = d_time(self.d.hour, self.d.minute, self.d.second, self.d.microsecond)
        self.u = "http://example.org"
        self.bn = "Firefox"
        self.bv = "3.0"
        self.bs = "places.sqlite"
        self.p = "netanalysis"
        self.ti = "Example.org"
        self.result = get_plotable(self.d, self.t, self.u, self.bn, self.bv, self.bs, self.p, self.ti)    
    def tearDown(self):
        self.result = self.d = self.t = None
    def testPlotable(self):
        unixepoch = float(self.result[0])/float(1000)
       
        self.assertEqual(self.result[0],time.mktime((self.d + timedelta(hours=1)).timetuple()) * 1000) # will break when GMT is fixed!
        self.assertEqual(self.result[1], float(self.t.hour) + self.t.minute/60.0 + self.t.second/3600.00)
        self.assertEqual(self.result[2], self.u)
        self.assertEqual(self.result[3], self.bn)
        self.assertEqual(self.result[4], self.bv)
        self.assertEqual(self.result[5], self.bs)
        self.assertEqual(self.result[6], get_name(self.p))
        self.assertEqual(self.result[7], self.ti)
        
        self.ti = None
        self.result = get_plotable(self.d, self.t, self.u, self.bn, self.bv, self.bs, self.p, self.ti)
        self.assertEqual(self.result[7], '--')
        
class BrowserTestCase(unittest.TestCase):
    def setUp(self):
        self.percent = Browser.getPercentages()
    def tearDown(self):
        self.percent = None
    def testgetPercentages(self):
        self.assertEqual(self.percent, [('Firefox', 1.0)])

class CaseTestCase(unittest.TestCase):
    def setUp(self):
        self.case = Case.get_case()
    def tearDown(self):
        self.case = None
    def testgetNewestEntry(self):
        entry = Case.getNewestEntry(self.case)
        d = datetime(2010, 8, 1)
        t = d_time(14, 8, 22)
        u = "http://en.wikipedia.org/w/index.php?title=Special:Search&search=Cryptography&go=Go"
        self.assertEqual(entry.access_date,d)
        self.assertEqual(entry.access_time,t)
        self.assertEqual(entry.url,u)
    def testgetOldestEntry(self):
        entry = Case.getOldestEntry(self.case)
        d = datetime(2010, 5, 1)
        t = d_time(16, 53, 24)
        u = "file:///C:/Documents%20and%20Settings/John/My%20Music/Anarchy%20in%20Tokyo%20+%20The%20Struggle%20-%2030%20Seconds%20To%20Mars.mp3"
        self.assertEqual(entry.access_date,d)
        self.assertEqual(entry.access_time,t)
        self.assertEqual(entry.url,u)  
    def testgetMinMax(self):
        date = datetime(2010, 6, 1)
        min_date = datetime(2010, 5, 1)
        max_date = min_date + timedelta(days=62)
        min, max = Case.getMinMax(date)
        
        self.assertEqual(min,time.mktime(min_date.timetuple()) * 1000)      
        self.assertEqual(max,time.mktime(max_date.timetuple()) * 1000) 
        

    def testfilter_queries(self):
        date = datetime(2010, 5, 1)
        q = session.query(Entry.url).join('browser').join('parsedurl').\
            join('group').outerjoin(Entry.search_terms).\
            filter(Entry.access_date==date)
        rem = FilterQuery()   
        rem.add_element('URL Parts','domain','Is','bbc.co.uk', None) 
        remove_funcs = [rem]
        high = FilterQuery()
        high.add_element('URL Parts','domain','Is','google.com',None) 
        highlight_funcs = [high]
        qrem, qhigh, qnot = Case.filter_queries(q, remove_funcs, highlight_funcs) 
        
        self.assertEqual(qrem.count(), 4)
        self.assertEqual(qhigh.count(), 10)
        self.assertEqual(qnot.count(), 15)  
        
    def testgetTimeGraph(self):
        startdate = datetime(2010, 5, 1)
        enddate = datetime(2010, 5, 1)
        starttime = d_time(0, 0, 0)
        endtime = d_time(23, 59, 59)
        rem = FilterQuery()   
        rem.add_element('URL Parts','domain','Is','bbc.co.uk', None) 
        remove_funcs = [rem]
        high = FilterQuery()
        high.add_element('URL Parts','domain','Is','google.com', None) 
        highlight_funcs = [high]
        qhigh, qnot, qrem = Case.getTimeGraph(startdate, enddate, starttime, endtime, 
                                              remove_funcs, highlight_funcs)
        for point in qrem, qhigh, qnot:
            self.assertEqual(point[0][0], time.mktime((startdate + timedelta(hours=1)).timetuple()) * 1000) 
            
        self.assertEqual(len(qhigh), 10)
        self.assertEqual(len(qnot), 15)
        self.assertEqual(len(qrem), 4)
        
              
class GroupTestCase(unittest.TestCase):
    def setUp(self):
        self.group = Group.get(1)
    def tearDown(self):
        self.group = None
    def testgetStartDate(self):
        date = datetime(2010, 5, 1).strftime("%I:%M%p %d %b %Y")
        startdate = self.group.getStartDate()
        self.assertEqual(date, startdate)
    def testgetEndDate(self):
        date = datetime(2010, 8, 1).strftime("%I:%M%p %d %b %Y")
        startdate = self.group.getEndDate()
        self.assertEqual(date, startdate)
    
class EntryTestCase(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass
    def testgenerateHeatMap(self):
        headers, table, high, low = Entry.generateHeatMap()
        self.assertEqual(high, 221)
        self.assertEqual(low, 0)
        self.assertEqual(table[0][1], [0,0,0,0,8,0,0])
        self.assertEqual(table[23][1], [122, 218, 139, 221, 0, 0, 0])
    def testaveragePages(self):
        average = Entry.averagePages()
        self.assertEqual(average, 15)
    def testpeakTime(self):
        peak = Entry.peakTime()
        self.assertEqual(peak, "23:00 - 23:59")
    def testfilesAccessed(self):
        drives, total = Entry.filesAccessed()
        self.assertEqual(total, 205)
        self.assertTrue('C' in drives)
        self.assertTrue('D' in drives)
        self.assertTrue('H' in drives)
        self.assertEqual(len(drives), 3)
        self.assertTrue('image' in drives['H'][0])
        self.assertEqual(len(drives['H'][0]), 1)
          
        
class URLTestCase(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass
    def testStaticMethods(self):
        pass
    def testTableLinks(self):
        pass
    
class FilterTestCase(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass
    def testStaticMethods(self):
        pass
    def testTableLinks(self):
        pass
    
if __name__ == "__main__":
    unittest.main()