'''
Created on Apr 14, 2010

@author: sean
'''

import dis
from opcode import *
import pdb

from compiler import ast
from compiler.visitor import ASTVisitor
import opcode
import compiler
import new
import sys
from clyther.api.ast.pythoncodegen import WritePython
import logging

STORE_CODES = ['STORE_FAST', 'STORE_ATTR', 'STORE_DEREF', 'STORE_GLOBAL',
              'STORE_MAP', 'STORE_NAME',
              'STORE_SLICE+0', 'STORE_SLICE+1', 'STORE_SLICE+2', 'STORE_SLICE+3',
              'STORE_SUBSCR']


class Test(ast.Node):
    def __init__(self, expr, jump_from, jump_to):
        self.expr = expr
        self.jump_to = jump_to
        self.jump_from = jump_from
        
    def __repr__(self):
        return "%s( %r, from=%s, to=%s )" % (self.__class__.__name__, self.expr, self.jump_from, self.jump_to)
    
class TestTrue(Test): 
    lineno = -1
class TestFalse(Test): 
    lineno = -1
    

class InstructionVisitor(object):
    
    def __init__(self, func, instructions):
        
        self.func = func
        self.co = func.func_code
        
        self.instructions = instructions
        self.instructions_orig = list(instructions)
        self.curridx = 0
#        self.pre = [ ]

        self.curr_instlst = []
        self.stacks = []
        self.iters = []
        self.tests = []
        self.post = [ ]
        self.callback_i = {}
        
        logging.basicConfig(level=logging.DEBUG , format='%(levelname)10s: %(message)s')
        
        self.log = logging.getLogger('InstructionVisitor')
        self.inc = 0
    
    def indent(self):
        self.inc += 1
    def dedent(self):
        self.inc -= 1
    def debug(self, msg, *args, **kwargs):
        self.log.debug(("    "*self.inc) + msg.format(*args, **kwargs))
    def dispatch(self, inst):
        
        opname = inst.opname.replace("+", "_")
        name = "visit%s" % opname
        self.debug('visit {instruction} {opname}' , opname=opname, instruction=inst.i)
        self.indent()
        meth = getattr(self, name, None)
        
        if meth is None:
            msg = "bytecode instruction %s (%i) is not yet implemented" % (inst.opname, inst.op)
            raise NotImplementedError(msg)
        
        self.curridx += 1
        
        if inst.i in self.callback_i:
            callback, data = self.callback_i[inst.i]
            callback(inst, data)
            
        result = meth(inst)
        self.dedent()
        self.debug('expr {expr}' , expr=result)
        
        return result
    
    def pop_expr(self):
        'return the last compiled expresion'
        stack = self.stacks[-1]
        
        node = stack.pop()
        
        clsname = node.__class__.__name__
        
        meth = getattr(self, "expr%s" % clsname, None)
        
        self.debug('  pop_expr - {0} ', node)
        if meth is None:
            return node
        else:
            return meth(node) 
        
    def poll_expr(self):
        return self.stacks[-1][-1]
    
    def push_expr(self, expr):
        self.stacks[-1].append(expr)
        self.debug('  push_expr - {0} ', expr)    
    
    def poll_inst(self):
        _instructions = self.curr_instlst[-1]
        if len(_instructions):
            return _instructions[ 0 ]
        else:
            return None
            
    
    def pull_inst(self):
        _instructions = self.curr_instlst[-1]
        self.debug('  pull_inst - {0} ', _instructions[0])
        return _instructions.pop(0)
    
    
    def pull_insts_until(self, name):
        self.debug('  pull_insts_until - {0} ', name)
        _instructions = self.curr_instlst[-1]
        result = []
        while _instructions[0].opname != name:
            result.append(_instructions.pop(0))
            
        return result

    def pull_insts_upto(self, loc):
        self.debug('  pull_insts_upto - {0} ', loc)
        _instructions = self.curr_instlst[-1]
        result = []
        while _instructions[0].i != loc:
            result.append(_instructions.pop(0))
            
        return result

    def pop_exprs(self, num):
        
        exprs = []
        
        for __ in range(num):
            
            node = self.pop_expr()
            exprs.insert(0, node)
        self.debug('  pop_exprs - {0} ', exprs)
        return exprs
        
    def seek(self, i , include=True):
        
        new_instlist = []
        
        while 1:
            inst = self.poll_inst()
            
            if inst is None:
                break
            
            if inst.i >= i:
                
                if include:
                    self.pull_inst()
                    new_instlist.append(inst)
                    
                break
            
            else:
                self.pull_inst()
                new_instlist.append(inst)
        
        return new_instlist
            
    def loop(self, instructions):
        
        if instructions:
            self.debug("  Looping over instructions: %i to %i" % (instructions[0].i, instructions[-1].i))
            self.indent()
            
        _instructions = list(instructions)
        self.curr_instlst.append(_instructions)
        stack = [ ]
        
        self.stacks.append(stack)

        
        while _instructions:
            
            inst = _instructions.pop(0)
            node = self.dispatch(inst)
            if node is not None:
                stack.append(node)
                
        self.curr_instlst.pop()
        self.stacks.pop()
        
        self.dedent()
        
        return stack
    def print_co(self):
        print
        print "=" * 80
        dis.dis(self.co)
