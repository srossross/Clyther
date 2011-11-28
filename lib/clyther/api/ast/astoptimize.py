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

#import StringIO
from clyther.api.cltypes import cltype, rtte, CLTypeException
from compiler import ast
#import pdb
#from clyther.api.ast.node import ResolveReturnType, CLFunction
import clyther.api.ast.node as nodes
#import copy
import new
from compiler.pycodegen import ExpressionCodeGenerator
import pdb
#from clyther.api.ast.printAST import printAST
from clyther.runtime import opencl_builtin_function, opencl_builtin_enum
#from clyther.memory import array_type
from clyther import __cl_builtins__ as cl_builtins
from inspect import isclass
from clyther.api.ast.node import CLStructDef, CLCast, CLCallFunc
from clyther.device_objects import device_object

class sr( object ):
    def __init__(self, string):
        self.string = string
    def __repr__(self):
        return str(self.string)
    
class Scope( object ):
    def __init__(  self, _globals ):
        self.local_variables = { }
        self.values = { }
        self._globals = _globals
        
    def __getitem__(self,item):
        return self.local_variables[item]

    def __setitem__(self,item,value):
#        print item,value
#        pdb.set_trace()
        self.local_variables[item] = value
        
    def __iter__(self):
        return iter(self.local_variables)
        
    def __contains__(self,k):
        return self.local_variables.__contains__(k)
    
    def isConst(self,name):
        return (name in self.values and isinstance( self.values[name], ast.Const) )
    
    def isFunction(self,name):
        
        from clyther.api.kernelfunction import OpenCLFunctionFactory,KernelFunction
        
        if name in self.local_variables:
            return isinstance( self.local_variables[name], (OpenCLFunctionFactory,KernelFunction) )
        
def is_device_function(value):
    
    from clyther.api.kernelfunction import OpenCLFunctionFactory,KernelFunction
    
    return isinstance( value, (OpenCLFunctionFactory,KernelFunction) )
    

class ASTOptimize( ASTVisitor ):
    
    def __init__( self, pyfunc, filename, glineno, pysource,  argtypes, namespace ):
        
        self.ast = None
        self.result = None
        self.pyfunc = pyfunc
        self.filename = filename
        self.global_lineno = glineno
        self._pysource = pysource.splitlines()
         
        self.namespace = namespace
        self.local_names = {}
        
        self.argtypes = argtypes
        self.args = []

        self._curr_scope = None 
        self._stack = [ ]
    
        self.sub_funcions = { }
        self.module_ns = { }
        self.sub_funcion_ns = { }
        
        ASTVisitor.__init__(self)
        
        self.ast_stack = [ ]
        self._assign = False
        
    def set_compile_ctx(self,pyfunc, filename, glineno, pysource,  argtypes):
        
        self.pyfunc = pyfunc
        self.filename = filename
        self.global_lineno = glineno
        self._pysource = pysource.splitlines() 
        self.argtypes = argtypes

    def push_scope(self,scope):
        
        self._stack.append( scope )
        self._curr_scope = scope
        
    def pop_scope(self):
        
        scope = self._curr_scope
        self._curr_scope = self._stack.pop( )
        
        return scope
    
    def _get_scope(self):
        return self._curr_scope
    
    scope = property( _get_scope )
    
    def default( self,node,*args):
        
        if node is None:
            return None
            
        newdict = {}
        for item in dir(node):
            if not item.startswith( "__" ):
                value = getattr(node,item)
                if isinstance(value, ast.Node):
                    result = self.dispatch( value )
                else:
                    result = value
                    
                newdict[item] = result
        
        return new.instance( node.__class__, newdict)
    
    def dispatch(self,node,*args):
#        print "dispatch", node
#        pdb.set_trace()
        self.ast_stack.append( node )
        
#        if node.__class__.__name__ == 'Name':
#            print "+ push %s( %r )"%( node.__class__.__name__,node.name)
#        else:
#            print "+ push", node.__class__.__name__
        try:
            result = ASTVisitor.dispatch(self, node,*args)
        except NotImplementedError as ni:
            self.warn( node, ni.args[0] )
            raise Exception( ni.args[0] )
            
        
        self.ast_stack.pop( )
