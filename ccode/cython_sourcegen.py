'''
Created on Jul 18, 2011

@author: sean
'''
from __future__ import print_function
from asttools import Visitor
from string import Formatter
from StringIO import StringIO
import numpy as np
import _ast
from asttools.type_tree import TypeTree

class ASTFormatter(Formatter):
    def __init__(self, argtypes, defined_locals):
        self.argtypes = argtypes
        self.defined_locals = defined_locals
    def format_field(self, value, format_spec):
        if format_spec == 'node':
            gen = ExprSourceGen(self.argtypes, self.defined_locals)
            gen.visit(value)
            return gen.dumps()
        elif format_spec == 'type':
            return self.typestr(value)
        elif value == '':
            return value
        else:
            return super(ASTFormatter, self).format_field(value, format_spec)

    def get_value(self, key, args, kwargs):
        if key == '':
            return args[0]
        elif key in kwargs:
            return kwargs[key]
        elif isinstance(key, (int, long)):
            return args[key]
        raise Exception

    def typestr(self, ctype):

        dtype = np.dtype(ctype)

        if dtype.str == '<i4':
            return 'long'
        elif ctype is object:
            return 'object'


class ExprSourceGen(Visitor):
    def __init__(self, argtypes, defined_locals=None):
        self.argtypes = argtypes
        self.out = StringIO()
        self.defined_locals = set() if defined_locals is None else defined_locals
        self.formatter = ASTFormatter(self.argtypes, self.defined_locals)
        self.indent = '    '
        self.level = 0

    def dump(self, file):
        self.out.seek(0)
        print(self.out.read(), file=file)

    def dumps(self):
        self.out.seek(0)
        value = self.out.read()
        return value

    def print(self, line, *args, **kwargs):
        line = self.formatter.format(line, *args, **kwargs)
        prx = self.indent * self.level
        print(prx, line, sep='', end='', file=self.out)


    def visitName(self, node):
        if isinstance(node.ctx, _ast.Param):
            ctype = self.argtypes[node.id]
            self.print('{type:type} {id}', type=ctype, id=node.id)
#        elif isinstance(node.ctx, _ast.Store):
#            ctype = node.ctype.resolve(self.argtypes)
##            ctype = self.argtypes[node.id]
#            self.print('{type:type} {id};\n', type=ctype, id=node.id)
        else:
            self.print(node.id)

    def visitCall(self, node):
        args = [self.formatter.format('{:node}', arg) for arg in  node.args]
        args = ','.join(args)

        self.print('{0:node}({1})', node.func, args)
        
    def visitAttribute(self, node):
        self.print('{0:node}.{1}' , node.value, node.attr)

    def visitarguments(self, node):
        args = list(node.args)
        arg = args.pop(0)
        self.visit(arg)
        while args:
            self.print(", ")
            arg = args.pop(0)
            self.visit(arg)

    def visitBinOp(self, node):
        self.print('({0:node} {1:node} {2:node})', node.left, node.op, node.right)

    def visitAdd(self, node):
        self.print('+')

class Indenter(object):
    def __init__(self, gen):
        self.gen = gen

    def __enter__(self):
        self.gen.print(' \n')
        self.gen.level += 1

    def __exit__(self, *args):
        self.gen.print('\n')
        self.gen.level -= 1
        self.gen.print('\n')

class CythonSourceGen(ExprSourceGen):

    @property
    def indenter(self):
        return Indenter(self)
    @property
    def brackets(self):
        return Indenter(self)

    def print_lines(self, lines,):
        prx = self.indent * self.level
        for line in lines:
            print(prx, line, sep='', file=self.out)

    def visitFunctionDef(self, node):

        ctype = node.return_type.resolve(self.argtypes)

        self.print('def {name}({args:node}):' , returns=ctype, name=node.name, args=node.args)

        with self.brackets:
            for stmnt in node.body:
                self.visit(stmnt)

    def visitAssign(self, node):

        targets = []
        for target in node.targets:

            targets.append(self.formatter.format('{:node}', target))

            if isinstance(target, _ast.Name) and isinstance(target.ctx, _ast.Store):
                if target.id not in self.defined_locals:
                    self.defined_locals.add(target.id)
                    ctype = target.ctype.resolve(self.argtypes)
                    self.print('cdef {0:type} {1}\n', ctype, target.id)

        self.print('{} = {value:node}\n' , ' = '.join(targets), value=node.value)

        pass #node.targets = 

    def visitReturn(self, node):
        self.print('\n')
        self.print('return {value:node}\n', value=node.value)

    def visitExpr(self, node):
        self.print('{:node}\n', node.value)

import tempfile

def cythonize(**cdefs):
    def decorator(func):
        
        from decompile import decompile_func
        ast = decompile_func(func)

        mutator = TypeTree()

        mutator.visit(ast)

        gen = CythonSourceGen(cdefs)

        gen.visit(ast)

        fname = 'cythonize_%s' % (func.func_name)

        from os.path import join
        tempfile.mkdtemp()

        pyx_file = join(tempfile.tempdir, '%s.pyx' % fname)
        c_file = join(tempfile.tempdir, '%s.c' % fname)
        o_file = join(tempfile.tempdir, '%s.o' % fname)
        so_file = join(tempfile.tempdir, '%s.so' % fname)

        gen.dump(open(pyx_file, 'w'))

        from Cython.Compiler.Main import compile_single, CompilationOptions

        compile_single(pyx_file, CompilationOptions(output_file=c_file))

        from subprocess import Popen

        from distutils.sysconfig import get_config_vars

        config_vars = get_config_vars()

        Popen('{CC} {CFLAGS} -I{CONFINCLUDEPY} -c {input} -o {output}'.format(input=c_file, output=o_file, **config_vars),
              shell=True).wait()
        Popen('{BLDSHARED} {CFLAGS} {input} -o {output}'.format(input=o_file, output=so_file, **config_vars),
              shell=True).wait()

        import sys

        sys.path.insert(0, tempfile.tempdir)

        cython_mod = __import__(fname)

        new_func = getattr(cython_mod, func.func_name)

        return new_func

    return decorator
