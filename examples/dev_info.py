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

import copencl as cl
platforms = cl.get_platforms( )

for platform in platforms:
    devices = platform.get_devices( cl.DEVICE_TYPE.ALL )
    for device in devices:
        print "--------------------------"
        print "vendor:", device.vendor
        print "name:", device.name
        print "type:", device.type
        print "memory: ", device.global_mem_size//1024//1024, 'MB'
        print "max clock speed:", device.max_clock_frequency, 'MHz'
        print "compute units:", device.max_compute_units
        print "OpenCL version:", device.version
        print "driver version:", device.driver_version
        print "--------------------------"
    