#        print "- pop", node.__class__.__name__
        
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
        
        
    def visitModule(self,node):
#        printAST( node )
        
        self.push_scope( Scope( {} ) )
        
        self.module_scope = self.scope 
        
        newnode = self.dispatch( node.node )
        
        args = self.args
        
        
#        print "visitModule", [ (item[0],item[1].keys()) for item in self.namespace.items( )]
        
        new_nodes = [ item['node'] for item in self.local_names.values( ) if ('node' in item  )]
        prototypes = [ item['proto'] for item in self.local_names.values( ) if ('proto' in item  )]
        
        newnode = ast.Stmt(new_nodes, node.lineno)
        
        self.result = ast.Module( node.doc, newnode, node.lineno )
        self.result.prototypes = prototypes
        self.args = args
        self.pop_scope()
        
#        print self,"self.namespace", self.namespace.keys() 
        return self.result 
#        self._print( '''
#struct _array_desc_ {
#    size_t start[3];
#    size_t stop[3];
#    size_t step[3];
#    size_t shape[3];
#    size_t size;
#};
#
#typedef struct _array_desc_ array_desc;
#''' )
   
#        self._print( "// === === === === === === === " )
#        self._print()
#        
#            
#        for item in node.node.nodes:
#            self.dispatch(item)
#            
#        self._print( "// === === === === === === === " )
#        self._print( "// === === === === === === === " )
        
    
    def visitCLFunction(self,node):

        self.push_scope( Scope( self.pyfunc.func_globals ) )
        
        if node.name in self.namespace:
            node_name = node.name
            node_name = "%s_%s" %(self.pyfunc.__module__.strip("_").replace('.','_'),node.name)
            i=0
            _node_name = node_name
            while node_name in self.namespace:
                i+=1
                node_name = "%s%i"%(_node_name,i)  
            
        else:
            node_name = node.name
            
        #placeholder
        self.node_name = node_name
#        self.namespace[node_name] = {}
        self.local_names[node_name] = {}
        
        for key,value in node.global_names.items( ):
            
            if key in self.pyfunc.func_globals:
                gvalue = self.pyfunc.func_globals[key]
            elif key in __builtins__:
                if hasattr( cl_builtins, key ):
                    gvalue = getattr( cl_builtins, key )
                else:
                    msg = "Python builtin %r is not yet supported in CLyther" %(key)
                    raise NotImplementedError( msg )
            else:
                raise NameError("global name %r is not defined" %(key) )    
            
#            print value, gvalue
#            pdb.set_trace( )
            value.set_type( gvalue )
            
#        print "node.global_names",node.global_names
        
        decorators = node.decorators
        
        for key in self.argtypes:
            
            proto = getattr( self.argtypes[key], 'proto', None)
            if proto is not None:
                struct_def = proto()
                if struct_def is not None:
                    struct_name =  self.argtypes[key].cdef( )
#                    print "if struct_def is not None:"
                    self.local_names[struct_name] = {'proto': CLStructDef(struct_def,lineno=node.lineno) } 
                
        for name,dec in node.constants.items():
            dec.type.set_type( self.argtypes[name] )
        
        clargnames = []
        for dec in node.argnames:
            name = dec.name
            ctype_or_const = self.argtypes[name]
            ctype = cltype.ctype( ctype_or_const )
            
            if cltype.is_const( ctype_or_const ):
                
#                self.constants[name] = _ctype
                
                self.scope[name] = ctype 
                self.scope.values[name] = ast.Const(ctype_or_const,lineno=node.lineno) 
                
                dec.type.set_type( ctype )
                
            elif cltype.is_function(ctype_or_const):
                
                self.scope[ctype_or_const.name] = ctype_or_const
                self.scope[name] = ctype_or_const
                dec.type.set_type( ctype_or_const )
                
            else:
                dec.type.set_type( ctype )
                clargnames.append( self.dispatch( dec ) )
                self.args.append( name )
                
                self.scope[name] = ctype
                
                if hasattr(ctype, 'size' ) and ctype.size is None:
