'''
Created on Jul 26, 2011

@author: sean
'''
from __future__ import print_function

from asttools import Visitor
from asttools import print_ast
from clyther.util import Ctype, clfunc, CIter, requires_slice_expansion
from ccode.buffer import Buffer, SimpleType, ComplexType
import _ast
import ctypes
import inspect

def cl_iter_size(value, subscript):
    '''
    Size of the iterable ast `value` with the
    :returns: ast node 
    '''
    ctype = value.ctype
    if issubclass(ctype, Buffer):
        return Buffer.__cl_iter_size__(value, subscript)
    else:
        return ctype.__cl_iter_size__(value, subscript)

def cl_iter_assign(value, subscript, idx):
    ctype = value.ctype
    if issubclass(ctype, Buffer):
        return Buffer.__cl_iter_assign__(value, subscript, idx)
    else:
        return ctype.__cl_iter_assign__(value, subscript, idx)

class MBody(object):
    '''
    Test class
    '''
    def __init__(self, *args):
        self._list = list(*args)

    def append(self, item):
        print('append', item)
        self._list.append(item)

    def insert(self, index, item):
        print('insert', index, item)
        import pdb;pdb.set_trace()
        self._list.insert(index, item)

    def __iter__(self):
        return iter(self._list)

class OpenCL_AST(Visitor):

    def __init__(self, filename):

        self.filename = filename

    def visit_func(self, node, cohash, scope, kernel=True):
        '''
        visit a function node and add it to the module 
        
        :param node: ast function node  
        :param cohash: hash of the code object  
        :param scope: scope object
        :param kernel: flag - is this a kernel or a device function
          
        '''
        self.scope = scope
        node.forward_declarations = []
        self.visit(node)

        if kernel:
            node.func_attr = '__kernel '
        else:
            node.func_attr = ''

        name_base = node.name
        name = name_base
        i = 0
        while scope.base.name_defined(name):
            i += 1
            name = '%s_%i' % (name_base, i)

        node.name = name

        self.scope.base.define_function(node.name, node, cohash)

    def visitFunctionDef(self, node):

        node.return_type = node.ireturn_type.resolve(self.scope)

        self.visit(node.args)

        for stmnt in node.body:
            self.visit(stmnt)

        arg_ctypes = [arg.ctype for arg in node.args.args]
#        const_ctypes = [arg.ctype for arg in node.args.args if is_const(arg.ctype)]

        node.ctype = ctypes.CFUNCTYPE(node.return_type, *arg_ctypes)
#        node.ctype.const_ctypes = const_ctypes

    def expand_slice_expr(self, node, sliced_subscripts):

        self.scope['_cl_i'] = ctypes.c_int
        _cl_i = _ast.Name(id='_cl_i', ctx=_ast.Load())
        _cl_i.ctype = ctypes.c_int

        iter_sizes = [cl_iter_size(sliced_subscript.value, sliced_subscript.slice) for sliced_subscript in sliced_subscripts]
        iter_assignments = [cl_iter_assign(sliced_subscript.value, sliced_subscript.slice, _cl_i) for sliced_subscript in sliced_subscripts]

        assign = _ast.Assign(targets=[_cl_i], value=_ast.Num(n=0))
        test = _ast.Compare(left=_cl_i, ops=[_ast.NotEq()], comparators=[iter_sizes[0]])
        inc = _ast.AugAssign(target=_cl_i, value=_ast.Num(n=1), op=_ast.Add())
        citer = CIter(assign, test, inc)


        for_ = _ast.For(target=None, iter=citer, body=[node])

        print('iter_assignment')
        for sliced_subscript, iter_assignment in zip(sliced_subscripts, iter_assignments):
            print_ast(iter_assignment)
            sliced_subscript.slice = _ast.Index(value=iter_assignment)

        self.scope.replace(node, for_)

    def visitAssign(self, node):

        self.visitDefault(node)

        sliced_subscripts = requires_slice_expansion(node)

        if sliced_subscripts:
            self.expand_slice_expr(node, sliced_subscripts)
            return
        else:

            for target in node.targets:
                if isinstance(target, _ast.Name) and target.id not in self.scope:
                    self.scope.define_var(target)


    def visitAugAssign(self, node):

        self.visitDefault(node)

        sliced_subscripts = requires_slice_expansion(node)

        if sliced_subscripts:
            self.expand_slice_expr(node, sliced_subscripts)


    def visitarguments(self, node):

        for i, arg in reversed(list(enumerate(node.args))):
            if arg.id in self.scope.constants:
                assert node.args[i] is arg
                del node.args[i]

            else:
                is_const = lambda ctype: inspect.isfunction(ctype)
                self.visit(arg)
                if is_const(arg.ctype):
                    is_const
                    del node.args[i]
                    del self.scope._locals[arg.id]
                    self.scope._constants[arg.id] = arg.ctype
                elif getattr(arg.ctype, '__extract_args__', None) is not None:
                    new_type = arg.ctype.__extract_args__()
                    print("new_type", new_type)
                    new_arg = _ast.Name(id=arg.id + '_struct', ctx=_ast.Param(), ctype=new_type)
                    node.args.insert(i + 1, new_arg)
                    assert inspect.isclass(new_type) and issubclass(new_type, ComplexType)
                    self.scope.base._add_struct(new_type)



    def visitName(self, node):
        node.ctype = node.ictype.resolve(self.scope)

    def visitExpr(self, node):
        self.visit(node.value)

    def visitDefault(self, node):
        for child in self.children(node):
            self.visit(child)

        if hasattr(node, 'ictype'):
            node.ctype = node.ictype.resolve(self.scope)

    def visitCall(self, node):

        if node.starargs or node.kwargs:
            raise Exception("openCL functions can not expand *args or **kwargs")

        for child in self.children(node):
            self.visit(child)

        keywords = {kw.arg:kw.value for kw in node.keywords}
        node.keywords = []

        return_value = node.ictype.resolve(self.scope)

        node.ctype = return_value

        if inspect.ismethod(node.ictype._func):
            assert False
