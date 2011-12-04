'''
Created on Dec 2, 2011

@author: sean
'''
from meta.decompiler import decompile_func
import ctypes
from clyther.rttt import replace_types

from clyther.clast.openCL_sourcegen import opencl_source
from clyther.clast.visitors.typify import typify_function
from clyther.clast.mutators.type_cast import call_type2type_cast
from clyther.clast.mutators.rm_const_params import remove_const_params
from clyther.clast.mutators.keywords import move_keywords_to_args
from clyther.clast.mutators.placeholder_replace import resolve_functions


source = """

__kernel void generate_sin(__global float2* a, float scale)
{
    int id = get_global_id(0);
    int n = get_global_size(0);
    float r = (float)id / (float)n;
    
    a[id].x = id;
    a[id].y = native_sin(r) * scale;
}
"""


def generate_sin(a, scale):
    
    id = get_global_id(0)
    n = clrt.get_global_size(0)
    r = id / n;
    
    a[id].x = id;
    a[id].y = clrt.native_sin(r) * scale;


def func2(x, y):
    
    return x * y

def func1(a, b, c=func2):
    y = int()

    return c(a, y=y) + b

def main():
    
    func_ast = decompile_func(func1)
    
    argtypes = {'a':ctypes.c_int, 'b':ctypes.c_int, 'c':func2}
    globls = func1.func_globals
    
    mod_ast = typify_function(argtypes, globls, func_ast)
    
    call_type2type_cast(mod_ast)
    
    remove_const_params(mod_ast)
    
    move_keywords_to_args(mod_ast)
    
    resolve_functions(mod_ast)
    
    replace_types(mod_ast)
    
    opencl_source(mod_ast)
    
if __name__ == '__main__':
    main()

