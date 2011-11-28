'''
Created on Mar 22, 2010 by GeoSpin Inc
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

def create_local_dict( argspec, args, kwargs, only_use=None):
    """
    Puts all arguments keyword and positional into a single 
    dictionary according to argspec
    """
        
    argnames = argspec[0]
    deflts = argspec[-1]

    if deflts is None:
        defaults = {}
    else:
        last_args = argnames[-len(deflts):]
        defaults = dict( zip( last_args, deflts ) )
        
    listargs = dict( zip( argnames[:len(args)], args ) )
    
    newargs = {}
    
    newargs.update( defaults )
    newargs.update( listargs )
    newargs.update( kwargs )

    if only_use:
        diff = set(only_use).difference( newargs.keys() )
    else:
        diff = set(argnames).difference( newargs.keys() )
    
    if diff:
        i1 = diff.intersection( argnames )
        i2 = diff.intersection( argnames )
        if i1:
            msg = 'required arguments [%r] were not given' %(", ".join(i1) )
            raise TypeError( msg )
        elif diff.intersection( argnames ):
            msg = 'foo() got an unexpected keyword arguments ' %(", ".join(i2) ) 
            raise TypeError( msg )
        
    
    return newargs
