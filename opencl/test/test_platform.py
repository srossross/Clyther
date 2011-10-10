'''
Created on Sep 27, 2011

@author: sean
'''

from opencl.copencl import Platform, get_platforms, Context, Device, Queue, Program, Buffer
from opencl.copencl import as_mem_view
import ctypes
import unittest
import numpy as np

def BufferCType(buffer):
    return buffer

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
        queue = Queue(ctx, ctx.devices[0])

        global foo
        
        foo = 0
        
        def incfoo(arg, op=lambda a, b: 0):
            global foo
            foo = op(foo, arg)
            
        queue.enqueue_native_kernel(incfoo, 4, op=lambda a, b: a + b)
        queue.enqueue_native_kernel(incfoo, 3, op=lambda a, b: a * b)
        
        queue.finish()
        
        self.assertEqual(foo, 12)

        
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
        
class TestBuffer(unittest.TestCase):
    
    def test_constructor(self):
        ctx = Context(device_type=Device.CPU)
        cl_buffer = Buffer(ctx, 12)
        
        self.assertEqual(12, cl_buffer.size)
        
    def test_read_buffer(self):
        
        array = np.arange(12)
        dest = np.zeros_like(array)
        
        ctx = Context(device_type=Device.CPU)
        
        cl_buffer = Buffer(ctx, host_buffer=array, copy=True)
        
        queue = Queue(ctx, ctx.devices[0])
        
        queue.enqueue_read_buffer(cl_buffer, dest).wait()
        
        self.assertTrue(np.all(array == dest))
        
    def test_map_buffer(self):
        ctx = Context(device_type=Device.CPU)
        
        array = np.arange(10, 22)
        cl_buffer = Buffer(ctx, host_buffer=array, copy=True)
        
        queue = Queue(ctx, ctx.devices[0])
        
        memview, _ = queue.enqueue_map_buffer(cl_buffer, blocking=True)
        
        result = np.frombuffer(memview, dtype=array.dtype)
        
        self.assertTrue(np.all(array == result))
        
        event = queue.enqueue_unmap(cl_buffer, memview)
        event.wait()
        
    def test_map_context(self):
        
        ctx = Context(device_type=Device.CPU)
        
        array = np.arange(10, 22)
        cl_buffer = Buffer(ctx, host_buffer=array, copy=True)
        
        queue = Queue(ctx, ctx.devices[0])
        
        with cl_buffer.map(queue) as buffer:
            
            result = np.frombuffer(buffer, dtype=array.dtype)
            
            self.assertTrue(np.all(array == result))
            
            result[2] = 45

        
        dest = np.zeros_like(array)
        queue.enqueue_read_buffer(cl_buffer, dest).wait()
        
        array[2] = 45
        
        self.assertTrue(np.all(array == dest))
        
    def test_getitem(self):
        ctx = Context(device_type=Device.CPU)
        
        array = "abcdefg"
        cl_buffer = Buffer(ctx, host_buffer=array, copy=True)
        
        buff = cl_buffer[1:-1]
        
        queue = Queue(ctx, ctx.devices[0])
        
        with buff.map(queue) as pybuffer:
            self.assertEqual(str(pybuffer), str(array[1:-1]))
            
    
class TestKernel(unittest.TestCase):
    
    def test_kernel_types_names(self):
        ctx = Context(device_type=Device.CPU)
        
        program = Program(ctx, source=source)
        
        program.build()
        
        generate_sin = program.kernel('generate_sin')
        
        generate_sin.argtypes = [BufferCType, ctypes.c_float]
        generate_sin.argnames = ['a', 'b']
        
        
        print generate_sin._format_args(1, b=2.3)

        
        
if __name__ == '__main__':
    unittest.main()
