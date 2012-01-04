'''
clyther.clast.visitors.typify
-----------------------------------

Generate a typed ast from a python ast.

This is the first step in the Python -> OpenCL pipeline.
'''

from clyther.clast import cast
from clyther.clast.cast import build_forward_dec, FuncPlaceHolder, n
from clyther.clast.visitors.returns import returns
from clyther.pybuiltins import builtin_map
from clyther.rttt import greatest_common_type, RuntimeFunction, cList, \
    is_vetor_type, derefrence
from ctypes import c_ubyte
from inspect import isroutine, isclass, ismodule, isfunction, ismethod
from meta.asttools.visitors import Visitor
from meta.asttools.visitors.print_visitor import print_ast
from meta.decompiler import decompile_func
import __builtin__ as builtins
import _ctypes
import ast
import ctypes
import re
import opencl as cl

class CException(Exception): pass
class CTypeError(TypeError): pass

CData = _ctypes._SimpleCData.mro()[1]

def is_type(func_call):
    if isinstance(func_call, cl.contextual_memory):
        return True
    elif isclass(func_call) and issubclass(func_call, CData):
        return True
    else:
        return False

var_builtins = set(vars(builtins).values())

class CLAttributeError(AttributeError):
    pass

def dict2hashable(dct):
    return tuple(sorted(dct.items(), key=lambda item:item[0]))

def is_slice(slice):
    if isinstance(slice, ast.Index):
        return False
    else:
        raise NotImplementedError(slice)


def get_struct_attr(ctype, attr):
    fields = dict(ctype._fields_)
    if attr in fields:
        return fields[attr]
    elif hasattr(ctype, attr):
        return getattr(ctype, attr)
    else:
        raise CLAttributeError("type %r has no attribute %s" % (ctype, attr))

def getattrtype(ctype, attr):
    '''
    Get the ctype of an attribute on a ctype 
    '''
    if isclass(ctype) and issubclass(ctype, _ctypes.Structure):
        return get_struct_attr(ctype, attr)
        
    elif ismodule(ctype):
        return getattr(ctype, attr)
    elif isinstance(ctype, cl.contextual_memory):
        if ctype.ndim == 0:
            return getattrtype(ctype.ctype, attr)
        else:
            return getattr(ctype, attr)
    elif is_vetor_type(ctype):
        return derefrence(ctype)
#        raise NotImplementedError("is_vetor_type", ctype, attr, derefrence(ctype))
    elif hasattr(ctype, attr):
        return getattr(ctype, attr)
    else:
        raise CLAttributeError("type %r has no attribute %r" % (ctype, attr))
    

