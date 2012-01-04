'''
clyther.rttt
--------------------

Run Time Type Tree (rttt)

'''

from clast import cast
from clyther.pybuiltins import builtin_map
from inspect import isroutine, isclass, isfunction
from meta.asttools.visitors import visit_children, Mutator
from meta.asttools.visitors.print_visitor import print_ast
from opencl import contextual_memory
from opencl.type_formats import type_format, cdefn
import _ctypes
import abc
import ast
import ctypes
import opencl as cl
import re

class cltype(object):
    __metaclass__ = abc.ABCMeta
    pass

cltype.register(contextual_memory)

class cList(cltype):
    def __init__(self, ctype):
        self.iter_type = ctype
        

class RuntimeConstant(object):
    '''
    define a constant value that is defined in the OpenCL runtime.
    
    :param name: the name of the constant in OpenCL.
    :param rtt: the ctype of the constant.
    
    '''
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
    '''
    a generic numeric type in OpenCL
    '''
    def __init__(self, *types):
        self.types = types
        
class ugentype(object):
    '''
    an unsigned generic numeric type in OpenCL
    '''
    def __init__(self, *types):
        self.types = types
        
class sgentype(object):
    '''
    a signed generic numeric type in OpenCL
    '''
    def __init__(self, *types):
        self.types = types
        
class RuntimeFunction(cltype):
    '''
    A function that is defined in the openCL runtime.
    
    :param name: the name of the function as per the oencl specification.
    :param return_type: Either a ctype or a function that returns a ctype
    :param argtypes: Either a ctype or a function that returns a ctype
    
    Keyword only parameters:
        :param doc: Either a ctype or a function that returns a ctype
        :param builtin: a python builtin function that is equivalent to this function
        :param emulate: A function that emulates the behavior of this function in python. 
            This argument is not required if `builtin` is given. 
    
    If `return_type` is a function it must have the same signature as the runtime function.
     
    '''
    
    def __init__(self, name, return_type, *argtypes, **kwargs):
        self.name = name
        self._return_type = return_type
        self.argtypes = argtypes
        self.kwargs = kwargs
        self.__doc__ = kwargs.get('doc', None)
        self.builtin = kwargs.get('builtin', None)
        self.emulate = kwargs.get('emulate', None)
        
        if self.builtin is not None:
            builtin_map[self.builtin] = self
        
    def return_type(self, argtypes):
        if isfunction(self._return_type):
            return self._return_type(*argtypes)
        else:
            if len(argtypes) != len(self.argtypes):
                raise TypeError('openCL builtin function %r expected %i argument(s) (got %i)' % (self.name, len(self.argtypes), len(argtypes)))
            
            return self._return_type
            
    def ctype_string(self):
        return None
    
    def __call__(self, *args):
        if self.builtin is not None:
            return self.builtin(*args)
        elif self.emulate is not None:
            return self.builtin(*args)
        else: 
            raise NotImplementedError("python can not emulate this function yet.")
         

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
  
vector_len = re.compile('^\((\d)\)([f|i|I|d|l|L])$')

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

def typeof(ctx, obj):
    if isinstance(obj, cl.MemoryObject):
        return cl.global_memory(obj.ctype, ndim=len(obj.shape), shape=obj.shape, context=ctx)
    elif isinstance(obj, cl.local_memory):
        return obj
    elif isfunction(obj):
        return obj
    
    elif isinstance(obj, int):
        return ctypes.c_int
    elif isinstance(obj, float):
        return ctypes.c_float
    elif isinstance(obj, ctypes.Structure):
        return cl.constant_memory(type(obj), 0, (), context=ctx)
#        raise NotImplementedError("ctypes.Structure as parameter")
    else:
        try:
            view = memoryview(obj)
            return cl.global_memory(view.format, ndim=len(view.shape), shape=view.shape, context=ctx)
        except TypeError:
            pass
        
        return type(obj)


def _greatest_common_type(left, right):
    if not isclass(left):
        left = type(left)
    if not isclass(right):
        right = type(right)
        
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


