'''
Created on Mar 05, 2010 by GeoSpin Inc
@author: Sean Ross-Ross srossross@geospin.ca
website: www.geospin.ca
'''


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

from compiler.visitor import ASTVisitor
import sys

import StringIO
#from clyther.api.cltypes import cltype
from compiler import ast
import pdb
from clyther.api.ast.node import ResolveReturnType
import copy
from clyther.api.cltypes import cltype

class sr( object ):
    def __init__(self, string):
        self.string = string
    def __repr__(self):
        return str(self.string)
    
class ASTWrite( ASTVisitor ):
    
    def __init__( self, pyfunc, filename, glineno, pysource ):
        
        self.ast = None
        self.pyfunc = pyfunc
        self.filename = filename
        self.global_lineno = glineno
        self._pysource = pysource.splitlines() 
        
        ASTVisitor.__init__(self)
        
        self.args = []
#        self.out = sys.stdout
        self.out = StringIO.StringIO( )
        self.indent = 0
        self._code = None
        self.constants = {}
        self._local_variables = {}
        self._comment_mode = False
    
    def set_comment_mode(self,value):
        self._comment_mode= value
        
    def default( self,node,*args):
        
        className = node.__class__.__name__
        
        msg = "OpenCL/Python compiler can not hadle python expression of type '%s' yet" %node.__class__.__name__
        self.warn( node, msg )
        raise SyntaxError( msg , node.lineno , node, )
    
    def dispatch(self,node,*args):
        
#        result = ASTVisitor.dispatch(self, node,*args)
        self.node = node
        klass = node.__class__
        meth = self._cache.get(klass, None)
        if meth is None:
            className = klass.__name__
            meth = getattr(self.visitor, 'visit' + className, self.default)
            self._cache[klass] = meth
        
        if isinstance( meth , str ):
#            pdb.set_trace()
            nodedict = vars(node).copy()
            for key,value in vars(node).items():
                if isinstance( value, ast.Node ):
                    nodedict[key] = self.dispatch( value )
                    
            result = meth.format( **nodedict ) 
        else:        
            result = meth(node, *args)

#        result = meth(node, *args)

        
        if result == NotImplemented:
            self.warn( node, "OpenCL/Python compiler can not hadle python expression of type '%s'. Ingnoring statement" %node.__class__.__name__, )
            return None
        else:
            return result
        
    def warn(self, node, msg ):
        
        try:
            _lineno = node.lineno
        except:
            print "node",node
            raise
        
        if _lineno is None:
            lineno = "???"
            linestr = '???'
        else:
            lineno = self.global_lineno+_lineno-1
            linestr = self._pysource[_lineno-1]
            
        print >>sys.stderr
        print >>sys.stderr, 'CLyther |  File "%s", line %s, in %s' %(self.filename, lineno, self.pyfunc.__name__ )
        print >>sys.stderr, 'CLyther |>>    %s' %(linestr)
        print >>sys.stderr, 'CLyther |  %s' %msg
        print >>sys.stderr
        
    def _get_code(self):
        
        if self._code is None:
            self.out.seek(0 )
            self._code = self.out.read()
        return self._code
    
    code = property( _get_code ) 
        
    def visitModule(self,node):
        
        self._print( "// === === === === === === === " )
#        self._print( "#include <math.h>" )
        self._print( "//CLyther Module" )
        self._print( '''
struct _array_desc_ {
    size_t start[3];
    size_t stop[3];
    size_t step[3];
    size_t shape[3];
    size_t size;
};

typedef struct _array_desc_ array_desc;
''' )
        
   
        self._print( "// === === === === === === === " )
        self._print( "// Prototypes" )
        self._print( "// === === === === === === === " )

        for proto in getattr( node , 'prototypes' , []):
            self.dispatch( proto )
            self._print()

        self._print( "// === === === === === === === " )
        self._print( "// End Prototypes" )
        self._print( "// === === === === === === === " )
        
        self._print()
        
            
        for item in node.node.nodes:
            self.dispatch(item)
            
        self._print( "// === === === === === === === " )
        self._print( "// === === === === === === === " )
        
    def _print(self,*args):
        
        if self._comment_mode:
            self.out.write( "// %s%s\n"%(" "*4*self.indent," ".join(args))  )
                
        else:
            self.out.write( "%s%s\n"%(" "*4*self.indent," ".join(args))  )
    
    def visitCLProtoType(self,node):
        
        for decorator in node.decorators:
            self._print( decorator )
            
        args = []

        for dec in node.argnames:
            str_def = self.dispatch( dec )
            args.append( str_def )
            
        argstr = ", ".join(args)
        
        self._print( "%s %s( %s );" %( node.return_type, node.name,argstr) )
        
        return 
        
    def visitCLFunction(self,node):
