'''
Created on Mar 5, 2010 by GeoSpin Inc
@author: Sean Ross-Ross srossross@geospin.ca
website: www.geospin.ca
'''
from clyther.api.kernelfunction import OpenCLFunctionFactory
from clyther.api.emulation import get_emulate, EmulateKernelFunction

#================================================================================#
# Copyright 2009 GeoSpin Inc.                                                    #
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


def kernel( function ):
    function.__kernel_type__ = 'kernel'
    if get_emulate( ):
        return EmulateKernelFunction( function )
    else:
        return OpenCLFunctionFactory( function, 'kernel' )

def task( function ):
    function.__kernel_type__ = 'task'
    if get_emulate( ):
        return function
    else:
        return OpenCLFunctionFactory( function, 'task' )


def device( function ):
    function.__kernel_type__ = 'device'
    if get_emulate():
        return function
    else:
        return OpenCLFunctionFactory( function, 'device' )


def const( name ):
    
    def const_decorator( func ):
        if hasattr(func, '__cl_constants__'):
            func.__cl_constants__.append( name )
        else:
            func.__cl_constants__ = [ name ]
        return func
            
    return const_decorator


def bind( name , value ):
        
    def bind_decorator( func ):
        if not hasattr(func, '__cl_bind__'):
            func.__cl_bind__ = []
        
        func.__cl_bind__.insert(0, (name, value) )
            
        return func
            
    return bind_decorator


