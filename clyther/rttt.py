'''
Run Time Type Tree (rttt)

Created on Nov 29, 2011

@author: sean
'''

import ctypes
from meta.asttools.visitors import Visitor, visit_children, Mutator
import ast
from inspect import isroutine, isclass, isfunction
from meta.asttools.visitors.print_visitor import print_ast
from clast import cast
import _ctypes
import abc
from opencl.type_formats import type_format, cdefn
import re

class cltype(object):
    __metaclass__ = abc.ABCMeta
    pass
from opencl import contextual_memory

cltype.register(contextual_memory)

class cList(cltype):
    def __init__(self, ctype):
        self.iter_type = ctype
        

class RuntimeConstant(object):
    def __init__(self, name, rtt):
        self.name = name
        self.rtt = rtt
    
    def ctype_string(self):
        return self.name
    
class RuntimeType(cltype):
    def __init__(self, name):
        self.name = name
    
            
    def __call__(self, name):
        return RuntimeConstant(name, self)
        
    def ctype_string(self):
        return self.name
    
class gentype(object):
    def __init__(self, *types):
        self.types = types
        
class RuntimeFunction(cltype):
    def __init__(self, name, return_type, *argtypes, **kwargs):
        self.name = name
        self._return_type = return_type
        self.argtypes = argtypes
        self.kwargs = kwargs
        self.__doc__ = kwargs.get('doc', None)
        
    def return_type(self, argtypes):
        if isfunction(self._return_type):
            return self._return_type(*argtypes)
        else:
            if len(argtypes) != len(self.argtypes):
                raise TypeError('openCL builtin function %r expected %i argument(s) (got %i)' % (self.name, len(self.argtypes), len(argtypes)))
            
            return self._return_type
            
    def ctype_string(self):
        return None


int_ctypes = {ctypes.c_int, ctypes.c_int32, ctypes.c_int8, ctypes.c_int16, ctypes.c_int64, ctypes.c_long , ctypes.c_longlong,
              ctypes.c_size_t, ctypes.c_ssize_t,
              ctypes.c_ubyte, ctypes.c_uint16, ctypes.c_uint64, ctypes.c_ulong, ctypes.c_ushort,
              ctypes.c_uint, ctypes.c_uint32, ctypes.c_uint8, ctypes.c_ulonglong,
              int}

unsigned_ctypes = {ctypes.c_ubyte, ctypes.c_uint16, ctypes.c_uint64, ctypes.c_ulong, ctypes.c_ushort,
                   ctypes.c_size_t, ctypes.c_ssize_t,
                   ctypes.c_uint, ctypes.c_uint32, ctypes.c_uint8, ctypes.c_ulonglong}

float_types = {ctypes.c_float, ctypes.c_double, ctypes.c_longdouble, float}

type_groups = {'unsigned': unsigned_ctypes, 'int':int_ctypes, 'float':float_types}
type_group_weight = ['unsigned', 'int', 'float']

def groupof(ctype):
    for gname, group in type_groups.items():
        if ctype in group:
            return gname
        
    return None

def same_group(left, right):
    return groupof(left) == groupof(right)

def greatest_common_type(*args):
    if len(args) == 1:
        args = args[0]
        
    if len(args) == 1:
        return args[0]
    else:
        return reduce(_greatest_common_type, args)
  
vector_len = re.compile('^\((\d)\)([f|i|d|l|L])$')

def is_vetor_type(ctype):
    return vector_len.match(type_format(ctype)) is not None

def derefrence(ctype):
    
    if isinstance(ctype, cltype):
        return ctype.derefrence()
    elif is_vetor_type(ctype):
        return ctype._type_
    elif isclass(ctype) and issubclass(ctype, _ctypes._Pointer):
        return ctype._type_
    else:
        raise NotImplementedError(slice)


