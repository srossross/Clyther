'''
Created on Dec 2, 2011

@author: sean
'''
from clyther.clast import cast
from clyther.clast.cast import build_forward_dec, FuncPlaceHolder, n
from clyther.clast.visitors.returns import returns
from clyther.pybuiltins import builtin_map
from clyther.rttt import greatest_common_type, cltype
from inspect import isroutine, isclass, ismodule
from meta.asttools.visitors import Visitor
from meta.asttools.visitors.print_visitor import print_ast
from meta.decompiler import decompile_func
from opencl import global_memory
from opencl.type_formats import type_format
import __builtin__ as builtins
import _ctypes
import ast
import ctypes
import re

class CException(Exception): pass

var_builtins = set(vars(builtins).values())


class RuntimeFunction(cltype):
    def __init__(self, name, return_type, *argtypes):
        self.name = name
        self.return_type = return_type
        self.argtypes = argtypes
        
    def ctype_string(self):
        return None


def dict2hashable(dct):
    return tuple(sorted(dct.items(), key=lambda item:item[0]))

def is_slice(slice):
    if isinstance(slice, ast.Index):
        return False
    else:
        raise NotImplementedError(slice)

vector_len = re.compile('^\((\d)\)([f|i|d|l|L])$')

def is_vetor_type(ctype):
    return vector_len.match(type_format(ctype)) is not None

def getattrtype(ctype, attr):
    if isclass(ctype) and issubclass(ctype, _ctypes.Structure):
        return dict(ctype._fields_)[attr]
    elif ismodule(ctype):
        return getattr(ctype, attr)
    elif isinstance(ctype, global_memory):
        return getattr(ctype, attr)
    elif is_vetor_type(ctype):
        return derefrence(ctype)
#        raise NotImplementedError("is_vetor_type", ctype, attr, derefrence(ctype))
    else:
        raise NotImplementedError("getattrtype", ctype, attr)
    
def derefrence(ctype):
    
    if isinstance(ctype, cltype):
        return ctype.derefrence()
    elif is_vetor_type(ctype):
        return ctype._type_
    elif isclass(ctype) and issubclass(ctype, _ctypes._Pointer):
        return ctype._type_
    else:
        raise NotImplementedError(slice)

class Typify(Visitor):
    def __init__(self, argtypes, globls):
        self.globls = globls
        self.argtypes = argtypes
        self.locls = argtypes.copy()
        
        self.function_calls = {}
        
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
            raise CException()
        
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
            raise KeyError() 
        
    def visitName(self, node, ctype=None):
        if isinstance(node.ctx, ast.Param):
            ctype = self.argtypes[node.id]
            return cast.CName(node.id, ast.Param(), ctype, **n(node))
        elif isinstance(node.ctx, ast.Load):
            ctype = self.scope(node.id)
            return cast.CName(node.id, ast.Load(), ctype, **n(node))
        elif isinstance(node.ctx, ast.Store):
            assert type is not None
            
            if node.id in self.locls:
                ectype = self.locls[node.id]
                ctype = greatest_common_type(ctype, ectype)
                
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
        type_map = {int:ctypes.c_long, float:ctypes.c_double}
        num_type = type(node.n)
#        ctype = rttt.const_type(type_map[num_type])
        return cast.CNum(node.n, type_map[num_type], **n(node))
    
    def call_python_function(self, node, func, args, keywords):
        
        args = list(self.visit_list(node.args))
        keywords = list(self.visit_list(node.keywords))

        func_ast = decompile_func(func)
        
        argtypes = {}
        for keyword in keywords:
            argtypes[keyword.arg] = keyword.ctype

        for param, arg  in zip(func_ast.args.args, args):
            argtypes[param.id] = arg.ctype
            
        
        func_dict = self.function_calls.setdefault(func, {})
        hsh = dict2hashable(argtypes)
        
        if hsh not in func_dict:
            typed_ast = Typify(argtypes, func.func_globals).make_cfunction(func_ast)
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
            raise CException()
        
        expr = ast.Expression(node.func, lineno=node.func.lineno, col_offset=node.func.col_offset)
        code = compile(expr, '<nofile>', 'eval')
        func = eval(code, self.globls, self.locls) 
        
        args = list(self.visit_list(node.args))
        keywords = list(self.visit_list(node.keywords))
        
        
        
        if func in var_builtins:
            cl_func = builtin_map[func]
            return cast.CCall(node.func, args, keywords, cl_func)
        if isroutine(func):
            return self.call_python_function(node, func, args, keywords)
        else:
            func_name = self.visit(node.func)
            
            if isinstance(func_name.ctype, RuntimeFunction):
                rt = func_name.ctype
                func = rt.return_type
                func_name = cast.CName(rt.name, ast.Load(), rt)
            else:
                pass
                # possibly a type cast
                #raise Exception()
                
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
        
        attr_type = getattrtype(value.ctype, node.attr)
        
        if isinstance(node.ctx, ast.Store):
            pass
        
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
        
def typify_function(argtypes, globls, node):
    typify = Typify(argtypes, globls)
    func_ast = typify.make_cfunction(node)
    return typify.make_module(func_ast)
