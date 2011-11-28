import unittest
import clyther
import random
from ctypes import c_float


class Test(unittest.TestCase):

    def test_add(self):
        @clyther.task
        def _test_add(a, b, output):
            output[0] = a + b
            
        a = random.uniform(0, 1)
        b = random.uniform(0, 1)

        clout = clyther.DeviceBuffer([1], c_float)
        _test_add(a, b, clout)
        
        output = [0]
        _test_add.func(a, b, output)
        
        self.failUnlessAlmostEqual(clout.item(), output[0], 4)

    def test_subtract(self):
        @clyther.task
        def _test_subtract(a, b, output):
            output[0] = a - b
            
        a = random.uniform(0, 1)
        b = random.uniform(0, 1)
        
        clout = clyther.DeviceBuffer([1], c_float)
        _test_subtract(a, b, clout)
        
        output = [0]
        _test_subtract.func(a, b, output)
        
        self.failUnlessAlmostEqual(clout.item(), output[0], 4)
        
    def test_mul(self):
        @clyther.task
        def _test_mul(a, b, output):
            output[0] = a * b
            
        a = random.uniform(0, 1)
        b = random.uniform(0, 1)
        
        clout = clyther.DeviceBuffer([1], c_float)
        _test_mul(a, b, clout)
        
        output = [0]
        _test_mul.func(a, b, output)
        
        self.failUnlessAlmostEqual(clout.item(), output[0], 4)
        
    def test_div(self):
        @clyther.task
        def _test_div(a, b, output):
            output[0] = a / b
            
        a = random.uniform(0, 1)
        b = random.uniform(0, 1)
        
        clout = clyther.DeviceBuffer([1], c_float)
        _test_div(a, b, clout)
        
        output = [0]
        _test_div.func(a, b, output)
        
        self.failUnlessAlmostEqual(clout.item(), output[0], 4)

    def test_unary_plus(self):
        @clyther.task
        def _test_unary_plus(a, output):
            output[0] = +(a)
            
        a = random.uniform(-1, 0)
        
        clout = clyther.DeviceBuffer([1], c_float)
        _test_unary_plus(a, clout)
        
        output = [0]
        _test_unary_plus.func(a, output)
        
        self.failUnlessAlmostEqual(clout.item(), output[0], 4)
        
    def test_unary_minus(self):
        @clyther.task
        def _test_unary_minus(a, output):
            output[0] = -(a)
            
        a = random.uniform(0, 1)
        
        clout = clyther.DeviceBuffer([1], c_float)
        _test_unary_minus(a, clout)
        
        output = [0]
        _test_unary_minus.func(a, output)
        
        self.failUnlessAlmostEqual(clout.item(), output[0], 4)

    def test_mod(self):
        @clyther.task
        def _test_mod(a, b, output):
            output[0] = a % b
            
        a = random.uniform(1, 100)
        b = random.uniform(1, 100)
        
        clout = clyther.DeviceBuffer([1], c_float)
        _test_mod(a, b, clout)
        
        output = [0]
        _test_mod.func(a, b, output)
        
        self.failUnlessAlmostEqual(clout.item(), output[0], 4)

if __name__ == "__main__":

    clyther.init( 'gpu' )
    unittest.main()
    clyther.finish( )
