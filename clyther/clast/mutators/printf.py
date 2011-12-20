'''
Created on Dec 9, 2011

@author: sean
'''
from meta.asttools.visitors import Mutator
from clyther.clast import cast
import ast
from opencl.type_formats import type_format

STR_FORMAT_MAP = {
                  'l': '%i',
                  'L': '%lu',
                  'f': '%f',
                  }
class PrintFMutator(Mutator):
    def mutatePrint(self, node):
        
        str_formats = []
        for val in node.values:
            if val.ctype == str:
                str_formats.append('%s')
            else:
                cfmt = type_format(val.ctype)
                fmt = STR_FORMAT_MAP[cfmt]
                str_formats.append(fmt)
        if node.nl: 
            str_formats.append('\\n')
            
        cstr = cast.CStr(" ".join(str_formats), str)
        
        arg = cast.CTypeCast(cstr, 'const char*')
        vlaue = cast.CCall(cast.CName('printf', ast.Load(), None), [arg] + node.values, [], None)
        
        return ast.Expr(vlaue)
    

def make_printf(mod_ast):
    
    printf = PrintFMutator()
    printf.mutate(mod_ast)
