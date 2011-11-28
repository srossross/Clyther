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

import copencl as cl
import clyther
from ctypes import c_float
from clyther import runtime as clrt
from clyther.memory import global_array_type
import numpy as np
import pdb

    
@clyther.kernel
@clyther.bind('global_work_size' ,'a.size')
@clyther.bind('local_work_size' ,'a.size')
def foobar( a , x ,y ):
    
    gid = clrt.get_global_id( 0 )
    
    loc = a[gid]
    b = x-y
    a[gid] = loc + b

@clyther.kernel
@clyther.bind('global_work_size' ,'a.size')
@clyther.bind('local_work_size' , 1)
def zeros(a):
    i = clrt.get_global_id(0)
    a[i] = 0


#===============================================================================
# Setup OpenCL
#===============================================================================
clyther.init('GPU')
devices = cl.get_devices( 'GPU' )
context = cl.Context( [devices[0]]) #use only one gpu unit
queue = cl.CommandQueue( context, context.devices[0] ) 



#===============================================================================
# Allocate memory on device and host
#===============================================================================
size = 16
host_result = np.zeros( [size], dtype=np.float32 )
device_buffer = clyther.DeviceBuffer( [size], c_float, clyther.mem.read_write, context=context )
zeros(device_buffer,context=context,queue=queue)


#===============================================================================
# Here we can create an instance of foobar with the function definition of ( __global float* a, float x, float y )
# the foobar.argtypes creates and compiles openCL code and allows 'fb' to be called like a python function
#
# to see the openCL source code do::
# >>> print fb.source
#===============================================================================
fb = foobar.argtypes( global_array_type( float, [size] ), float, float, context=context)


#===============================================================================
# There are two ways to call the foobar function
# In this case fb calls foobar with the explicit types "float* a, float x, float y" declared above
#===============================================================================
event = fb(  device_buffer, 1., 0.7, queue=queue)

#we could do :
# >>> event.wait()


#===============================================================================
# In the second case foobar is called directly without explicit typing
# The types are guessed from the arguments given. 
# The function below is equivalent to the function above
#===============================================================================
event = foobar( device_buffer, 3.0, .3, context=context, queue=queue )

#===============================================================================
# Now we are ready to copy the memory back to the host
#===============================================================================
event = device_buffer.to_host(  host_result, queue=queue )

queue.finish( )

print 
print "result should be an array of sixteen three's"
print "#==============================================================================="
print "result",host_result
print "#==============================================================================="
