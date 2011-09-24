'''
Created on Sep 24, 2011

@author: sean
'''

import _ast
import ctypes
import abc
from ctypes import c_int, Structure

class SimpleType(object):
    __metaclass__ = abc.ABCMeta

class ComplexType(object):
    __metaclass__ = abc.ABCMeta

class BufferAttributes(Structure):
    _fields_ = (('size', c_int),
                ('offset', c_int),
                ('stride', c_int))


class Buffer(object):
    ctype = None
    mem_scope = None

    def from_param(self):
        pass


    @staticmethod
    def __cl_iter_size__(value, subscript):

        struct = _ast.Name(id=value.id + '_struct', ctx=_ast.Load())

        lower = _ast.Num(0) if subscript.lower is None else subscript.lower

        lower = _ast.BinOp(left=_ast.Attribute(value=struct, attr='offset', ctx=_ast.Load()), right=lower, op=_ast.Add())

        if subscript.upper:
            upper = _ast.BinOp(left=_ast.Attribute(value=struct, attr='offset', ctx=_ast.Load()), right=subscript.upper, op=_ast.Add())
        else:
            upper = _ast.BinOp(left=_ast.Attribute(value=struct, attr='offset', ctx=_ast.Load()), right=_ast.Attribute(value=struct, attr='size', ctx=_ast.Load()), op=_ast.Add())

        sub = _ast.BinOp(left=upper, right=lower, op=_ast.Sub())

        if subscript.step is None:
            return sub
        else:
            return _ast.BinOp(left=sub, right=subscript.step, op=_ast.Div())

    @staticmethod
    def __cl_iter_assign__(value, subscript, idx):
        
        struct = _ast.Name(id=value.id + '_struct', ctx=_ast.Load())

        if subscript.lower is None:
            lower = _ast.Attribute(value=struct, attr='offset', ctx=_ast.Load())
        else:
            lower = subscript.lower

        start = _ast.BinOp(left=idx, right=lower, op=_ast.Add())

        if subscript.step is None:
            return start
        else:
            return _ast.BinOp(left=start, right=subscript.step, op=_ast.Mult())

    @staticmethod
    def __extract_args__():
        return BufferAttributes


class BufferType(type):
    def __new__(cls, ctype, mem_scope=None, const=False, _global=True):
        return type.__new__(BufferType, '%sBuffer' % ctype.__name__, (Buffer,), dict(_type_=ctype, mem_scope=None, const=False, _global=True))

    def __init__(cls, ctype, mem_scope=None, const=False, _global=True):
        pass


int_p = BufferType(ctypes.c_int, _global=True)
