'''
Created on Jan 2, 2012

@author: sean
'''
import clyther as cly
import opencl as cl
from ctypes import Structure
from clyther.array import CLArrayContext

class Foo(Structure):
    _fields_ = [('i', cl.cl_float), ('j', cl.cl_float)]

    def bar(self):
        return self.i ** 2 + self.j ** 2
    
@cly.task
def objects(ret, foo):
    ret[0] = foo.bar()

def main():
    ca = CLArrayContext()  
    
    a = ca.empty([1], ctype='f')
    
    foo = Foo(10., 2.)
     
    objects(ca, a, foo)
    
    print "compiled result: ", a.item().value
    print "python result:   ", foo.bar()
    
    


if __name__ == '__main__':
    main()