#                    raise Exception("")
                    attr_name = "_desc_%s" %( name )
                     
                    self.scope[attr_name] = ctype
                    
                    self.args.append( attr_name )
                    self.args.append( attr_name )
                    
        
        var_defns = []
        for var in node.var_defns:
            var_defns.append( self.dispatch(var) )
        
#        print ast.Function.code
        clcode = self.dispatch(node.code)
        
        
        
        clnode = nodes.CLFunction( decorators, node_name, clargnames, None, node.flags, node.doc, clcode , lineno=node.lineno )
        clprototype = nodes.CLProtoType( decorators, node_name, clargnames )
        return_type = node.return_type
#        if return_type is None:
#            clnode.return_type = "void"
            
        creturn_type = cltype.ctype( return_type )
        clnode.return_type = cltype.cdef( creturn_type )
        clprototype.return_type = clnode.return_type
        
        
        
        clnode.var_defns = var_defns

        self.pop_scope(  )
        
#        print "self.namespace", node_name, self.namespace.keys()
#        self.namespace[node_name]['node']=clnode
        self.local_names[node_name]['node']=clnode
        self.local_names[node_name]['proto']=clprototype
        
#        pdb.set_trace( )
#        return clnode
        
#
#
    def visitAssign(self,node):
        
        expr =  self.dispatch( node.expr )
        cl_nodes =  [self.dispatch( val ) for val in node.nodes]
        
#        print "visit Assign", expr, cl_nodes
        for cnode in cl_nodes:
            if hasattr( cnode, 'name' ):
                if self.currInsideControllFlow():
                    self.scope.values[ cnode.name ] = None
                else:
                    self.scope.values[ cnode.name ] = node.expr
        
        
        return ast.Assign( cl_nodes, expr, node.lineno)
    
    def visitCallFunc(self,node):
        
#        pdb.set_trace( )
#        print "PY visitCallFunc", node
#        if hasattr(node, 'arg_types'):
#            print "node.arg_types", node.arg_types
            
        cl_name = self.dispatch( node.node )
        
        cl_args = [self.dispatch( arg ) for arg in node.args]
        
        
        return ast.CallFunc( cl_name, cl_args, None, None, node.lineno ) 
    
    def visitCLCallFunc( self, node ):
        
#        print node.node
#        print node
#        pdb.set_trace( )
        cl_name = self.dispatch( node.node )
        
        cl_args = [self.dispatch( arg ) for arg in node.args]
        arg_types = node.arg_types
        
        
        if self.isConstant( cl_name ):
            cl_function = self.evaluateConstantNode( cl_name )
            
        else:
            cl_function = cl_name
            
        if cl_function in __builtins__.values():
            cl_function = getattr( cl_builtins, cl_function.__name__ )
#            cl_name = ast.Name( getattr( cl_function, 'device_name', cl_function.__name__) )

        if is_device_function(cl_function):
            cldevicefunc = self.scope[cl_name.name]
            
            newargtypes = []
            new_cl_args = []
            
            for value, argt in zip(cl_args,arg_types):
                
                if hasattr(argt,'resolve' ):
                    argt = argt.resolve( )
                ctype = cltype.ctype( argt )
                
                if self.isConstant( value ):
                    constvalue = self.evaluateConstantNode( value )
                    ctype = ctype(constvalue)
                else:
                    new_cl_args.append(value)
                newargtypes.append(ctype)
                
            newargtypes = tuple(newargtypes)
            cl_args = tuple(new_cl_args) 
#            self.sub_funcions[newargtypes] = cldevicefunc
            
            #===================================================================
            # ## New 
            #===================================================================
#            pdb.set_trace( )
            devobj = cldevicefunc.argtypes( *newargtypes, __namespace__=self.local_names )
            
            self.local_names.update( devobj.local_names )
            
