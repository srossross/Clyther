'''

not sure this will be used

Created on Mar 15, 2010 by GeoSpin Inc
@author: Sean Ross-Ross srossross@geospin.ca
website: www.geospin.ca
'''
from clyther.memory import array_type
from ctypes import c_int
from clyther.runtime import cl_size_t


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



class opencl_iterator(object): pass


class range(opencl_iterator):
    @classmethod 
    def get_restype( cls, *args):
        return cl_size_t
    

int = int
float = float

class gentype( object ):
    pass

from clyther.clmath import fabs as abs
from clyther.clmath import round
from clyther.clmath import fmax as max
from clyther.clmath import fmin as min

