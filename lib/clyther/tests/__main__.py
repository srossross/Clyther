'''
Created on Apr 2, 2010 by GeoSpin Inc
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

from __init__ import main 
import sys
from os.path import dirname

def test_harnes( ):
#    pdb.set_trace()
    # returns "/path/to/" from  file name "/path/to/clyther/tests/__main__.py"
    clyther_path = dirname(dirname(dirname( __file__ )))
    
    sys.path.insert(0, clyther_path )
    
    import clyther
    
    if clyther.__path__[0] not in __file__:
        raise Exception("clyther import does not match the path of this test file") 


if __name__ == '__main__':
    test_harnes( )
    main( )
