'''
Created on Apr 9, 2010 by GeoSpin Inc
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

from clyther.device_objects import DeviceObjectType
from clyther.device_objects import StructType
from ctypes import Structure
from ctypes import c_uint,c_int,c_float,c_uint8,c_int8
import pdb
import math
import itertools

class VectorType( StructType ):
    
    def __new__(cls, name, bases, dct):
        
        base = dct.get('base',None)
        
        if base is None:
            return StructType.__new__(cls, name, bases, dct)
        
        vector_len = dct['vlen']
        ctype = dct['_ctype']
        
        dct['cdef'] = "%s%i" %(base,vector_len)
        
        fields = []
        valid = '0123456789ABCDEF'
        for i in valid[:vector_len]:
            name ='s%s' %i
            fields.append( (name,ctype) )
            
        dct['_fields_'] = fields
        
        return DeviceObjectType.__new__(cls, name, bases, dct)
    
    def __repr__(self):
        return '<type %r>' %self.cdef
    
    def __str__(self):
        return '<type %r>' %self.cdef
    
    def __getattr__(self,name):
        return self.__getattr_type__( name )
        
    
class VectorBase( Structure ):
    __metaclass__ = VectorType
    
    proto = None
    
    def __hash__(self):
        return hash( tuple(self._fields_) ) 

    def __init__( self, *args, **kwargs):
        
        arglen = len(args)
        if arglen == 0:
            pass
        elif arglen > self.vlen:
            raise TypeError( "%r takes up to %i args (got %i)" %(self,self.vlen,arglen) )
        elif arglen == 1:
            value = args[0]
            for name,_ in self._fields_:
                setattr( self, name, value)
        elif arglen == self.vlen:
            for value,(name,_) in zip(args,self._fields_):
                setattr( self, name, value)
        else:
            newsize = self.vlen / float(arglen)
            if math.floor(newsize) != newsize:
                raise TypeError( "%r wron number of arguments %i" %(self,arglen) )
            
            newargs = itertools.chain( *args )
            for value,(name,_) in zip(newargs,self._fields_):
                setattr( self, name, value)

            
        for name,value in kwargs.items():
            setattr( self, name, value)
            
    def __iter__(self):
        for item in range(self.vlen):
            name = 's%i' %item
            i0 = getattr( self, name, None)
            yield i0
    
    def __len__(self):
        return self.vlen
    
    def __eq__(self,other):
        if type(self) != type(other):
            return False
        
        for item in range(self.vlen):
            name = 's%i' %item
            i0 = getattr( self, name, None)
            
            try:
                i1 = getattr( other, name, None)
            except:
                return False
            
            if i0 != i1:
                return False 
            
        return True
                    
    @classmethod
    def __getattr_type__(cls,name):
        
        attrs = cls._formatname(name)
        
        newlen = len(attrs)
        if newlen == 1:
            
            return cls._ctype
        
        typename = "%s%s"%(cls.base,newlen)
        
        newtype = globals().get( typename ,None)
        
        if newtype is None:
            raise Exception("could not find vector type %r " %typename)
         
        return newtype
    
    
    @classmethod
    def _formatname(cls,name):
        
        valid = '0123456789ABCDEF'
        name = name.upper()
        
        if name in ['HI','LO','ODD','EVEN']:
            if name == 'LO':
                newname = valid[:cls.vlen//2]
            elif name == 'HI':
                newname = valid[cls.vlen//2:cls.vlen]
            elif name == 'EVEN':
                newname = valid[:cls.vlen:2]
            elif name == 'ODD':
                newname = valid[1:cls.vlen:2]

            
        elif name.startswith( 'S' ):
            newname = name[1:]
            for i in newname:
                if i not in valid:
                    raise TypeError("invalid attribute name %s" %name )
        else:
            for i in name:
                if i not in 'XYZW':
                    raise TypeError("invalid attribute name %s" %name )
                 
            newname = (name.replace( 'X', '0').replace( 'Y', '1')
                        .replace( 'Z', '2').replace( 'W', '3') )

        return ["s%s"%elem for elem in newname]
#        return newname
    
    def __getattr__(self,name):
        
        
        attrs = self._formatname(name)
        
        if len(attrs) ==1:
            return getattr(self, attrs[0] )
        else:
            vtype = self.__getattr_type__( name )
            lst = [ getattr(self, attr) for attr in attrs ]
            result = vtype( *lst )
            return result
    
    def __setattr__(self,name,value):
        
        attrs = self._formatname(name)
        
        try:
            len(value)
            viter = iter(value)
        except:
            viter = itertools.repeat( value )
             
        for attr,value in zip(attrs,viter):
            Structure.__setattr__( self, attr, value )
            
        return
    
    def __repr__(self):
        arglist = [ getattr( self, name) for name,_ in self._fields_ ]
        args = ", ".join( [repr(arg) for arg in arglist] )
        return "%s( %s )" %( self.cdef, args )

    @classmethod
    def get_restype( cls, gentype1, gentype2=None ):
        return cls

#===============================================================================
# 
#===============================================================================

class uchar2( VectorBase ):
    
    _ctype = c_uint8
    base = 'uchar'
    vlen = 2

class uchar4( VectorBase ):
    
    _ctype = c_uint8
    base = 'uchar'
    vlen = 4

class uchar8( VectorBase ):

    _ctype = c_uint8
    base = 'uchar'
    vlen = 8

class uchar16( VectorBase ):
    
    _ctype = c_uint8
    base = 'uchar'
    vlen = 16
#===========================================================================
# 
#===========================================================================
class uint2( VectorBase ):
    
    _ctype = c_uint
    base = 'uint'
    vlen = 2

#===============================================================================
# 
#===============================================================================
class uint4( VectorBase ):
    
    _ctype = c_uint
    base = 'uint'
    vlen = 4

class uint8( VectorBase ):

    _ctype = c_uint
    base = 'uint'
    vlen = 8

class uint16( VectorBase ):
    
    _ctype = c_uint
    base = 'uint'
    vlen = 16
#===============================================================================
# 
#===============================================================================
class char2( VectorBase ):
    
    _ctype = c_int8
    base = 'char'
    vlen = 2

class char4( VectorBase ):
    
    _ctype = c_uint8
    base = 'char'
    vlen = 4

class char8( VectorBase ):

    _ctype = c_int8
    base = 'char'
    vlen = 8

class char16( VectorBase ):
    
    _ctype = c_int8
    base = 'char'
    vlen = 16
#===============================================================================
# 
#===============================================================================
class int2( VectorBase ):
    
    _ctype = c_int
    base = 'int'
    vlen = 2

class int4( VectorBase ):
    
    _ctype = c_int
    base = 'int'
    vlen = 4

class int8( VectorBase ):

    _ctype = c_int
    base = 'int'
    vlen = 8

class int16( VectorBase ):
    
    _ctype = c_int
    base = 'int'
    vlen = 16

#===============================================================================
# 
#===============================================================================
class float2( VectorBase ):
    
    _ctype = c_float
    base = 'float'
    vlen = 2

class float4( VectorBase ):
    
    _ctype = c_float
    base = 'float'
    vlen = 4

class float8( VectorBase ):

    _ctype = c_float
    base = 'float'
    vlen = 8

class float16( VectorBase ):
    
    _ctype = c_float
    base = 'float'
    vlen = 16

