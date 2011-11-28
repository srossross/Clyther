'''
Created on Mar 18, 2010 by GeoSpin Inc
@author: Sean Ross-Ross srossross@geospin.ca
website: www.geospin.ca
'''
import clyther
from clyther.memory import global_array_type
from ctypes import c_int

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

@clyther.kernel
@clyther.const( 'group_size' )
@clyther.bind( 'global_work_size', 'group_size' )
@clyther.bind( 'local_work_size','group_size' )
def reduce( input, group_size=512 ):

    for cgs in [ 512 , 256, 128, 64, 32, 16, 8, 4, 2]:
        if group_size >= cgs:
            input[0] = 0


print reduce.argtypes( global_array_type( c_int, [32]) ).source


#@clyther.kernel
#@clyther.const( 'group_size' )
#@clyther.bind( 'global_work_size', 'group_size' )
#@clyther.bind( 'local_work_size','group_size' )
#def reduce( output, input, shared, oper, group_size=512 ):
#
#    lid = clrt.get_local_id(0)
#
#    gid = clrt.get_group_id(0)
#    gsize = clrt.get_num_groups(0)
#
#    gs2 = group_size * 2
#
#    stride = gs2 * gsize
#
#    shared[lid] = 0.0
#
#    i = gid * gs2 + lid
#
#    shared[lid] = 0
#
#    while i < input.size:
#        shared[lid] = oper( shared[lid], input[i] )
#        shared[lid] = oper( shared[lid], input[i+group_size] )
#
#        i += stride
#
#        clrt.barrier( clrt.CLK_LOCAL_MEM_FENCE )
#
#    for cgs in [ 512 , 256, 128, 64, 32, 16, 8, 4, 2]:
#        if group_size >= cgs:
#            if lid < cgs/2:
#                shared[lid] = oper( shared[lid], shared[lid + cgs/2] )
#            clrt.barrier( clrt.CLK_LOCAL_MEM_FENCE )
#
#    if lid == 0:
#        output[gid] = shared[0]
#
