'''
Created on Feb 21, 2010

@author: sean
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


#from distutils.core import setup
from setuptools import setup 
from distutils.extension import Extension 

from pkg_resources import get_build_platform
from glob import glob
from os.path import isdir

plat = get_build_platform()


#Mac
if plat.startswith( 'macosx' ):
    flags = dict(extra_link_args=['-framework','OpenCL'] )
#Windows 
elif plat.startswith( 'win32' ):
    if isdir('C:\\Program Files\\ATI Stream'):
        flags = dict(libraries=['OpenCL'], include_dirs=['C:\\Program Files\\ATI Stream\\include'], 
                     library_dirs=['C:\\Program Files\\ATI Stream\\lib\\x86'])
#Linux
else:
    flags = dict(libraries=['OpenCL'], include_dirs=['/usr/include/CL'], library_dirs=['/usr/lib'])

ext_modules = [Extension("copencl", ["src/opencl_wrap.c"] , **flags )]
    
 
setup( name = 'clyther',
       version='0.1-beta-3',
       author='Sean Ross-Ross',
       author_email='srossross@geospin.ca',
       url='http://clyther.sourceforge.net/',
       description='Python extention to OpenCL GPU language',
       license='Apache 2.0',
       
       ext_modules = ext_modules,
       packages=['clyther', 'clyther.api', 'clyther.api.ast','clyther.tests'], 
       package_dir = {'': 'lib'},
        
       test_suite = "clyther.tests",
       
       headers=['src/pyopencl.h'],

#       entry_points = {
#                "distutils.setup_keywords": [
#                    "device_type = clyther.tests:set_device_type",
#                ],
#            },
)


