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

import pdb

from clyther.api.ast.node import RuntimeConst, TypeTree,RuntimeResolveType,\
    CLCallFunc, CLMod
from clyther.api.ast.node import ResolveAttrType,ResolveReturnType

from clyther import __cl_builtins__, clmath
from clyther.api.cltypes import cltype
from clyther.api.ast.printAST import printAST

"""
"""
#import pdb

import sys

from compiler.visitor import ASTVisitor

from compiler import ast 
import ctypes 

import node as nodes


class ASTConvert( ASTVisitor ):
    
    def __init__( self, pyfunc, filename, glineno, pysource, decorator='kernel'):
        
        self.ast = None
        self.pyfunc = pyfunc
        self.filename = filename
        self.global_lineno = glineno
        self._pysource = pysource.splitlines() 
        self.tmp_index = 0
        self.decorator = decorator 
        
        ASTVisitor.__init__(self)
        
        self.defined_locals = [ ]
        
        self.module = ast.Module( ''' ''',  ast.Stmt( [], 0) )
        self.module.functions = []
        self.module.__local_variables__ = {}
        self.module.var_defns = []
        self._prev_scopes = []
        self.scope = self.module
        self.return_type = None
        self.global_names = {}
        
    def push_scope(self,node):
        
        self._prev_scopes.append( self.scope )
        self.scope = node
        
    def pop_scope(self):
        node = self.scope
        self.scope = self._prev_scopes.pop()
        
        return node
        
        
    
    def default( self,node,*args):
        
        className = node.__class__.__name__
        
        msg = "OpenCL/Python compiler can not hadle python expression of type '%s' yet" %node.__class__.__name__
        self.warn( node, msg )
        
        if hasattr(node,'lineno'):
            _lineno = node.lineno
        else:
            _lineno = None
                
        raise SyntaxError( msg , _lineno , node, )
    
    def dispatch(self,node,*args):
        if node is None:
            return None
        
        result = ASTVisitor.dispatch(self, node,*args)
        
#        name = "visit%s" %node.__class__.__name__
#        if not isinstance( result, tuple ):
#            raise Exception( "OpenCL/Python compiler %r method must return a 2-tuple of (ast.Node,ctype)" % name)
#        elif len(result) != 2:
#            raise Exception( "OpenCL/Python compiler %r method must return a 2-tuple of (ast.Node,ctype)" % name)
#        
        
        if result == NotImplemented:
            self.warn( node, "OpenCL/Python compiler can not hadle python expression of type '%s'. Ingnoring statement" %node.__class__.__name__, )
            return None
        else:
            return result
        
    def warn(self, node, msg ):
        
        if hasattr(node, 'lineno'):
            _lineno = node.lineno
        else:
            _lineno = None
        
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

        
    def visitFunction(self,node):
        
#        printAST( node) 
        clargnames = []
        clconstants = {}
        local_vars = {}
        for argname in node.argnames:
            
#            if argname in self.constants:
#                clconstants[ argname ] = nodes.CLVarDeclaration( argname )
#            else:
            clarg = nodes.CLVarDeclaration( argname, lineno=node.lineno )
            local_vars[argname] = clarg
            clargnames.append( clarg )
        
        clnode = nodes.CLFunction( [self.decorator], node.name, clargnames, node.defaults, node.flags, node.doc, None, lineno=node.lineno )
        
        
        clnode.__local_variables__ = local_vars
        
        clnode.var_defns = [ ]
        clnode.functions = [ ]
        clnode.constants = clconstants
        clnode.global_names = self.global_names
        
        self.push_scope( clnode )
        
        clcode = self.dispatch( node.code )
        
        
        clnode.return_type = self.return_type
        self.module.return_type = self.return_type
        clnode.code = clcode
        
        #print "clnode.code", clnode.code
        self.pop_scope( )
        
        self.module.node.nodes.append( clnode )
        
#        self.module.node.nodes.append(  )
        
        return clnode
    
    def isinArgnames(self,name):
        x = [ arg for arg in self.scope.argnames if arg.name == name ]
        return len(x)
    
    def visitStmt(self,node):
        
        nodes = []
        for stmnt in node.nodes:
            newnode = self.dispatch(stmnt)
            if newnode is None:
                pass
            elif isinstance( newnode, (list,tuple) ):
                nodes.extend( newnode )
            else:
                nodes.append( newnode )
                 
        clnode = ast.Stmt( nodes, node.lineno)
        
        return clnode
    
    def visitAssign(self,node):
        
