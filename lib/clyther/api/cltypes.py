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

from ctypes import c_int
from ctypes import c_double, c_float
import ctypes
import pdb
import new

class rtte( object ):
    """
    RunTime Type Evaluation (RTTE)
    """
    pass

class CLTypeException( Exception ): pass

class cltype( object ):
    """
    Class to manage and standardize all python types
    """
    @classmethod
    def is_function( cls, ctype ):
        """
        Test dsifctype is a function 
        """
        if hasattr(  ctype, '_is_function' ):
            return ctype._is_function
        else:
            return False

    @classmethod
    def is_type( cls, ctype ):
        """
        Test if ctype is a type. Must be in cltype.type_map dictionary 
        or have  attribute 'ctype'  
        """
        if ctype in cls.type_map:
            return True
        else:
            return hasattr( ctype, 'ctype' )
            

    @classmethod
    def is_const(cls ,ctype ):
        """
        Test if ctype is a constant. Must be an instance of type or rtte 
        """
        if isinstance(  ctype, (type,rtte) ):
            return False
        else:
            return True
        
    
    @classmethod
    def typeify( cls, ctype ):
        """
        get ctype from instance or class  
        """
        if ctype == None:
            res = ctype
        elif cls.is_function( ctype ):
            res = ctype
        elif cls.is_const(ctype):
            res = type(ctype)
        else:
            res = ctype
    
        return res
        
    @classmethod
    def check_in_map( cls, ctype, name  ):
        """
        check if 'name' is in type_map[ctype] and is not None    
        """

        if ctype in cls.type_map and name in cls.type_map[ctype]:
            return cls.type_map[ctype][name] is not None
        else:
            return False
    
    
    @classmethod
    def ctype(cls, ctype ):
        """
        Ensure that 'ctype' is a ctype 
        """
#        ctype = cls.typeify( ctype )
        if ctype == None:
            ctype_result = None
            
#        elif isinstance( ctype , new.module ):
#            return ctype
        
        elif hasattr( ctype, '__array__' ):
            from clyther.memory import global_array_type
            return global_array_type( ctype.dtype, ctype.shape )
        elif cls.check_in_map(ctype,'as_parameter'):
            ctype_result = cls.type_map[ctype]['as_parameter']( ctype )
        elif hasattr( ctype, 'ctype' ):
            ctype_result = ctype.ctype
        elif hasattr( ctype, 'resolve' ):
            ctype_result = cls.ctype( ctype.resolve() )
        else:
            ctype_result = ctype
        
        ctype = cls.typeify( ctype_result )
        return ctype
    
    @classmethod
    def cdef(cls, ctype ):
        """
        return OpenCL string declaration of 'ctype' 
        """

        ctype = cls.typeify( ctype )
        
        if ctype == None:
            cdef = 'void'
        elif cls.check_in_map(ctype,'cdef'):
            cdef = cls.type_map[ctype]['cdef']( ctype )
            
        elif hasattr( ctype, 'cdef' ):
            if isinstance(ctype.cdef, str ):
                cdef = ctype.cdef
            else:
                cdef = ctype.cdef( )
                
        elif hasattr( ctype, 'resolve' ):
            return cls.cdef( ctype.resolve() )
        else:
            raise TypeError('could not create C definition for type %r' %(ctype) )
        
        return  cdef
    
    @classmethod
    def sizeof(cls,param):
        """
        return the size of param in bytes 
        """
        ctype = cls.ctype( param )
        
        if ctype == None:
            return 0
        elif hasattr(param, 'cl_sizeof' ):
            return param.cl_sizeof( )
        elif param == long:
            return ctypes.sizeof( ctypes.c_long )
        else:
            return ctypes.sizeof( ctype)
        
    
    type_map = {}
    family_pref = ['char','int','float','complex',]
    
    @classmethod
    def regiseter( cls, ctype, cdef=None, family=None, as_parameter=None, signed=None):
        """
        Register a new type 
        """

        cls.type_map[ctype] = {}
        cls.type_map[ctype]['cdef'] = cdef
        cls.type_map[ctype]['family'] = family
        cls.type_map[ctype]['signed'] = signed
        cls.type_map[ctype]['as_parameter'] = as_parameter
        
        
    @classmethod
    def is_signed(cls,ctype):
        """
        test if ctype is a signed type 
        """

        ctype = cls.typeify( ctype )
        
        if cls.check_in_map( ctype, 'signed'):
            return cls.type_map[ctype]['signed']
        elif hasattr(ctype, 'is_signed'):
            return ctype.is_signed( )
        else:
            raise Exception("type %r is not comparable, no type signed defined"%ctype)
        
    @classmethod
    def family(cls,ctype):
        """
        Return the family and family rank of ctype  
        """
        ctype = cls.typeify( ctype )
        
        if cls.check_in_map( ctype, 'family'):
            fam = cls.type_map[ctype]['family']
        elif hasattr( ctype, 'type_family'):
            fam = ctype.type_family()
        else:
            raise CLTypeException("type %r is not comparable, no type family defined"%ctype)
        
        if fam not in cls.family_pref:
            raise CLTypeException("type %r is not comparable, undefined family of types %r"%fam)
        
        idx = cls.family_pref.index( fam )
        return idx,fam
    
    
    @classmethod
    def maxtype(cls,cleft,cright):
        """
        Return the type of cleft or cright that contains greater precision.
        """
        if cleft == cright:
            return cleft
        
        lfamidx,lfam = cls.family( cleft )
        rfamidx,rfam = cls.family( cright )
        lsign = cls.is_signed( cleft )
        rsign = cls.is_signed( cright )
        
        if lfam == rfam:
            
            if lsign and not rsign:
                return cleft
            elif rsign and not lsign:
                return cright
            
            if cls.sizeof( cleft ) > cls.sizeof( cright ):
                return cleft
            else:
                return cright
        elif lfamidx > rfamidx:
            return cleft
        else:
            return cright
        
            raise Exception("types %r and %r are not comparable"%(cleft,cright))
        
    
cltype.regiseter( bool, lambda arg: 'short', family='int', as_parameter=lambda arg: c_int ,signed=True)

cltype.regiseter( int, lambda arg: 'int', family='int', as_parameter=lambda arg: c_int ,signed=True)
cltype.regiseter( c_int, lambda arg: 'int', family='int' ,signed=True)
cltype.regiseter( ctypes.c_uint, lambda arg: 'uint', family='int' ,signed=False )

cltype.regiseter( long, lambda arg: 'long', family='int' ,signed=True )
cltype.regiseter( ctypes.c_long, lambda arg: 'long', family='int' ,signed=True )

cltype.regiseter( ctypes.c_ulong, lambda arg: 'unsigned long int', family='int' ,signed=True)

cltype.regiseter( float, lambda arg: 'float', family='float',as_parameter=lambda arg: c_float ,signed=True)
cltype.regiseter( c_float, lambda arg: 'float', family='float' ,signed=True)
cltype.regiseter( c_double, lambda arg: 'double', family='float' ,signed=True)
    

