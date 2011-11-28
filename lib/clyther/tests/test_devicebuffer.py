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
import unittest

from ctypes import c_float
from clyther import DeviceBuffer
import copencl as cl #@UnresolvedImport IGNORE:F0401
import numpy as np
import pdb
import clyther

class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testCopy(self):
        
        size = 32
#        devices = cl.get_devices(  'GPU' )
#        context = cl.Context( devices)

#        queue = cl.CommandQueue( context, context.devices[0] )

        host_buff = np.zeros( [size], dtype=np.float32 )
        host_buff[:] = np.random.ranf()
        
        host_buff_res = np.zeros( [size], dtype=np.float32 )
        
        buff2 = DeviceBuffer( [size], c_float, flags=cl.MEM.READ_WRITE  )
        
        buff2.from_host(  host_buff , block=True )
        buff2.to_host(  host_buff_res, block=True )
        
        self.failUnless(  np.alltrue( host_buff == host_buff_res) )
        


if __name__ == "__main__":
    
    clyther.init( 'gpu' )
    unittest.main()
    clyther.finish( )
    