#        print "visitAssign",node
        clexpr,cltype = self.dispatch( node.expr )
        clnodes = [self.dispatch( nd, cltype ) for nd in node.nodes]
        
        return ast.Assign( clnodes, clexpr, lineno=node.lineno )
    
    def visitCallFunc(self,node):
        
#        print "GEN visitCallFunc", node.node
#        name =  getattr(node.node,'name',None)
#        if name =='oper':
#            pdb.set_trace( )
        
        if node.star_args or node.dstar_args:
            msg = "CLyther does not support * or ** magic function calls" 
            self.warn(node, msg)
            raise SyntaxError( msg )
        
        
        clargs = []
        clarg_types = []
        
        for arg in node.args:
            
            clarg,clarg_type = self.dispatch(arg)
            clargs.append( clarg )
            clarg_types.append( clarg_type )
        
        
        clnode, clfunctype = self.dispatch( node.node )
        
#        print "clfunctype",clfunctype
#        pdb.set_trace()
        if cltype.is_type( clfunctype ):
            if len(clargs) == 0:
                return nodes.CLCast( clfunctype, ast.Const(0), node.lineno ), clfunctype
            elif len(clargs) == 1:
                return nodes.CLCast( clfunctype, clargs[0], node.lineno ), clfunctype
            else:
                raise SyntaxError( 'function call with type %s is assumed to be a typecast. Takes at most 1 argument (got %i)' %(clnode,len(clargs)) )
        else:
            function_res = ResolveReturnType( clfunctype, clarg_types )
#            function_res = clfunctype.get_restype( clarg_types )
            self.scope.functions.append( clfunctype )
            return nodes.CLCallFunc(clnode, clargs, clarg_types, lineno=node.lineno ), function_res
        
        
    def visitConst(self,node):
        
        ctype = cltype.ctype( node.value )
        #ctype =  nodes.get_ctype( type(node.value) )
        return ast.Const( node.value, lineno=node.lineno ), ctype
    
    def visitGetattr(self,node):
        
#        if isinstance( node.expr, ast.Name):
            
        expr, expr_type = self.dispatch( node.expr )
            
        ctype = ResolveAttrType( expr, expr_type, node.attrname )
        cl_node =  ast.Getattr( expr, node.attrname, node.lineno)
        cl_node.ctype = expr_type
        return cl_node, ctype
              
                
#        raise Exception("could not get attribute %r" %node )
            
#        return 
    
    def define(self,name,type, lineno ):
        
        if ( name not in self.scope.__local_variables__):
            self.scope.__local_variables__[name] = type
            type = self.scope.__local_variables__[name]
            self.scope.var_defns.append( nodes.CLVarDeclaration(name, type, lineno=lineno) )
            
        return self.scope.__local_variables__[name]


    def visitAssName(self, node, type):
        
        if node.flags == 'OP_ASSIGN':
            
            self.define(node.name,type,node.lineno)
            
            clnode = ast.AssName( node.name, node.flags, node.lineno )
            
            return clnode
        
        else:
            msg = "CLyther error" 
            self.warn(node, msg)
            raise SyntaxError( msg )
    
    
    def visitMul(self,node):
        lnode,ltype = self.dispatch(node.left)
        rnode,rtype = self.dispatch(node.right)
        
        ctype = TypeTree( ltype, rtype )
        return ast.Mul( (lnode, rnode), node.lineno),ctype 
    
    def visitAdd(self,node):

        lnode,ltype = self.dispatch(node.left)
        rnode,rtype = self.dispatch(node.right)
        
        ctype = TypeTree( ltype, rtype )
        
        return ast.Add( (lnode, rnode), node.lineno),ctype

    def visitSub(self,node):

        lnode,ltype = self.dispatch(node.left)
        rnode,rtype = self.dispatch(node.right)
        
        ctype = TypeTree( ltype, rtype )
        
        return ast.Sub( (lnode, rnode), node.lineno),ctype
    
    def visitDiv(self,node):

        lnode,ltype = self.dispatch(node.left)
        rnode,rtype = self.dispatch(node.right)
        
        ctype = TypeTree( ltype, rtype )
        
        return ast.Div( (lnode, rnode), node.lineno),ctype

    def visitFloorDiv(self,node):
        
        left,ltype = self.dispatch( node.left )
        right,rtype = self.dispatch( node.right )
        
        return ast.FloorDiv( (left, right), node.lineno ), int
        
    def visitMod(self,node):
        
        left,ltype = self.dispatch( node.left )
        right,rtype = self.dispatch( node.right )
                
        return CLMod(left, right, ltype, rtype, node.lineno), TypeTree(ltype, rtype)

    def lookUp(self,name):
        
        if name in self.scope.__local_variables__:
            res = self.scope.__local_variables__[name]
            if hasattr(res,'type'):
                return res.type
            else:
                return self.scope.__local_variables__[name]
        
