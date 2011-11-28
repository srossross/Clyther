'''
Created on Mar 28, 2010 by GeoSpin Inc
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
from clyther import kernel,bind,DeviceBuffer,mem,ExportCModule
from clyther.memory import global_array_type
import clyther.runtime as clrt
import copencl as cl
import numpy
from ctypes import c_float
import clyther
import sys


clyther.init('GPU')

@kernel
@bind('global_work_size' ,'a.size')
@bind('local_work_size' , 1)
def sum(a,b,ret):
    i = clrt.get_global_id(0)
    ret[i] = a[i] + b[i]


if __name__ == '__main__':
    
    modname = sys.argv[1]
    mod = ExportCModule(  modname )
    
    csum = sum.argtypes( global_array_type( c_float, shape=[32] ),global_array_type( c_float, shape=[32] ),global_array_type( c_float, shape=[32] ) )
    
    mod.CExport( sum=csum )
    
    mod.create( )
    
    
    
    
    