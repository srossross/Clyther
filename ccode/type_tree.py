'''
Created on Jul 18, 2011

@author: sean
'''
from asttools import Visitor, dont_visit
import _ast
import numpy as np
import ctypes
import _ctypes
import inspect
from buffer import Buffer
from ccode.buffer import ComplexType

class CompileTypeError(Exception):
    pass

def format_args(argnames, varargs, kwargs):
    argcdefs = dict.fromkeys(argnames)

    for argname, ctype in zip(argnames, varargs):
        argcdefs[argname] = ctype

    for argname in argcdefs.keys():
        if argname in kwargs:
            argcdefs[argname] = kwargs[argname]

    undefined_type = [name for (name, ctype) in argcdefs.items() if ctype == None]
    if len(undefined_type):
        raise Exception('arguments %r are undefined' % undefined_type)

    return argcdefs

class FType(object):
    def __init__(self, cohash, args=None, ctype=None):
        from clyther import Undefined

        self.cohash = cohash

        assert (args is None) ^ (ctype is None)


        if ctype:
            self.ctype = ctype
            self.argtypes = ctype._argtypes_
            self.restype = ctype._restype_
        else:
            self.args = args
            self.argtypes = tuple(arg[1] for arg in args)
            self.restype = Undefined


    def __eq__(self, other):
        if type(self) != type(other):
            return False

        if self.cohash != other.cohash:
            return False

        if self.argtypes != other.argtypes:
            return False

        return True

    def __hash__(self):
        return hash((self.cohash, self.argtypes))

class Type(object):
    pass


class ConcreteType(Type):
    def __init__(self, ctype):
        self.ctype = ctype
    def resolve(self, typedict, scope=None):
        return self.ctype

class CType(Type):

    def __init__(self, id):
        self.assign = None
        self.id = id

    def resolve(self, scope):
        if self.assign:
            return self.assign.resolve(scope)
        if self.id in scope:
            return scope.typeof(self.id)
        else:
            raise NameError("could not find type for name %r" % self.id)

class SubstriptType(Type):
    def __init__(self, base_type, slices):
        self.base_type = base_type
        self.slices = slices
    def resolve(self, scope):

        ctype = self.base_type.resolve(scope)

        assert issubclass(ctype, Buffer)

        if self.slices:
            return ctype
        else:
            return ctype._type_

def derefrence(ctype):
    return ctype

class CommonType(Type):
    def __init__(self, ltype, rtype):
        assert ltype is not None
        assert rtype is not None
        self.ltype = ltype
        self.rtype = rtype

    def resolve(self, scope):
        ltype = self.ltype.resolve(scope)
        rtype = self.rtype.resolve(scope)

        if ltype == rtype:
            return ltype
        elif np.dtype(ltype) > np.dtype(rtype):
            return ltype
        else:
            return rtype
        return

class ReturnType(Type):

    def __init__(self, caller_type, argtypes):
        self.caller_type = caller_type
        self.argtypes = argtypes
        self._func = None

    @property
    def _argnames(self):
        return None

    def resolve(self, scope):
        caller_type = self.caller_type.resolve(scope)
        self._func = caller_type


        if inspect.ismethod(caller_type):

            assert  False

        elif inspect.isfunction(caller_type):

            kwargs = {key:atype.resolve(scope) for key, atype in self.argtypes.items()}
            varargs = []
            i = 0
            while i in kwargs:
                varargs.append(kwargs.pop(i))
                i += 1

            code = caller_type.func_code
            argnames = code.co_varnames[:code.co_argcount]
            self.cc_argnames = argnames
            argtypes = format_args(argnames, varargs, kwargs)

            self.cc_argtypes = argtypes

            args = tuple(sorted(argtypes.items()))

            cohash = hash(caller_type.func_code)

            ftype = FType(cohash=cohash, args=args)


            func_name = scope.base.function_defined_as(ftype)

            if func_name is None:

                node = scope.make_function(caller_type, argtypes)
                self.function_type = FType(cohash, ctype=node.ctype)

            else:
                self.function_type = FType(cohash, ctype=scope.base.get_define(func_name).ctype)

            return self.function_type.restype

        elif caller_type in scope.builtin_map:
            return scope.builtin_map[caller_type]
        elif issubclass(caller_type, _ctypes.CFuncPtr):
            return caller_type._restype_
        else:
            return caller_type
