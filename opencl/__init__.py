'''
Created on Jul 25, 2011

@author: sean
'''
from __future__ import print_function
from decompile import decompile_func
import marshal
from os.path import splitext
from ccode.type_tree import TypeTree, format_args
from asttools import Visitor
from StringIO import StringIO
from string import Formatter
import numpy as np
import weakref
import _ast
import pyopencl as cl #@UnresolvedImport
import atexit
import _ctypes
import ctypes
import struct
import time
from mutator import OpenCL_AST
from opencl.scope import Scope
from opencl.sourcegen import OpenCLSourceGen, type_to_str
from os.path import getmtime
from os.path import exists

from util import *
import inspect
from asttools import print_ast

def format_argctypes(func, cdefs, kwcdefs):

    code = func.func_code

    argnames = code.co_varnames[:code.co_argcount]

    return format_args(argnames, cdefs, kwcdefs)


def bind(global_size, local_size=None):

    def decorator(py_kernel):
        py_kernel.set_binding(global_size, local_size)
        return py_kernel

    return decorator

def kernel(**cdefs):

    def decorator(func):
        return PyKernel(func, cdefs)

    return decorator

class ComileTimeClosure(object):
    def __init__(self, value):
        self.value = value

class FileDB(object):
    magic = 0x123abc
    __singletons__ = {}
    def __init__(self, file_key, filebase):
        self.__dict__ = type(self).__singletons__.setdefault(file_key, {})
        if not self.__dict__:
            self.init(file_key, filebase)

    def init(self, file_key, filebase):

        self.file_key = file_key

        atexit.register(self.store)

        if exists(file_key):
            with open(self.file_key, 'rb') as db:
                m = db.read(4)
                magic = struct.unpack('L', m)[0]
                if magic != self.magic:
                    self.init_no_file()
                    return

                fmodtime = struct.unpack('L', db.read(4))[0]

                if getmtime(filebase + '.py') > fmodtime:
                    self.init_no_file()
                    return

                self._file_modification_time = fmodtime
                self.modification_time = fmodtime

                self.raw_data = marshal.load(db)
        else:
            self.init_no_file()



    def init_no_file(self):

        self.modification_time = int(time.time())
        self._file_modification_time = self.modification_time - 1
        self.raw_data = {}

    def store(self):
        if self._file_modification_time == self.modification_time:
            return

        with open(self.file_key, 'wb') as db:
            m = struct.pack('L', self.magic)
            db.write(m)
            t = struct.pack('L', int(time.time()))
            db.write(t)
            marshal.dump(self.raw_data, db)

    def __contains__(self, key):
        ctx, arghash, codehash = key

        if codehash not in self.raw_data:
            return False
        if arghash not in self.raw_data[codehash]:
            return False

        return True

    def __setitem__(self, key, value):
        ctx, arghash, codehash = key

        codespec = self.raw_data.setdefault(codehash, {})

        codespec[arghash] = value.raw()

        self.modification_time = int(time.time())

    def __getitem__(self, key):
        ctx, func, cdefs = key

        codehash = hash(func.func_code)

        arghash = tuple(((name, type_to_str(cdefs[name])) for name in sorted(cdefs.keys())))

        raw = self.raw_data[codehash][arghash]

        src = raw['src']
        bin = raw['bin']

        devices = ctx.get_info(cl.context_info.DEVICES)

        prog = cl._cl._Program(ctx, devices=devices, binaries=bin)
        prog.build()

        return CompiledKernel(func, prog, cdefs, src)


class PyKernel(object):
    use_cache = True
    def __init__(self, func, cdefs):
        self._cdefs = cdefs
        self._func = func

        self._global_size_bind = None
        self._local_size_bind = None

        self._ast = None

    @property
    def name(self):
        self._func.func_name

    @property
    def ast(self):
        if self._ast is None:
            self._ast = decompile_func(self._func)

        return self._ast

    def set_binding(self, global_size, local_size=None):
        self._global_size_bind = global_size
        self._local_size_bind = local_size

    def db(self):
        filename = self._func.func_code.co_filename

        name, _ = splitext(filename)
        return FileDB(name + '.cly', name)

    def split_constants(self, kwcdefs):
        constants = {}

        for key, value in kwcdefs.items():
            if inspect.isfunction(value):
                kwcdefs.pop(key)
                constants[key] = value
            elif isinstance(value, SimpleType):
                kwcdefs.pop(key)
                constants[key] = value

        return constants

    def compile_no_cache(self, ctx, **kwcdefs):

#        constants = self.split_constants(kwcdefs)

        module = _ast.Module(body=[], lineno=0, col_offset=0)

        scope = Scope('<module>', node=module, globals=self._func.func_globals, constants={}, locals={})

        scope.make_function(self._func, kwcdefs, True)

        gen = OpenCLSourceGen()
        gen.visit(module)

        src = gen.dumps()
        import tempfile

        try:
            prog = cl._cl._Program(ctx, src).build()
        except:
            tmp = tempfile.mktemp('.cl', 'source')
            open(tmp, 'w').write(src)
            print( " wrote output to %r" % (tmp))
            raise

        return CompiledKernel(self._func, prog, argctypes=kwcdefs, src=src)

    def compile(self, ctx, *cdefs, **kwcdefs):

        _cdefs = format_argctypes(self._func, cdefs, kwcdefs)

        if type(self).use_cache:

            codehash = hash(self._func.func_code)

            arghash = tuple(((name, type_to_str(_cdefs[name])) for name in sorted(_cdefs.keys())))

            db = self.db()
            key = (ctx, arghash, codehash)

            if key not in db:
                db[key] = self.compile_no_cache(ctx, **_cdefs)
                print("NOT using Cached Value")
            else:
                print("using Cached Value")

            return db[ctx, self._func, _cdefs]
        else:
            return self.compile_no_cache(ctx, **_cdefs)

class Undefined(object): pass

class CompiledKernel(object):

    def __init__(self, func, prog, argctypes, src):
        self.func = func
        self.prog = prog
        self.argctypes = argctypes
        self.src = src

    @property
    def name(self):
        return self.func.func_name

    @property
    def kernel(self):
        return getattr(self.prog, self.name)


    def raw(self):

        raw_data = {}
        bin = self.prog.get_info(cl.program_info.BINARIES)
        raw_data['bin'] = bin
        raw_data['src'] = self.src

        return raw_data

    def coerse(self, arg, ctype):

        if not isinstance(arg, ctype):
            return ctype(arg)
        return arg

    def __call__(self, queue, global_size, local_size, *args, **kwargs):

        kwargs = format_argctypes(self.func, args, kwargs)
        args = self.format_args(kwargs)

        self.kernel(queue, global_size, local_size, *args)