#        printDis(self.co, self.instructions)
    
    def start(self):
        self.debug("Start")
        lineno = self.instructions[0].lineno
        
        try:
            nodes = self.loop(self.instructions)
        except:
            self.print_co()
            raise
        
        decorators = None
        name = self.func.__name__
        argnames = list(self.co.co_varnames[ :self.co.co_argcount ])
        doc = self.func.__doc__
        code = ast.Stmt(nodes, lineno)
        lineno = self.co.co_firstlineno
        flags = 0
        if self.func.func_defaults is None:
            defaults = []
        else:
            defaults = []
            for item in self.func.func_defaults:
                if item in self.func.func_globals.values():
                    for key in self.func.func_globals.keys():
                        if item is self.func.func_globals[key]:
                            defaults.append(ast.Name(key))
                            break
                else:
                    defaults.append(ast.Const(item))
        
        self.function = ast.Function(decorators, name, argnames, defaults, flags, doc, code, lineno)
        
        self.debug("Finished")
        return self.function
        
    def visitDELETE_FAST(self, inst):
        
        name = getattr(inst.code, inst.arg_type)[inst.oparg]
        
        return ast.AssName(name, 'OP_DELETE', inst.lineno)
    
    def visitLOAD_FAST(self, inst):
        
        name = getattr(inst.code, inst.arg_type)[inst.oparg]
        
        return ast.Name(name, inst.lineno)

    def visitLOAD_GLOBAL(self, inst):
        
        name = getattr(inst.code, inst.arg_type)[inst.oparg]
        
        return ast.Name(name, inst.lineno)
    
    def visitLOAD_CONST(self, inst):
        
        value = getattr(inst.code, inst.arg_type)[inst.oparg]
        if isinstance(value, tuple):
            nodes = [ ast.Const(val, inst.lineno) for val in value]
            return ast.Tuple(nodes, inst.lineno) 
        return ast.Const(value, inst.lineno)
    
    def visitBINARY_SUBSCR(self, inst):
        
        subs = self.pop_expr()
        expr = self.pop_expr()
        
        if isinstance(subs, ast.Tuple):
            subs = subs.nodes
        else:
            subs = [subs]

        return ast.Subscript(expr, 'OP_APPLY', subs, inst.lineno)
    
    def visitBINARY_ADD(self, inst):
        
        right = self.pop_expr()
        left = self.pop_expr()
        
        return ast.Add((left, right), inst.lineno)

    def visitBINARY_SUBTRACT(self, inst):
        
        right = self.pop_expr()
        left = self.pop_expr()
        
        return ast.Sub((left, right), inst.lineno)
    
    def visitBINARY_MULTIPLY(self, inst):
        
        right = self.pop_expr()
        left = self.pop_expr()
        
        return ast.Mul((left, right), inst.lineno)

    def visitBINARY_DIVIDE(self, inst):
        
        right = self.pop_expr()
        left = self.pop_expr()
        
        return ast.Div((left, right), inst.lineno)

    def visitBINARY_FLOOR_DIVIDE(self, inst):
        
        right = self.pop_expr()
        left = self.pop_expr()
        
        return ast.FloorDiv((left, right), inst.lineno)

    def visitBINARY_TRUE_DIVIDE(self, inst):
        
        right = self.pop_expr()
        left = self.pop_expr()
        
        return ast.Div((left, right), inst.lineno)

    def visitBINARY_POWER(self, inst):
        
        right = self.pop_expr()
        left = self.pop_expr()
        
        return ast.Power((left, right), inst.lineno)

    def visitBINARY_AND(self, inst):
        
        right = self.pop_expr()
        left = self.pop_expr()
        
        if isinstance(left , ast.Bitand):
            return ast.Bitand(left.nodes + [right], inst.lineno)
        else:
            return ast.Bitand([left, right], inst.lineno)

    def visitBINARY_OR(self, inst):
        
        right = self.pop_expr()
        left = self.pop_expr()
        
        if isinstance(left , ast.Bitor):
            return ast.Bitor(left.nodes + [right], inst.lineno)
        else:
            return ast.Bitor([left, right], inst.lineno)

    def visitBINARY_LSHIFT(self, inst):
        
        right = self.pop_expr()
        left = self.pop_expr()
        
        return ast.LeftShift((left, right), inst.lineno)

    def visitBINARY_RSHIFT(self, inst):
        
        right = self.pop_expr()
        left = self.pop_expr()
        
        return ast.RightShift((left, right), inst.lineno)
    
    def visitBINARY_XOR(self, inst):
        right = self.pop_expr()
        left = self.pop_expr()
        
        return ast.Bitxor((left, right), inst.lineno)
        

    def visitBINARY_MODULO(self, inst):
        
        right = self.pop_expr()
        left = self.pop_expr()
        
        return ast.Mod((left, right), inst.lineno)
    
    def visitBREAK_LOOP(self, inst):
        return ast.Break(inst.lineno)
    
    def build_list_comp(self, inst):
        # List Comprehension
        dup_top = self.pull_inst()
        store_fast = self.pull_inst()
        insts = self.pull_insts_until('GET_ITER')
        iter_over = self.loop(insts)
        
        print "iter_over", iter_over
        self.push_expr(iter_over)
        
        get_iter = self.pull_inst()
        for_iter = self.pull_inst()
        
        store = self.pull_inst()
        assign = self.dispatch(store)
        
        print "assign", assign
        
        insts = self.pull_insts_upto(for_iter.to)
        
        print "insts up to %s %s" % (for_iter.to, insts)
        
        jump_absolute = insts.pop()
        
        xxx = insts.pop()
        
        print xxx.opname
        if xxx.opname == 'LIST_APPEND':
            #No if statement
            
            #unused 
            load_fast = insts.pop(0)
            print ":load_fast", load_fast
            
            body, = self.loop(insts)
            print "body", body
            expr, = assign.expr
            assng, = assign.nodes
            quals = [ast.ListCompFor(assng, expr, [], lineno=inst.lineno)]
            
        elif xxx.opname == 'POP_TOP':
            
            jump_absolute2 = insts.pop()
            list_append = insts.pop()
            
            exprs = self.loop(insts)
            
            cb, data = self.callback_i[xxx.i]
            print data
            
            tests = []
            body = []
            for _ in range(len(data)):
                tests.append(exprs.pop(0))
                
            if len(tests) == 1:
                texpr = tests[0].expr
                if isinstance(tests[0], TestFalse):
                    test = texpr
                else:
                    test = ast.Not(texpr, lineno=texpr.lineno)
            else:
                raise Exception("adf")
                for test in tests:
                    pass
            
            unused, body = exprs
            
            expr, = assign.expr
            assng, = assign.nodes

            compif = ast.ListCompIf(test, lineno=test.lineno)
            quals = [ast.ListCompFor(assng, expr, [compif], lineno=inst.lineno)]
            
        else:
            raise Exception("dev err? expected")
             
        delete_fast = self.pull_inst()
         
        expr = assign.nodes
        return ast.ListComp(body, quals, inst.lineno)
        

    def visitBUILD_LIST(self, inst):
        
        nargs = inst.oparg
        
        
        if nargs == 0:
            return self.build_list_comp(inst)
        else:
            # List Creation
            nodes = self.pop_exprs(nargs)
            return ast.List(nodes, inst.lineno)

    def visitBUILD_TUPLE(self, inst):
        
        nargs = inst.oparg
        
        nodes = self.pop_exprs(nargs)
        
        return ast.Tuple(nodes, inst.lineno)

    def visitCOMPARE_OP(self, inst):
        
        right = self.pop_expr()
        left = self.pop_expr()
        
        op = opcode.cmp_op[inst.oparg]
        ops = [(op, right)]
        
        return ast.Compare(left, ops, inst.lineno)
    
    def visitUNARY_NOT(self, inst):
        
        expr = self.pop_expr()
        return ast.Not(expr, inst.lineno)
    
    def visitUNARY_NEGATIVE(self, inst):
        expr = self.pop_expr()
        return ast.UnarySub(expr, inst.lineno)
    
    def visitUNARY_POSITIVE(self, inst):
        expr = self.pop_expr()
        return ast.UnaryAdd(expr, inst.lineno)

    def visitUNARY_INVERT(self, inst):
        expr = self.pop_expr()
        return ast.Invert(expr, inst.lineno)
        
    def visitDUP_TOP(self, inst):
        expr = self.pop_expr()
        
        
        store1 = self.pull_STORE()
        stores = store1

        while self.poll_inst().opname == "DUP_TOP":
            self.pull_inst()
            store = self.pull_STORE()
            stores.extend(store) 
            
        store2 = self.pull_STORE()
        stores.extend(store2)
         
        
        assign = ast.Assign(stores, expr, lineno=inst.lineno)

        return assign
        
    
    def visitINPLACE_ADD(self, inst):
        
        op = "+="
        expr = self.pop_expr()
        node = self.pop_expr()
        
        next = self.pull_inst()
        
        if (next.opname != 'STORE_FAST'):
            raise Exception("next op should be STORE_FAST")
        
        return ast.AugAssign(node, op, expr, inst.lineno)

    def visitINPLACE_AND(self, inst):
        
        op = "&="
        
        expr = self.pop_expr()
        node = self.pop_expr()
        
        next = self.pull_inst()
        
        if (next.opname != 'STORE_FAST'):
            raise Exception("next op should be STORE_FAST")
        
        return ast.AugAssign(node, op, expr, inst.lineno)

    def visitINPLACE_DIVIDE(self, inst):
        
        op = "/="
        
        expr = self.pop_expr()
        node = self.pop_expr()
        
        next = self.pull_inst()
        
        if (next.opname != 'STORE_FAST'):
            raise Exception("next op should be STORE_FAST")
        
        return ast.AugAssign(node, op, expr, inst.lineno)

    def visitINPLACE_FLOOR_DIVIDE(self, inst):
        
        op = "//="
        
        expr = self.pop_expr()
        node = self.pop_expr()
        
        next = self.pull_inst()
        
        if (next.opname != 'STORE_FAST'):
            raise Exception("next op should be STORE_FAST")
        
        return ast.AugAssign(node, op, expr, inst.lineno)
    
    def visitINPLACE_LSHIFT(self, inst):
        
        op = "<<="
        
        expr = self.pop_expr()
        node = self.pop_expr()
        
        next = self.pull_inst()
        
        if (next.opname != 'STORE_FAST'):
            raise Exception("next op should be STORE_FAST")
        
        return ast.AugAssign(node, op, expr, inst.lineno)

    def visitINPLACE_RSHIFT(self, inst):
        
        op = ">>="
        
        expr = self.pop_expr()
        node = self.pop_expr()
        
        next = self.pull_inst()
        
        if (next.opname != 'STORE_FAST'):
            raise Exception("next op should be STORE_FAST")
        
        return ast.AugAssign(node, op, expr, inst.lineno)
    
    def visitINPLACE_MODULO(self, inst):
        
        op = "%="
        
        expr = self.pop_expr()
        node = self.pop_expr()
        
        next = self.pull_inst()
        
        if (next.opname != 'STORE_FAST'):
            raise Exception("next op should be STORE_FAST")
        
        return ast.AugAssign(node, op, expr, inst.lineno)
    
    def visitINPLACE_MULTIPLY(self, inst):
        
        op = "*="
        
        expr = self.pop_expr()
        node = self.pop_expr()
        
        next = self.pull_inst()
        
        if (next.opname != 'STORE_FAST'):
            raise Exception("next op should be STORE_FAST")
        
        return ast.AugAssign(node, op, expr, inst.lineno)

    def visitINPLACE_OR(self, inst):
        
        op = "|="
        
        expr = self.pop_expr()
        node = self.pop_expr()
        
        next = self.pull_inst()
        
        if (next.opname != 'STORE_FAST'):
            raise Exception("next op should be STORE_FAST")
        
        return ast.AugAssign(node, op, expr, inst.lineno)

    def visitINPLACE_POWER(self, inst):
        
        op = "**="
        
        expr = self.pop_expr()
        node = self.pop_expr()
        
        next = self.pull_inst()
        
        if (next.opname != 'STORE_FAST'):
            raise Exception("next op should be STORE_FAST")
        
        return ast.AugAssign(node, op, expr, inst.lineno)
    
    def visitINPLACE_SUBTRACT(self, inst):
        
        op = "-="
        
        expr = self.pop_expr()
        node = self.pop_expr()
        
        next = self.pull_inst()
        
        if (next.opname != 'STORE_FAST'):
            raise Exception("next op should be STORE_FAST")
        
        return ast.AugAssign(node, op, expr, inst.lineno)
    
    def visitINPLACE_TRUE_DIVIDE(self, inst):
        
        op = "/="
        
        expr = self.pop_expr()
        node = self.pop_expr()
        
        next = self.pull_inst()
        
        if (next.opname != 'STORE_FAST'):
            raise Exception("next op should be STORE_FAST")
        
        return ast.AugAssign(node, op, expr, inst.lineno)

    def visitINPLACE_XOR(self, inst):
        
        op = "^="
        
        expr = self.pop_expr()
        node = self.pop_expr()
        
        next = self.pull_inst()
        
        if (next.opname != 'STORE_FAST'):
            raise Exception("next op should be STORE_FAST")
        
        return ast.AugAssign(node, op, expr, inst.lineno)
    
    def visitPRINT_ITEM(self, inst):
        
        
        expr = self.pop_expr()
        
        if self.poll_inst().opname == 'PRINT_NEWLINE':
            
            newline = self.pull_inst()
            return ast.Printnl([expr], None, inst.lineno)
        else:
            return ast.Print([expr], None, inst.lineno)
        
    def visitSLICE_0(self, inst):
        
        expr = self.pop_expr()
        
        lower = None
        upper = None
        flags = "OP_APPLY"
        return ast.Slice(expr, flags, lower, upper, lineno=inst.lineno)
    
    def visitSLICE_1(self, inst):
        
        s1 = self.pop_expr() 
        expr = self.pop_expr()
        
        lower = s1
        upper = None
        flags = "OP_APPLY"
        return ast.Slice(expr, flags, lower, upper, lineno=inst.lineno)

    def visitSLICE_2(self, inst):
        
        s1 = self.pop_expr() 
        expr = self.pop_expr()
        
        lower = None
        upper = s1
        flags = "OP_APPLY"
        return ast.Slice(expr, flags, lower, upper, lineno=inst.lineno)
    
    def visitSLICE_3(self, inst):
        
        s2 = self.pop_expr() 
        s1 = self.pop_expr() 
        expr = self.pop_expr()
        
        lower = s1
        upper = s2
        flags = "OP_APPLY"
        return ast.Slice(expr, flags, lower, upper, lineno=inst.lineno)
    
    def visitSTORE_SLICE_0(self, inst):
        expr = self.pop_expr()
        nodes = self.pop_expr()
