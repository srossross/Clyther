'''
Created on Jul 27, 2011

@author: sean
'''
import _ast
import ctypes
import abc
import _ctypes
from asttools import Visitor
from ccode.buffer import ComplexType, SimpleType


class OpenCLException(Exception): pass
class CompileError(OpenCLException): pass

class NodeRecorder(Visitor):
    def __init__(self, Node):
        self.Node = Node
        self.subscripts = []

    def visitDefault(self, node):

        seen_node = []
        for child in self.children(node):
            seen_node.append(self.visit(child))

        return any(seen_node)

    def visitSubscript(self, node):

        if self.visitDefault(node):
            self.subscripts.append(node)
            return True
        else:
            return False

    def visitSlice(self, node):
        return True

def requires_slice_expansion(node):

    rec = NodeRecorder(_ast.Slice)
    rec.visit(node)
    return rec.subscripts

class NameRecorder(Visitor):
    def __init__(self):
        self.names = set()
    def visitDefault(self, node):
        for child in self.children(node):
            self.visit(child)

    def visitName(self, node):
        self.names.add(node.id)

class Reductor(Visitor):
    def __init__(self, scope):
        self.scope = scope

    def children_setter(self, node):
        for field in node._fields:
            value = getattr(node, field)
            if isinstance(value, (list, tuple)):
                for i, item in enumerate(value):
                    if isinstance(item, _ast.AST):

                        def setlst(new_value):
                            value[i] = new_value
                        yield setlst, item
                    else:
                        pass
            elif  isinstance(value, _ast.AST):
                def setnode(new_value):
                    setattr(node, field, new_value)
                yield setnode, value
        return

    def visitDefault(self, node):

        if self.scope.is_const(node):
            print(node, self.scope.eval(node))

        for setter, child in self.children_setter(node):

            setter(self.visit(child))

        return node

    def visitAttribute(self, node):
        if self.scope.is_const(node):
            print(self.scope.eval(node))
            assert False
        else:
            return node


def get_names(node):
    rec = NameRecorder()
    rec.visit(node)
    return rec.names


#===============================================================================
# 
#===============================================================================

def clPOINTER(ctype, _global=False, const=False):
    ptr = ctypes.POINTER(ctype)
    ptr._global = _global
    ptr._const = const

    return ptr


class OpenCLType(type):
    __metaclass__ = abc.ABCMeta


ComplexType.register(ctypes.Structure)

SimpleType.register(ctypes.c_int)
SimpleType.register(int)
SimpleType.register(ctypes.c_float)
SimpleType.register(float)

class CDec(_ast.AST):
    _fields = ('id', 'type', 'initial_value')

class CIter(_ast.AST):
    _fields = ('assign', 'test', 'inc')

class Ctype(_ast.AST):
    _fields = ('type',)

def range_args(arg_list):
    if len(arg_list) == 1:
        return _ast.Num(n=0), arg_list[0], _ast.Num(n=1)
    elif len(arg_list) == 2:
        return arg_list[0], arg_list[1], _ast.Num(n=1)
    elif len(arg_list) == 3:
        return arg_list
    else:
        raise Exception("range has too many arguments")



class clfunc(_ctypes.CFuncPtr):
    _flags_ = 0

class get_global_id(clfunc):
    _flags_ = 0
    _restype_ = ctypes.c_int
    _cl_name = 'get_global_id'
