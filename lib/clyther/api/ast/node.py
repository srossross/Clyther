'''
Created on Mar 05, 2010 by GeoSpin Inc
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
from compiler import ast

import ctypes
from clyther.api.cltypes import cltype, rtte
import pdb
import new 

def ispointer(ctype):
    return not isinstance(ctype._type_, str)


class RuntimeResolveType( rtte ):
    
    def __init__(self, derefrenced_type=None ):
        self.derefrenced_type=derefrenced_type
        self.type = None
        self._restype = None
        
    def derefrence(self):
        return RuntimeResolveType( self )
    
    def set_type(self,type):
        
        self.type = type
        
        
    def resolve(self):
        if self.derefrenced_type is not None:
            
            if isinstance( self.derefrenced_type, RuntimeResolveType):
                array_ctype = self.derefrenced_type.resolve()
            else:
                array_ctype = self.derefrenced_type
                
            return array_ctype.elem_type
        
        elif isinstance( self.type, RuntimeResolveType):
            return self.type.resolve( )
        else:
            return self.type
            
    
    def __repr__(self):
        if self.derefrenced_type is not None:
            return "RuntimeResolveType( derefrenced_type=%r )" %(self.derefrenced_type)
        elif self.type is not None:
            return repr(self.type)
        else:
            return "RuntimeResolveType( %s )" %hash(self)
        
    def _get_restype(self):
        
        if self._restype is None:
            self._restype = RuntimeResolveType( )
            
        return self._restype
    
#    def get_restype(self,args):
#            self.resolve( )
#            
#            return ResolveReturnType( self, args )
    
    
class ResolveReturnType( RuntimeResolveType ):
    
    def __init__(self, functype, args):
        self.functype = functype
        self.args = args
        
    def resolve(self):
#        pdb.set_trace()
#        print self.functype
#        print self.args
        if hasattr( self.functype, 'resolve' ):
            functype = self.functype.resolve()
        else:
            functype = self.functype
        
        args = []
        for arg in self.args:
            if hasattr( arg, 'resolve' ):
                args.append( arg.resolve() )
            else:
                args.append( arg )
                
        return functype.get_restype( args )
#        print isinstance(self.functype, class_or_type_or_tuple)
#        return ctypes.c_int
    
#        raise Exception
    
    def __repr__(self):
        return "ResolveReturnType( %r, %r )" %(self.functype,self.args)

     

class ResolveAttrType( RuntimeResolveType ):
    
    def __init__(self, expr, rrt , attr):
        self.rttr = rrt
        self.expr = expr
        self.attr = attr
    
    def set_type(self,type):
        raise Exception
        
        
    def resolve(self):
#        pdb.set_trace()
        
        if hasattr( self.rttr, 'resolve'):
            resolved = self.rttr.resolve()
        else:
            resolved = self.rttr
        
        
        resolved2 = getattr( resolved, self.attr, None )
        
        if resolved2 is None:
            raise AttributeError( "%r object has no attribute %r" %(resolved, self.attr) )
        
        ctype = cltype.ctype( resolved2 )
        
        return ctype
        
#        print "resolve", getattr( resolved, self.attr, None )
##        print "resolved",resolved
##        pdb.set_trace()
#        ctype = cltype.ctype( resolved )
#        
#        if  ctype == new.module:
#            return getattr( resolved, self.attr )
#        
#        elif hasattr( ctype, "_fields_" ):
#            
#            field = [ (fld,_ctype) for fld,_ctype in ctype._fields_ if fld==self.attr]
#            
#            if field:
#                return cltype.ctype( field[0][1] )
#        
#        if hasattr( ctype, self.attr ):
#            cvalue = getattr( ctype, self.attr ) 
#            return cltype.ctype( cvalue )
#        elif hasattr( ctype, "__getattr_type__"):
#            cvalue = ctype.__getattr_type__( self.attr )
#            if cvalue == NotImplemented:
#                raise AttributeError( "%r object has no attribute %r" %(self.rttr, self.attr) )
#            return cltype.ctype( cvalue )
#        
#        else:
#            raise AttributeError( "%r object has no attribute %r" %(ctype, self.attr) )
##        if isinstance( self.type, RuntimeResolveType):
##            return self.type.resolve( )
##        else:
##            return self.type
            
    
    def __repr__(self):
        return "ResolveAttrType( %r, %r, %r )" %(self.rttr, self.expr, self.attr )
        
    def _get_restype(self):
        
        if self._restype is None:
            self._restype = RuntimeResolveType( )
            
        return self._restype


def largest_index( left, right, items ):
    
    if left._type_ in items: l = items.index( left._type_ ) 
    else: l = -1

    if right._type_ in items: r = items.index( right._type_ ) 
    else: r = -1
    
    if l < r:
        return right
    else:
        return left
        
        
    return max( l, r )

class TypeTree( RuntimeResolveType ):
    
    def __init__(self,  left, right ):
        self.left = left
        self.right = right

    def derefrence(self):
        return RuntimeResolveType( self )
    
    def set_type(self):
        raise Exception
    
    def resolve(self):
        
        if isinstance( self.left, RuntimeResolveType ):
            left = self.left.resolve( )
        else:
            left = self.left

        if isinstance( self.right, RuntimeResolveType ):
            right = self.right.resolve( )
        else:
            right = self.right
        
    
        cleft = cltype.ctype( left )
        cright = cltype.ctype( right )
        
        return cltype.maxtype( cleft, cright)

    
    def __repr__(self):
        return "TypeTree( %r, %r )" %(self.left,self.right)
    


class CLVarDeclaration( ast.Node ):
    
    def __init__(self, name,type=None,lineno=None):
        self.name = name
        self._is_function = None
        self._restype = None
        self.lineno = lineno
        
        if type is None:
            self.type = RuntimeResolveType( )
        else:
            self.type = type
    
    def __repr__(self):
        if self._is_function:
        
            return "CLFunctionDeclaration(%r, %r)" %( self.name, self.restype)
        else:
            return "CLVarDeclaration(%r, %r)" %( self.name, self.type )
    
    def getChildren(self):
        
        yield self.name 
        yield self._restype 
    
    def getChildNodes(self):
        
        yield self.name

    def _get_restype(self):
        if self._is_function is False:
            raise Exception("can not be of type function")
        
        if self._restype is None:
            self._restype = RuntimeResolveType( )
        self._is_function = True    
        return self._restype
    
    restype = property( _get_restype )
    
    
class CPPDefine( ast.Node ):
    def __init__(self, name, lineno=None):
        
        self.name = name
        self.lineno = lineno
    
    def getChildren(self):
        
        yield self.name

    def getChildNodes(self):
        
        yield self.name

class CLFunction( ast.Function ):
    constants=None
    var_defns =None
    
    def __repr__(self):
        
        return "CLFunction(%r, %r, %r, %r, %r, %r, %r, %r, %r)" % (self.decorators, self.name, self.constants, self.var_defns, self.argnames, self.defaults, self.flags, self.doc, self.code )


class RuntimeConst( ast.Node ):
    def __init__(self, name, lineno=None):
        
        self.lineno = lineno
        self.name = name
        
        
class CLCast( ast.Node ):
    def __init__(self, ctype, expr, lineno=None):
        
        self.lineno = lineno
        self.type = ctype
        self.expr = expr
        

    def __repr__(self):
        return "CLCast( %r, %r )" %( self.type, self.expr )

    def getChildren(self):
        
        yield self.expr
        yield self.ctype


    def getChildNodes(self):
        
        yield self.expr

class CLGetattr( ast.Node ):
    
    def __init__(self, expr, ctype, attrname , lineno=None):
        
        self.lineno = lineno
        self.ctype = ctype
        self.expr = expr
        self.attrname  = attrname 
    
    def __repr__(self):
        return "CLGetattr( %r, %r, %r )" %( self.ctype, self.expr, self.attrname )
    
    def getChildren(self):
        
        yield self.expr
        yield self.ctype
        yield self.attrname

    def getChildNodes(self):
        
        yield self.expr

class CLCallFunc(ast.Node):
    
    def __init__( self, node, args, arg_types, lineno ):
        self.node = node
        self.args = args
        self.arg_types = arg_types
        self.lineno = lineno

    def __repr__(self):
        return "CLCallFunc( %r, %r, %r )" %( self.node, self.args, self.arg_types )

    def getChildren(self):
        
        yield self.node
        yield self.args
        yield self.arg_types
    
    def getChildNodes(self):
        
        yield self.node
        yield self.args
    


class CLForLoop(ast.Node):
    
    def __init__( self, assign, body, start, stop, step, lineno=None ):
        self.assign = assign
        self.body=body
        self.start = start
        self.stop = stop
        self.step = step
        self.lineno = lineno
        

    def __repr__(self):
        return "CLForLoop( %r, %r, %r, %r, %r )" %( self.assign, self.start, self.stop, self.step, self.body )

    def getChildren(self):
        
        yield self.assign 
        yield self.body
        yield self.start
        yield self.stop
        yield self.step
    
    def getChildNodes(self):
        
        yield self.assign 
        yield self.body
        yield self.start
        yield self.stop
        yield self.step
    
    
class CLProtoType( ast.Node ):
    
    def __init__(self, decorators, node_name, clargnames ):
        self.decorators = decorators
        self.name = node_name
        self.argnames = clargnames
    
    def __repr__(self):
        return "CLProtoType( %r, %r, %r )" %( self.decorators, self.name, self.argnames)
    
    def getChildren(self):
        
        yield self.node_name 
        yield self.decorators
        yield self.clargnames
    
    def getChildNodes(self):
        
        yield self.node_name 
        yield self.decorators
        yield self.clargnames

class CLStructDef( ast.Node ):
    
    def __init__(self, string, lineno ):
        self.string = string
        self.lineno = lineno
    
    def getChildren(self):
        
        yield self.string 
    
    def getChildNodes(self):
        return []
    
    def __repr__(self):
        return "CLStructDef( %r )" %self.string
        
class CLMod(ast.Node):
    def __init__(self, left, right, ltype, rtype, lineno):
        self.left = left
        self.right = right
        self.ltype = ltype
        self.rtype = rtype
        self.lineno = lineno
        
    def getChildren(self):
        yield left
        yield right
        
    def getChildNodes(self):
        yield left
        yield right
        
    def __repr__(self):
        return "CLMod( %r, %r )" % (self.left, self.right)
