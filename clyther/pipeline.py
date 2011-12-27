'''
clyther.pipeline
----------------------


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
from clyther.clast.mutators.replace_constants import replace_constants




def make_kernel(cfunc_def):
    returns = return_nodes(cfunc_def.body)
    for return_node in returns:
        return_node.value = None
    
    cfunc_def.decorator_list.insert(0, cast.clkernel())
    cfunc_def.return_type = None
    
    
def typify_function(name, argtypes, globls, node):
    typify = Typify(name, argtypes, globls)
    func_ast = typify.make_cfunction(node)
    make_kernel(func_ast)
    return typify.make_module(func_ast), func_ast


def create_kernel_source(function, argtypes):
    '''
    Create OpenCL source code from a Python function.
    
    :param function: A pure python function
    :param argtypes: A dict of name:type for the compiler to use in optimizing the function.
    
    Steps:
        
        * Decompile to AST.:
            Get AST from python bytecode
        * Typify AST: 
            This transforms the AST in to a partially typed OpenCL AST.
            It will recursively dive into pure Python functions and add thoes to the OpenCL module.
            Function names will be replace with placeholders for the namespace conflict resolution stage.
        * Replace Constants:
            Replace Python constants with values. e.g. `math.e` -> `2.7182`
        * Unpack memobjects:
            To support multi-dimensional indexing and non contiguous memory arrays. 
            CLyther adds a uint8 to the function signature to store this information.
        * Replace calls of types to type casts e.g. int(i) -> ((int)(i))
        * Format for loops:
            only `range` or a explicit Python list is currently supported as the iterator in a for loop.
        * Remove arguments to functions that are constant. e.g. python functions. 
        * Move keyword arguments in function calls to positional arguments.
        * Resolve function place-holders
        * Make printf statements from print
        * Replace Types:
            Replace python ctype objects with OpenCL type names.
            This will also define structs in the module if required. 
        * Generate Source
    '''
    
    func_ast = decompile_func(function)
    
    globls = function.func_globals
    
    mod_ast, func_ast = typify_function(function.func_name, argtypes, globls, func_ast)
    
    mod_ast = replace_constants(mod_ast)
    
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
    
