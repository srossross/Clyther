'''
Created on May 9, 2010 by GeoSpin Inc
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
from compiler import ast

class sr(object):
    def __init__(self, string):
        self.string = string
    def __repr__(self):
        return str(self.string)
    
class WritePython(ASTVisitor):
    
    def __init__(self):
        self.out = StringIO.StringIO()
        self._cache = {}
        self._code = None
        
        self.indent = 0
        
        
    def default(self, node, *args):
        
        className = node.__class__.__name__
        raise SyntaxError("could not handle python syntax %s" % className , node.lineno , node,)
    
    def dispatch(self, node, *args):
        
#        result = ASTVisitor.dispatch(self, node,*args)
        self.node = node
        klass = node.__class__
        meth = self._cache.get(klass, None)
        if meth is None:
            className = klass.__name__
            meth = getattr(self, 'visit' + className, self.default)
            self._cache[klass] = meth
        
        if isinstance(meth , str):
#            pdb.set_trace()
            nodedict = vars(node).copy()
            for key, value in vars(node).items():
                if isinstance(value, ast.Node):
                    nodedict[key] = self.dispatch(value)
                    
            result = meth.format(**nodedict) 
        else:        
            result = meth(node, *args)

#        result = meth(node, *args)

        
        if result == NotImplemented:
            raise SyntaxError("could not handle python syntax %s" % className , node.lineno , node,)
        
        return result
        
    def _get_code(self):
        
        if self._code is None:
            self.out.seek(0)
            self._code = self.out.read()
        return self._code
    
    code = property(_get_code) 
        
    def visitModule(self, node):
        
            
        for item in node.node.nodes:
            self.dispatch(item)
            
        self.out.seek(0)
        
        print self.out.read()
        
    def _print(self, *args):
        
        self.out.write("%s%s\n" % (" "*4 * self.indent, " ".join(args)))
    
    def visitFunction(self, node):
        if node.decorators:
            for decorator in node.decorators:
                self._print(decorator)
            
        args = ", ".join(node.argnames)

        self._print("def %s(%s):" % (node.name, args))
        
        self.indent += 1
        self._print()
        
#        print ast.Function.code
        for stmnt in  node.code.nodes:
            
            small_stmnt = self.dispatch(stmnt)
            if small_stmnt:
                self._print("%s" % (small_stmnt)) 
        
        
        self._print("")
        
        self.indent -= 1 
        self._print("")
        
        
        


    def visitAssign(self, node):
        
        small_expr = self.dispatch(node.expr)
        small_nodes = [self.dispatch(val) for val in node.nodes]
        
        return "%s = %s" % (" = ".join(small_nodes), small_expr)
    
    def visitCallFunc(self, node):
        
        small_name = self.dispatch(node.node)
        small_args = [self.dispatch(arg) for arg in node.args]
#        print node.node
        return "%s(%s)" % (small_name, ", ".join(small_args))
    
    def visitAssName(self, node):
        
        if node.flags == 'OP_DELETE':
            return 'del %s' % node.name
            
        else:
            return node.name
    
    def visitName(self, node):
        return node.name    
    
    
    def visitConst(self, node):
        result = repr(node.value)
        
        return result 
    
    visitMul = '({left}) * ({right})'
    visitAdd = '({left}) + ({right})'
    visitSub = '({left}) - ({right})'
    visitDiv = '({left}) / ({right})'
    visitFloorDiv = '({left}) // ({right})'
    visitIfExp = "(({then}) if ({test}) else ({else_}))"
    visitNot = "not ({expr})"
    visitContinue = 'continue'
    visitUnaryAdd = '+({expr})'
    visitUnarySub = '-({expr})'
    visitAugAssign = "{node} {op} {expr}"
    visitGetattr = '{expr}.{attrname}'
    visitLeftShift = '{left} << {right}'
    visitRightShift = '{left} >> {right}'
    visitBreak = 'break'
    visitYield = 'yield {value}'
    visitInvert = '~{expr}'
    def visitPrintnl(self, node):
        
        nodes = [self.dispatch(n) for n in node.nodes]
        if node.dest:
            dest = self.dispatch(dest)
            return "print >> %s, %s" % (dest, ", ".join(nodes))
        else:
            return "print %s" % (", ".join([str(x) for x in nodes]),)
        
        
    def visitListComp(self, node):
        
        expr = self.dispatch(node.expr)
        quals = [self.dispatch(qual) for qual in node.quals]
        return "[%s %s]" % (expr, ' '.join(quals))
    
    def visitAssTuple(self, node):
        nodes = [ self.dispatch(n) for n in node.nodes]
        if len(nodes) == 1:
            return '(%s,)' % (nodes[0])
        else:
            return '(%s)' % (", ".join(nodes))
            
        
    def visitListCompFor(self, node):
        
        assign = self.dispatch(node.assign)
        list_ = self.dispatch(node.list)
        
        ifs = [self.dispatch(if_) for if_ in node.ifs]
        ifs = ' '+' '.join(ifs) if ifs else ''
         
        return "for %s in %s%s" % (assign, list_, ifs)
    
    visitListCompIf = 'if {test}'
    
    def visitSubscript(self, node):
        
        expr = self.dispatch(node.expr)
        subs = [self.dispatch(sub) for sub in node.subs]
        
        return "%s[%s]" % (expr, ",".join(subs))
    
    def visitSliceobj(self, node):
        nodes = []
        for n in node.nodes:
            n = self.dispatch(n)
            if n == 'None':
                nodes.append('')
            else:
                nodes.append(n)
        
        return ":".join(nodes)
        
    def visitWhile(self, node):
        
        test = self.dispatch(node.test)
        
        self._print('while %s:' % (test))
        self.indent += 1
        
        self.dispatch(node.body)
#        ast.While(test, body, else_, node.lineno)

        self.indent -= 1 

    def visitCompare(self, node):
        
#        print "node.expr",node.expr
        expr = self.dispatch(node.expr)
        
        string_list = ["(%s)" % expr] 
        for opname, opexpr in node.ops:
            oexpr = self.dispatch(opexpr)
            string_list.append("%s (%s)" % (opname, oexpr))
        
        return " ".join(string_list)
        
#        ast.Compare(expr, ops, lineno)        
        
    def visitStmt(self, node):
        
        for stmnt in node.nodes:
            
            s = self.dispatch(stmnt)
            
            if s is None:
                self._print("")
            else:
                self._print("%s" % s)
            
    
    
    def visitIf(self, node):
        
        
        cltests = []
        
        test, body = node.tests[0]
        str_test = self.dispatch(test)
    
        self._print('if %s:' % (str_test))
        self.indent += 1
        
        self.dispatch(body)
        
        self.indent -= 1
        
        for test, body in node.tests[1:]:
            str_test = self.dispatch(test)
        
            self._print('elif %s:' % (str_test))
            self.indent += 1
            
            self.dispatch(body)
            
            self.indent -= 1
            
        if node.else_:
            
            self._print('else:')
            self.indent += 1
            
            self.dispatch(node.else_)
            
            self.indent -= 1
        else:
            self._print("")
            
            
        return None
    
    def visitDiscard(self, node):
        
        return self.dispatch(node.expr)

    def visitReturn(self, node):
        
        value = self.dispatch(node.value)
         
        return "return %s" % value
    
    def visitOr(self, node):
        return "((%s))" % ") or (".join([ self.dispatch(nd) for nd in node.nodes if nd is not None])

    def visitBitor(self, node):
        return "((%s))" % ") | (".join([ self.dispatch(nd) for nd in node.nodes if nd is not None])
        
    def visitAnd(self, node):
        return "((%s))" % ") and (".join([ self.dispatch(nd) for nd in node.nodes if nd is not None])
    
    def visitBitand(self, node):
        return "((%s))" % ") & (".join([ self.dispatch(nd) for nd in node.nodes if nd is not None])
        
    def visitBitxor(self, node):
        return "((%s))" % ") ^ (".join([self.dispatch(nd) for nd in node.nodes if nd is not None])    
    
    def visitTuple(self, node):
        clnodes = [ self.dispatch(nd) for nd in node.nodes]
        result = '(%s)' % ", ".join(clnodes)
        return result 
        
    def visitFor(self, node):
        
#        ast.For(assign, list, body, else_, lineno)
                
        assign = self.dispatch(node.assign)
        list_ = self.dispatch(node.list)
        
        self._print('for %s in %s:' % (assign, list_))
        self.indent += 1
        
        self.dispatch(node.body)
#        ast.While(test, body, else_, node.lineno)

        self.indent -= 1
         
        if node.else_:
            self._print('else: ' % (assign, list_))
            self.indent += 1
            
            else_ = self.dispatch(node.else_)
    
            self.indent -= 1
            
    
    visitPass = 'pass'
            
    def visitList(self, node):
        
        
        nodes = [self.dispatch(item) for item in node.nodes]
            
        return "[%s]" % ", ".join(nodes)
        
        ast.List(nodes, node.lineno)
    
    def visitImport(self, node):
        
        return "import %s" % ", ".join([str(name[0]) for name in  node.names]) 
    
    
