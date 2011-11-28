'''
Created on Mar 28, 2010 by GeoSpin Inc
@author: Sean Ross-Ross srossross@geospin.ca
website: www.geospin.ca
'''
from clyther.api.cltypes import cltype
from new import classobj
from ctypes import Structure
import pdb


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

def _makeGetter(name):
    """Return a method that gets compiledName's value."""
    return lambda self: getattr( self._container, name )

def _makeSetter(name):
    """Return a method that sets compiledName's value."""    
    return lambda self, value: setattr(self._container, name, value)

class device_attribute( object ):
    static_lineno = 0
    def __init__(self,ctype,default=None):
        device_attribute.static_lineno += 1
        self.ctype = ctype
        self.default = default
        self.lineno = device_attribute.static_lineno
        

StructType = type(Structure) 

class DeviceObjectType( StructType ):
    
    def __new__(cls, name, bases, dct):
        
        
#        pdb.set_trace() 
        fields = []
        dct['_defaults'] = {}
        
        mycmp = lambda v1,v2: cmp(v1[1].lineno,v2[1].lineno)
        
        properties = filter(lambda arg: isinstance(arg[1], device_attribute), dct.items() )
        
        for key,value in sorted( properties , mycmp ):
            dct.pop( key )
            dct['_defaults'][key] = value.default
            fields.append( (key, value.ctype) )
                
#        @classmethod
#        def cdef(cls):
#            if 'cdef' in dct:
#                return dct['cdef']
#            else:
#                return "struct _struct%s" %( cls.__name__ )
#
#        @classmethod
#        def proto(cls):
#            if 'proto' in dct:
#                return dct['proto']
#            else:
#                body = " ".join(["%s %s;"%(cltype.cdef(defn),name) for name,defn in cls._fields_])
#                return "struct _struct%s {%s};" %( cls.__name__, body )
        

#        struct = classobj( "_c%s" %name, (Structure,), {'_fields_':fields, 
#                                                         })
        
        if fields:
            dct['_fields_'] = fields
            dct['_dfields_'] = dict( fields )
            
            
#        print "DeviceObjectType.__new__", name, bases, bool(fields)
        
        return  StructType.__new__( cls, name, bases, dct )
                
#        print
#        print "bases", cls, bases
#        print 
#    def __getattr__(self,name):
#        
#        if hasattr( self,'_dfields_'):
#            if name in self._dfields_:
#                print self,"__getattr__, ",name
#            return StructType.__getattr__(self,name)
#        else:
#            return type.__getattribute__(self,name)
            
    
    def __getattribute__(self,name):
        
        if name != "__dict__":
            if '_dfields_' in  self.__dict__:
                _dfields_ = StructType.__getattribute__( self, '_dfields_' )
                if name in _dfields_:
                    return _dfields_[name]

        return StructType.__getattribute__(self,name)
    

class device_object( Structure ):
    __metaclass__ = DeviceObjectType
    
    def __init__(self, *args,**kwargs):
#        print( 'init device_object', args, kwargs )
        Structure.__init__( self )
#        self._container = self._cstruct( )
        
        for key,value in self._defaults.items():
            if value is not None:
                setattr( self, key, value )
                
        for value,name in zip(args,self._fields_):
            setattr( self, name, value)

        for name,value in kwargs.items():
            setattr( self, name, value)
            
    def __hash__(self):
        return hash( tuple(self._fields_) ) 
    
    @classmethod
    def cdef(cls):
        return "_struct_%s" %( cls.__name__ )
      
    @classmethod
    def proto(cls):
        defns = []
        for name,type in cls._fields_:
#            defn = CLType(type).cdef()
            defn = cltype.cdef( type ) 
            defns.append( "%s %s" %(defn,name) )   
        
        body = "; ".join( defns )
    
        return "typedef struct { %s; } _struct_%s" %(body, cls.__name__)

    @classmethod
    def get_restype( cls, gentype1, gentype2=None ):
        return cls
    

class DeviceObject( object ):
    pass