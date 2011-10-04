'''
Created on Jul 26, 2011

@author: sean
'''
from __future__ import print_function
from asttools import Visitor
from StringIO import StringIO
from string import Formatter
import weakref
import _ast
import ctypes
from ccode.buffer import ComplexType, Buffer
import inspect


ctype_map = {
             ctypes.c_int: 'int',
             ctypes.c_long: 'long',
             ctypes.c_float: 'float',
             int: 'int',
             float: 'float',
             }

def type_to_str(ctype):
    if ctype is None:
        return 'void'
    elif ctype in ctype_map:
        return ctype_map[ctype]
    elif inspect.isfunction(ctype):
        return '<function>' 
    elif issubclass(ctype, Buffer):
        glob = '__global ' if getattr(ctype, '_global', False) else ''
        const = 'const ' if getattr(ctype, '_const', False) else ''
        return '%s%s%s*' % (glob, const, type_to_str(ctype._type_),)
    elif issubclass(ctype, ComplexType):
        return ctype.__name__
    else:
        raise Exception('could not map ctype %r to string' % ctype)

class CLFormatter(Formatter):

    def format_field(self, value, format_spec):
        if format_spec == 'node':
            gen = OpenCLExprGen()
            gen.visit(value)
            return gen.dumps()
        elif format_spec == 'type':
            return self.typestr(value)
        elif value == '':
            return value
        else:
            return super(CLFormatter, self).format_field(value, format_spec)

    def get_value(self, key, args, kwargs):
        if key == '':
            return args[0]
        elif key in kwargs:
            return kwargs[key]
        elif isinstance(key, (int, long)):
            return args[key]
        raise Exception

    def typestr(self, ctype):
        return type_to_str(ctype)

class IndentContext(object):
    def __init__(self, sourcegen):
        self.sourcegen = weakref.ref(sourcegen)

class CodeBlockIndenter(IndentContext):

    def __enter__(self):
        sourcegen = self.sourcegen()
        sourcegen.print('{{\n', level=0)
        self.old_level = sourcegen.level
        sourcegen.level += 1

    def __exit__(self, *args):

        sourcegen = self.sourcegen()
        sourcegen.print('\n')
        sourcegen.level -= 1
        sourcegen.print('}}\n')

        return

class NoIndenter(IndentContext):

    def __enter__(self):
        sourcegen = self.sourcegen()
        self.old_level = sourcegen.level
        sourcegen.level = 0

    def __exit__(self, *args):

        sourcegen = self.sourcegen()
        sourcegen.level = self.old_level

def simple(value):
    def vistNode(self, node):
        with self.no_indent:
            self.print(value, **node.__dict__)

    return vistNode

class OpenCLExprGen(Visitor):

    def __init__(self):
        self.out = StringIO()
        self.formatter = CLFormatter()
        self.indent = '    '
        self.level = 0

    def print(self, line, *args, **kwargs):

        line = self.formatter.format(line, *args, **kwargs)

        level = self.level if kwargs.get('level') is None else kwargs.get('level')

        prx = self.indent * level
        print(prx, line, sep='', end='', file=self.out)

    def dumps(self):
        self.out.seek(0)
        return self.out.read()

    @property
    def no_indent(self):
        return NoIndenter(self)

    def visitarguments(self, node):
        with self.no_indent:
            args = list(node.args)
            
            if args:
                arg = args.pop(0)
                self.visit(arg)
            while args:
                self.print(', ')
                arg = args.pop(0)
                self.visit(arg)

    def visitName(self, node):

        with self.no_indent:
            if isinstance(node.ctx, _ast.Param):
                self.print('{type:type} {id}', type=node.ctype, id=node.id)
            else:
                self.print('{id}', id=node.id)

    def visitBinOp(self, node):
        with self.no_indent:
            self.print('({left:node} {op:node} {right:node})', **node.__dict__)

    visitAdd = simple('+')
    visitMult = simple('*')
    visitSub = simple('-')
    visitDiv = simple('/')

    visitNotEq = simple('!=')


    def visitCall(self, node):
        brace = '()'
        with self.no_indent:
            if node.cast:
                if node.cast == 'complex':
                    brace = '{}'
                self.print('({:type}){brace}', node.func.type, brace=brace[0])
            else:
                self.print('{:node}(', node.func)

            args = list(node.args)

            if args:
                arg = args.pop(0)
                self.print('{:node}', arg)
            while args:
                arg = args.pop(0)
                self.print(', {:node}', arg)

            self.print('{brace}', brace=brace[1])

    def visitNum(self, node):
        self.print('{!r}' , node.n)


    def visitSubscript(self, node):

        self.print('{0:node}[{1:node}]' , node.value, node.slice)

    def visitIndex(self, node):
        self.print('{0:node}' , node.value)

    def visitCompare(self, node):
        with self.no_indent:
            self.print('({0:node}' , node.left)

            ops = zip(node.ops, node.comparators)

            op, cmp = ops.pop(0)
            self.print(' {0:node} {1:node}', op, cmp)

            while ops:
                op, cmp = ops.pop(0)
                self.print(' {0:node} {1:node}', op, cmp)

            self.print(')')

    def visitIfExp(self, node):
        self.print('(({0:node}) ? ({1:node}) : ({2:node}))', node.test, node.body, node.orelse)

    def visitAttribute(self, node):
        self.print("{0:node}.{1}", node.value, node.attr)

