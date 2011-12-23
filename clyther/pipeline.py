'''
Created on Dec 22, 2011

@author: sean
'''

from clyther.clast import cast
from clyther.clast.mutators.for_loops import format_for_loops
from clyther.clast.mutators.keywords import move_keywords_to_args
from clyther.clast.mutators.placeholder_replace import resolve_functions
from clyther.clast.mutators.printf import make_printf
from clyther.clast.mutators.rm_const_params import remove_const_params
from clyther.clast.mutators.type_cast import call_type2type_cast
from clyther.clast.mutators.unpacker import unpack_mem_args
from clyther.clast.openCL_sourcegen import opencl_source
from clyther.clast.visitors.returns import return_nodes
from clyther.clast.visitors.typify import Typify
from clyther.rttt import replace_types
from meta.decompiler import decompile_func




def make_kernel(cfunc_def):
    returns = return_nodes(cfunc_def.body)
    for return_node in returns:
        return_node.value = None
    
    cfunc_def.decorator_list.insert(0, cast.clkernel())
    cfunc_def.return_type = None
    
    
def typify_function(argtypes, globls, node):
    typify = Typify(argtypes, globls)
    func_ast = typify.make_cfunction(node)
    make_kernel(func_ast)
    return typify.make_module(func_ast), func_ast


def create_kernel_source(function, argtypes):
    '''
    
    '''
    
    func_ast = decompile_func(function)
    
    globls = function.func_globals
    
    mod_ast, func_ast = typify_function(argtypes, globls, func_ast)
    
    unpack_mem_args(mod_ast, argtypes)
    # convert type calls to casts 
    # eg int(i) -> ((int) (i))
    call_type2type_cast(mod_ast)
    
    format_for_loops(mod_ast)
    
    # Remove arguments to functions that are constant
    # eg. functions modules. etc
    remove_const_params(mod_ast)
    
    #C/opencl do not accept keword arguments. 
    #This moves them to positional arguments 
    move_keywords_to_args(mod_ast)
    
    #typify created function placeholders. resolve them here 
    resolve_functions(mod_ast)
    
    make_printf(mod_ast)
    
    defaults = function.func_defaults
    
    args = [(arg.id, arg.ctype) for arg in func_ast.args.args]
    
    #replace python type objects with strings 
    replace_types(mod_ast)
    
#    mod_ast.body.insert(0, ast.Exec(cast.CStr('#pragma OPENCL EXTENSION cl_amd_printf : enable', str), None, None))
    
    #generate source
    return args, defaults, opencl_source(mod_ast), func_ast.name
    
