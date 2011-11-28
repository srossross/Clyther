:mod:`clyther.clmath` --- OpenCL builtin math functions.
===================================================================================

.. module:: clyther.clmath
   :synopsis: OpenCL builtin math functions.
.. moduleauthor:: Sean Ross-Ross <srossross@geospin.ca>

.. versionadded:: 1.0.1.alpha

.. function:: acos(x)

    Arc cosine function.

.. function:: acosh(x)

    Inverse hyperbolic cosine.

.. function:: acospi(x)

    Compute acos (x) / pi

.. function:: asin(x)

    Arc sine function.

.. function:: asinh(x)

    Inverse hyperbolic sine.

.. function:: asinpi(x)

    Inverse hyperbolic sine.

.. function:: atan(x)

    Arc tangent function.

.. function:: atan2(x,y)
    
    atan2( y ,x ) -> a
    Arc tangent of y / x.
    
.. function:: atan2pi(x,y)



.. function:: atanh(x)

    Hyperbolic arc tangent.

.. function:: atanpi(x)

    Compute atan (x) / pi

.. function:: cbrt(x)

    Compute cube-root.

.. function:: ceil(x)

    Round to integral value using the round to +ve infinity rounding mode.

.. function:: copysign(x,y)

    Returns x with its sign changed to match the sign of y

.. function:: cos(x)

    Compute cosine.

.. function:: cosh(x)

    Compute hyperbolic consine.

.. function:: cospi(x)

    Compute hyperbolic consine.

.. function:: erf(x)

    Error function encountered in integrating the normal distribution.

.. function:: erfc(x)

    Complementary error function.

.. function:: exp(x)

    Compute the base- e exponential of x.

.. function:: exp10(x)

    Exponential base 2 function.

.. function:: exp2(x)

    Exponential base 2 function.

.. function:: expm1(x)

    Compute e^x - 1.0.

.. function:: fabs(x)

    Compute absolute value of a floating-point number

.. function:: fdim(x,y)

    x - y if x > y, +0 if x is less than or equal to y.

.. function:: floor(x)

    x - y if x > y, +0 if x is less than or equal to y.

.. function:: fma(x)    

    Returns the correctly rounded floating-point representation of the sum of c with the infinitely precise product of a and b. 
    Rounding of intermediate products shall not occur. Edge case behavior is per the IEEE 754-2008 standard.
    
.. function:: fmax(x,y)
    
    Returns the maximum of x and y.
    
.. function:: fmin(x,y)

    Returns the minimum of x and y.
    
.. function:: fmod(x,y)


.. function:: ilogb(x)

    Return the exponent as an integer value.

.. function:: ldexp()

    
.. function:: lgamma()


.. function:: log(x)

    Compute natural logarithm.

.. function:: log10(x)

    Compute a base 10 logarithm.

.. function:: log1p(x)

    Compute log(1.0 + x).

.. function:: log2(x)

    Compute a base 2 logarithm..

.. function:: logb(x)

    Compute the exponent of x, which is the integral part of logr | x |.

.. function:: mad(a,c,b)
    

.. function:: nextafter(x,y)
    

    Computes the next representable single-precision floating-point value following 
    x in the direction of y. 
    Thus, if y is less than x, nextafter() returns the largest representable 
    floating-point number less than x.
        
    
.. function:: pow(x,y)

    Compute x to the power y.

.. function:: pown(x,y)

    Compute x to the power y, where y is an integer.

.. function:: powr(x,y)

    Compute x to the power y, where x is >= 0.

.. function:: remainder(x,y)
    
    Compute the value r such that r = x - n*y, where n is the integer 
    nearest the exact value of x/y. If there are two integers closest 
    to x/y, n shall be the even one. If r is zero, it is given 
    the same sign as x.
    
.. function:: rint(x)
    
    Round to integral value (using round to nearest even rounding mode) 
    in floating-point format.
    
.. function:: rootn(x,y)
    
    Compute x to the power 1/y.
    
.. function:: round(x)
    
    round x.
    
.. function:: rsqrt(x,y)
    
    Compute x to the power 1/y.
    
.. function:: sin(x)
    
    Compute sine
    
.. function:: sinh(x)
    
    Compute hyperbolic sine
    
.. function:: sinpi(x)
    
    Compute sin(pi*x)
    
.. function:: sqrt(x)
    
    Square root
    
.. function:: tan(x)
    
    Compute tangent
    
.. function:: tanh(x)
    
    Compute hyperbolic tangent
    
.. function:: tanpi(x)
    
    Compute tan(pi*x) 
    
.. function:: tgamma(x)
    
    Compute the gamma function.
    
.. function:: trunc(x)
    
    Round to integral value using the round to zero rounding mode.
