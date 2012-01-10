'''
Created on Jan 9, 2012

@author: sean
'''
import clyther as cly
from clyther.array import CLArrayContext
import opencl as cl
import unittest
import math
import os
import numpy as np
import clyther.runtime as clrt

ca = None
def setUpModule():
    global ca
    
    
    DEVICE_TYPE_ATTR = os.environ.get('DEVICE_TYPE', 'DEFAULT')
    DEVICE_TYPE = getattr(cl.Device, DEVICE_TYPE_ATTR)
    
    ca = CLArrayContext(device_type=DEVICE_TYPE)
    
    print ca.devices


class TestBinaryOp(unittest.TestCase):

    def run_function(self, func, b, c):
        
        fmt = cl.type_formats.type_format(type(b))
        a = ca.empty([1], ctype=fmt)
        
        @cly.task
        def foo(a, b, c, function):
            a[0] = function(b, c)
            
        foo(ca, a, b, c, func)
        
        
        d = func(b, c)
        
        self.assertAlmostEqual(a[0].item().value, d)
     
    def test_add(self):
        
        self.run_function(lambda a, b: a + b, 1.0, 2.0)
         
    def test_sub(self):
        
        self.run_function(lambda a, b: a - b, 1.0, 2.0) 
        
    def test_mul(self):
        
        self.run_function(lambda a, b: a * b, 1.0, 2.0) 
        
    def test_pow(self):
        
        self.run_function(lambda a, b: a ** b, 2.0, 2.0) 
        
    def test_div(self):
        
        self.run_function(lambda a, b: a / b, 2.0, 5.0) 

class TestCompOp(unittest.TestCase):

    def run_function(self, func, b, c):
        
        a = ca.empty([1], ctype='B')
        
        @cly.task
        def foo(a, b, c, function):
            a[0] = function(b, c)
            
        foo(ca, a, b, c, func)
        
        
        d = func(b, c)
        
        self.assertAlmostEqual(a[0].item().value, d)

    def test_lt(self):
        
        self.run_function(lambda a, b: a < b, 2.0, 5.0) 
        self.run_function(lambda a, b: a < b, 5.0, 2.0) 

    def test_gt(self):

        self.run_function(lambda a, b: a > b, 2.0, 5.0) 
        self.run_function(lambda a, b: a > b, 5.0, 2.0) 

    def test_gtEq(self):

        self.run_function(lambda a, b: a >= b, 2.0, 5.0) 
        self.run_function(lambda a, b: a >= b, 5.0, 2.0) 
        self.run_function(lambda a, b: a >= b, 5.0, 5.0) 
        

    def test_ltEq(self):

        self.run_function(lambda a, b: a <= b, 2.0, 5.0) 
        self.run_function(lambda a, b: a <= b, 5.0, 2.0) 
        self.run_function(lambda a, b: a <= b, 5.0, 5.0) 
        
    def test_eq(self):

        self.run_function(lambda a, b: a == b, 2.0, 5.0) 
        self.run_function(lambda a, b: a == b, 5.0, 5.0) 

    def test_neq(self):

        self.run_function(lambda a, b: a != b, 2.0, 5.0) 
        self.run_function(lambda a, b: a != b, 5.0, 5.0) 
        

class TestStatements(unittest.TestCase):
    pass
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_add']
    unittest.main()

