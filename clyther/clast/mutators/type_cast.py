'''
Created on Dec 2, 2011

@author: sean
'''
from meta.asttools.visitors import Mutator
from inspect import isroutine
from clyther.clast import cast
from clyther.clast.visitors.typify import RuntimeFunction
import _ctypes


class TypeCaster(Mutator):
    
    def mutateCCall(self, node):
        
        new_node = self.mutateDefault(node)
        if new_node:
            node = new_node
        
        if hasattr(node.func, 'ctype') \
            and not isroutine(node.func.ctype) \
            and not isinstance(node.func.ctype, RuntimeFunction):
            
            if len(node.args) == 0:
                arg = cast.CNum(0, node.func.ctype)
            elif len(node.args) == 1:
                arg = self.mutate(node.args[0])
                arg = node.args[0] if arg is None else arg
            elif issubclass(node.ctype, _ctypes.Array):
                return cast.CVectorTypeCast(node.args, node.ctype)
            else:
                raise TypeError()
            return cast.CTypeCast(arg, node.func.ctype)
        
        return new_node
            
def call_type2type_cast(node):
    caster = TypeCaster()
    caster.mutate(node)

