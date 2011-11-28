'''
Created on Mar 15, 2010 by GeoSpin Inc
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

from __future__ import with_statement

#from clyther.api.emulation import get_emulate

import threading
_local = threading.local()

barrier_condition = threading.Condition( ) 
barrier_count = 0

def get_global_id( tidx ):
    return _local.global_id[tidx]

def get_group_id( tidx ):
    return _local.group_id[tidx]

def get_local_id( tidx ):
    return _local.local_id[tidx]

def get_num_groups( tidx ):
    return _local.num_groups[tidx]

def get_local_size( tidx ):
    return _local.local_work_size[tidx]

def get_global_size( tidx ):
    return _local.global_work_size[tidx]

def _get_local_size_(  ):
    return reduce( lambda x,y: x*y, _local.local_work_size )

def synchronous( lock ):
    
    def sync_decorator(func):
        
        def sync( *args,**kwargs):
            with lock:
                result = func( *args,**kwargs)
            return result
        return sync
    
    return sync_decorator

    
def barrier( *args ):
    
    global barrier_count
    with barrier_condition:
    
        barrier_count +=1
        if barrier_count < _get_local_size_():
            barrier_condition.wait( )
        else:
            barrier_count = 0
            barrier_condition.notifyAll( )
        
    
    
    
CLK_LOCAL_MEM_FENCE = 'CLK_LOCAL_MEM_FENCE'

def replace_globals( ):
    pass
