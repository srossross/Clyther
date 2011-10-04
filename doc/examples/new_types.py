'''
Created on Sep 25, 2011

@author: sean
'''


from ctypes import Structure, c_int, c_float
from clyther import kernel
import pyopencl as cl

class M(Structure):
    _fields_ = [('a', c_int),
                ('b', c_float),
                ]
    
    def foo(self):
        return self.a + self.b

def func(a): return a + 1

@kernel()
def kern(m, f2):
    
    c = func(m.a) + f2(m.b)
    

ctx = cl.Context()


built = kern.compile(ctx, m=M, f2=func)

m = M(a=1, b=2)

queue = cl.CommandQueue(ctx)
global_size = (1,)
local_size = (1,)
built(queue, global_size, local_size, m)