#        nodes_ = self.pop_expr( )
        
        lower = None
        upper = None
        flags = "OP_ASSIGN"
        slice_ = ast.Slice(expr, flags, lower, upper, lineno=inst.lineno)
        
        return ast.Assign([slice_], nodes, lineno=inst.lineno)

    def visitSTORE_SLICE_1(self, inst):
        
        s1 = self.pop_expr()
        expr = self.pop_expr()
        nodes = self.pop_expr()
#        nodes_ = self.pop_expr( )
        
        lower = s1
        upper = None
        flags = "OP_ASSIGN"
        slice_ = ast.Slice(expr, flags, lower, upper, lineno=inst.lineno)
        
        return ast.Assign([slice_], nodes, lineno=inst.lineno)
    
    def visitSTORE_SLICE_2(self, inst):
        
        s2 = self.pop_expr()
#        s1 = self.pop_expr( )
        expr = self.pop_expr()
        nodes = self.pop_expr()
#        nodes_ = self.pop_expr( )
        
        lower = None
        upper = s2
        flags = "OP_ASSIGN"
        slice_ = ast.Slice(expr, flags, lower, upper, lineno=inst.lineno)
        
        return ast.Assign([slice_], nodes, lineno=inst.lineno)

    def visitSTORE_SLICE_3(self, inst):
        
        s2 = self.pop_expr()
        s1 = self.pop_expr()
        expr = self.pop_expr()
        nodes = self.pop_expr()
