'''
Created on Aug 11, 2010

@author: sean
'''
import unittest
from clyther.disasembler import ast_from_function, expression_from_ast
import compiler
from inspect import getsource

def func2(a=1, b=getsource):
    return a, b

class Test(unittest.TestCase):

    def compare_deco_function(self, func, *args, **kwargs):
        
        astnodes = ast_from_function(func)
        
        new_func = expression_from_ast(astnodes, func)
        
        expected = func(*args, **kwargs)
        result = new_func(*args, **kwargs)
        self.assertEqual(result, expected)


    def test_lambdas(self):
        self.compare_deco_function(lambda : 1 or 2)
        self.compare_deco_function(lambda : True and False)
        self.compare_deco_function(lambda : True and False or True)
        self.compare_deco_function(lambda : 1.0 + 2.0 / 3.2 * 5.0)
        
    def test_if(self):
        
        def func(test1, test2):
            if test1:
                if test2:
                    return 1
                else:
                    return 2
            elif test2:
                return 3
            else:
                if test2:
                    return 4
                else:
                    return 5
                
        for test1 in [True, False]:
            for test2 in [True, False]:
                self.compare_deco_function(func, test1, test2)
                
    def test_if2(self):
        
        def func(test1, test2):
            if test1 and test2:
                return 1
            elif test1 and not test2:
                return 2
            else:
                return 3
                
            
                
        for test1 in [True, False]:
            for test2 in [True, False]:
                self.compare_deco_function(func, test1, test2)

    def test_assign(self):
        
        def func(test1, test2):
            tmp = test2 or test1
            tmp2 = test2 and test1
            
            return tmp, tmp2
                
        for test1 in [True, False]:
            for test2 in [True, False]:
                self.compare_deco_function(func, test1, test2)

    def test_math(self):
        
        def func():
            r = []
            r.append(float(1.0 + 2.03 / 3 // 4))
            r.append(10 % 3)
            
            return r
        
        self.compare_deco_function(func)

    def test_varargs(self):
        
        def func(*args):
            return args
        self.compare_deco_function(func)
        self.compare_deco_function(func, 1, 2, 3)

    
    def test_kwargs(self):
        
        def func(**kwargs):
            return dict(kwargs)
        
        self.compare_deco_function(func)
        self.compare_deco_function(func, a=1, b=2, c=3)
        
        self.compare_deco_function(func2)
        self.compare_deco_function(func2, a=2)
    
    def test_for(self):
        
        def func(x):
            result = 0
            for i in range(x):
                result += i
            
            return result
        
        self.compare_deco_function(func, 1)
        self.compare_deco_function(func, 10)

    def test_ctrl1(self):
        
        def func(x):
             
            while x:
                x-=1
                
        
        self.compare_deco_function(func, 2)
        self.compare_deco_function(func, 1)

    def test_ctrl2(self):
        
        def func(x,y):
             
            while x and y:
                x-=1
                y+=1
                
            return x,y
                        
        
        self.compare_deco_function(func, 2,1)
        self.compare_deco_function(func, 10,10)

    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
