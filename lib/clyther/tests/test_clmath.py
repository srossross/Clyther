'''
Created on Apr 1, 2010 by GeoSpin Inc
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


import unittest
import clyther
import random
import clyther.clmath as cmath
import math
from ctypes import c_float, c_int
from clyther.api.emulation import emulate



class Test(unittest.TestCase):


    def test_acos(self):
        "clmath: Checking OpenCL function 'acos' against Python emulation" 
        
        @clyther.task
        def _test_acos( a, output ):
            output[0] = cmath.acos( a )
    
        a = random.uniform(0,1)
        clout = clyther.DeviceBuffer( [1], c_float )
        _test_acos( a, clout)
        
        #emulation
        output = [0]
        _test_acos.func( a , output )
        
        self.failUnlessAlmostEqual( output[0], clout.item( ), 4 )

    def test_acosh(self):
        "clmath: Checking OpenCL function 'acosh' against Python emulation"
        
        @clyther.task
        def _test_acosh( a, output ):
            output[0] = cmath.acosh( a )
    
        a = 1000*random.uniform(0,1)
        
        clout = clyther.DeviceBuffer( [1], c_float )
        _test_acosh( a, clout)
        
        #emulation
        output = [0]
        _test_acosh.func( a , output )
        
        self.failUnlessAlmostEqual( output[0], clout.item( ) , 4)

    def test_asin(self):
        "clmath: Checking OpenCL function 'asin' against Python emulation"
        
        @clyther.task
        def _test_asin( a, output ):
            output[0] = cmath.asin( a )
    
        a = random.uniform(0,1)
        
        clout = clyther.DeviceBuffer( [1], c_float )
        _test_asin( a, clout)
        
        #emulation
        output = [0]
        _test_asin.func( a , output )
        
        self.failUnlessAlmostEqual( output[0], clout.item( ) , 4)

    def test_asinh(self):
        "clmath: Checking OpenCL function 'asinh' against Python emulation"
        
        @clyther.task
        def _test_asinh( a, output ):
            output[0] = cmath.asinh( a )
    
        a = 1000*random.uniform(0,1)
        
        clout = clyther.DeviceBuffer( [1], c_float )
        _test_asinh( a, clout)
        
        #emulation
        output = [0]
        _test_asinh.func( a , output )
        
        self.failUnlessAlmostEqual( output[0], clout.item( ) , 4)

    def test_atan(self):
        "clmath: Checking OpenCL function 'atan' against Python emulation"
        
        @clyther.task
        def _test_atan( a, output ):
            output[0] = cmath.tan( a )
    
        a = random.uniform(0,1)
        
        clout = clyther.DeviceBuffer( [1], c_float )
        _test_atan( a, clout)
        
        #emulation
        output = [0]
        _test_atan.func( a , output )
        
        self.failUnlessAlmostEqual( output[0], clout.item( ) , 4)

    def test_atan2(self):
        "clmath: Checking OpenCL function 'atan2' against Python emulation"
        
        @clyther.task
        def _test_atan2( a, b, output ):
            output[0] = cmath.atan2( a,b )
    
        a = random.uniform(0,1)
        b = random.uniform(0,1)
        
        clout = clyther.DeviceBuffer( [1], c_float )
        
        _test_atan2( a, b, clout )
        
        #emulation
        output = [0]
        _test_atan2.func( a,b , output )
        
        self.failUnlessAlmostEqual( output[0], clout.item( ) , 4)

    def test_cbrt(self):
        "clmath: Checking OpenCL function 'cbrt' against Python emulation"
        
        @clyther.task
        def _test_cbrt( a, output ):
            output[0] = cmath.cbrt( a )
    
        a = random.uniform(0,1)
        
        clout = clyther.DeviceBuffer( [1], c_float )
        _test_cbrt( a, clout)
        
        #emulation
        output = [0]
        _test_cbrt.func( a , output )
        
        self.failUnlessAlmostEqual( output[0], clout.item( ) , 4)

    def test_ceil(self):
        "clmath: Checking OpenCL function 'ceil' against Python emulation"
        
        @clyther.task
        def _test_ceil( a, output ):
            output[0] = cmath.ceil( a )
    
        a = 1000*random.uniform(0,1)
        
        clout = clyther.DeviceBuffer( [1], c_float )
        _test_ceil( a, clout)
        
        #emulation
        output = [0]
        _test_ceil.func( a , output )
        
        self.failUnlessAlmostEqual( output[0], clout.item( ) , 4)

    def test_copysign(self):
        "clmath: Checking OpenCL function 'copysign' against Python emulation"
        
        @clyther.task
        def _test_copysign( a,b, output ):
            output[0] = cmath.copysign( a, b )
    
        a = random.uniform(0,1)-0.5
        b = random.uniform(0,1)-0.5
        clout = clyther.DeviceBuffer( [1], c_float )
        
        _test_copysign( a,b, clout)
        
        #emulation
        output = [0]
        _test_copysign.func( a,b , output )
        
        self.failUnlessAlmostEqual( output[0], clout.item( ) , 4)


    def test_cos(self):
        "clmath: Checking OpenCL function 'cos' against Python emulation"
        
        @clyther.task
        def _test_cos( a, output ):
            output[0] = cmath.cos( a )
    
        a = random.uniform(0,1)
        clout = clyther.DeviceBuffer( [1], c_float )
        _test_cos( a, clout)
        
        #emulation
        output = [0]
        _test_cos.func( a , output )
        
        self.failUnlessAlmostEqual( output[0], clout.item( ), 4 )

    def test_cosh(self):
        "clmath: Checking OpenCL function 'cosh' against Python emulation"
        
        @clyther.task
        def _test_cosh( a, output ):
            output[0] = cmath.cosh( a )
    
        a = random.uniform(0,1)
        clout = clyther.DeviceBuffer( [1], c_float )
        _test_cosh( a, clout)
        
        #emulation
        output = [0]
        _test_cosh.func( a , output )
        
        self.failUnlessAlmostEqual( output[0], clout.item( ), 4 )

    def test_exp(self):
        "clmath: Checking OpenCL function 'exp' against Python emulation"
        
        @clyther.task
        def _test_exp( a, output ):
            output[0] = cmath.exp( a )
    
        a = random.uniform(0,1)
        clout = clyther.DeviceBuffer( [1], c_float )
        _test_exp( a, clout)
        #emulation
        output = [0]
        _test_exp.func( a , output )
        
        self.failUnlessAlmostEqual( output[0], clout.item( ), 3 )

    def test_exp10(self):
        "clmath: Checking OpenCL function 'exp10' against Python emulation"
        
        @clyther.task
        def _test_exp10( a, output ):
            output[0] = cmath.exp10( a )
    
        a = random.uniform(0,1)
        clout = clyther.DeviceBuffer( [1], c_float )
        _test_exp10( a, clout)
        #emulation
        output = [0]
        _test_exp10.func( a , output )
        
        self.failUnlessAlmostEqual( output[0], clout.item( ), 4 )

    def test_exp2(self):
        "clmath: Checking OpenCL function 'exp2' against Python emulation"
        
        @clyther.task
        def _test_exp2( a, output ):
            output[0] = cmath.exp2( a )
    
        a = random.uniform(0,1)
        clout = clyther.DeviceBuffer( [1], c_float )
        _test_exp2( a, clout)
        #emulation
        output = [0]
        _test_exp2.func( a , output )

    def test_expm1(self):
        "clmath: Checking OpenCL function 'expm1' against Python emulation"
        
        @clyther.task
        def _test_expm1( a, output ):
            output[0] = cmath.expm1( a )
    
        a = 2*(random.uniform(0,1)-0.5)
        clout = clyther.DeviceBuffer( [1], c_float )
        _test_expm1( a, clout)
        #emulation
        output = [0]
        _test_expm1.func( a , output )
        
        self.failUnlessAlmostEqual( output[0], clout.item( ), 4 )

    def test_fabs(self):
        
        "clmath: Checking OpenCL function 'fabs' against Python emulation"
        @clyther.task
        def _test_fabs( a, output ):
            output[0] = cmath.fabs( a )
    
        a = 2*(random.uniform(0,1)-0.5)
        clout = clyther.DeviceBuffer( [1], c_float )
        _test_fabs( a, clout)
        #emulation
        output = [0]
        _test_fabs.func( a , output )
        
        self.failUnlessAlmostEqual( output[0], clout.item( ), 4 )

    def test_abs(self):
        "clmath: Checking OpenCL function 'abs' against Python emulation"
        
        @clyther.task
        def _test_fabs( a, output ):
            output[0] = abs( a )
    
        a = 2*(random.uniform(0,1)-0.5)
        clout = clyther.DeviceBuffer( [1], c_float )
        _test_fabs( a, clout)
        #emulation
        output = [0]
        _test_fabs.func( a , output )
        
        self.failUnlessAlmostEqual( output[0], clout.item( ), 4 )

    def test_fdim(self):
        "clmath: Checking OpenCL function 'fdim' against Python emulation"
        
        @clyther.task
        def _test_fdim( a,b, output ):
            output[0] = cmath.fdim( a,b )
    
        a = 2*(random.uniform(0,1)-0.5)
        b = 2*(random.uniform(0,1)-0.5)
        clout = clyther.DeviceBuffer( [1], c_float )
        _test_fdim( a,b, clout)
        #emulation
        output = [0]
        _test_fdim.func( a,b , output )
        
        self.failUnlessAlmostEqual( output[0], clout.item( ), 4 )

    def test_floor(self):
        "clmath: Checking OpenCL function 'floor' against Python emulation"
        
        @clyther.task
        def _test_floor( a, output ):
            output[0] = cmath.floor( a )
    
        a = 20*(random.uniform(0,1)-0.5)
        clout = clyther.DeviceBuffer( [1], c_float )
        _test_floor( a, clout)
        #emulation
        output = [0]
        _test_floor.func( a , output )
        
        self.failUnlessAlmostEqual( output[0], clout.item( ), 4 )


    def test_fmin(self):
        "clmath: Checking OpenCL function 'fmin' against Python emulation"
        
        @clyther.task
        def _kernel_test( a,b, output ):
            output[0] = cmath.fmin( a, b )
    
        a = 20*(random.uniform(0,1)-0.5)
        b = 20*(random.uniform(0,1)-0.5)
        
        clout = clyther.DeviceBuffer( [1], c_float )
        _kernel_test( a,b, clout)
        #emulation
        output = [0]
        _kernel_test.func( a, b , output )
        
        self.failUnlessAlmostEqual( output[0], clout.item( ), 4 )

    def test_fmax(self):
        "clmath: Checking OpenCL function 'fmax' against Python emulation"
        
        @clyther.task
        def _kernel_test( a,b, output ):
            output[0] = cmath.fmax( a, b )
    
        a = 20*(random.uniform(0,1)-0.5)
        b = 20*(random.uniform(0,1)-0.5)
        
        clout = clyther.DeviceBuffer( [1], c_float )
        _kernel_test( a,b, clout)
        #emulation
        output = [0]
        _kernel_test.func( a, b , output )
        
        self.failUnlessAlmostEqual( output[0], clout.item( ), 4 )

    def test_fmod(self):
        "clmath: Checking OpenCL function 'fmod' against Python emulation"
        
        @clyther.task
        def _kernel_test( a,b, output ):
            output[0] = cmath.fmod( a, b )
    
        a = 20*(random.uniform(0,1)-0.5)
        b = 20*(random.uniform(0,1)-0.5)
        
        clout = clyther.DeviceBuffer( [1], c_float )
        _kernel_test( a,b, clout)
        #emulation
        output = [0]
        _kernel_test.func( a, b , output )
        
        self.failUnlessAlmostEqual( output[0], clout.item( ), 4 )

    def test_ilogb(self):
        "clmath: Checking OpenCL function 'ilogb' against Python emulation"
        @clyther.task
        def _kernel_test( a, output ):
            output[0] = cmath.ilogb( a )
    
        a = 1+random.uniform(0,1)
        
        clout = clyther.DeviceBuffer( [1], c_int )
        _kernel_test( a, clout)
        #emulation
        output = [0]
        _kernel_test.func( a , output )
        
        self.failUnlessAlmostEqual( output[0], clout.item( ), 4 )

    def test_log(self):
        "clmath: Checking OpenCL function 'log' against Python emulation"
        @clyther.task
        def _kernel_test( a, output ):
            output[0] = cmath.log( a )
    
        a = random.uniform(0,1)
        
        clout = clyther.DeviceBuffer( [1], c_float )
        _kernel_test( a, clout )
        #emulation
        output = [0]
        _kernel_test.func( a , output )
        
        self.failUnlessAlmostEqual( output[0], clout.item( ), 4 )

    def test_log10(self):
        "clmath: Checking OpenCL function 'log10' against Python emulation"
        @clyther.task
        def _kernel_test( a, output ):
            output[0] = cmath.log10( a )
    
        a = random.uniform(0,1)
        
        clout = clyther.DeviceBuffer( [1], c_float )
        _kernel_test( a, clout )
        #emulation
        output = [0]
        _kernel_test.func( a , output )
        
        self.failUnlessAlmostEqual( output[0], clout.item( ), 4 )

    def test_log1p(self):
        "clmath: Checking OpenCL function 'log1p' against Python emulation"
        @clyther.task
        def _kernel_test( a, output ):
            output[0] = cmath.log1p( a )
    
        a = random.uniform(0,1)
        
        clout = clyther.DeviceBuffer( [1], c_float )
        _kernel_test( a, clout )
        #emulation
        output = [0]
        
        emulate( _kernel_test, a , output)
        
        
        self.failUnlessAlmostEqual( output[0], clout.item( ), 4 )


    
    
if __name__ == "__main__":
    
    clyther.init('gpu')
    
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
    
    clyther.finish( )
#    test_acos( None )