#        nodes_ = self.pop_expr( )
        
        lower = s1
        upper = s2
        flags = "OP_ASSIGN"
        slice_ = ast.Slice(expr, flags, lower, upper, lineno=inst.lineno)
        
        return ast.Assign([slice_], nodes, lineno=inst.lineno)
    
    

    
    def visitBUILD_SLICE(self, inst):
        
        inst.oparg
        
        args = self.pop_exprs(num=inst.oparg)
#        s1 = self.pop_expr()
#        s2 = self.pop_expr()
#        s3 = self.pop_expr()
        
        return ast.Sliceobj(args, lineno=inst.lineno)
        
    
    def find(self, to):
        
        for i, inst in enumerate(self.curr_insts):
            if inst.i == to:
                return i, inst
            
        return - 1, None
        
    def get(self, idx):
        return self.instructions[idx]
    
    def _get_curr_insts(self):
        return self.curr_instlst[-1]
    
    curr_insts = property(_get_curr_insts)
    
    def assign_test_(self, inst, data):
        expr = self.pop_expr()
        
        for key in sorted(data.keys()):
            item = data[key]
            
            if item not in [True, False]:
                raise Exception("dev error?")
            
            testif_expr = self.pop_expr()
            Node = ast.Or if item is True else ast.And
              
            expr = Node([testif_expr.expr, expr], testif_expr.expr.lineno)
            
        self.push_expr(expr)
        
    def _warp_bool_assign(self, inst, pop_top, value):
        
        if inst.to not in self.callback_i:
            self.callback_i[inst.to] = [self.assign_test_, {inst.i:value}]
        else:
            self.callback_i[inst.to][1][inst.i] = value
            
        #=======================================================================
        # Special case
        #=======================================================================
        if pop_top.i in self.callback_i:
            _, data = self.callback_i[pop_top.i]
            self.callback_i[inst.to][1].update(data)
            
    def visitJUMP_IF_FALSE(self, inst):
        
        expr = self.pop_expr()
        pop_top = self.pull_inst()
        
        self._warp_bool_assign(inst, pop_top, False)
        
        return TestFalse(expr, inst.i, inst.to)
        
    def visitJUMP_IF_TRUE(self, inst):

        expr = self.pop_expr()
        pop_top = self.pull_inst()
        
        self._warp_bool_assign(inst, pop_top, True)
        
        return TestTrue(expr, inst.i, inst.to)
        
    def format_tests(self, tests, jump_to):
        
        prev_test = tests[0]
        
        node = prev_test.expr
         
        if tests[1:]:
            for test in tests[1:]:
                if prev_test.jump_to < jump_to:
                    node = ast.Or((node, test.expr), test.expr.lineno)
                elif prev_test.jump_to == jump_to:
                    node = ast.And((node, test.expr), test.expr.lineno)
                prev_test = test
        elif isinstance(prev_test, TestTrue):
            node = ast.Not(node, node.lineno) 
                
        
        return node
    
    def close_if(self, inst, data):
        tests = []
        else_stmnt = []
        expr = self.pop_expr()
        while not isinstance(expr, ast.If):
            else_stmnt.insert(0, expr)
            expr = self.pop_expr()
            
        if else_stmnt:
            else_ = ast.Stmt(else_stmnt, else_stmnt[0].lineno)
        else:  
            else_ = None
            
        while expr is not data[0]:
            if not isinstance(expr, ast.If):
                raise Exception("dev error?")
            
            tests = expr.tests + tests
            
            expr = self.pop_expr()
            
        tests = expr.tests + tests
        
        result = ast.If(tests, else_, tests[0][0].lineno)
        
        self.push_expr(result)
        
    
    def visitJUMP_FORWARD(self, inst):
        

        code_block = []
        expr = self.pop_expr()
        while not isinstance(expr, Test):
            code_block.insert(0, expr)
            expr = self.pop_expr()
            
        next_inst = self.pull_inst()
        inst_no = next_inst.i
        
        test = expr
        tests = [] 
        while 1:
            if not isinstance(test, Test):
                self.push_expr(test)
                break
            elif test.jump_to > inst_no:
                self.push_expr(test)
                break
            else:
                tests.insert(0, test)
            
            if len(self.stacks[-1]):   
                test = self.pop_expr()
            else:
                break

        body = ast.Stmt(code_block, code_block[0].lineno)
        tests_ = self.format_tests(tests, inst_no), body
        
        result = ast.If([tests_], None, tests_[0].lineno)
