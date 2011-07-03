#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Copyright (C) 2010 Sarah Lowman
    
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
     
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
     
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
    
        
    Starting Webscavator
    --------------------
    
    To start webscavator:
    
    ::
    
        > python launch.py runserver
    
    
    Then go to your preferred web browser and go to http://localhost:5000
"""
 
import sys, os
from werkzeug import script

sys.path.append('webscavator')

def make_app():
    """
        Runs webscavator. First runs `setup()` in :doc:`utils` 
        which loads the configuration file, and 
        then runs `make_app()` in :doc:`application`.
    """
    import webscavator.utils.utils
    webscavator.utils.utils.setup()
    from webscavator.application import make_app
    return make_app()

action_runserver = script.make_runserver(make_app, use_reloader=True)
action_shell = script.make_shell(lambda: {'app': make_app()})


def action_runtests(functional=False, unit=False):
    """ 
        Run tests by first calling `setup()` in :doc:`utils` and then `runTests(unit, functional)` in 
        :doc:`testing` 
    """
    if not (functional or unit):
        functional = unit = True

    import webscavator.utils.utils
    webscavator.utils.utils.setup()
    import webscavator.test
    webscavator.test.runTests(unit, functional)
    
if __name__ == '__main__':
    script.run()
