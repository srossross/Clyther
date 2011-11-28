'''
Created on Mar 22, 2010 by GeoSpin Inc
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

import copencl as cl
import clyther
from clyther import runtime as clrt

import numpy as np

#===============================================================================
# Set the emulation mode
# Don't need to Setup C/OpenCL
#===============================================================================
clyther.init( 'EMULATE' )

#===============================================================================
# Un-comment this line to run on GPU
# clrt = clyther.init( 'GPU' )
#===============================================================================

#===============================================================================
# Can not use Contexts,Queues or devices (yet) 
# Eventually want to do emulation with CPU clEnqueueNativeKernel I can not seem to get it to work    
#===============================================================================
#devices = cl.get_devices( 'GPU' )
#context = cl.Context( [devices[0]]) #use only one gpu unit
#queue = cl.CommandQueue( context, context.devices[0] ) 

@clyther.kernel
@clyther.bind('global_work_size' ,'a.size')
@clyther.bind('local_work_size' ,'a.size')
def foobar( a , x ,y ):
    
    gid = clrt.get_global_id( 0 )

    loc = a[gid]
    b = x-y
    a[gid] = loc + b
    
#===============================================================================
# Allocate memory on host only
#===============================================================================
size = 16
host_result = np.zeros( [size], dtype=np.float32 )
buffer = np.zeros( [size], dtype=np.float32 )

foobar( buffer, 3.0, .3 )
foobar( buffer, 1, .7 )

print 
print "result should be an array of sixteen three's"
print "#==============================================================================="
print "result",buffer
print "#==============================================================================="

