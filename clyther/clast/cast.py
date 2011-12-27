'''
Created on Nov 29, 2011

@author: sean
'''
import ast

class CError(Exception):
    def __init__(self, node, exc, msg):
        self.exc = exc
        self.node = node
        self.msg = msg
        Exception.__init__(self,  node, exc, msg)
    
class CTypeCast(ast.expr):
    _fields = 'value', 'ctype'
    
class CVectorTypeCast(ast.expr):
    _fields = 'values', 'ctype'
    
class Comment(ast.AST):
    _fields = 's',
    
class CGroup(ast.AST):
    _fields = 'body',
    
class CTypeName(ast.AST):
    _fields = 'typename',

class CVarDec(ast.AST):
    _fields = 'id', 'ctype',
    
class CNum(ast.Num):
    _fields = 'n', 'ctype'
    
class CStr(ast.Str):
    _fields = 's', 'ctype'
    
class CCall(ast.Call):
    _fields = 'func', 'args', 'keywords', 'ctype'
    
class CReturn(ast.AST):
    _fields = 'value', 'ctype'
    
class CFunctionForwardDec(ast.AST):
    _fields = 'name', 'args', 'return_type'
    
class CFunctionDef(ast.AST):
    _fields = 'name', 'args', 'body', 'decorator_list', 'return_type'
        
class CName(ast.Name):
    _fields = 'id', 'ctx', 'ctype'

class CBinOp(ast.AST):
    _fields = 'left', 'op', 'right', 'ctype'

class CUnaryOp(ast.AST):
    _fields = 'op', 'operand', 'ctype'

class ckeyword(ast.AST):
    _fields = 'arg', 'value', 'ctype'
    
class clkernel(ast.AST):
    _fields = ()

class CSubscript(ast.Subscript):
    _fields = 'value', 'slice', 'ctx', 'ctype'
    
class CAttribute(ast.Attribute):
    _fields = 'value', 'attr', 'ctx', 'ctype'
    
class CPointerAttribute(ast.Attribute):
    _fields = 'value', 'attr', 'ctx', 'ctype'

class CIfExp(ast.IfExp):
    _fields = 'test', 'body', 'orelse', 'ctype'
    
class CCompare(ast.Compare):
    _fields = 'left', 'ops', 'comparators', 'ctype'

class CFor(ast.AST):
    _fields = 'init', 'condition', 'increment', 'body', 'orelse'

class CStruct(ast.AST):
    _fields = "id", 'declaration_list'
    
class CAssignExpr(ast.expr):
    _fields = 'targets', 'value', 'ctype'
    
class CAugAssignExpr(ast.expr):
    _fields = 'target', 'op', 'value', 'ctype'

class CList(ast.List):
    _fields = 'elts', 'ctx', 'ctype'


class CBoolOp(ast.BoolOp):
    _fields = 'op', 'values', 'ctype'

#===============================================================================
# 
#===============================================================================
class FuncPlaceHolder(object):
    def __init__(self, name, key, node):
        self.name = name
        self.key = key
        self.node = node
        
    def __repr__(self):
        return 'placeholder(%r)' % (self.name)

def n(node):
    return {'lineno':node.lineno, 'col_offset':node.col_offset}


def build_forward_dec(func_def):
    return CFunctionForwardDec(func_def.name, func_def.args, func_def.return_type)



    