#            print "devobj", devobj.name, devobj.local_names.keys()

            #===================================================================
            # 
            #===================================================================
            cl_name = ast.Name( devobj.name )
#            if newargtypes not in self.sub_funcion_ns:
#                self.sub_funcion_ns[newargtypes] = ast.Name( devobj.name )
#                
#            cl_name = self.sub_funcion_ns[newargtypes]
            
        elif isclass(cl_function) and issubclass( cl_function, (opencl_builtin_function, opencl_builtin_enum) ):
            
            cl_name = ast.Name( getattr( cl_function, 'device_name', cl_function.__name__) )
            
        elif cl_function == cl_builtins.range:
            
            return ast.CallFunc( cl_name, cl_args, None, None, node.lineno )
        
        elif cltype.ctype( cl_function) == cl_function:
            
            if issubclass(cl_function, device_object):
                return None
#                self.warn( node, "can not instantiate" )
                                
##                    raise SyntaxError( "can not instantiate" )
#                if cl_function.__init__ ==  device_object.__init__:
#                    # no init defined
#                
#                else:
#                    raise SyntaxError( "can not instantiate" )
#                    pass
                
            else:
#            pdb.set_trace()
            # Not a function it is a type cast
                if len(node.args) == 0:
                    clargs = ast.Tuple([ast.Const(0)], node.lineno )
                else:
                    clargs = ast.Tuple(cl_args, node.lineno )
                    
                defn = cltype.cdef( cl_function )
                return CLCast( defn, clargs, node.lineno )
        
        
        
        return ast.CallFunc( cl_name, cl_args, None, None, node.lineno ) 
    
#    def visitAssName(self,node):
#        
#        return node.name
#    

    def visitName(self,node):
        
        name = node.name
        
#        print "name",name 
#        if name == 'CLK_LOCAL_MEM_FENCE':
##            print 
##            print "visitName", name , [nd.__class__.__name__ for nd in self.ast_stack]#self.currInsideControllFlow()
##            print 
#            import pdb; pdb.set_trace( )
#            
        
        
        if self.scope.isConst(name) and not self._assign:
            result = self.scope.values[name]
            
#        elif self.scope.isFunction(name):
#            funcname = self.scope[name]
#            result = ast.Name( funcname.name, node.lineno )
        else:
            if self._assign:
                self.scope.values[ node.name ] = None
                
            result = ast.Name( name, node.lineno)
            
        return result 
#        else:
#            return node.name
#        
#    
    def visitConst(self,node):
        return ast.Const( node.value, node.lineno )
#    
    def visitCLVarDeclaration(self,node):
        
        try:
            ctypedef = cltype.cdef( node.type )
        except AttributeError as err:
            self.warn( node, err.args[0] )
            raise
        except CLTypeException as err:
            self.warn( node, err.args[0] )
            raise
            
        
        return nodes.CLVarDeclaration( node.name, ctypedef, node.lineno)
#    
    def visitMul(self,node):
        left = self.dispatch( node.left )
        right = self.dispatch( node.right )
        return ast.Mul((left, right), node.lineno)
    
    def visitAdd(self,node):
        left = self.dispatch( node.left)
        right = self.dispatch( node.right)
        return ast.Add((left, right), node.lineno)

    def visitSub(self,node):
        left = self.dispatch( node.left)
        right = self.dispatch( node.right)
        return ast.Sub((left, right), node.lineno)

    def visitDiv(self,node):
        left = self.dispatch( node.left)
        right = self.dispatch( node.right)
        return ast.Div( (left, right), node.lineno)
#    
    def visitSubscript(self,node):
        
        expr = self.dispatch( node.expr )
        subs = [self.dispatch( sub ) for sub in node.subs]
        
        return ast.Subscript(expr, node.flags, subs, node.lineno)
    
    def visitWhile( self, node ):
        
        test = self.dispatch(node.test)
        
        body = self.dispatch(node.body)
        return ast.While( test, body, None, node.lineno )


    def visitCompare(self,node):
        
