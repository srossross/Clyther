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
             
    def visitCUnaryOp(self, node):
        self.print('({op:node}{operand:node})', op=node.op, operand=node.operand)
    def visitCBinOp(self, node):
        
        if isinstance(node.op, ast.Pow):
            self.print('pow({left:node}, {right:node})', left=node.left, op=node.op, right=node.right)
        else:
            self.print('({left:node} {op:node} {right:node})', left=node.left, op=node.op, right=node.right)
    
    visitMult = simple_string('*')
    visitAdd = simple_string('+')
    visitUAdd = simple_string('+')
    visitSub = simple_string('-')
    visitUSub = simple_string('-')
    visitDiv = simple_string('/')
    visitMod = simple_string('%')
    
    visitNot = simple_string('!')

    visitBitOr = simple_string('|')
    visitBitAnd = simple_string('&')
    visitBitXor = simple_string('^')
    
    visitLShift = simple_string('<<')
    visitRShift = simple_string('>>')
    
    def visitCStr(self, node):
        with self.no_indent:
            self.print('"{!s}"', node.s)
            
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
            
    def visitCVectorTypeCast(self, node):
        with self.no_indent:
            self.print('(({0:node}) (', node.ctype)
            
            
            self.print('({0:node})', node.values[0])
            
            for value in node.values[1:]:
                self.print(', ({0:node})', value)
                
            self.print('))', node.ctype)
#            self.print('(({0:node}) ({1:node}))', node.ctype)
    
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

    def visitCPointerAttribute(self, node):
        with self.no_indent:
            self.print('{0:node}->{1}', node.value, node.attr)
        
    def visitCIfExp(self, node):
        with self.no_indent:
            self.print('{0:node} ? {1:node} : {2:node}', node.test, node.body, node.orelse)
    
    def visitCCompare(self, node):
        with self.no_indent:
            self.print('({0:node}', node.left)
            
            for op, right in zip(node.ops, node.comparators):
                self.print(' {0:node} {1:node}', op, right)
                
            self.print(')')
            
    visitLt = simple_string('<')
    visitGt = simple_string('>')
    visitGtE = simple_string('>=')
    visitLtE = simple_string('<=')
    visitEq = simple_string('==')
    visitNotEq = simple_string('!=')
    
    
    def visitCAssignExpr(self, node):
        with self.no_indent:
            targets = list(node.targets)
            self.print('{0:node} = ', targets.pop()) 
            
            for target in targets:
                self.print('{0:node} = ', target)
                
            self.print('{0:node}', node.value)
        
    def visitCAugAssignExpr(self, node):
        # 'target', 'op', 'value'
        with self.no_indent:
            self.print('{0:node} {1:node}= {2:node}', node.target, node.op, node.value)

    def visitExec(self, node):
        self.print('// Begin Exec Statement\n')
        self.print('{0!s}\n', node.body.s)
        self.print('// End exec Statement\n')
            
    def visitCBoolOp(self, node):
        with self.no_indent:
            self.print('(')
            self.print('{0:node}', node.values[0])
            for value in node.values[1:]:
                self.print(' {0:node} {1:node}', node.op, value)
            self.print(')')
            
    visitAnd = simple_string('&&')
    visitOr = simple_string('||')
            
        
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
        
    def visitCStruct(self, node):
        
        self.print("typedef struct {{")
        with self.indenter:
            for dec in node.declaration_list:
                self.visit(dec)
        self.print("}} {0};\n\n", node.id)
        
    def visitAugAssign(self, node):
        # 'target', 'op', 'value'
        self.print('{0:node} {1:node}= {2:node};\n', node.target, node.op, node.value)
        
    def visitCFor(self, node):
        #'init', 'condition', 'increment', 'body', 'orelse'
        self.print('for ({0:node}; {1:node}; {2:node})', node.init, node.condition, node.increment)
        
        with self.brace:
            for statement in node.body:
                self.visit(statement)
                
    def visitExpr(self, node):
        self.print('{0:node};\n', node.value)
        
    def visitIf(self, node):
        
        self.print('if ({0:node}) {{\n', node.test)
        with self.indenter:
            for statement in node.body:
                self.visit(statement)
        
        self.print('}}')
        
        if not node.orelse:
            self.print('\n')
            
        for orelse in node.orelse:
            self.print(' else ')
            if isinstance(orelse, ast.If):
                self.visit(orelse)
            else:
                self.print('{{')
                with self.indenter:
                    self.visit(orelse)
                self.print('}}\n')

    def visitWhile(self, node):
        
        self.print('while ({0:node}) {{\n', node.test)
        with self.indenter:
            for statement in node.body:
                self.visit(statement)
        
        self.print('}}\n')
        
    def visitComment(self, node):
        
        commentstr = node.s
        if '\n' in commentstr:
            assert False
        else:
            self.print('// {0!s}\n', commentstr)
            
    def visitCGroup(self, node):
        for statement in node.body:
            self.visit(statement)
            
    def visitBreak(self, node):
        self.print('break;\n')

    def visitContinue(self, node):
        self.print('continue;\n')
            
    
def opencl_source(node):
    source_gen = GenOpenCLSource()
    source_gen.visit(node)
    return source_gen.dumps()