#        print "self.callback_i" ,inst.to

        if inst.to not in self.callback_i:
            self.callback_i[inst.to] = (self.close_if, [result])
        else:
            self.callback_i[inst.to][1].append(result)

        return result 

        
    def visitLOAD_ATTR(self, inst):
        
        expr = self.pop_expr()
        
        attrname = getattr(inst.code, inst.arg_type)[inst.oparg]
        
        return ast.Getattr(expr, attrname, inst.lineno)
    
    def visitSTORE_ATTR(self, inst):
        
        expr = self.pop_expr()
        
        attrname = getattr(inst.code, inst.arg_type)[inst.oparg]
        
        expr2 = self.pop_expr()
        nodes = [ast.AssAttr(expr, attrname, 'OP_ASSIGN', inst.lineno)]
        
        return ast.Assign(nodes, expr2, inst.lineno)
    
    def visitPOP_TOP(self, inst):
        
        expr = self.pop_expr()
        
        return ast.Discard(expr, inst.lineno)
        
    def visitSTORE_FAST(self, inst):
        
        
        expr = self.pop_expr()
        
        name = getattr(inst.code, inst.arg_type)[inst.oparg]
        node = ast.AssName(name, 'OP_ASSIGN', inst.lineno)
          
        nodes = [node]
        
        return ast.Assign(nodes, expr, inst.lineno)
    
    def visitSTORE_SUBSCR(self, inst):
        
        subs = self.pop_expr()
        
        if isinstance(subs, ast.Tuple):
            subs = subs.nodes
        else:
            subs = [subs]
        sexpr = self.pop_expr()
        expr = self.pop_expr()
        subscr = ast.Subscript(sexpr, 'OP_ASSIGN', subs, lineno=inst.lineno)
        
        return ast.Assign([subscr], expr, lineno=inst.lineno)
    
    
        
    def visitRETURN_VALUE(self, inst):
        
        value = self.pop_expr()
        
        return ast.Return(value, inst.lineno)
    

    def visitCALL_FUNCTION(self, inst):
        
        nargs = (inst.oparg & ((1 << 9) - 1))
        nkwargs = (inst.oparg >> 8)
        
        kwargs = self.pop_exprs(nkwargs * 2)
        args = list(self.pop_exprs(nargs))
        
        while kwargs:
            
            name = kwargs.pop(0).value
            expr = kwargs.pop(0)
            
            result = ast.Keyword(name, expr, lineno=inst.lineno)
            
            args.append(result)
            
        node = self.pop_expr()
        
        star_args = None
        dstar_args = None
        
        return ast.CallFunc(node, args, star_args, dstar_args, inst.lineno)
    
    
    def create_for_loop(self, inst, loop_items):
    
        self.iters.append([])
        
        body_nodes = self.loop(loop_items)
        
        if not len(body_nodes):
            body_nodes = [ast.Pass(inst.lineno)]
        
        
        body = ast.Stmt(body_nodes, lineno=inst.lineno)
        iters = self.iters.pop()
        
        
        list_ = iters[0]
        assign = iters[1][0]
        
        return ast.For(assign, list_, body, None, lineno=inst.lineno)

    def close_while(self, inst, data):
        
        tests = []
        else_stmnt = []
        expr = self.pop_expr()
        while not isinstance(expr, ast.If):
            else_stmnt.insert(0, expr)
            expr = self.pop_expr()
            
        if else_stmnt:
            else_ = ast.Stmt(else_stmnt, else_stmnt[0].lineno)
        else:  
            else_ = None
            
        while expr is not data[0]:
            if not isinstance(expr, ast.If):
                raise Exception("dev error?")
            
            tests = expr.tests + tests
            
            expr = self.pop_expr()
            
        tests = expr.tests + tests
        
        result = ast.If(tests, else_, tests[0][0].lineno)
        
        self.push_expr(result)
        

    def create_while_loop(self, inst, loop_items, pop_top):
        

        body_nodes = self.loop(loop_items)
        
        else_ = None
        
        cb, data = self.callback_i[pop_top.i]
        
        test = body_nodes.pop(0).expr
        
        for key in sorted(data.keys())[:-1]:
            item = data[key]
            
            if item not in [True, False]:
                raise Exception("dev error?")
            
            testif_expr = body_nodes.pop(0)
            Node = ast.Or if item is True else ast.And
              
            test = Node([test, testif_expr.expr], testif_expr.expr.lineno)
        
        

        if not len(body_nodes):
            body_nodes = [ast.Pass(inst.lineno)]
        
        body = ast.Stmt(body_nodes, lineno=inst.lineno)
        
        return ast.While(test, body, else_, lineno=inst.lineno)
    
    def visitSETUP_LOOP(self, inst):
        
        loop_items = self.pull_insts_upto(inst.to)
        
        return self.loop(loop_items)