#        print "node.expr",node.expr
        expr = self.dispatch( node.expr )
        
        newops = [] 
        for opname,opexpr in node.ops:
            oexpr = self.dispatch( opexpr )
            newops.append( (opname,oexpr) )
        
        
        return ast.Compare(expr, newops, node.lineno)        
        
    def visitStmt(self,node):
        
        newnodes = []
        for stmnt in node.nodes:
            
            s = self.dispatch( stmnt )
            if s is None:
                continue
            elif isinstance( s, (list,tuple) ):
                newnodes.extend( s )
            else:
                newnodes.append( s )
        
        return ast.Stmt(newnodes, node.lineno)
            

    def visitAugAssign(self,node):
        
        self._assign = True
        left = self.dispatch( node.node )
        self._assign = False
#        print "visitAugAssign",node.node,"left",left
        
        expr = self.dispatch( node.expr )

        return ast.AugAssign(left, node.op, expr, node.lineno)
    
    def visitGetattr(self,node):
        
#        print "visitGetattr", node
        expr = self.dispatch( node.expr )
        
#        print "visitGetattr", expr, self.isConstant( expr )
#        pdb.set_trace()
#        ctype = cltype.ctype( node.ctype )
        
        if self.isConstant( node ):
            
            result = self.evaluateConstantNode( node )
            if isclass(result) and issubclass( result, (opencl_builtin_function,opencl_builtin_enum) ):
                return ast.Name( result.__name__ )
            else:
                return ast.Const( result )
            
        if hasattr( node, 'ctype'):
            
            ctype = cltype.ctype( node.ctype )
#            print "ctype", ctype
            
            isok = False
            
            if isinstance(ctype, rtte ):
                attr = getattr( ctype , node.attrname )
                return ast.Const( attr )
            elif hasattr( ctype, node.attrname):
                isok = True
            elif hasattr( ctype, '_fields_'):
                res = [(name,_ctype) for name,_ctype in ctype._fields_ if name == node.attrname]
                if res: isok = True
            if hasattr( ctype, '__getattr_type__'):
                cvalue = ctype.__getattr_type__( node.attrname )
                
                if cvalue != NotImplemented:
                    isok = True
                      
            if not isok:
                msg = "undefined attribute  %r" %node.attrname
                self.warn(node, msg)
                
#            if isinstance( node, class_or_type_or_tuple)
            
#            raise Exception
#            
#        else:
#            
#            raise Exception
        
        return ast.Getattr(expr, node.attrname, node.lineno)

    def visitCLCast(self,node):
        
        expr = self.dispatch( node.expr) 
    
        return nodes.CLCast(node.ctype, expr, node.lineno)
#    
    def visitCLGetattr(self,node):
#        
        print "node.expr      ",node.expr
        print "node.ctype     ",node.ctype
        print "node.attrname  ",node.attrname
        
        print "self.isConstant" ,self.isConstant( node )
#        if issubclass( result, opencl_builtin_function):
#            return ast.Name( node.attrname ), result

        raise Exception
#        
#        ctype = node.ctype.resolve()
#        
#        res = getattr(ctype,node.attrname)
#        if res is None:
#            expr = self.dispatch( node.expr )
#            return "_desc_%s.%s" %(expr,node.attrname)
#        else:
#            return "%r" %(res)
#        
    def isConstant(self,node):
        
        if isinstance( node, ast.Const ):
            result = True
        elif isinstance( node, ast.Name ):
            if node.name in self.scope:
                if self.scope.isConst( node.name ):
                    return True
                elif self.scope.isFunction( node.name ):
                    return True
                
                return False
            
            elif node.name in self.pyfunc.func_globals:
                return True
            elif node.name in __builtins__:
                return True
            else:
                return False
            
        elif isinstance( node, ast.Node ):
            
            children = node.getChildren( )
            
            for child in children:
                if isinstance(child, ast.Node ):
                    if not self.isConstant( child ):
                        return False
                    else:
                        continue
            result = True
        else:
            result = True
        
        return result
    
    def currInsideControllFlow(self):
        
#        print "     currInsideControllFlow"
        for node in self.ast_stack:
