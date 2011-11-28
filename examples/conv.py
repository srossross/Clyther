'''
Created on 2010 by Paul Kienzle
@author: Paul Kienzle
'''
#size=100
#window=5
from clyther.api.cltypes import cltype
size=1<<20
window=15555


#================================================================================#
# Copyright 2010 Paul Kienzle                                              #
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


#===============================================================================
# Setup OpenCL
#===============================================================================
devices = cl.get_devices(  'GPU' )
context = cl.Context( [devices[0]] )
queue = cl.CommandQueue( context, context.devices[0] )    

#===============================================================================
# Create function conv
#===============================================================================
@kernel
@bind('global_work_size','a.size/512')
@bind('local_work_size', 512)
def conv(a,b,ret):
    
    i = clrt.get_global_id(0)
    
    w = (b.size-1)/2
    
    start = 0 if (i < w) else i-w
    stop = a.size if (i+w >= a.size) else i+w+1 
    
    sum = 0.
    for k in range(start,stop):
        sum += a[k] * b[k+w-i]
        
    ret[i] = sum

## The desired C kernel
#void
#conv(const float a[], const float b[], size_t na, size_t nb, float ret[])
#{
#   unsigned int w, start, stop, b_offset, k;
#   float sum;
#
#   w = (nb-1)/2;
#   start = i > w ? i-w : 0;
#   stop = i + w < na-1 ? i+w : na-1;
#   sum = 0.f;
#   for (k=start; k <= stop; k++) sum += a[k]+b[k+w-i];
#   ret[i] = sum ;
#}

#===============================================================================
# Create buffer in host
#===============================================================================
A = numpy.arange(size,dtype='float32')
B = numpy.ones(window,dtype='float32')/window
C = numpy.empty_like(A)

#===============================================================================
# Create buffer in opencl context : alloc memory into GPU
#===============================================================================
buff1 = DeviceBuffer( [size], c_float, cl.MEM.READ_WRITE, context=context )
buff2 = DeviceBuffer( [window], c_float, cl.MEM.READ_WRITE, context=context )
buffr = DeviceBuffer( [size], c_float, cl.MEM.READ_WRITE, context=context )

#===============================================================================
# Send data to opencl
#===============================================================================
buff1.from_host(  A, queue=queue  )
buff2.from_host(  B, queue=queue  )

#===============================================================================
# Run conv 
#===============================================================================
#convarg = conv.argtypes(cltype.ctype( buff1 ),cltype.ctype( buff2 ), cltype.ctype(  buffr), context=context)
#print convarg.source
conv( buff1, buff2, buffr, context=context , queue=queue )

#===============================================================================
# Receive data from opencl to host
#===============================================================================
buffr.to_host( C ,queue=queue)
queue.finish()


if 1:
    print "---------------------------------------------"
    print "A =",str(A)
    print "B =",str(B)
    print "A(*)B =",str(C)
    print "---------------------------------------------"