#        ast.Function.argnames
        for decorator in node.decorators:
            self._print( decorator )
            
        args = []

        for dec in node.argnames:
            str_def = self.dispatch( dec )
            args.append( str_def )
            
        argstr = ", ".join(args)
        
        self._print( "%s %s( %s )" %( node.return_type, node.name,argstr) )
        
        self._print( "{" ) ; self.indent+=1
        
        self._print( "/* function %s */" %(node.name)  ) 
        self._print()
        for var in node.var_defns:
            small_dec = self.dispatch(var)
            self._print( "%s;" %(small_dec,) )
        self._print()
            
        
#        print ast.Function.code
        for stmnt in  node.code.nodes:
            
            small_stmnt =  self.dispatch( stmnt )
            if small_stmnt:
                self._print( "%s;" %(small_stmnt)  ) 
                
        
        
        self._print( "" )
        
        self.indent-=1; self._print( "}" ) 
         
        self._print( "" )
        self._print( "" )
        self._print( "" )
        


    def visitAssign(self,node):
        
        small_expr =  self.dispatch( node.expr )
        small_nodes =  [self.dispatch( val ) for val in node.nodes]
        
        return "%s = %s" %(" = ".join(small_nodes), small_expr)
    
    def visitCallFunc(self,node):
        
        small_name = self.dispatch( node.node )
        small_args = [self.dispatch( arg ) for arg in node.args]
#        print node.node
        return "%s( %s )" %(small_name,", ".join(small_args) )
    
    def visitAssName(self,node):
        
        return node.name
    
    def visitName(self,node):
        
#        if node.name in self.constants:
#            return repr( self.constants[node.name] )
#        
#        else:
        return node.name
        
    
    def visitConst(self,node):
#        print "Const",repr(node.value)
        result = repr(node.value)
        if isinstance(node.value , (long,int) ):
            if result.endswith('L'): result = result[:-1]
        
        return result 
    
    visitCLVarDeclaration = '{type} {name}'
    
    visitMul = '({left})*({right})'
    visitAdd = '({left})+({right})'
    visitSub = '({left})-({right})'
    visitDiv = '({left})/({right})'
    visitFloorDiv = '(int)floor({left})/({right})'
    visitIfExp = "( ({test}) ? ({then}) : ({else_}) )"
    visitNot = "!(short)({expr})"
    visitContinue = 'continue'
    visitUnaryAdd = '+( {expr} )'
    visitUnarySub = '-( {expr} )'
    visitAugAssign = "{node} {op} {expr}"
    visitGetattr = '{expr}.{attrname}'
    visitCLCast = '({type}){expr}'
    visitLeftShift = '{left} << {right}'
    visitRightShift = '{left} >> {right}'
    
    def visitSubscript(self,node):
        
        expr = self.dispatch( node.expr )
        subs = [self.dispatch( sub ) for sub in node.subs]
        
        return "%s[ %s ]" %( expr, ",".join(subs) )
    
    def visitWhile(self,node):
        
        test = self.dispatch(node.test)
        
        self._print( 'while ( %s )' %(test) )
        self._print( "{" ) ; self.indent+=1
        
        self.dispatch(node.body)
#        ast.While(test, body, else_, node.lineno)

        self.indent-=1; self._print( "}" ) 

    def visitCompare(self,node):
        
#        print "node.expr",node.expr
        expr = self.dispatch( node.expr )
        
        string_list = ["(%s)" %expr] 
        for opname,opexpr in node.ops:
            oexpr = self.dispatch( opexpr )
            string_list.append("%s (%s)" %( opname, oexpr))
        
        return " ".join(string_list)
        
