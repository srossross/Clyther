'''
Created on 2010 by Stephane Planquart
@author: Stephane Planquart stephane@planquart.com
website: www.planquart.com
'''


#================================================================================#
# Copyright 2010 Stephane Planquart                                              #
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
from clyther import kernel,bind,DeviceBuffer
import clyther.runtime as clrt
import copencl as cl
import numpy
from ctypes import c_float
import clyther
import pdb


#===============================================================================
# Setup OpenCL
#===============================================================================
devices = cl.get_devices(  'GPU' )
context = cl.Context( [devices[0]] )
queue = cl.CommandQueue( context, context.devices[0] )	
size=10

#===============================================================================
# Create function sum
#===============================================================================
@kernel
@bind('global_work_size' ,'a.size')
@bind('local_work_size' , 1)
def sum(a,b,ret):
	i = clrt.get_global_id(0)
	ret[i] = a[i] + b[i]

#===============================================================================
# Create buffer in host
#===============================================================================
A = numpy.random.rand(size).astype(numpy.float32)
B = numpy.random.rand(size).astype(numpy.float32)
C = numpy.empty_like(A)

#===============================================================================
# Create buffer in opencl context : alloc memory into GPU
#===============================================================================
flags = clyther.cl.MEM.READ_WRITE
buff1 = DeviceBuffer( [size], c_float, flags, context=context )
buff2 = DeviceBuffer( [size], c_float, flags, context=context )
buffr = DeviceBuffer( [size], c_float, flags, context=context )

#===============================================================================
# Send data to opencl
#===============================================================================
buff1.from_host(  A,queue=queue  )
buff2.from_host(  B,queue=queue  )

#===============================================================================
# Run sum
#===============================================================================
sum(buff1,buff2,buffr,context=context,queue=queue)

#===============================================================================
# You can use explicite function definition 
# and after get C OpenCL source code with csum.source
# >> csum = sum.argtypes( global_array_type( float, [size] ), 
# global_array_type( float, [size] ), global_array_type( float, [size] ), context=context)
# >> csum(buff1,buff2,buffr,queue=queue)
#===============================================================================


#===============================================================================
# Receiv data from opencl to host
#===============================================================================
buffr.to_host( C ,queue=queue)
queue.finish()
print "_____________________________________________"
print "example sum: A+B=C with 2 random float arrays"
print "---------------------------------------------"
print "A = " + str(A)
print "+"
print "B = " + str(B)

print "="
print "C = " + str(C)
print "---------------------------------------------"
