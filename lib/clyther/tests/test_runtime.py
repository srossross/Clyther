'''
Created on Mar 05, 2010 by GeoSpin Inc
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

import copencl as cl #@UnresolvedImport
import clyther
from clyther import runtime as clrt
from ctypes import c_int32
import pdb

from numpy import all as np_all #@UnresolvedImport
from numpy import int32 as np_int32 #@UnresolvedImport
from numpy import zeros as np_zeros #@UnresolvedImport
@clyther.kernel
def dev_test_sizes( a ):
    
    gid = clrt.get_global_id( 0 )
    
    gsize = clrt.get_global_size( 0 )
    lsize = clrt.get_local_size( 0 )
    nsize = clrt.get_num_groups( 0 )
    
    if gid==0: 
        a[0] = gsize 
        a[1] = lsize 
        a[2] = nsize 
        
@clyther.kernel
def dev_test_local_id( a ):
    
    gid = clrt.get_global_id( 0 )
    id = clrt.get_local_id( 0 )
    a[gid] = id 


@clyther.kernel
def dev_test_global_id( a ):
    
    id = clrt.get_global_id( 0 )
    a[id] = id 

@clyther.kernel
def dev_test_group_id( a ):
    
    gid = clrt.get_global_id( 0 )
    id = clrt.get_group_id( 0 )
    a[gid] = id 





#devices = cl.get_devices( 'GPU' )
#context = cl.Context( [devices[0]] )
#queue = cl.CommandQueue( context, context.devices[0] )





class Test(unittest.TestCase):


    def setUp(self):
        self.size = 32
        self.intarray = c_int32*self.size

    def tearDown(self):
        pass


    def test_get_local_id(self):
        "runtime: Checking get_local_id"
        
        size = 32

        host_buffer1 = np_zeros( [size], dtype=np_int32 )
        host_buffer2 = np_zeros( [size], dtype=np_int32 )
        
        device_buffer1 = clyther.DeviceBuffer( [size], c_int32, cl.MEM.READ_WRITE )
        
        
        for local_work_size in [1,2,4,8,32]:
            
            dev_test_local_id( device_buffer1, global_work_size=size, local_work_size=local_work_size )
            
            device_buffer1.to_host( host_buffer1, block=True )
            
            clyther.emulate(dev_test_local_id, host_buffer2, 
                            global_work_size=size, local_work_size=local_work_size )
            
            assertion = np_all( host_buffer1 == host_buffer2 )
            
            self.failUnless(assertion)

    def test_get_global_id(self):
        "runtime: Checking get_global_id"
        
        size = 32

        host_buffer1 = np_zeros( [size], dtype=np_int32 )
        host_buffer2 = np_zeros( [size], dtype=np_int32 )
        
        device_buffer1 = clyther.DeviceBuffer( [size], c_int32, cl.MEM.READ_WRITE )
        
        
        for local_work_size in [1,2,4,8,32]:
            
            dev_test_global_id( device_buffer1, global_work_size=size, local_work_size=local_work_size )
            
            device_buffer1.to_host( host_buffer1, block=True )
            
            clyther.emulate(dev_test_global_id, host_buffer2, 
                            global_work_size=size, local_work_size=local_work_size )
            
            assertion = np_all( host_buffer1 == host_buffer2 )
            
            self.failUnless(assertion)

    def test_get_group_id(self):
        "runtime: Checking get_group_id"
        
        size = 32

        host_buffer1 = np_zeros( [size], dtype=np_int32 )
        host_buffer2 = np_zeros( [size], dtype=np_int32 )
        
        device_buffer1 = clyther.DeviceBuffer( [size], c_int32, cl.MEM.READ_WRITE )
        
        
        for local_work_size in [1,2,4,8,32]:
            
            dev_test_group_id( device_buffer1, global_work_size=size, local_work_size=local_work_size )
            
            device_buffer1.to_host( host_buffer1, block=True )
            
            clyther.emulate(dev_test_group_id, host_buffer2, 
                            global_work_size=size, local_work_size=local_work_size )
            
            assertion = np_all( host_buffer1 == host_buffer2 )
            
            self.failUnless(assertion)


    def test_get_sizes(self):
        "runtime: Checking get_local_size get_global_size and get_num_groups"
        
        size = 3

        host_buffer1 = np_zeros( [size], dtype=np_int32 )
        host_buffer2 = np_zeros( [size], dtype=np_int32 )
        
        device_buffer1 = clyther.DeviceBuffer( [size], c_int32, cl.MEM.READ_WRITE )
        
        
        for local_work_size in [1,2,4,8,32]:
            
            dev_test_sizes( device_buffer1, global_work_size=32, local_work_size=local_work_size )
            
            device_buffer1.to_host( host_buffer1, block=True )
            
            clyther.emulate(dev_test_sizes, host_buffer2, 
                            global_work_size=32, local_work_size=local_work_size )
            
            
            assertion = np_all( host_buffer1 == host_buffer2 )
            
            self.failUnless( assertion ,"%s != %s"%(host_buffer1, host_buffer2))

if __name__ == "__main__":
    clyther.init( 'gpu' )
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main( )
    
    clyther.finish( )
    
    
