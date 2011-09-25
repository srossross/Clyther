'''
Created on Jul 29, 2011

@author: sean
'''
from __future__ import print_function
from opencl.mutator import OpenCL_AST
from opencl.pybuiltins import builtin_map
from opencl.util import CDec, SimpleType, ComplexType, get_names, \
    Reductor
from ccode.type_tree import TypeTree, FType
from decompile import decompile_func
import _ast
import inspect
import weakref
from asttools.mutators.replace_mutator import Replacer



class Scope(object):

    def __init__(self, namespace, node, globals, constants, locals, parent=None):

        self.namespace = namespace
        self.node = node
        self._globals = globals
        self._constants = constants
        self._locals = locals
        self._defined = {}

        self.builtin_map = builtin_map
        self.compiled_functions = {}
        self.structs = set()

        if parent is not None:
            parent = weakref.ref(parent)

        self._parent = parent

        self._inner_scopes = []

    def __str__(self):
        return '<Scope %r>' % (self.namespace)

    def define_function(self, name, node, cohash):

        assert self.base is self
        assert node.ctype is not None

        mod_scope = self.base
        mod_scope._defined[name] = node
        self.compiled_functions[FType(cohash, ctype=node.ctype)] = name

        mod_scope.node.body.append(node)

    def name_defined(self, name):
        return name in self._defined

    def get_define(self, key):
        return self._defined[key]

    def defined(self, name, ctype):

        assert self.base is self
        assert ctype is not None

        if name in self._defined:
            return self._defined[name].ctype == ctype
        else:
            return False

    @property
    def base(self):
        if self.parent is None:
            return self
        else:
            return self.parent.base

    @property
    def constants(self):
        if self._constants is None:
            return self.parent.constants
        else:
            return self._constants
    @property
    def parent(self):
        if self._parent is None:
            return None
        else:
            return self._parent()

    def inner(self, namespace, node, globals=None, locals=None, constants=None, local_names=None):

        if local_names is not None:
            locals = {}
            for item in local_names:
                locals[item] = self[item]

        scope = Scope(namespace, node, globals=globals, constants=constants, locals=locals, parent=self)

        self._inner_scopes.append(scope)
        return scope

    def __setitem__(self, item, value):
        self._locals[item] = value

    def __contains__(self, key):
        return (self.in_globals(key) or self.in_locals(key))

    def __getitem__(self, key):
        if self.in_locals(key):
            return self.get_local(key)
        else:
            return self.get_global(key)

    @property
    def globals(self):
        if self._globals is None:
            return self.parent._globals
        else:
            return self._globals

    def get_global(self, key):
        builtins = self.builtins()

        if key in self.constants:
            return self.constants[key]
        elif key in self.globals:
            return self.globals[key]
        elif key in builtins:
            return builtins[key]
        else:
            assert False, key

    def get_local(self, key):
        return self.locals[key]

    def in_globals(self, key):
        if key in self.globals:
            return True
        elif key in self.builtins():
            return True
        elif key in self.constants:
            return True

        return False

    @property
    def locals(self):
        return self._locals

    def in_locals(self, key):
        for inner in self.locals:
            if key in inner:
                return True

    def typeof(self, key):

        from opencl import Undefined
        ctype = Undefined

        if self.in_globals(key):
            value = self.get_global(key)

            if value is None:
                return None
            elif isinstance(value, SimpleType):
                if key not in self.constants:
                    self.mod.body.insert(0, CDec(id=key, type=type(value), initial_value=_ast.Num(n=value)))
                    self.constants[key] = type(value)
                ctype = type(value)
            else:
                ctype = value
        elif self.in_locals(key):
            ctype = self.get_local(key)

        if ctype is Undefined:
            raise Exception("ctype is Undefined" % ctype)

        elif inspect.isclass(ctype) and issubclass(ctype, ComplexType):
            self._add_struct(ctype)

        return ctype

    def _add_struct(self, ctype):
        if ctype not in self.structs:


            body = []

            for name, field in ctype._fields_:
                cdec = CDec(id=name, type=field, initial_value=None)
                body.append(cdec)

            class_def = _ast.ClassDef(name=ctype.__name__,
                                      bases=None,
                                      decorator_list=None,
                                      body=body)

            self.base.node.body.insert(0, class_def)

            self.structs.add(ctype)

        return ctype


    def _add_method(self, method, argtypes):
        print('add_method', method, argtypes)
        if method not in self.compiled_functions:

            ast = decompile_func(method)

            mutator = TypeTree()
            mutator.visit(ast)

            for key in self.constants.keys():
                if key in argtypes:
                    argtypes.pop(key)

            cl_mut = OpenCL_AST(self)

            cl_mut.visit_func(ast, kernel=False)

            ast.name = '%s_%s' % (method.im_class.__name__, ast.name)

            self.compiled_functions[method] = ast.return_type

        return self.compiled_functions[method]


    def make_function(self, function, argtypes, kernel=False):

        ast = decompile_func(function)

        mutator = TypeTree(function.func_code.co_filename)
        mutator.visit(ast)

        for key in self.constants.keys():
            if key in argtypes:
                argtypes.pop(key)

        cl_mut = OpenCL_AST(function.func_code.co_filename)

        inner = self.base.inner(function.func_name, ast, locals=argtypes, constants={})

        cl_mut.visit_func(ast, hash(function.func_code), scope=inner, kernel=kernel)

        return ast

    def function_defined_as(self, ftype):
        return self.compiled_functions.get(ftype, None)

    def define_var(self, node):
        assert isinstance(node, _ast.Name)

        self.node.forward_declarations.append(CDec(id=node.id, type=node.ctype, initial_value=None))

    def is_function(self, node):
        return inspect.isfunction(node.ctype)
#    def add_function(self, function, argtypes):
#
#        print("argtypes", argtypes)
#        args = tuple(sorted(argtypes.items()))
#        ftype = CLFunctionType(cohash=hash(function.func_code), args=args)
#
#        print('add_function', function, argtypes)
#
#        if not self.base.function_defined(ftype):
#            ctype = self.make_function(function, argtypes).ctype
#        else:
#            assert False
#
#        return ctype


    def builtins(self):
        builtins = self.globals.get('__builtins__', {})
        if not isinstance(builtins, dict):
            builtins = vars(builtins)
        return builtins

    def eval(self, node):
        expr = _ast.Expression(node, lineno=0, col_offset=0)
        code = compile(expr, '<string>', 'eval')

        globals = self.globals.copy()
        globals.update(self.constants)
        result = eval(code, globals)

        try:
            test = result in self.builtin_map
        except TypeError:
            'Unhashable type'
            return result

        if test:
            return self.builtin_map[result]

        return result

    def is_const(self, node):
#        if inspect.isfunction(node.ctype):
#            return True
        for name in get_names(node):
            if self.in_locals(name):
                return False
        return True

    def reduce(self, node):
        reductor = Reductor(self)
        return reductor.visit(node)

    def replace(self, old, new):
        repl = Replacer(old, new)
        repl.visit(self.node)
