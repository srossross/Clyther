'''
Created on Mar 29, 2010 by GeoSpin Inc
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


import math as pymath
from clyther.runtime import opencl_builtin_function


class acos( opencl_builtin_function ):
    "Arc cosine function."
    emulate = pymath.acos
     
    @classmethod
    def get_restype(cls,gentype):
        return gentype

class acosh( opencl_builtin_function ):
    "Inverse hyperbolic cosine."
    emulate = pymath.acosh
    @classmethod
    def get_restype(cls,gentype):
        return gentype

class acospi( opencl_builtin_function ):
    "Compute acos (x) / pi"
    emulate =staticmethod(  lambda x: pymath.acos(x) / pymath.pi)
    @classmethod
    def get_restype(cls,gentype):
        return gentype

class asin( opencl_builtin_function ):
    "Arc sine function."
    emulate = pymath.asin
    @classmethod
    def get_restype(cls,gentype):
        return gentype

class asinh( opencl_builtin_function ):
    "Inverse hyperbolic sine."
    emulate = pymath.asinh
    @classmethod
    def get_restype(cls,gentype):
        return gentype


class asinpi( opencl_builtin_function ):
    "Inverse hyperbolic sine."
    emulate = staticmethod( lambda x: pymath.asin(x) / pymath.pi)
    @classmethod
    def get_restype(cls,gentype):
        return gentype


class atan( opencl_builtin_function ):
    "Arc tangent function."
    emulate = pymath.atan
    @classmethod
    def get_restype(cls,gentype):
        return gentype

class atan2( opencl_builtin_function ):
    '''
    atan2( y ,x ) -> a
    Arc tangent of y / x.
    '''
    emulate = pymath.atan2
    @classmethod
    def get_restype(cls,gentype,gentype2):
        return gentype


class atanh( opencl_builtin_function ):
    "Hyperbolic arc tangent."
    emulate = pymath.atanh
    
    @classmethod
    def get_restype(cls,gentype):
        return gentype

class atanpi( opencl_builtin_function ):
    "Compute atan (x) / pi"
    emulate = staticmethod( lambda x: pymath.atan(x) / pymath.pi )
    
    @classmethod
    def get_restype(cls,gentype):
        return gentype


class atan2pi( opencl_builtin_function ):
    "Hyperbolic arc tangent."
    emulate = staticmethod( lambda x,y: pymath.atan(x,y) / pymath.pi)
    
    @classmethod
    def get_restype(cls,gentype,gentype2):
        return gentype

class cbrt( opencl_builtin_function ):
    "Compute cube-root."
    emulate = staticmethod( lambda  x: x**(1/3.))
    
    @classmethod
    def get_restype(cls,gentype):
        return gentype

class ceil( opencl_builtin_function ):
    "Round to integral value using the round to +ve infinity rounding mode."
    emulate = pymath.ceil
    
    @classmethod
    def get_restype(cls,gentype):
        return gentype

class copysign( opencl_builtin_function ):
    "Returns x with its sign changed to match the sign of y"
    emulate = pymath.copysign
    
    @classmethod
    def get_restype(cls,gentype,gentype2):
        return gentype

class cos( opencl_builtin_function ):
    "Compute cosine."
    emulate = pymath.cos
    
    @classmethod
    def get_restype(cls,gentype):
        return gentype

class cosh( opencl_builtin_function ):
    "Compute hyperbolic consine."
    emulate = pymath.cosh
    
    @classmethod
    def get_restype(cls,gentype):
        return gentype

class cospi( opencl_builtin_function ):
    "Compute hyperbolic consine."
    emulate = lambda x: pymath.cos(pymath.pi * x)
    
    @classmethod
    def get_restype(cls,gentype):
        return gentype


class erfc( opencl_builtin_function ):
    "Complementary error function."
    
    @classmethod
    def get_restype(cls,gentype):
        return gentype

class erf( opencl_builtin_function ):
    "Error function encountered in integrating the normal distribution."
    
    @classmethod
    def get_restype(cls,gentype):
        return gentype


class exp( opencl_builtin_function ):
    "Compute the base- e exponential of x."
    
    emulate = pymath.exp
    
    @classmethod
    def get_restype(cls,gentype):
        return gentype
    
class exp2( opencl_builtin_function ):
    "Exponential base 2 function."
    emulate = staticmethod( lambda x: 2**x )
    @classmethod
    def get_restype(cls,gentype):
        return gentype

class exp10( opencl_builtin_function ):
    "Exponential base 2 function."
    emulate = staticmethod( lambda x: 10**x)
    @classmethod
    def get_restype(cls,gentype):
        return gentype

class expm1( opencl_builtin_function ):
    "Compute e^x - 1.0."
    emulate = staticmethod( lambda x: pymath.exp(x) - 1.0)
    @classmethod
    def get_restype(cls,gentype):
        return gentype

class fabs( opencl_builtin_function ):
    "Compute absolute value of a floating-point number"
    emulate = pymath.fabs
    @classmethod
    def get_restype(cls,gentype):
        return gentype

class fdim( opencl_builtin_function ):
    "x - y if x > y, +0 if x is less than or equal to y."
    emulate = staticmethod( lambda x,y: x - y if x > y else 0)
    @classmethod
    def get_restype(cls,gentype,gentype2):
        return gentype
    

class floor( opencl_builtin_function ):
    "x - y if x > y, +0 if x is less than or equal to y."
    emulate = pymath.floor
    @classmethod
    def get_restype(cls,gentype):
        return gentype

class fma( opencl_builtin_function ):
    """
    Returns the correctly rounded floating-point representation of the sum of c with the infinitely precise product of a and b. 
    Rounding of intermediate products shall not occur. Edge case behavior is per the IEEE 754-2008 standard.
    """
    emulate = staticmethod( lambda a,b,c: (a*b)+c) 
    
    @classmethod
    def get_restype(cls,gentype,gentype2,gentype3):
        return gentype

class fmax( opencl_builtin_function ):
    """
    Returns the correctly rounded floating-point representation of the sum of c with the infinitely precise product of a and b. 
    Rounding of intermediate products shall not occur. Edge case behavior is per the IEEE 754-2008 standard.
    """
    emulate = max 
    
    @classmethod
    def get_restype(cls,gentype,gentype2):
        return gentype

class fmin( opencl_builtin_function ):
    """
    Returns the correctly rounded floating-point representation of the sum of c with the infinitely precise product of a and b. 
    Rounding of intermediate products shall not occur. Edge case behavior is per the IEEE 754-2008 standard.
    """
    emulate = min 
    
    @classmethod
    def get_restype(cls,gentype,gentype2):
        return gentype
    

class fmod( opencl_builtin_function ):
    
    emulate = pymath.fmod
    
    @classmethod
    def get_restype(cls,gentype1,gentype2):
        return gentype1

class ilogb( opencl_builtin_function ):
    'Return the exponent as an integer value.'
    emulate = staticmethod( lambda x: int(pymath.log(x)))
    
    @classmethod
    def get_restype(cls,gentype):
        return int

class ldexp( opencl_builtin_function ):
    'Return the exponent as an integer value.'
    emulate = staticmethod( lambda x,n: x* (2**n))
    
    @classmethod
    def get_restype(cls,gentype,gentype2):
        return gentype


class lgamma( opencl_builtin_function ):
    'Return the exponent as an integer value.'
    
    @classmethod
    def get_restype(cls,gentype):
        return gentype

class log( opencl_builtin_function ):
    'Compute natural logarithm.'
    
    emulate = pymath.log

    @classmethod
    def get_restype(cls,gentype):
        return gentype

class log2( opencl_builtin_function ):
    'Compute a base 2 logarithm..'
    
    @classmethod
    def get_restype(cls,gentype):
        return gentype

class log10( opencl_builtin_function ):
    'Compute a base 10 logarithm.'
    emulate = pymath.log10

    @classmethod
    def get_restype(cls,gentype):
        return gentype


class log1p( opencl_builtin_function ):
    'Compute log(1.0 + x).'
    emulate = pymath.log1p

    @classmethod
    def get_restype(cls,gentype):
        return gentype

class logb( opencl_builtin_function ):
    'Compute the exponent of x, which is the integral part of logr | x |.'

    @classmethod
    def get_restype(cls,gentype):
        return gentype

class mad( opencl_builtin_function ):
    'Compute the exponent of x, which is the integral part of logr | x |.'
    emulate = staticmethod( lambda a,b,c: a * b + c )
    @classmethod
    def get_restype(cls,gentype,gentype2,gentype3):
        return gentype



class nextafter( opencl_builtin_function ):
    '''
    Computes the next representable single-precision floating-point value following 
    x in the direction of y. 
    Thus, if y is less than x, nextafter() returns the largest representable 
    floating-point number less than x.
    '''
    @classmethod
    def get_restype(cls,gentype,gentype2):
        return gentype



class pow( opencl_builtin_function ):
    'Compute x to the power y.'
    emulate = pymath.pow
    
    @classmethod
    def get_restype(cls,gentype1,gentype2):
        return gentype1



class pown( opencl_builtin_function ):
    'Compute x to the power y, where y is an integer.'
    emulate = pymath.pow
    
    @classmethod
    def get_restype(cls,gentype1,gentype2):
        return gentype1

class powr( opencl_builtin_function ):
    'Compute x to the power y, where x is >= 0.'
    emulate = pymath.pow
    
    @classmethod
    def get_restype(cls,gentype1,gentype2):
        return gentype1

class remainder( opencl_builtin_function ):
    '''
    Compute the value r such that r = x - n*y, where n is the integer 
    nearest the exact value of x/y. If there are two integers closest 
    to x/y, n shall be the even one. If r is zero, it is given 
    the same sign as x.
    '''
    emulate = staticmethod( lambda x,y: x - round( x/float(y) )*y)
    
    @classmethod
    def get_restype(cls,gentype1,gentype2):
        return gentype1

class rint( opencl_builtin_function ):
    '''
    Round to integral value (using round to nearest even rounding mode) 
    in floating-point format.
    '''
    emulate = round
    
    @classmethod
    def get_restype(cls,gentype):
        return gentype
    
class rootn( opencl_builtin_function ):
    '''
    Compute x to the power 1/y.
    '''
    emulate = staticmethod( lambda x,y: x**(1./y) )
    
    @classmethod
    def get_restype(cls,gentype):
        return gentype
    
class round( opencl_builtin_function ):
    '''
    Compute x to the power 1/y.
    '''
    emulate = round
    
    @classmethod
    def get_restype(cls,gentype):
        return gentype
    

class rsqrt( opencl_builtin_function ):
    '''
    Compute x to the power 1/y.
    '''
    emulate = pymath.sqrt
    
    @classmethod
    def get_restype(cls,gentype):
        return gentype
    

class sin( opencl_builtin_function ):
    '''
    Compute sine
    '''
    emulate = pymath.sin
    
    @classmethod
    def get_restype(cls,gentype):
        return gentype
    

class sinh( opencl_builtin_function ):
    '''
    Compute hyperbolic sine
    '''
    emulate = pymath.sinh
    
    @classmethod
    def get_restype(cls,gentype):
        return gentype
    
class sinpi( opencl_builtin_function ):
    '''
    Compute sin(pi*x)
    '''
    emulate = staticmethod( lambda x: pymath.sin(pymath.pi*x) )
    
    @classmethod
    def get_restype(cls,gentype):
        return gentype
    
class sqrt( opencl_builtin_function ):
    '''
    Square root
    '''
    emulate = pymath.sqrt
    
    @classmethod
    def get_restype(cls,gentype):
        return gentype
    
    
    
    
class tan( opencl_builtin_function ):
    '''
    Compute tangent
    '''
    emulate = pymath.tan
    
    @classmethod
    def get_restype(cls,gentype):
        return gentype
    
    
    
class tanh( opencl_builtin_function ):
    '''
    Compute hyperbolic tangent
    '''
    emulate = pymath.tanh
    
    @classmethod
    def get_restype(cls,gentype):
        return gentype
    
class tanpi( opencl_builtin_function ):
    '''
    Compute tan(pi*x) 
    '''
    emulate = staticmethod( lambda x: pymath.tan(pymath.pi*x) )
    
    @classmethod
    def get_restype(cls,gentype):
        return gentype

class tgamma( opencl_builtin_function ):
    '''
    Compute the gamma function.
    '''
    
    @classmethod
    def get_restype(cls,gentype):
        return gentype
    
    
class trunc( opencl_builtin_function ):
    '''
    Round to integral value using the round to zero rounding mode.
    '''
    
    @classmethod
    def get_restype(cls,gentype):
        return gentype
    
    
    