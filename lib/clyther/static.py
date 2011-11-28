'''
Created on Mar 05 by GeoSpin Inc
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

import copencl as cl #@UnresolvedImport IGNORE:F0401
from clyther.api import emulation_runtime
from clyther import runtime

class StaticOpenCL( object ):
    
    instance = None
    
    def __init__(self, type , profile=False ):
        
        if isinstance(type,str):
            type = type.upper( )
            
        devices = cl.get_devices( type )
        self.device = devices[0]
            
        self.context = cl.Context( devices[:1] )
        
        self.queue = cl.CommandQueue( self.context, self.device, profile=profile )
        self.profile = profile
     
    @classmethod
    def getInstance( cls, type, profile ):
        
        if isinstance(type ,str ):
            type = type.upper()
             
            if type == 'EMULATE':
                type = cl.DEVICE_TYPE.ALL
                from clyther.api.emulation import  set_emulate
                set_emulate( True )
                
            elif type == 'ALL':
                type = cl.DEVICE_TYPE.ALL
                
            elif type == 'CPU':
                type = cl.DEVICE_TYPE.CPU
                
            elif type == 'GPU':
                type = cl.DEVICE_TYPE.GPU
                
            elif type == 'ACCELERATOR':
                type = cl.DEVICE_TYPE.ACCELERATOR
                
            elif  type == 'DEFAULT':
                
                type = cl.DEVICE_TYPE.DEFAULT
        
        if cls.instance is None:
            cls.instance = StaticOpenCL( type, profile=profile)
            
        return cls.instance

def get_context( ):
    
    global _cl_static
    if _cl_static is None:
        raise Exception("must call clyther.init() to use static functions")
    else:
        return _cl_static.context
    return

def get_queue( ):
    
    global _cl_static
    if _cl_static is None:
        raise Exception("must call clyther.init() to use static functions")
    else:
        return _cl_static.queue
    return

def get_profile( ):
    
    global _cl_static
    if _cl_static is None:
        return False
    else:
        return _cl_static.profile
    
    return



_cl_static = None

def init( type=cl.DEVICE_TYPE.DEFAULT , profile=False ):
    
    global _cl_static
    
    _cl_static = StaticOpenCL.getInstance( type ,profile=profile )
    
    if isinstance(type, str):
        type = type.upper()
        
    if type == 'EMULATE':
        return emulation_runtime
    else:
        return runtime 

def finish( ):
    """
    finish calles queue.finish on the current static queue and 
    clears the current init 
    """
    get_queue( ).finish( )
    _cl_static = None
