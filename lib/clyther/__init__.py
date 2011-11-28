'''
Created on Mar 05, 2010 by GeoSpin Inc
@author: Sean Ross-Ross srossross@geospin.ca
website: www.geospin.ca
'''

import copencl as cl

from static import init, finish, get_context, get_queue
from memory import DeviceBuffer, Shared
from device_objects import device_object, device_attribute

from vector_types import uint2,uint4,uint8,uint16
from vector_types import int2,int4,int8,int16
from vector_types import float2,float4,float8,float16

from decorators import kernel,device,task, bind,const

from api.emulation import get_emulate, set_emulate, emulate

from export import ExportCModule

from tests import main as test

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



