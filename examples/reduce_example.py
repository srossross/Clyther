
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

import clyther
from ctypes import c_float
from clyther import runtime as clrt
import numpy as np


@clyther.device
def cladd( a, b ):
    return a+b


@clyther.device
def clprod( a, b ):
    return a * b


@clyther.device
def clmax( a, b ):
    if a > b:
        return a
    else:
        return b


    
@clyther.kernel
@clyther.const( 'group_size' )
@clyther.bind( 'global_work_size', 'group_size' )
@clyther.bind( 'local_work_size','group_size' )
def reduce( output, input, shared, oper, group_size, initial=0.0 ):

    lid = clrt.get_local_id(0)

    gid = clrt.get_group_id(0)
    gsize = clrt.get_num_groups(0)

    gs2 = group_size * 2

    stride = gs2 * gsize

    i = gid * gs2 + lid

    shared[lid] = initial

    while i < input.size:
        shared[lid] =  oper(shared[lid], input[i])
        shared[lid] = oper(shared[lid], input[i+group_size])
         
        i += stride
        
        clrt.barrier( clrt.CLK_LOCAL_MEM_FENCE )
        
    #The clyther compiler identifies this loop as a constant a
    # unrolls this loop 
    for cgs in [ 512 , 256, 128, 64, 32, 16, 8, 4, 2]:
        
        #acts as a preprocessor define #if (group_size >= 512) etc. 
        if group_size >= cgs:
            
            if lid < cgs/2:
                shared[lid] = oper(shared[lid] , shared[lid + cgs/2] )
                 
            clrt.barrier( clrt.CLK_LOCAL_MEM_FENCE )
            
    if lid == 0:
        output[gid] = shared[0]


#===============================================================================
# Setup OpenCL
#===============================================================================
clyther.init( 'GPU' )
#queue1 = cl.CommandQueue( clyther.get_context( ), clyther.get_context( ).devices[0] ) 
#queue2 = cl.CommandQueue( clyther.get_context( ), clyther.get_context( ).devices[0] ) 

size = 32

#===============================================================================
# Here is an optional intermediate step. The 'argtypes' compiles and builds 
# the openCL functions returns a callable object
# 
# output_type = global_array_type( c_float, [1])
# input_type = global_array_type( c_float, [size])
# shared_type = shared_array_type( c_float, [size] )
#
# cl_sum = reduce.argtypes( output_type, input_type, shared_type, oper=cladd, group_size=size//2, initial=c_float )
# cl_max = reduce.argtypes( output_type, input_type, shared_type, oper=clmax, group_size=size//2, initial=c_float )
#
#===============================================================================


#===============================================================================
# Allocate Host and device memory
#===============================================================================

flags = clyther.cl.MEM.READ_WRITE

host_init = np.zeros( size, dtype=c_float )
host_init[:] = np.random.ranf( size )+1
host_result = np.zeros( [1], dtype=c_float )
device_input = clyther.DeviceBuffer( [size], c_float, flags=flags )
shared = clyther.Shared( [size], c_float )

sum_output = clyther.DeviceBuffer( [1], c_float, flags=flags )
max_output = clyther.DeviceBuffer( [1], c_float, flags=flags )
prod_output = clyther.DeviceBuffer( [1], c_float, flags=flags )

#===============================================================================
# Copy Host memory to device 
#===============================================================================
event = device_input.from_host( host_init ) 

#===============================================================================
# Call reduce function with different inputs
#===============================================================================

event = reduce( sum_output, device_input ,shared, cladd, group_size=size//2 )
event = reduce( max_output, device_input ,shared, clmax, group_size=size//2 )
event = reduce( prod_output, device_input ,shared, clprod, group_size=size//2 , initial=1.0 )

#===============================================================================
# Print the results 
#===============================================================================

print
print "starting array", host_init
print
print "            numpy |     OpenCL  "
print "------------------+-------------"
print "sum    %10.2f = %10.2f"%( host_init.sum( ), sum_output.item( ) )
print "prod   %10.2f = %10.2f"%( host_init.prod( ), prod_output.item( ) )
print "max    %10.2f = %10.2f"%( host_init.max( ), max_output.item( ) )
print
print
#
#print "done"


