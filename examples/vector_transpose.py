'''
Created on Apr 13, 2010 by GeoSpin Inc
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

import clyther
from clyther.vector_types import float16,float4
import copencl as cl
from clyther.api.cltypes import cltype
import numpy as np
#from clyther.static import finish

clyther.init('gpu')


@clyther.task
def transpose( m ):
    """
    transpose a 4x4 matrix
    """
    
    t = float16()
    
    x = float16( m[0], m[1], m[2], m[3] )
    
    t.even = x.lo
    t.odd = x.hi
    x.even = t.lo
    x.odd = t.hi
    
    #write back 
    m[0] = x.lo.lo 
    m[1] = x.lo.hi
    m[2] = x.hi.lo
    m[3] = x.hi.hi
    

flags = cl.MEM.COPY_HOST_PTR | cl.MEM.READ_WRITE 

clbuff = clyther.DeviceBuffer( [4], clyther.float4, flags=flags, 
                               host_buffer=np.arange( 16, dtype=np.float32) )

transpose(  clbuff )

with clbuff as hostbuff:
    
    host = (float4*4).from_buffer( hostbuff )
    
    print "OpenCL Transpose "
    print "=================="
    print host[0]
    print host[1]
    print host[2]
    print host[3]
    
    clyther.emulate( transpose, host )
    print
    print
    print "Python Transpose back"
    print "====================="
    
    print host[0]
    print host[1]
    print host[2]
    print host[3]

