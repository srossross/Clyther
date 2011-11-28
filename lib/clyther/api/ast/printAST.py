'''
Created on Mar 25, 2010 by GeoSpin Inc
@author: Sean Ross-Ross srossross@geospin.ca
website: www.geospin.ca
'''
from compiler import ast
from compiler.visitor import ASTVisitor
import compiler
import inspect

#================================================================================#
# Copyright 2009 GeoSpin Inc.                                                     #
#                                                                                # 
# Licensed under the Apache License, Version 2.0 (the "License");                #
# you may not use this file except in compliance with the License.               #
# You may obtain a copy of the License at                                        #
#                                                                                #
#      http://www.apache.org/licenses/LICENSE-2.0                                #
#                                                                                #
# Unless required by applicable law or agreed to in writing, software            #
# distributed under the License is distributed on an "AS IS" BASIS,              #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.       #
# See the License for the specific language governing permissions and            #
# limitations under the License.                                                 #
#================================================================================#

class ASTPrinter( ASTVisitor ):
    
    def default( self,node,*args):
        
        if not len(args):
            indent = 0
        else:
            indent = args[0]
            
        if node is None:
            return None
            
        print node.__class__.__name__
        
        for name in dir(node):
            if not name.startswith( "_" ) and name != 'lineno':
                value = getattr(node,name)
                if isinstance( value , (list,tuple) ):
                    for i,item in enumerate(value):
                        self.printme("%s[%i]"%(name,i), item, indent)
                
                else:
                    self.printme(name, value, indent)
    def do_indent(self,indent):
        if indent:
            return ("    +" * (indent-1)) + "    "
        else:
            return ""
    
    def printme(self,name,value,indent):
        
        istring = self.do_indent(indent)
        if isinstance( value , (list,tuple) ):
            if isinstance( value , (list,tuple) ):
                for i,item in enumerate(value):
                    self.printme("%s[%i]"%(name,i), item, indent)
        elif isinstance(value, ast.Node):
            print "%s+ %s "%(istring,name), 
            self.dispatch( value, indent+1)
        elif inspect.isroutine( value ):
            pass
        else:
            print "%s- %s = %r "%(istring,name, value)

        
def printAST( node ):
    
    printer = ASTPrinter( )
    compiler.visitor.walk( node , printer, printer,  verbose=True )