#        pop_block = loop_items.pop()
#        jump = loop_items.pop()
#        
#        if jump.opname == 'JUMP_ABSOLUTE':
#            return self.create_for_loop(inst, loop_items)
#        else:
#            pop_top = jump
#            jump = loop_items.pop()
#            return self.create_while_loop(inst, loop_items, pop_top)
    
    def visitJUMP_ABSOLUTE(self, inst):
        
        return ast.Continue(inst.lineno)
    
        print inst
        inst = self.pull_inst()
        
#        
        if inst.opname != "POP_BLOCK":
            raise Exception("dev: error creating loop got %r" % inst.opname)
        
        return
    
    
    def visitFOR_ITER(self, inst):
        
        stored = self.pull_STORE()
        self.iters[-1].append(stored)
        
        return 
    
    def visitGET_ITER(self, inst):
        
        expr = self.pop_expr()
        self.iters[-1].append(expr)
        
        return
    
    def visitYIELD_VALUE(self, inst):

        expr = self.pop_expr()
        return ast.Yield(expr, inst.lineno)
    
    def pull_STORE(self):
        
        sflag = False
        stack = self.stacks[-1]
        
        while sflag is False:
            
            newinst = self.pull_inst()
        
            sflag = newinst.opname in STORE_CODES
            if sflag:
                if newinst.opname in ['STORE_SUBSCR']:
                    stack.insert(-2, None)
                else:
                    stack.append(None)
                    
            node = self.dispatch(newinst)
            
            if not sflag:
                stack.append(node)

             
        if isinstance(node, ast.Assign):
            anode = node.nodes
        else:
            raise Exception("dev: check this")
                
        return anode

    
    def visitUNPACK_SEQUENCE(self, inst):
        
        
        expr = self.pop_expr()
        
        stores = []
        
        while len(stores) < inst.oparg:
            
            snode = self.pull_STORE()
            stores.append(snode[0])
        
        asstup = ast.AssTuple(stores , lineno=inst.lineno)
        return ast.Assign([asstup], expr, lineno=inst.lineno)
            
    def visitIMPORT_NAME(self, inst):
        e = self.pop_expr()
        _ = self.pop_expr()
        
        
        print inst.argname
         
        if self.poll_inst().opname == 'STORE_FAST':
            self.pull_inst()
            
        return ast.Import([(inst.argname, e)], inst.lineno)
    
        
    
