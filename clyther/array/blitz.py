'''
Created on Dec 13, 2011

@author: sean
'''
from meta.decompiler import decompile_func
from meta.asttools.visitors import Visitor
import ast
from meta.asttools.visitors.print_visitor import print_ast

import clyther as cly
import clyther.runtime as clrt
import opencl as cl

from clyther.array.utils import broadcast_shapes

n = lambda node: {'lineno':node.lineno, 'col_offset': node.col_offset}

class BlitzVisitor(Visitor):
    
    def __init__(self, filename, func_globals):
        self.filename = filename
        self.func_globals = func_globals
        self.locls = {}
        self.count = 0
        
    
    def new_var(self):
        self.count += 1
        return 'var%03i' % self.count
    
    def visitLambda(self, node):
        body = self.visit(node.body)
        
        args = ast.arguments(args=[], vararg=None, kwarg=None, defaults=[])
        
        for var_id in sorted(self.locls.keys()):
            args.args.append(ast.Name(var_id, ast.Param(), **n(node))) 
        return ast.Lambda(args, body, **n(node))
    
    def visitDefault(self, node):
        codeobj = compile(ast.Expression(node), self.filename, 'eval')
        value = eval(codeobj, self.func_globals)
        
        var_id = self.new_var()
        
        self.locls[var_id] = value
        
        return ast.Name(var_id, ast.Load(), **n(node))
    
    def visitBinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        
        return ast.BinOp(left, node.op, right, **n(node))

blitzed_kernel_py_source = '''
def blitzed_kernel(function, out, {args}):
    gid = clrt.get_global_id(0)
    
    {arg_index}
    
    out[gid] = function({arg_values})
'''

def create_n_arg_kernel(keys):
    args = ', '.join(key for key in keys) 
    arg_values = ', '.join('%s_i' % key for key in keys) 
    arg_index = '\n    '.join('%s_i = %s[gid]' % (arg, arg) for arg in keys) 
    
    py_source = blitzed_kernel_py_source.format(args=args, arg_index=arg_index, arg_values=arg_values)

    locls = {}
    eval(compile(py_source, '', 'exec'), globals(), locls)
    
    blitzed_kernel = cly.kernel(locls['blitzed_kernel'])
    blitzed_kernel.global_work_size = eval(compile('lambda %s: [%s.size]' % (keys[0], keys[0]), '', 'eval'))

    return blitzed_kernel
     
def blitz(queue, func, out=None):
    '''
    lets get blitzed!
    '''
    func_ast = decompile_func(func)
    
    func_globals = func.func_globals.copy()
    
    if func.func_closure:
        func_globals.update({name:cell.cell_contents for name, cell in zip(func.func_code.co_freevars, func.func_closure)}) 
        
    blitzer = BlitzVisitor(func.func_code.co_filename, func_globals)
    
    blitzed = ast.Expression(blitzer.visit(func_ast))
    
    blitzed_code = compile(blitzed, func.func_code.co_filename, 'eval')
    blitzed_func = eval(blitzed_code)
    
    blitz_kernel = create_n_arg_kernel(sorted(blitzer.locls.keys()))
    
    args = {}
    
    for key, var in blitzer.locls.items():
        if not isinstance(var, cl.DeviceMemoryView):
            var = cl.from_host(queue.context, var)
        args[key] = var
        
    shape = broadcast_shapes([var.shape for var in args.values()])
    
    print "shape", shape
    
    for key, var in args.items():
        args[key] = cl.broadcast(var, shape)
        
    print "out, **args", out, args
    blitz_kernel(queue, blitzed_func, out, **args)
    
#    print blitzed_func()
    
    
    
    
    