def _greatest_common_type(left, right):
    
    if left == int:
        left = ctypes.c_int32
    elif left == float:
        left = ctypes.c_float
    if right == int:
        right = ctypes.c_int32
    elif right == float:
        right = ctypes.c_float
    
    if left == right:
        return left
    
    if issubclass(left, _ctypes.Array):
        if not isinstance(right, _ctypes.Array):
            return left
        else:
            raise TypeError("type conversion for vector logic is not implemented yet")
    elif issubclass(right, _ctypes.Array):
        if not isinstance(left, _ctypes.Array):
            return right
        else:
            raise TypeError("type conversion for vector logic is not implemented yet")
        
    
    elif same_group(left, right):
        return max(left, right, key=lambda ctype:ctypes.sizeof(ctype))
    else:
        size = max(ctypes.sizeof(left), ctypes.sizeof(right))
        group = max(groupof(left), groupof(right), key=lambda group:type_group_weight.index(group))
        
        test = lambda ctype: issubclass(ctype, _ctypes._SimpleCData) and ctypes.sizeof(ctype) >= size 
        ctype = min([ctype for ctype in type_groups[group] if test(ctype)], key=lambda ctype:ctypes.sizeof(ctype))

        return ctype


class rtt(object):
    def __repr__(self):
        return '%s()' % self.__class__.__name__

class const_type(rtt):
    def __init__(self, ctype):
        self._ctype = ctype
    
    def resolve(self, locls, globls):
        return self._ctype

class type_tree(rtt):
    def __init__(self, ctype_list):
        self._ctype_list = ctype_list

class parameter_type(rtt):
    def __init__(self, param_id):
        self.param_id = param_id
        
class return_type(rtt):
    pass

class local_type(rtt):
    def __init__(self, param_id):
        self.param_id = param_id
    
    def resolve(self, locls, globls):
        return eval(self.param_id, locls, globls)


type_map = {ctypes.c_float:'float',
            ctypes.c_double:'double',
            float:'double',
            ctypes.c_longdouble:'long double',
            ctypes.c_short:'short',
            ctypes.c_ushort:'unsigned short',
            ctypes.c_long:'int',
            int:'long',
            ctypes.c_ulong:'unsigned int',
            ctypes.c_byte:'char',
            ctypes.c_longlong:'long long',
            ctypes.c_ulonglong:'unsigned long long',
            ctypes.c_ubyte:'unsigned char',
            }



def str_type(ctype, defined_types):
    if ctype in defined_types:
        return defined_types[ctype]
    elif ctype in type_map:
        return type_map[ctype]
    elif isroutine(ctype):
        return None
    elif isinstance(ctype, cltype):
        return ctype.ctype_string()
    elif isinstance(ctype, str):
        return ctype
    else:
        format = type_format(ctype)
        return cdefn(format)

class TypeReplacer(Mutator):
    '''
    Replace ctype with opencl type string. 
    '''
    def __init__(self, defined_types):
        self.defined_types = defined_types
        
    def visitCVarDec(self, node):
        if not isinstance(node.ctype, cast.CTypeName):
            node.ctype = cast.CTypeName(str_type(node.ctype, self.defined_types))
        
        self.visitDefault(node)
        
    def visitCFunctionForwardDec(self, node):
        if not isinstance(node.return_type, cast.CTypeName):
            node.return_type = cast.CTypeName(str_type(node.return_type, self.defined_types))
        
        self.visitDefault(node)
            
    def visitCFunctionDef(self, node):
        if not isinstance(node.return_type, cast.CTypeName):
            node.return_type = cast.CTypeName(str_type(node.return_type, self.defined_types))
            
        self.visitDefault(node)
        
    def mutateDefault(self, node):
        if isinstance(node, ast.expr):
            if isinstance(node.ctype, RuntimeConstant):
                return cast.CName(node.ctype.name, ast.Load(), node.ctype.rtt)
        return Mutator.mutateDefault(self, node)
                
    def visitDefault(self, node):
        if isinstance(node, ast.expr):
            if not isinstance(node.ctype, cast.CTypeName):
                node.ctype = cast.CTypeName(str_type(node.ctype, self.defined_types))
        visit_children(self, node)
        
        
        

def replace_types(node):
    defined_types = {None:'void', str:'char*'}
    if isinstance(node, ast.Module):
        for statement in node.body:
            if isinstance(statement, cast.CStruct):
                defined_types[statement.ctype] = statement.id
    
    type_replacer = TypeReplacer(defined_types)
    type_replacer.mutate(node)
    type_replacer.visit(node)
    