class Typify(Visitor):
    '''
    Makes a copy of an ast
    '''
    def __init__(self, name, argtypes, globls):
        self.globls = globls
        self.argtypes = argtypes
        self.locls = argtypes.copy()
        self.func_name = name
        self.function_calls = {}
    
    def visit(self, node, *args, **kwargs):
        new_node = Visitor.visit(self, node, *args, **kwargs)
        if isinstance(new_node, ast.AST):
            if not hasattr(new_node, 'lineno'): 
                new_node.lineno = node.lineno
            if not hasattr(new_node, 'col_offset'): 
                new_node.col_offset = getattr(node, 'col_offset', 0)
                
        return new_node
    
    def visitDefault(self, node):
        raise cast.CError(node, NotImplementedError, 'python ast node %r is not yet supported by clyther' % type(node).__name__)
    
    def make_cfunction(self, node):
        
        if isinstance(node, ast.FunctionDef) and node.decorator_list:
            raise CException()

        func_ast = self.visit(node)
        
        local_names = set(self.locls.keys()) - set(self.argtypes.keys())
        for local_name in local_names:
            func_ast.body.insert(0, cast.CVarDec(local_name, self.locls[local_name]))
            
        return func_ast
        
    def make_module(self, func_ast):
        mod = ast.Module([])
        
        forward = []
        body = []
        
        for func_dict in self.function_calls.values():
            for fast in func_dict.values():
                forward.append(build_forward_dec(fast))
                body.append(fast)
                
        forward.append(build_forward_dec(func_ast))
        body.append(func_ast)
        
        mod.body.extend(forward)
        mod.body.extend(body)
        
        return mod 
    
    def visitLambda(self, node):
        args = self.visit(node.args)
        body = self.visit(node.body)
        
        return_type = body.ctype
        
        new_body = [ast.Return(body)]
        return cast.CFunctionDef('lambda', args, new_body, [], return_type)
    
    def visitFunctionDef(self, node):
        #'name', 'args', 'body', 'decorator_list'
        
        args = self.visit(node.args)
        body = list(self.visit_list(node.body))
        
        return_types = returns(body)
        if len(return_types) == 0:
            return_type = None
        else:
            return_type = greatest_common_type(return_types)
        
        return cast.CFunctionDef(node.name, args, body, [], return_type)
    
    def visitarguments(self, node):
        #'args', 'vararg', 'kwarg', 'defaults'
        
        if node.kwarg or node.vararg:
            raise cast.CError(node, NotImplementedError, 'star args or kwargs')
        
        args = list(self.visit_list(node.args))
        defaults = list(self.visit_list(node.defaults))
        
        return ast.arguments(args, None, None, defaults)
    
    def visitReturn(self, node):
        value = self.visit(node.value)
        return ast.Return(value, lineno=node.lineno, col_offset=node.col_offset)
    
    def scope(self, key):
        if key in self.locls:
            return self.locls[key]
        elif key in self.globls:
            return self.globls[key]
        elif key in dir(builtins):
            return getattr(builtins, key)
        else:
            raise NameError("name %r is not defined" % (key,)) 
        
    def visitName(self, node, ctype=None):
        if isinstance(node.ctx, ast.Param):
            if node.id not in self.argtypes:
                raise CTypeError(node.id, 'function %s() requires argument %r' % (self.func_name, node.id))
            ctype = self.argtypes[node.id]
            return cast.CName(node.id, ast.Param(), ctype, **n(node))
        elif isinstance(node.ctx, ast.Load):
            try:
                ctype = self.scope(node.id)
            except NameError as err:
                raise cast.CError(node, NameError, err.args[0])
                
            return cast.CName(node.id, ast.Load(), ctype, **n(node))
        
        elif isinstance(node.ctx, ast.Store):
            assert type is not None
            
            if node.id in self.locls:
                ectype = self.locls[node.id]
                try:
                    greatest_common_type(ctype, ectype)
                except: # Raise a custom exception if the types are not compatible
                    raise
                ctype = ectype
                
            self.locls[node.id] = ctype
            
            return cast.CName(node.id, ast.Store(), ctype, **n(node))
        else:
            assert False
    
    def visitBinOp(self, node):
        left = self.visit(node.left)
        op = node.op
        right = self.visit(node.right)
        ctype = greatest_common_type(left.ctype, right.ctype)
        return cast.CBinOp(left, op, right, ctype)
    
    def visitkeyword(self, node):
        value = self.visit(node.value) 
        return cast.ckeyword(node.arg, value, value.ctype)
    
    def visitNum(self, node):
        type_map = {int:ctypes.c_int, float:ctypes.c_double}
        num_type = type(node.n)