#        print "look golbal",name
        if name not in self.global_names:
            self.global_names[name] = RuntimeResolveType( )
            
        
        return self.global_names[name]
    
#        if name in self.scope.constants:
#            return self.scope.constants[name].type
#        
#        elif self.isinArgnames(name):
#            return self.pyfunc.func_globals[name].type 
#        
#        elif name in self.pyfunc.func_globals:
#            return self.pyfunc.func_globals[name]
#        
#        elif name in __builtins__:
#            if hasattr( __cl_builtins__, name ):
#                return getattr( __cl_builtins__, name )
#            else:
#                msg = "Python builtin %r is not yet supported in CLyther" %(name)
#                raise NotImplementedError(msg )
#        else:
#            return NotImplemented
            
        
    def visitName(self,node):

        
        ctype = self.lookUp( node.name )
        
#        print 
#        print "visitName", node.name
        
        if ctype == NotImplemented:
            msg = 'name %r is not defined' %(node.name,)
            self.warn(node, msg)
            raise NameError( msg )
        if node.name in self.scope.constants:
            return RuntimeConst( node.name, lineno=node.lineno ), ctype

        return ast.Name(node.name), ctype
    
#        clnode.__local_variables__
    
    
    def visitSubscript(self,node,ctype=None):
        
        
        clexpr,exprtype = self.dispatch( node.expr )
        clsubs = []
        for sub in node.subs:
            _sub,_ =  self.dispatch( sub )
            clsubs.append( _sub )
        
        resnode = ast.Subscript( clexpr, node.flags, clsubs, node.lineno )
        if node.flags == 'OP_ASSIGN':
            return resnode
        else: 
#            print "exprtype", exprtype, exprtype.type
            return resnode, exprtype.derefrence( )
        
    def visitWhile(self,node):
        
        test,_type = self.dispatch(node.test)
        body = self.dispatch(node.body)
        
        return ast.While( test, body, None, node.lineno )
    
    def visitCompare(self,node):
        
        expr,_type = self.dispatch( node.expr )
        
        ops =  []
        for opname,val in  node.ops:
            _val,_type = self.dispatch(val)
            ops.append( (opname,_val) )
        
        return ast.Compare(expr, ops, node.lineno), bool

    def visitAugAssign(self,node):
        
        clnode,ndtype = self.dispatch( node.node)
        expr,extype = self.dispatch( node.expr)
        
        return ast.AugAssign(clnode, node.op, expr, node.lineno)
    
    def visitPrintnl(self,node):
        self.warn(node, 'ignoring print statements in opencl code')
        return None 
    
    def visitReturn( self, node ):
#        pdb.set_trace( )
        value,ctype = self.dispatch( node.value )
#        print "value",value
        self.return_type = ctype
        
        return ast.Return(value, node.lineno)

    def visitDiscard(self, node ):
        node,_ = self.dispatch(node.expr)
        
        if isinstance( node, ast.Const ):
            if node.value == None:
                return None
            
        return node
#        return ast.Discard( self.dispatch(node.expr), node.lineno)
        
    def visitFor(self, node ):
        # asdf=ast.For(assign, list, body, else_, lineno)
#        print "visitFor", node
        if isinstance(node.list, (ast.Tuple, ast.List) ):
            
            if node.list.nodes:
                clnode,ctype = self.dispatch( node.list.nodes[0] )
                
                clnodes = [clnode]
                for item in  node.list.nodes[1:]:
                    clnode_next,ctype_next = self.dispatch( item )
                    clnodes.append( clnode_next )
                    ctype = TypeTree( ctype, ctype_next )
                    
#                self.define( node.assign, type )
                assign = self.dispatch( node.assign, ctype )
                
                new_body = []
                for item in clnodes:
                    assgn = ast.Assign( [assign], item, node.assign.lineno )
                    new_body.append(assgn)
                    new_body.append( self.dispatch(node.body) )
                    
                return new_body
            else:
                return None