#            raise Exception("Asdf")

class AttrType(Type):
    def __init__(self, ctype, attr):
        self.inner = ctype
        self.attr = attr

    def resolve(self, scope):
        inner = self.inner.resolve(scope)

        if getattr(inner, '__extract_args__', None) is not None:
            inner = inner.__extract_args__()

        if issubclass(inner, ComplexType) and self.attr in [name for (name, _) in inner._fields_]:
            ctype = [ctype for (name, ctype) in inner._fields_ if name == self.attr][0]
            return ctype
        else:
            try:
                ctype = getattr(inner, self.attr)
            except AttributeError as error:
                raise CompileTypeError(error)

            return ctype

class IterType(Type):

    def __init__(self, iter):
        self.iter_ctype = iter

    def resolve(self, scope):
        ctype = self.iter_ctype.resolve(scope)
        return ctype

class TypeTree(Visitor):

    def __init__(self, filename, **argtypes):
        self.filename = filename
#        self.argtypes = {key:CType(value) for (key,value) in argtypes.items()}
        self.local_types = {}

    def typeof(self, id):

        if id not in self.local_types:
            self.local_types[id] = CType(id)

        return self.local_types[id]


    def visitFunctionDef(self, node):
        #fields = ('name', 'args', 'body', 'decorator_list')

        self.visit(node.args)

        for stmnt in node.body:
            self.visit(stmnt)

        if isinstance(node.body[-1], _ast.Return):
            return_type = node.body[-1].ictype
        else:
            return_type = ConcreteType(None)

        node.ireturn_type = return_type


    def visitarguments(self, node):

        for arg in node.args:
            self.visit(arg)

    def visitAssign(self, node):
        self.visit(node.value)
        ctype = node.value.ictype

        for target in node.targets:
            self.visit(target)
            target.ictype.assign = ctype

    def visitBinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)

        ltype = node.left.ictype
        rtype = node.right.ictype

        node.ictype = CommonType(ltype, rtype)

    def visitName(self, node):
        node.ictype = self.typeof(node.id)

    def visitReturn(self, node):
        self.visit(node.value)
        node.ictype = node.value.ictype

    def visitExpr(self, node):
        self.visit(node.value)

    def visitCall(self, node):

        for child in self.children(node):
            self.visit(child)

        argtypes = {i:arg.ictype for i, arg in enumerate(node.args)}
        argtypes.update({keyword.arg:keyword.value.ictype for keyword in node.keywords})

        node.ictype = ReturnType(node.func.ictype, argtypes)

    def visitkeyword(self, node):
        for child in self.children(node):
            self.visit(child)

    def visitAttribute(self, node):

        self.visit(node.value)
        ctype = node.value.ictype
        node.ictype = AttrType(ctype, node.attr)

    def visitNum(self, node):
        if isinstance(node.n, int):
            node.ictype = ConcreteType(ctypes.c_long)
        elif isinstance(node.n, float):
            node.ictype = ConcreteType(ctypes.c_float)
        else:
            raise Exception('number type %r not supported yet' % (type(node.n)))

    def visitSubscript(self, node):

        self.visit(node.value)
        self.visit(node.slice)

        slices = isinstance(node.slice, _ast.Slice)

        node.ictype = SubstriptType(base_type=node.value.ictype, slices=slices)

    def visitIndex(self, node):

        self.visit(node.value)
        node.ictype = node.value.ictype

    def visitSlice(self, node):
        for child in self.children(node):
            self.visit(child)


    def visitIf(self, node):
        for child in self.children(node):
            self.visit(child)

    def visitFor(self, node):
        for child in self.children(node):
            self.visit(child)
        node.target.ictype = IterType(node.iter.ictype)

    def visitExec(self, node):
        for child in self.children(node):
            self.visit(child)

    def visitStr(self, node):
        node.ictype = ConcreteType(ctypes.c_char_p)

    def visitIfExp(self, node):
        for child in self.children(node):
            self.visit(child)

        node.ictype = CommonType(node.body.ictype, node.orelse.ictype)

    def visitAugAssign(self, node):
        for child in self.children(node):
            self.visit(child)


    visitAdd = dont_visit

def typeify(filename, node):
    TypeTree(filename).visit(node)
    