#        ctype = rttt.const_type(type_map[num_type])
        return cast.CNum(node.n, type_map[num_type], **n(node))
    
    def call_python_function(self, node, func, args, keywords):

        func_ast = decompile_func(func)
        
        argtypes = {}
        for keyword in keywords:
            argtypes[keyword.arg] = keyword.ctype

        for param, arg  in zip(func_ast.args.args, args):
            argtypes[param.id] = arg.ctype
            
        
        func_dict = self.function_calls.setdefault(func, {})
        hsh = dict2hashable(argtypes)
        
        if hsh not in func_dict:
            try:
                typed_ast = Typify(func.func_name, argtypes, func.func_globals).make_cfunction(func_ast)
            except CTypeError as err:
                argid = err.args[0]
                ids = [arg.id for arg in func_ast.args.args]
                if argid in ids:
                    pos = ids.index(argid)
                else:
                    pos = '?'
                    
                raise cast.CError(node, TypeError, err.args[1] + ' at position %s' % (pos))
                
            key = (func, hsh)
            plchldr = FuncPlaceHolder(func.func_name, key, typed_ast)
            typed_ast.name = plchldr 
            func_dict[hsh] = typed_ast
        else:
            typed_ast = func_dict[hsh]
            plchldr = typed_ast.name
    
        return cast.CCall(plchldr, args, keywords, typed_ast.return_type) 
    
    def visitCall(self, node):
        #('func', 'args', 'keywords', 'starargs', 'kwargs')
        if node.starargs or node.kwargs:
            raise cast.CError(node, NotImplementedError, '* and ** args ar not supported yet')
        
        expr = ast.Expression(node.func, lineno=node.func.lineno, col_offset=node.func.col_offset)
        code = compile(expr, '<nofile>', 'eval')
        try:
            func = eval(code, self.globls, self.locls)
        except AttributeError as err:
            raise cast.CError(node, AttributeError, err.args[0])   
        
        args = list(self.visit_list(node.args))
        keywords = list(self.visit_list(node.keywords))
        if func in builtin_map:
            cl_func = builtin_map[func]
            if isinstance(cl_func, RuntimeFunction):
                argtypes = [arg.ctype for arg in args]
                try:
                    return_type = cl_func.return_type(argtypes)
                except TypeError as exc:
                    raise cast.CError(node, type(exc), exc.args[0])
                
                func_name = cast.CName(cl_func.name, ast.Load(), cl_func)
                return cast.CCall(func_name, args, keywords, return_type)
            else:
                func = self.visit(node.func)
                return cast.CCall(func, args, keywords, cl_func)
        
        
        elif isfunction(func):
            return self.call_python_function(node, func, args, keywords)
        elif ismethod(func):
            value = self.visit(node.func.value)
            return self.call_python_function(node, func.im_func, [value] + args, keywords)
        else:
            func_name = self.visit(node.func)
            
            if isinstance(func_name.ctype, RuntimeFunction):
                rt = func_name.ctype
                argtypes = [arg.ctype for arg in args]
                try:
                    func = rt.return_type(argtypes)
                except TypeError as exc:
                    raise cast.CError(node, type(exc), exc.args[0])
                func_name = cast.CName(rt.name, ast.Load(), rt)
            elif is_type(func):
                # possibly a type cast
                pass
            else:
                msg = ('This function is not one that CLyther understands. '
                       'A function may be a) A native python function. '
                       'A python built-in function registered with clyther.pybuiltins '
                       'or a ctype (got %r)' % (func))
                raise cast.CError(node, TypeError, msg)
                
            return cast.CCall(func_name, args, keywords, func) 
            
        
    
    def visitAssign(self, node):
        value = self.visit(node.value)
        
        tragets = list(self.visit_list(node.targets, value.ctype))

        assign = ast.Assign(tragets, value)
        
        return assign
    
    def visitIndex(self, node):
        value = self.visit(node.value)
        index = ast.Index(value)
        
        return index
        
    def visitSubscript(self, node, ctype=None):
        
        value = self.visit(node.value)
        slice = self.visit(node.slice)
        
        if is_slice(slice):
            ctype = value.ctype
        else:
            ctype = derefrence(value.ctype)
        ctx = node.ctx
        subscr = cast.CSubscript(value, slice, ctx, ctype)
        
        return subscr
    
    def visitIfExp(self, node, ctype=None):
        test = self.visit(node.test)
        body = self.visit(node.body)
        orelse = self.visit(node.orelse)
        
        ctype = greatest_common_type(body.ctype, orelse.ctype)
        
        return cast.CIfExp(test, body, orelse, ctype)
        
    def visitAttribute(self, node, ctype=None):
        
        value = self.visit(node.value)
        
        try:
            attr_type = getattrtype(value.ctype, node.attr)
        except CLAttributeError as err:
            raise cast.CError(node, CLAttributeError, err.args[0])
        
        if isinstance(node.ctx, ast.Store):
            pass
        
        if isinstance(value.ctype, cl.contextual_memory) and value.ctype.ndim == 0:
            attr = cast.CPointerAttribute(value, node.attr, node.ctx, attr_type)
        else:
            attr = cast.CAttribute(value, node.attr, node.ctx, attr_type)
        
        return attr
    
    def visitCompare(self, node):
        # ('left', 'ops', 'comparators')
        left = self.visit(node.left)
        comparators = list(self.visit_list(node.comparators))
        
        return cast.CCompare(left, list(node.ops), comparators, ctypes.c_ubyte)
    
    def visitAugAssign(self, node):
        # 'target', 'op', 'value' 
        value = self.visit(node.value)
        target = self.visit(node.target, value.ctype)
        
        return ast.AugAssign(target, node.op, value)
        
    def visitFor(self, node):
        # 'target', 'iter', 'body', 'orelse'
        
        if node.orelse:
            raise NotImplementedError("todo: for - else")
        
        iter = self.visit(node.iter)
        target = self.visit(node.target, iter.ctype.iter_type)
        
        body = list(self.visit_list(node.body))
        
        return ast.For(target, iter, body, None)
    
    def visitPrint(self, node):
        #('dest', 'values', 'nl')
        
        if node.dest is not None:
            raise cast.CError(node, NotImplementedError, ("print '>>' operator is not allowed in openCL"))
        
        values = list(self.visit_list(node.values))
        
        return ast.Print(None, values, node.nl)
        
    def visitExec(self, node):
        # ('body', 'globals', 'locals')
        if node.globals is not None:
            raise cast.CError(node, NotImplementedError, ("exec globals is not allowed in openCL"))
        if node.locals is not None:
            raise cast.CError(node, NotImplementedError, "exec locals is not allowed in openCL")
        
        body = self.visit(node.body)
        
        return ast.Exec(body, None, None)
    
    def visitStr(self, node):
        return cast.CStr(node.s, str)
    
    def visitIf(self, node):
        #('test', 'body', 'orelse')
        test = self.visit(node.test)
        body = list(self.visit_list(node.body))
        orelse = list(self.visit_list(node.orelse))
        return ast.If(test, body, orelse)
    
    def visitWhile(self, node):
        #('test', 'body', 'orelse')
        if node.orelse:
            raise cast.CError(node, NotImplementedError, "while ... else is not yet allowed in openCL")
        
        test = self.visit(node.test)
        body = list(self.visit_list(node.body))
        
        return ast.While(test, body, None)
        
    def visitExpr(self, node):
        value = self.visit(node.value)
        return ast.Expr(value) 
    
    def visitList(self, node):
        elts = list(self.visit_list(node.elts))
        
        ltypes = [elt.ctype for elt in elts]
        ctype = greatest_common_type(ltypes)
        return cast.CList(elts, node.ctx, cList(ctype))
    
    def visitBoolOp(self, node):
        #('op', 'values')
        print node.op, node.values
        
        values = list(self.visit_list(node.values))
        
        return cast.CBoolOp(node.op, values, c_ubyte) 
     
    def visitTuple(self, node):
        
        elts = list(self.visit_list(node.elts))
        
        ltypes = [elt.ctype for elt in elts]
        ctype = greatest_common_type(ltypes)
        return cast.CList(elts, node.ctx, cList(ctype))
        
    def visitBreak(self, node):
        return ast.copy_location(ast.Break(), node)
    
    def visitContinue(self, node):
        return ast.copy_location(ast.Continue(), node)
    
    def visitUnaryOp(self, node):
        #('op', 'operand')
        operand = self.visit(node.operand)
        new_node = cast.CUnaryOp(node.op, operand, operand.ctype)
        return ast.copy_location(new_node, node)
            
def typify_function(name, argtypes, globls, node):
    typify = Typify(name, argtypes, globls)
    func_ast = typify.make_cfunction(node)
    return typify.make_module(func_ast)
