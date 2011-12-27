'''
Created on Dec 7, 2011

@author: sean
'''
from clyther.array.ufunc_framework import binary_ufunc, unary_ufunc
import clyther.runtime as clrt 
from clyther.array.array_context import CLArrayContext

@CLArrayContext.method('add')
@binary_ufunc
def add(a, b):
    return a + b

sum = CLArrayContext.method("sum")(add.reduce)


@CLArrayContext.method('subtract')
@binary_ufunc
def subtract(a, b):
    return a - b


@CLArrayContext.method('power')
@binary_ufunc
def power(a, b):
    return a ** b


@CLArrayContext.method('multiply')
@binary_ufunc
def multiply(a, b):
    return a * b

@CLArrayContext.method('sin')
@unary_ufunc
def cly_sin(x):
    return clrt.sin(x)

sin = cly_sin