#            print "     ", node.__class__
            if isinstance( node , (ast.If,ast.While,ast.For) ):
                return True
#        print "     ", "False"
        return False
    
    def evaluateConstantNode(self,node):
        
        lam = ast.Lambda( (), (), 0, node, lineno=0 )
        lamast = ast.Expression(lam)
        lam.filename = 'dummy'
        lamast.filename = 'dummy'
        
        lam_globals = self.pyfunc.func_globals.copy()
        
#        pdb.set_trace()
        
        for item in self.scope:
            if self.scope.isConst(item):
                lam_globals[item] = self.scope.values[item].value
#                print "lam_globals[",item,"]",lam_globals[item]
            elif  self.scope.isFunction(item):
                lam_globals[item] = self.scope[item] 
#                print item, "func", self.scope.isFunction(item)
            
        
        codeobj = ExpressionCodeGenerator(lamast).getCode( )
        
        result = eval( codeobj, lam_globals )( )
        return result
        

    def visitIf(self,node):
        
#        print "=== visitIf", node
#        
#        pdb.set_trace( )
        if len(node.tests) == 1:
            test,body = node.tests[0]

            cl_test = self.dispatch(test)
            cl_body = self.dispatch(body)
            
            if self.isConstant( cl_test ):
                
                test_result = self.evaluateConstantNode( cl_test )
                
                if test_result:
                    result = self.dispatch( cl_body )
                else:
                    result = self.dispatch( node.else_ )
            else:
                else_ = self.dispatch( node.else_ )
#                print "should Get here", else_
                result = ast.If([(cl_test,cl_body)], else_, node.lineno)

        else:
            
            cltests = []
            
            for test,body in node.tests:
                 
                cl_test = self.dispatch(test)
                cl_body = self.dispatch(body)
                
                cltests.append( (cl_test,cl_body) )
            
            else_ = self.dispatch( node.else_)
    
            result = ast.If(cltests, else_, node.lineno)

        return result
    
    def visitIfExp(self,node):
        
        test = self.dispatch( node.test )
        
        
        then = self.dispatch( node.then )
        else_ = self.dispatch( node.else_ )
        
        if self.isConstant( test ):
            
            test_result = self.evaluateConstantNode( test )
            
            if test_result:
                return then
            else:
                return else_
            
        else:
            return ast.IfExp( test, then, else_, node.lineno)

    def visitReturn(self,node):
        
#        print "node.value", node.value
        value = self.dispatch(node.value)
        
        return ast.Return(value, node.lineno)
     
        
        
    def visitFor(self,node):
        
#        print "visitFor"
        
#        pdb.set_trace( )
        
        list_ = self.dispatch( node.list )
        if isinstance( list_, (ast.CallFunc,CLCallFunc) ):
#            print 
            if self.isConstant( list_.node ):
                result = self.evaluateConstantNode( list_.node )
                
                if result == range:
#                    print "list_.args", list_.args
                    if len(list_.args) == 1:
                        start = ast.Const(0)
                        stop = list_.args[0]
                        step = ast.Const(1)
                    elif len(list_.args) == 2:
                        start = list_.args[0]
                        stop = list_.args[1]
                        step = ast.Const(1)
                    elif len(list_.args) == 3:
                        start = list_.args[0]
                        stop = list_.args[1]
                        step = list_.args[2]
                    else:
                        raise Exception("range takes 1-3 arguments not %i " %len(list._args) )
                    
                    assign = self.dispatch(  node.assign )
                    body  = self.dispatch(  node.body )
                    loop_ = nodes.CLForLoop( assign, body, start, stop, step , lineno=node.lineno)
                    return loop_
#                    raise NotImplementedError("can not handle function %r as iterator yet..." %(result) )
                else:
                    raise NotImplementedError("can not handle function %r as iterator yet..." %(result) )
            else:
                raise NotImplementedError( "can not handle non-constant generator function yet..." )

#            print
            
            raise NotImplementedError("can not handle loop yet")
        
        else:  
            raise NotImplementedError("can not handle loop yet")
        
    
        