class Instruction(object):
    lineno = -1
    i = None
    opname = None
    arg_type = None
    op = None
    
    HAVE_ARGUMENT = False
    def __init__(self, code):
        self.code = code
        
    
    def __repr__(self):
        
        arg = self.argname
        
        return "%s(  %i , arg=%r, lineno=%i )" % (self.opname, self.i, arg, self.lineno)
    
    def _get_argname(self):
        
        if self.HAVE_ARGUMENT:
            if self.arg_type == 'jrel':
                arg = "to %r" % self.to 
            elif self.arg_type == 'cmp_op':
                arg = "cmp_op"
            elif self.arg_type == None:
                arg = ""
            else:
                arg = getattr(self.code, self.arg_type)[self.oparg]
        else:
            arg = None
            
        return arg
              
    argname = property(_get_argname)

def disassemble(co, lasti= -1):
    
    """Disassemble a code object."""
    
    instructions = []
    code = co.co_code
    labels = dis.findlabels(code)
    linestarts = dict(dis.findlinestarts(co))
    n = len(code)
    i = 0
    extended_arg = 0
    free = None
    lastline = -1
    while i < n:
        instc = Instruction(co)
        c = code[i]
        op = ord(c)
        
        if i in linestarts:
            lastline = linestarts[i]
            
        instc.lineno = lastline
        instc.i = i
        instc.op = op
        instc.opname = opname[op]
        
        i = i + 1
        if op >= HAVE_ARGUMENT:
            instc.HAVE_ARGUMENT = True
            
            oparg = ord(code[i]) + ord(code[i + 1]) * 256 + extended_arg
            
            instc.oparg = oparg
            extended_arg = 0
            
            i = i + 2
            if op == EXTENDED_ARG:
                extended_arg = oparg * 65536L

            if op in hasconst:
                instc.arg_type = 'co_consts'

            elif op in hasname:
                instc.arg_type = 'co_names'

            elif op in hasjrel:
                instc.arg_type = 'jrel'
                instc.to = i + oparg
                
            elif op in haslocal:
                instc.arg_type = 'co_varnames'
            elif op in hascompare:
                instc.arg_type = 'cmp_op'
            elif op in hasfree:
                
                if free is None:
                    free = co.co_cellvars + co.co_freevars
                    
                raise NotImplementedError("don't know what this is")
                instc.arg_type = 'free'
        else:
            
            instc.HAVE_ARGUMENT = False
            instc.oparg = None
            
        instructions.append(instc)
        
    return instructions