class OpenCLSourceGen(OpenCLExprGen):


    @property
    def code_block(self):
        return CodeBlockIndenter(self)


    def visitFunctionDef(self, node):
        self.print('{funcattr}{type:type} {name}({args:node}) ', funcattr=node.func_attr, name=node.name, args=node.args, type=node.return_type)

        with self.code_block:
            self.newln()
            for decl in node.forward_declarations:
                self.visit(decl)
                self.newln()
            self.newln()
            for expr in node.body:
                self.visit(expr)
                self.newln()

    def visitCDec(self, node):
        self.print('{type:type} {id}' , type=node.type, id=node.id)

        if node.initial_value is not None:
            self.print(' = {0:node}' , node.initial_value, level=0)

        self.print(';', level=0)



    def visitExpr(self, node):
        self.print('') #write indent
        self.visit(node.value)
        self.print(';', level=0) #write indent

    def visitAssign(self, node, end=';'):

        self.print('')

        targets = list(node.targets)
        target = targets.pop(0)

        with self.no_indent:
            self.visit(target)
            self.print(' = ')

            while targets:
                self.visit(target)
                self.print(' = ')

            self.visit(node.value)
            self.print(end)

    def visitAugAssign(self, node, end=';'):

        self.print("{0:node} {1:node}= {2:node}{end}", node.target, node.op, node.value, end=end)

    def visitReturn(self, node):
        if isinstance(node.value, _ast.Name) and node.value.id == 'None':
            self.print('return;')
        else:
            self.print('return {:node};', node.value)

    def newln(self):
        self.print('\n', level=0)

    def visitModule(self, node):
        self.print('\n')
        self.print('// This is an automatically generated OpenCL module')
        for child in node.body:
            self.print('\n')
            self.print('\n')
            self.visit(child)

    def visitIf(self, node):
        self.print('if ({test:node}) ', test=node.test)

        with self.code_block:
            for item in node.body:
                self.visit(item)
            self.newln()
        if len(node.orelse) == 1 and isinstance(node.orelse[0], _ast.If):
            self.print('else ')
            self.visit(node.orelse[0])
            self.newln()
        elif node.orelse:
            self.print('else ')
            with self.code_block:
                for item in node.orelse:
                    self.visit(item)
            self.newln()

    def visitFor(self, node):
        self.print('for (')
        with self.no_indent:
            self.print('{:type} ', node.iter.assign.targets[0].ctype)
            self.visit(node.iter.assign)
            self.print(' ')

            self.visit(node.iter.test)
            self.print('; ')

            self.visit(node.iter.inc, end='')
            self.print(') ')

        with self.code_block:
            for child in node.body:
                self.visit(child)
                self.newln()

    def visitExec(self, node):
        string = node.body.s
        self.print('// Begin Python exec statement\n')
        #no formatting
        print(string, file=self.out)
        self.newln()
        self.print('// End Python exec statement\n')

    def visitClassDef(self, node):

        self.print('typedef struct ')
        with self.code_block:
            for stmnt in node.body:
                self.visit(stmnt)
                self.newln()


        self.print('{0};\n', node.name)



