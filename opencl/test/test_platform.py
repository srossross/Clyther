'''
Created on Sep 27, 2011

@author: sean
'''

from opencl.copencl import Platform, get_platforms, Context, Device, Queue, Program
import unittest

source = """

__kernel void generate_sin(__global float2* a, float scale)
{
    int id = get_global_id(0);
    int n = get_global_size(0);
    float r = (float)id / (float)n;
    float x = r * 16.0f * 3.1415f;
    
    a[id].x = r * 2.0f - 1.0f;
    a[id].y = native_sin(x) * scale;
}
"""

class Test(unittest.TestCase):
    
    
    def test_get_platforms(self):
        print get_platforms()

    def test_get_devices(self):
        plat = get_platforms()[0]
        print plat.devices()
        print [dev.native_kernel for dev in plat.devices()]

    def test_context(self):
        
        ctx = Context(device_type=Device.CPU)
        
        print ctx
        
    
    def test_create_queue(self):
        ctx = Context(device_type=Device.CPU)
        print ctx
        queue = Queue(ctx, ctx.devices[0])
        print queue
    
        def printfoo():
            print "foo"
            
        queue.enqueue_native_kernel(printfoo)
        
        queue.finish()

            
        
class TestProgram(unittest.TestCase):
        
    def test_program(self):
        ctx = Context(device_type=Device.CPU)
        
        program = Program(ctx, source=source)
        
        program.build()
        
    def test_devices(self):
        ctx = Context(device_type=Device.CPU)
        
        program = Program(ctx, source=source)
        
        program.build()
        
        print program.devices
    def test_kernel(self):
        ctx = Context(device_type=Device.CPU)
        
        program = Program(ctx, source=source)
        
        program.build()
        
        generate_sin = program.kernel('generate_sin')
        
        generate_sin.argtypes = [Buffer, ctypes.c_float]

        
        
        
if __name__ == '__main__':
    unittest.main()
