'''
Created on Dec 24, 2011

@author: sean
'''

from sphinx.ext.autodoc import ModuleLevelDocumenter 
import inspect

class RuntimeFunctionDocumenter(ModuleLevelDocumenter):
    """
    Specialized Documenter subclass for functions.
    """
    objtype = 'clrt'
    directivetype = 'function'
    member_order = 30

    @classmethod
    def can_document_member(cls, member, membername, isattr, parent):
        import clyther.rttt
        return isinstance(member, clyther.rttt.RuntimeFunction)

    def format_args(self):
        argtypes = self.object.argtypes
        
        args = '(' + ', '.join([str(arg.__name__) for arg in argtypes]) + ')'
        return args
    
    def document_members(self, all_members=False):
        pass



def setup(app):
    app.add_autodocumenter(RuntimeFunctionDocumenter)