#            f = copy.deepcopy(node.func)
#            value_self = f.value
#            kw = dict(lineno=0, col_offset=0)
#
#            node.func = _ast.Attribute(value=_ast.Name(id='BufferAttributes', ctx=_ast.Load(), **kw), attr='xsize', ctx=_ast.Load(), **kw)
#
#            keywords['self'] = value_self

        if node.ictype._argnames:
            argnames = node.ictype._argnames[len(node.args):]
            for name in argnames:
                value = keywords.pop(name)
                node.args.append(value)
            if keywords:
                raise TypeError('%r() got an unexpected keyword arguments %r' % (node.func, keywords))

        node.cast = False
        if self.scope.is_const(node.func):
            func = self.scope.eval(node.func)
            if inspect.ismethod(func):
                assert False
#                node.func = _ast.Name(id='BufferAttributes_xsize', ctx=_ast.Load())

            elif inspect.isfunction(func):
                func_name = self.scope.base.function_defined_as(node.ictype.function_type)
                assert func_name is not None

                for i, name in reversed(list(enumerate(node.ictype.cc_argnames))):
                    if name not in node.ictype.cc_argtypes:
                        if i < len(node.args):
                            del node.args[i]
                        else:
                            assert False
                    else:
                        pass

                node.func = _ast.Name(id=func_name, ctx=_ast.Load())



            elif issubclass(func, SimpleType):
                node.cast = 'simple'
                node.func = Ctype(type=func)

            elif issubclass(func, ComplexType):
                node.cast = 'complex'
                node.func = Ctype(type=func)

            elif issubclass(func, clfunc):
                node.func = _ast.Name(id=func._cl_name, ctx=_ast.Load())

        print("func name" , end='')
        print_ast(node.func)

    def visitFor(self, node):

        self.visit(node.target)
        self.visit(node.iter)

        if node.orelse:
            raise Exception("can not handle else stmnt yet")
        if isinstance(node.iter, _ast.Call):
            if self.scope.is_const(node.iter.func):
                ast_iter_mutator = self.scope.eval(node.iter.func)

                ast_iter_mutator.__cl_iter__(self.scope, node)

                for expr in node.body:
                    self.visit(expr)

                return

        raise Exception("unhandled iterator type")

    def visitAttribute(self, node):
        self.visit(node.value)

        if getattr(node.value.ctype, '__extract_args__', None) is not None:
            ctype = node.value.ctype.__extract_args__()
            node.value = _ast.Name(id=node.value.id + '_struct', ctx=_ast.Load(), ctype=ctype)

        return


