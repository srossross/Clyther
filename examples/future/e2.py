'''
Created on Mar 24, 2010 by GeoSpin Inc
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
from ctypes import c_uint
from clyther.api.cltypes import cltype
import copencl as  cl
import numpy as np
import pdb


clyther.init('CPU')

@clyther.task
def foobar( a , b ):
    c = clyther.uint4( 1,2,3,4 )
    d = c.xy
    d.y = c.x
    



#    
#
foo = clyther.uint8( 0,1,2,3,4,5,6,7 )

#pdb.set_trace()
print foo
print foo.lo
print foo.hi
print foo.even
print foo.odd

#
flags = cl.MEM.READ_WRITE 
##
##
buff = clyther.DeviceBuffer( [2], elem_type=clyther.uint2, flags=flags )
#
#z = np.frombuffer( buff.host, dtype=np.uint32 )
#
#print "0 array", z
#
foobar.argtypes( cltype.ctype(buff), foo ).source
#
#event, host = buff.map( )
#event, host2 = buff.map( )
#event.wait( )
#
#x = np.frombuffer( host, dtype=np.uint32 )
#
#print "x array", x 
#print "y", repr(host)
#print repr(host2)
#print repr(buff.host)
#print "1 array", z 
#
##event = buff.unmap( buffer )
#
#clyther.finish( )
#
#print "2 array", z
# 