#                raise Exception
        else:
#            import pdb;pdb.set_trace()
            list_,list_type = self.dispatch( node.list ) 
            assign  = self.dispatch( node.assign,list_type ) 
            else_ = self.dispatch( node.else_ ) 
            body  = self.dispatch( node.body ) 
            return ast.For( assign=node.assign, list=list_, body=body, else_=else_, lineno=node.lineno)
    
    
    def visitIf(self,node):
        
        
        cltests = []
        for test,body in node.tests:
            cltest,ctype = self.dispatch(test)
            clbody = self.dispatch(body)
            
            cltests.append((cltest,clbody))
        
        if node.else_:
            else_ = self.dispatch( node.else_ )
        else:
            else_ = None
            
        return ast.If( cltests, else_, node.lineno)
        
    def visitIfExp(self,node):
        
        test,_ = self.dispatch( node.test )
        then,then_type = self.dispatch( node.then )
        else_,else_type = self.dispatch( node.else_ )
        
        restype = TypeTree( then_type, else_type)
        return ast.IfExp(test, then, else_, node.lineno), restype
    
    
    def visitOr(self,node):
        
        cl_nodes = []
        
        for nd in node.nodes:
            
            cl_node,_ = self.dispatch( nd )
            cl_nodes.append(  cl_node )
        
        
        return ast.Or(cl_nodes, node.lineno), bool 

    def visitAnd(self,node):
        
        cl_nodes = []
        
        for nd in node.nodes:
            
            cl_node,_ = self.dispatch( nd )
            cl_nodes.append(  cl_node )
        
        
        return ast.And(cl_nodes, node.lineno), bool 
        
    def visitBitand(self,node):

        nd,nd_type = self.dispatch( node.nodes[0] )
        cl_nodes = [nd]
        for nd in node.nodes[1:]:
            
            cl_node,nd_type2 = self.dispatch( nd )
            
            cl_nodes.append(  cl_node )
            
            nd_type = TypeTree( nd_type, nd_type2 )
        
        return ast.Bitand( cl_nodes, node.lineno ), nd_type

    def visitBitor(self,node):

        nd,nd_type = self.dispatch( node.nodes[0] )
        cl_nodes = [nd]
        for nd in node.nodes[1:]:
            
            cl_node,nd_type2 = self.dispatch( nd )
            
            cl_nodes.append(  cl_node )
            
            nd_type = TypeTree( nd_type, nd_type2 )
        
        return ast.Bitor( cl_nodes, node.lineno ), nd_type
        
    def visitBitxor(self,node):
        nd, nd_type = self.dispatch(node.nodes[0])
        cl_nodes = [nd]
        for nd in node.nodes[1:]:
            cl_node,nd_type2 = self.dispatch(nd)            
            cl_nodes.append(cl_node)
            nd_type = TypeTree(nd_type, nd_type2)
        return ast.Bitxor(cl_nodes, node.lineno), nd_type

    def visitNot(self,node):
        
        expr,_ = self.dispatch( node.expr )
        return ast.Not( expr, node.lineno), bool
    
    def visitContinue(self,node):
        
        return ast.Continue(node.lineno)
    
    
    def visitUnaryAdd(self,node):
        expr,ndtype = self.dispatch( node.expr )
        return ast.UnaryAdd( expr, node.lineno),ndtype

    def visitUnarySub(self,node):
        expr,ndtype = self.dispatch( node.expr )
        return ast.UnarySub( expr, node.lineno),ndtype

    def visitPass(self,node):
        return None

    def visitPower(self,node):
        
        left,ltype = self.dispatch( node.left )
        right,rtype = self.dispatch( node.right )
        
        return CLCallFunc( ast.Const( math.pow ), (left, right), (ltype,rtype), node.lineno ),ltype
    
 
#        return ast.Power((left, right), node.lineno), ltype
    def visitLeftShift(self,node):
        left,ltype = self.dispatch(node.left)
        right,rtype = self.dispatch(node.right)
        
        return ast.LeftShift((left, right), node.lineno), ltype

    def visitRightShift(self,node):
        left,ltype = self.dispatch(node.left)
        right,rtype = self.dispatch(node.right)
        
        return ast.RightShift((left, right), node.lineno), ltype
    
    

    def visitAssAttr(self,node,ctype):
        expr,extype = self.dispatch(node.expr)
        return ast.AssAttr(expr, node.attrname, node.flags, node.lineno)

