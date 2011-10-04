'''
Created on Sep 25, 2011

@author: sean
'''

from asttools import Visitor, print_ast

from clyther.sourcegen import type_to_str
from decompile import decompile_func
from os.path import exists, getmtime
import atexit
import marshal
import pyopencl as cl #@UnresolvedImport
import struct
import time


class FileDB(object):
    '''
    '''
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
        from clyther import CompiledKernel
        return CompiledKernel(func, prog, cdefs, src)

