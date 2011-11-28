import unittest
import clyther
import random
from ctypes import c_int32

def randint32(a=-(2**31), b=(2**31 - 1)):
    return random.randint(a, b)

class Test(unittest.TestCase):

    def test_left_shift(self):
        @clyther.task
        def _test_left_shift(a, b, output):
            output[0] = a << b
        
        clout = clyther.DeviceBuffer([1], c_int32)
        _test_left_shift(2, 2, clout)
        
        output = [0]
        _test_left_shift.func(2, 2, output)
        
        self.failUnlessEqual(clout.item(), output[0])
        
    def test_right_shift(self):
        @clyther.task
        def _test_right_shift(a, b, output):
            output[0] = a >> b
        
        clout = clyther.DeviceBuffer([1], c_int32)
        _test_right_shift(8, 2, clout)
        
        output = [0]
        _test_right_shift.func(8, 2, output)
        
        self.failUnlessEqual(clout.item(), output[0])
        
    def test_bit_xor(self):
        @clyther.task
        def _test_bit_xor(a, b, output):
            output[0] = a ^ b
            
        a = randint32()
        b = randint32()
        
        clout = clyther.DeviceBuffer([1], c_int32)
        _test_bit_xor(a, b, clout)
        
        output = [0]
        _test_bit_xor.func(a, b, output)
        
        self.failUnlessEqual(clout.item(), output[0])
        
    def test_bit_and(self):
        @clyther.task
        def _test_bit_and(a, b, output):
            output[0] = a & b
            
        a = randint32()
        b = randint32()
        
        clout = clyther.DeviceBuffer([1], c_int32)
        _test_bit_and(a, b, clout)
        
        output = [0]
        _test_bit_and.func(a, b, output)
        
        self.failUnlessEqual(clout.item(), output[0])
        
    def test_bit_or(self):
        @clyther.task
        def _test_bit_or(a, b, output):
            output[0] = a | b
            
        a = randint32()
        b = randint32()
        
        clout = clyther.DeviceBuffer([1], c_int32)
        _test_bit_or(a, b, clout)
        
        output = [0]
        _test_bit_or.func(a, b, output)
        
        self.failUnlessEqual(clout.item(), output[0])
        
    def test_add(self):
        @clyther.task
        def _test_add(a, b, output):
            output[0] = a + b
            
        # Keep them small to avoid overflow
        a = randint32(-1000000000, 1000000000)
        b = randint32(-1000000000, 1000000000)
        
        clout = clyther.DeviceBuffer([1], c_int32)
        _test_add(a, b, clout)
        
        output = [0]
        _test_add.func(a, b, output)
        
        self.failUnlessEqual(clout.item(), output[0])

    def test_subtract(self):
        @clyther.task
        def _test_subtract(a, b, output):
            output[0] = a - b
            
        # Keep them small to avoid overflow
        a = randint32(-1000000000, 1000000000)
        b = randint32(-1000000000, 1000000000)
        
        clout = clyther.DeviceBuffer([1], c_int32)
        _test_subtract(a, b, clout)
        
        output = [0]
        _test_subtract.func(a, b, output)
        
        self.failUnlessEqual(clout.item(), output[0])
        
    def test_mul(self):
        @clyther.task
        def _test_mul(a, b, output):
            output[0] = a * b
            
        # Keep them small to avoid overflow
        a = randint32(-32768, 32767)
        b = randint32(-32768, 32767)
        
        clout = clyther.DeviceBuffer([1], c_int32)
        _test_mul(a, b, clout)
        
        output = [0]
        _test_mul.func(a, b, output)
        
        self.failUnlessEqual(clout.item(), output[0])
        
    def test_div(self):
        @clyther.task
        def _test_div(a, b, output):
            output[0] = a / b
            
        a = randint32(1, 32767)
        b = randint32(1, 32767)
        
        clout = clyther.DeviceBuffer([1], c_int32)
        _test_div(a, b, clout)
        
        output = [0]
        _test_div.func(a, b, output)
        
        self.failUnlessEqual(clout.item(), output[0])

    def test_unary_plus(self):
        @clyther.task
        def _test_unary_plus(a, output):
            output[0] = +(a)
            
        a = randint32(-(2**31) + 1, -1)
        
        clout = clyther.DeviceBuffer([1], c_int32)
        _test_unary_plus(a, clout)
        
        output = [0]
        _test_unary_plus.func(a, output)
        
        self.failUnlessEqual(clout.item(), output[0])
        
    def test_unary_minus(self):
        @clyther.task
        def _test_unary_minus(a, output):
            output[0] = -(a)
            
        a = randint32(a=1)
        
        clout = clyther.DeviceBuffer([1], c_int32)
        _test_unary_minus(a, clout)
        
        output = [0]
        _test_unary_minus.func(a, output)
        
        self.failUnlessEqual(clout.item(), output[0])
        
    def test_mod(self):
        @clyther.task
        def _test_mod(a, b, output):
            output[0] = a % b
            
        a = randint32(a=1)
        b = randint32(a=1)
        
        clout = clyther.DeviceBuffer([1], c_int32)
        _test_mod(a, b, clout)
        
        output = [0]
        _test_mod.func(a, b, output)
        
        self.failUnlessEqual(clout.item(), output[0])


if __name__ == "__main__":

    clyther.init( 'gpu' )
    unittest.main()
    clyther.finish( )
