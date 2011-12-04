'''
Created on Dec 2, 2011

@author: sean
'''
from meta.asttools.visitors import Mutator
from inspect import isroutine
from clyther.clast import cast


class TypeCaster(Mutator):
    
    def mutateCCall(self, node):
        if hasattr(node.func, 'ctype') and not isroutine(node.func.ctype):
            
            if len(node.args) == 0:
                arg = cast.CNum(0, node.func.ctype)
            elif len(node.args) == 1:
                arg = self.mutate(node.args[0])
                arg = node.args[0] if arg is None else arg
            else:
                raise TypeError()
            return cast.CTypeCast(arg, node.func.ctype)
        else:
            return self.mutateDefault(node)
            
def call_type2type_cast(node):
    caster = TypeCaster()
    caster.mutate(node)