def printDis(co, instructs, file=sys.stdout):
    
    code = co.co_code
    labels = dis.findlabels(code)
    linestarts = dict(dis.findlinestarts(co))
    print "=" * 50
    for inst in instructs:
        
        if inst.i in linestarts:
            if inst.i > 0:
                print
            print "%3d" % inst.lineno,
        else:
            print '   ',
            
        print '   ',
        if inst.i in labels: print '>>',
        else: print '  ',

        print repr(inst.i).rjust(4),
        print inst.opname.ljust(20),
        
        if inst.HAVE_ARGUMENT:
            print repr(inst.oparg).rjust(5),
            print "(%s)" % str(inst.argname),
        
        print 

def ast_from_function(func):
    
    if not hasattr(func, 'func_code'):
        msg = "%r object of type %r does not have required attribute 'func_code'" % (func, type(func))
        raise ValueError(msg)
    
    instructs = disassemble(func.func_code)
    visitor = InstructionVisitor(func, instructs)
    astfunc = visitor.start()
    
    return astfunc

def code_from_ast(node):
    wp = WritePython()
    compiler.visitor.walk(node, visitor=wp, walker=wp)
    print wp.code

def expression_from_ast(astnodes, func):
    
    astexpr = compiler.ast.Expression(astnodes)
    astexpr.filename = 'expression_from_ast_dummy.py'
    astnodes.filename = 'expression_from_ast_dummy.py'
    c = compiler.pycodegen.ExpressionCodeGenerator(astexpr)
    code = c.getCode()
    
    fcode = func.func_code

    ncode = new.code(fcode.co_argcount, fcode.co_nlocals, fcode.co_stacksize, fcode.co_flags,
                     fcode.co_code, fcode.co_consts, fcode.co_names, fcode.co_varnames,
                     fcode.co_filename, fcode.co_name, fcode.co_firstlineno, fcode.co_lnotab,
                     code.co_freevars, fcode.co_cellvars)
    
    func = new.function(ncode, func.func_globals, name=func.func_name,
                        argdefs=func.func_defaults, closure=func.func_closure)
        
    return func

