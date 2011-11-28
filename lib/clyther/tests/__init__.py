'''
Created on Mar 5, 2010 by GeoSpin Inc
@author: Sean Ross-Ross srossross@geospin.ca
website: www.geospin.ca
'''


#================================================================================#
# Copyright 2009 GeoSpin Inc.                                                     #
#                                                                                # 
# Licensed under the Apache License, Version 2.0 (the "License");                #
# you may not use this file except in compliance with the License.               #
# You may obtain a copy of the License at                                        #
#                                                                                #
#      http://www.apache.org/licenses/LICENSE-2.0                                #
#                                                                                #
# Unless required by applicable law or agreed to in writing, software            #
# distributed under the License is distributed on an "AS IS" BASIS,              #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.       #
# See the License for the specific language governing permissions and            #
# limitations under the License.                                                 #
#================================================================================#


from unittest import findTestCases,TextTestRunner,TestSuite
from glob import glob
from os.path import dirname,join,split,splitext
import sys
import pdb



if __package__:
    #run from clyther.test()
    split_mod = lambda mfile: ("%s.%s" %(__package__,splitext(split(mfile)[1])[0]),splitext(split(mfile)[1])[0])
else:
    #run from command line
    split_mod = lambda mfile: ("%s" %(splitext(split(mfile)[1])[0]),splitext(split(mfile)[1])[0])
    

    #check that this is the local version

def get_modules():
    """
    Returns all of the test modules in the clyther.tests package.
    """
    mod_files = glob( join( dirname( __file__ ), "test_*" ) )
    module_names = [ split_mod(mfile) for mfile in mod_files ]
    
    
    _modules = {}
    modules = {}
    
    for mod,name in  module_names:
        statement = "import %s as %s" %(mod,name)
        exec statement in _modules
        modules[name] = _modules[name]
    
#    print "modules",modules.keys()
    return modules.values()

def additional_tests():
    
    import clyther
    clyther.init('gpu')
    
#    pdb.set_trace()
    modules = get_modules()
    suite = TestSuite( [ findTestCases(mod) for mod in modules ] )
    return suite 

def set_device_type( dist, attr, value ):
    print "set_device_type", attr, value
    
def main( ):
    
    suite = additional_tests()
    runner = TextTestRunner(sys.stdout, descriptions=2, verbosity=2)

    return runner.run( suite )
    


