'''
Created on Jul 25, 2011

@author: sean


'''
from __future__ import print_function

from cly_kernel import kernel, global_work_size, local_work_size

from clyther.array.functions import arange, ones, empty_like


#from StringIO import StringIO
#from meta.asttools import Visitor, print_ast
#from ccode.type_tree import TypeTree, format_args
#from clyther.scope import Scope
#from clyther.sourcegen import OpenCLSourceGen, type_to_str
#from decompile import decompile_func
#from mutator import OpenCL_AST
#from os.path import splitext
#from util import *
#import _ast
#import _ctypes
#import inspect
#import marshal
#import numpy as np
#import pyopencl as cl #@UnresolvedImport
#import struct
#import time
#import weakref
#from clyther.clydb import FileDB
#
#
#def format_argctypes(func, cdefs, kwcdefs):
#    '''
#    returns a dictionary of keyword arguemens from positional and 
#    keyword arguments
#    
#    :param func: a function 
#    :param cdefs: positional arguments
#    :param kwcdefs: keyword arguments
#     
#    '''
#    
#
#    code = func.func_code
#
#    argnames = code.co_varnames[:code.co_argcount]
#
#    return format_args(argnames, cdefs, kwcdefs)
#
#
#def bind(global_size, local_size=None):
#    '''
#    decorator to bind global_size, local_size to be dependant 
#    on the arguments.
#    '''
#    def decorator(py_kernel):
#        py_kernel.set_binding(global_size, local_size)
#        return py_kernel
#
#    return decorator
#
#def kernel(**cdefs):
#    '''
#    decorator to create a opencl kernel from a 
#    python function.
#    '''
#    def decorator(func):
#        return PyKernel(func, cdefs)
#
#    return decorator
#
#class ComileTimeClosure(object):
#    def __init__(self, value):
#        self.value = value
#
#
#class PyKernel(object):
#    '''
#    Intermediat object to store the python function 
#    before the cdefs have been determined 
#    '''
#    use_cache = True
#    def __init__(self, func, cdefs):
#        self._cdefs = cdefs
#        self._func = func
#
#        self._global_size_bind = None
#        self._local_size_bind = None
#
#        self._ast = None
#
#    @property
#    def name(self):
#        self._func.func_name
#
#    @property
#    def ast(self):
#        if self._ast is None:
#            self._ast = decompile_func(self._func)
#
#        return self._ast
#
#    def set_binding(self, global_size, local_size=None):
#        self._global_size_bind = global_size
#        self._local_size_bind = local_size
#
#    def db(self):
#        filename = self._func.func_code.co_filename
#
#        name, _ = splitext(filename)
#        return FileDB(name + '.cly', name)
#
#    def split_constants(self, kwcdefs):
#        '''
#        remove the constant types from a dict.
#        
#        constant types are functions and types. 
#        '''
#        constants = {}
#
#        for key, value in kwcdefs.items():
#            if inspect.isfunction(value):
#                kwcdefs.pop(key)
#                constants[key] = value
#            elif isinstance(value, SimpleType):
#                kwcdefs.pop(key)
#                constants[key] = value
#
#        return constants
#
#    def compile_no_cache(self, ctx, **kwcdefs):
#        '''
#        kernel compilation steps:
#         
#         * convert positional and keyword arguments to dict.
#         * decompile function and create type tree.
#         * create c_ast module node.  
#         * get global and argument types 
#             * define complex types and functions. if not in module level scope
#             * Remove constant arguments.
#         * convert python ast to opencl ast.
#         *  
#
#        '''
##        constants = self.split_constants(kwcdefs)
#
#        module = _ast.Module(body=[], lineno=0, col_offset=0)
#
#        scope = Scope('<module>', node=module, globals=self._func.func_globals, constants={}, locals={})
#
#        scope.make_function(self._func, kwcdefs, True)
#
#        gen = OpenCLSourceGen()
#        gen.visit(module)
#
#        src = gen.dumps()
#        import tempfile
#
#        try:
#            prog = cl._cl._Program(ctx, src).build()
#        except:
#            tmp = tempfile.mktemp('.cl', 'source')
#            open(tmp, 'w').write(src)
#            print( " wrote output to %r" % (tmp))
#            raise
#
#        return CompiledKernel(self._func, prog, argctypes=kwcdefs, src=src)
#
#    def compile(self, ctx, *cdefs, **kwcdefs):
#        '''
#        Like compile 
#        '''
#        _cdefs = format_argctypes(self._func, cdefs, kwcdefs)
#
#        if type(self).use_cache:
#
#            codehash = hash(self._func.func_code)
#
#            arghash = tuple(((name, type_to_str(_cdefs[name])) for name in sorted(_cdefs.keys())))
#
#            db = self.db()
#            key = (ctx, arghash, codehash)
#
#            if key not in db:
#                db[key] = self.compile_no_cache(ctx, **_cdefs)
#                print("NOT using Cached Value")
#            else:
#                print("using Cached Value")
#
#            return db[ctx, self._func, _cdefs]
#        else:
#            return self.compile_no_cache(ctx, **_cdefs)
#
#class Undefined(object): pass
#
#class CompiledKernel(object):
#    '''
#    holds a pyopencl kernel object. 
#    '''
#    def __init__(self, func, prog, argctypes, src):
#        self.func = func
#        self.prog = prog
#        self.argctypes = argctypes
#        self.src = src
#
#    @property
#    def name(self):
#        return self.func.func_name
#
#    @property
#    def kernel(self):
#        return getattr(self.prog, self.name)
#
#
#    def raw(self):
#
#        raw_data = {}
#        bin = self.prog.get_info(cl.program_info.BINARIES)
#        raw_data['bin'] = bin
#        raw_data['src'] = self.src
#
#        return raw_data
#
#    def coerse(self, arg, ctype):
#
#        if not isinstance(arg, ctype):
#            return ctype(arg)
#        return arg
#
#    def __call__(self, queue, global_size, local_size, *args, **kwargs):
#
#        kwargs = format_argctypes(self.func, args, kwargs)
#        args = self.format_args(kwargs)
#
#        self.kernel(queue, global_size, local_size, *args)
