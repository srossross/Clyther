'''
Created on Dec 1, 2011

@author: sean
'''
from __future__ import print_function

from meta.asttools.visitors import Visitor
import sys
from StringIO import StringIO
from string import Formatter
import ast
from meta.asttools.visitors.print_visitor import print_ast
from clyther.clast import cast

class ASTFormatter(Formatter):

    def format_field(self, value, format_spec):
        if format_spec == 'node':
            gen = GenOpenCLExpr()
            gen.visit(value)
            return gen.dumps()
        elif value == '':
            return value
        else:
            return super(ASTFormatter, self).format_field(value, format_spec)

    def get_value(self, key, args, kwargs):
        if key == '':
            return args[0]
        elif key in kwargs:
            return kwargs[key]
        elif isinstance(key, int):
            return args[key]

        key = int(key)
        return args[key]

        raise Exception

class NoIndent(object):
    def __init__(self, gen):
        self.gen = gen

    def __enter__(self):
        self.level = self.gen.level
        self.gen.level = 0

    def __exit__(self, *args):
        self.gen.level = self.level

class Indenter(object):
    def __init__(self, gen):
        self.gen = gen

    def __enter__(self):
        self.gen.print('\n', level=0)
        self.gen.level += 1

    def __exit__(self, *args):
        self.gen.level -= 1
        
class Bracer(object):
    def __init__(self, gen):
        self.gen = gen

    def __enter__(self):
        self.gen.print('{{\n', level=0)
        self.gen.level += 1

    def __exit__(self, *args):
        self.gen.print('\n')
        self.gen.level -= 1
        self.gen.print('}}\n')

def simple_string(value):
    def visitNode(self, node):
        self.print(value, **node.__dict__)
    return visitNode

class GenOpenCLExpr(Visitor):
    
    def __init__(self):
        self.out = StringIO()
        self.formatter = ASTFormatter()
        self.indent = '    '
        self.level = 0


    @property
    def brace(self):
        return Bracer(self)
    @property
    def indenter(self):
        return Indenter(self)

    @property
    def no_indent(self):
        return NoIndent(self)

    def dump(self, file=sys.stdout):
        self.out.seek(0)
        print(self.out.read(), file=file)

    def dumps(self):
        self.out.seek(0)
        value = self.out.read()
        return value

    def print(self, line, *args, **kwargs):
        line = self.formatter.format(line, *args, **kwargs)

        level = kwargs.get('level')
        prx = self.indent * (level if level else self.level)
        print(prx, line, sep='', end='', file=self.out)

    def visitCTypeName(self, node):
        with self.no_indent:
            self.print(node.typename)
            
    def visitarguments(self, node):
        with self.no_indent:
            i = 0
            for arg in node.args:
                if i:
                    self.print(', ')
                self.print('{0:node}', arg)
                i += 1
            
    def visitCName(self, node):
        with self.no_indent:
            if isinstance(node.ctx, ast.Param):
                self.print('{0:node} {1:s}', node.ctype, node.id)
            elif isinstance(node.ctx, ast.Load):
                self.print('{0:s}', node.id)
            elif isinstance(node.ctx, ast.Store):
                self.print('{0:s}', node.id)
            else:
                raise Exception()
             
    def visitCBinOp(self, node):
        self.print('({left:node} {op:node} {right:node})', left=node.left, op=node.op, right=node.right)
    
    visitMult = simple_string('*')
    visitAdd = simple_string('+')
    visitDiv = simple_string('/')

    def visitCNum(self, node):
        with self.no_indent:
            self.print('{!r}', node.n)
            
    def visitCCall(self, node):

        self.print('{func:node}(' , func=node.func)
        i = 0

        print_comma = lambda i: self.print(", ") if i > 0 else None
        with self.no_indent:

            for arg in node.args:
                print_comma(i)
                self.print('{:node}', arg)
                i += 1
            self.print(')')
    
    def visitCTypeCast(self, node):
        with self.no_indent:
            self.print('(({0:node}) ({1:node}))', node.ctype, node.value)
    
    def visitclkernel(self, node):
        with self.no_indent:
            self.print('__kernel')
            
    def visitIndex(self, node):
        with self.no_indent:
            self.print('{0:node}', node.value)
            
    def visitCSubscript(self, node):
        with self.no_indent:
            self.print('{0:node}[{1:node}]', node.value, node.slice)
            
    def visitCAttribute(self, node):
        with self.no_indent:
            self.print('{0:node}.{1}', node.value, node.attr)
        

class GenOpenCLSource(GenOpenCLExpr):

    def print_lines(self, lines,):
        prx = self.indent * self.level
        for line in lines:
            print(prx, line, sep='', file=self.out)
    
    def visitModule(self, node):
        self.print('// This file is automatically generated please do not edit\n\n')
        for stmnt in node.body:
            self.visit(stmnt)
            
    def visitCFunctionForwardDec(self, node):
        self.print('{0:node} {1:s}({2:node});', node.return_type, node.name, node.args)
        self.print('\n\n')
    
    def visitCFunctionDef(self, node):
        for decorator in node.decorator_list:
            self.print('{0:node}\n', decorator)
             
        self.print('{0:node} {1:s}({2:node})', node.return_type, node.name, node.args)
        with self.brace:
            for stmnt in node.body:
                self.visit(stmnt)
        self.print('\n\n')
        
    def visitReturn(self, node):
        if node.value is None:
            self.print('return;\n')
        else:
            self.print('return {0:node};\n', node.value)
        
    def visitAssign(self, node):
        targets = list(node.targets)
        self.print('{0:node} = ', targets.pop()) 
        
        with self.no_indent:
            for target in targets:
                self.print('{0:node} = ', target)
                
            self.print('{0:node};\n', node.value)
            
    def visitCVarDec(self, node):
        
        self.print('{0:node} {1};\n', node.ctype, node.id) 
        
def opencl_source(node):
    source_gen = GenOpenCLSource()
    source_gen.visit(node)
    return source_gen.dumps()