#        ast.Compare(expr, ops, lineno)        
        
    def visitStmt(self,node):
        
        for stmnt in node.nodes:
            
            s = self.dispatch( stmnt )
            
            if s is None:
                self._print( "" )
            else:
                self._print( "%s;"%s )
            
    
    def visitCLGetattr(self,node):
        
        ctype = node.ctype.resolve()
        
        res = getattr(ctype,node.attrname)
        if res is None:
            expr = self.dispatch( node.expr )
            return "_desc_%s.%s" %(expr,node.attrname)
        else:
            return "%r" %(res)

    
    def visitIf(self,node):
        
        
        cltests = []
        
        test,body = node.tests[0]
        str_test = self.dispatch(test)
    
        self._print( 'if ( %s )' %( str_test ) )
        self._print( "{" ) ; self.indent+=1
        
        self.dispatch(body)
        
        self.indent-=1; self._print( "}" )
        
        for test,body in node.tests[1:]:
            str_test = self.dispatch(test)
        
            self._print( 'if ( %s )' %( str_test ) )
            self._print( "{" ) ; self.indent+=1
            
            self.dispatch(body)
            
            self.indent-=1; self._print( "}" )
            
        if node.else_:
            
            self._print( 'else' )
            self._print( "{" ) ; self.indent+=1
            
            self.dispatch(node.else_)
            
            self.indent-=1; self._print( "}\n" )
        else:
            self._print( "" )
            
            
        return None
    
    def visitDiscard(self,node):
        
        return self.dispatch( node.expr )

    def visitReturn(self,node):
        value = self.dispatch( node.value )
        
        if value in ['None',None]:
            return "return"
        else:
            return "return %s" % value
    
    
    def visitCLForLoop(self,node):
        
        assign = self.dispatch( node.assign )
        start = self.dispatch( node.start )
        stop = self.dispatch( node.stop )
        step = self.dispatch( node.step )
        
        self._print( 'for ( %s=%s; %s != %s; %s += %s ) ' %(assign,start,assign,stop, assign,step))
        self._print( "{" ) ; self.indent+=1
        
        self.dispatch( node.body )
        
        self.indent-=1; self._print( "}\n" )
        
        return None
    
    
    
    def visitOr(self,node):
        return "( (%s) )" % ") || (".join([ self.dispatch(nd) for nd in node.nodes if nd is not None])

    def visitBitor(self,node):
        return "( (%s) )" % ") | (".join([ self.dispatch(nd) for nd in node.nodes if nd is not None])
        
    def visitAnd(self,node):
        return "( (%s) )" % ") && (".join([ self.dispatch(nd) for nd in node.nodes if nd is not None])
    
    def visitBitand(self,node):
        return "( (%s) )" % ") & (".join([ self.dispatch(nd) for nd in node.nodes if nd is not None])
        
    def visitBitxor(self, node):
        return "( (%s) )" % ") ^ (".join([self.dispatch(nd) for nd in node.nodes if nd is not None])    
    
    def visitTuple(self,node):
        clnodes = [ self.dispatch(nd) for nd in node.nodes]
        result =  '( %s )' %", ".join( clnodes )
        return result 
        
    
        
    def visitCLStructDef(self,node):
#        print "visitCLStructDef", node
        self._print( "%s;" %node.string )
#        return str(node.string)

    def visitCLMod(self, node):
        left, right = node.left, node.right
        ltype, rtype = node.ltype, node.rtype

        if hasattr(ltype, 'resolve'):
            ltype = ltype.resolve()

        if hasattr(rtype, 'resolve'):
            rtype = rtype.resolve()
            
        max = cltype.maxtype(ltype, rtype)
        family = cltype.family(max)[1]
        cdef = cltype.cdef(max)
        
        if family == 'int':
            return "( (%s) %% (%s) )" % (self.dispatch(left), self.dispatch(right))
        elif family == 'float':
            return "fmod( (%s)(%s), (%s)(%s) )" % (cdef, self.dispatch(left),
                                                   cdef, self.dispatch(right))

    visitAssAttr ='{expr}.{attrname}' 
         