from opencl import cl_types
type_map = {
    cl_types.cl_char : 'char',
    cl_types.cl_char16 : 'char16',
    cl_types.cl_char2 : 'char2',
    cl_types.cl_char4 : 'char4',
    cl_types.cl_char8 : 'char8',
    cl_types.cl_double : 'double',
    cl_types.cl_double16 : 'double16',
    cl_types.cl_double2 : 'double2',
    cl_types.cl_double4 : 'double4',
    cl_types.cl_double8 : 'double8',
    cl_types.cl_float : 'float',
    cl_types.cl_float16 : 'float16',
    cl_types.cl_float2 : 'float2',
    cl_types.cl_float4 : 'float4',
    cl_types.cl_float8 : 'float8',
    cl_types.cl_half : 'half',
    cl_types.cl_int : 'int',
    cl_types.cl_int16 : 'int16',
    cl_types.cl_int2 : 'int2',
    cl_types.cl_int4 : 'int4',
    cl_types.cl_int8 : 'int8',
    cl_types.cl_long : 'long',
    cl_types.cl_long16 : 'long16',
    cl_types.cl_long2 : 'long2',
    cl_types.cl_long4 : 'long4',
    cl_types.cl_long8 : 'long8',
    cl_types.cl_short : 'short',
    cl_types.cl_short16 : 'short16',
    cl_types.cl_short2 : 'short2',
    cl_types.cl_short4 : 'short4',
    cl_types.cl_short8 : 'short8',
    cl_types.cl_uchar : 'uchar',
    cl_types.cl_uchar16 : 'uchar16',
    cl_types.cl_uchar2 : 'uchar2',
    cl_types.cl_uchar4 : 'uchar4',
    cl_types.cl_uchar8 : 'uchar8',
    cl_types.cl_uint : 'uint',
    cl_types.cl_uint16 : 'uint16',
    cl_types.cl_uint2 : 'uint2',
    cl_types.cl_uint4 : 'uint4',
    cl_types.cl_uint8 : 'uint8',
    cl_types.cl_ulong : 'ulong',
    cl_types.cl_ulong16 : 'ulong16',
    cl_types.cl_ulong2 : 'ulong2',
    cl_types.cl_ulong4 : 'ulong4',
    cl_types.cl_ulong8 : 'ulong8',
    cl_types.cl_ushort : 'ushort',
    cl_types.cl_ushort16 : 'ushort16',
    cl_types.cl_ushort2 : 'ushort2',
    cl_types.cl_ushort4 : 'ushort4',
    cl_types.cl_ushort8 : 'ushort8',

    }




def str_type(ctype, defined_types):
    if ctype in defined_types:
        return defined_types[ctype]
    elif ctype in type_map:
        return type_map[ctype]
    elif isroutine(ctype):
        return None
    elif isinstance(ctype, cl.contextual_memory):
        base_str = str_type(ctype.ctype, defined_types)
        return '%s %s*' % (ctype.qualifier, base_str)
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
        self.new_types = {}
        
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
                
                try:
                    type_repr = str_type(node.ctype, self.defined_types)
                except KeyError:
                    if isinstance(node.ctype, cl.contextual_memory):
                        ctype = node.ctype.ctype
                    else:
                        ctype = node.ctype
                        
                    base_name = 'cly_%s' % (ctype.__name__) 
                    type_repr = base_name
                    i = 0
                    while type_repr in self.defined_types.viewvalues():
                        i += 1
                        type_repr = '%s_%03i' % (base_name, i)
                        
                    self.defined_types[ctype] = type_repr
                    self.new_types[type_repr] = ctype
                    
                    if isinstance(node.ctype, cl.contextual_memory):
                        type_repr = str_type(node.ctype, self.defined_types)
                    
                node.ctype = cast.CTypeName(type_repr)
                
        visit_children(self, node)
        
        
def create_cstruct(struct_id, ctype, defined_types):
    decs = []
    
    for name, field in ctype._fields_:
        typename = cast.CTypeName(str_type(field, defined_types))
        decs.append(cast.CVarDec(name, typename))
    
    return cast.CStruct(struct_id, decs)

def replace_types(node):
    defined_types = {None:'void', str:'char*'}
    if isinstance(node, ast.Module):
        for statement in node.body:
            if isinstance(statement, cast.CStruct):
                defined_types[statement.ctype] = statement.id
    
    type_replacer = TypeReplacer(defined_types)
    
    type_replacer.mutate(node)
    type_replacer.visit(node)
    
    for name, ctype in type_replacer.new_types.items():
        c_struct = create_cstruct(name, ctype, type_replacer.defined_types)
        node.body.insert(0, c_struct)
