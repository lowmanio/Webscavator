"""
    This is where all the unit and functional tests are kept. 
"""

import unittest
from webscavator.utils.utils import setup

test_units = [
    'unittests.test_validators',
    'unittests.test_forms',
    'unittests.test_models',
]

test_functions = [
    'functionaltests.test_caseController',
    'functionaltests.test_generalController',
    'functionaltests.test_visualController',
]

def getSuiteFromModule(name):
    return unittest.defaultTestLoader.loadTestsFromName('%s.%s' % (__name__, name))

def buildAppSuite(listname):
    suite = unittest.TestSuite()    
    for name in listname:
        suite.addTest(getSuiteFromModule(name))
    return suite

# This is for launch.py to run
def runTests(unittests=True, functionaltests=True):
    """
        Tests are run from :doc:`launch` by typing in the command line:
        
        ::
        
            python launch.py runtests 
            
    """

    if unittests:
        setup(True)
        suiteUnitTests = buildAppSuite(test_units)
        unittest.TextTestRunner(verbosity=2).run(suiteUnitTests)

    if functionaltests:
        setup(True)
        suiteFunctionalTests = buildAppSuite(test_functions)
        unittest.TextTestRunner(verbosity=2).run(suiteFunctionalTests)
