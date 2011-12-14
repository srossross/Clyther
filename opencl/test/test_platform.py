'''
Created on Sep 27, 2011

@author: sean
'''

from opencl import Platform, get_platforms, Context, Device, Queue, Program, DeviceMemoryView, empty
from opencl import ContextProperties, global_memory, UserEvent, Event
from opencl.kernel import parse_args
import opencl as cl

import unittest
import ctypes
from ctypes import c_int, c_float, sizeof
import numpy as np
import gc
import time
from threading import Event as PyEvent
import sys

source = """

__kernel void generate_sin(__global float2* a, float scale)
{
    int id = get_global_id(0);
    int n = get_global_size(0);
    float r = (float)id / (float)n;
    
    a[id].x = id;
    a[id].y = native_sin(r) * scale;
}
"""

class Test(unittest.TestCase):
    
    
    def test_get_platforms(self):
        platforms = get_platforms()

    def test_get_devices(self):
        plat = get_platforms()[0]
        devices = plat.devices()
        native_kernels = [dev.has_native_kernel for dev in devices]

    def test_enqueue_native_kernel_refcount(self):
        if not ctx.devices[0].has_native_kernel:
            self.skipTest("Device does not support native kernels")
            
        queue = Queue(ctx, ctx.devices[0])

        def incfoo():
            pass
        
        self.assertEqual(sys.getrefcount(incfoo), 2)
            
        e = cl.UserEvent(ctx)
        queue.enqueue_wait_for_events(e)
        queue.enqueue_native_kernel(incfoo)
        
        self.assertEqual(sys.getrefcount(incfoo), 3)
        
        e.complete()
        
        queue.finish()
        
        self.assertEqual(sys.getrefcount(incfoo), 2)
        
    def test_enqueue_native_kernel(self):
        
        if not ctx.devices[0].has_native_kernel:
            self.skipTest("Device does not support native kernels")
            
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
        
#        
#    def test_native_kernel_maps_args(self):
#        
#        if not ctx.devices[0].has_native_kernel:
#            self.skipTest("Device does not support native kernels")
#            
#        queue = Queue(ctx, ctx.devices[0])
#        a = cl.empty(ctx, [10], 'f')
#        
#
#        global foo
#        
#        foo = 0
#        
#        def incfoo(arg):
#            global foo
#            
#            print 'arg', arg
#        
#        print "queue.enqueue_native_kernel"
#        queue.enqueue_native_kernel(incfoo, a)
#        
#        print "queue.finish"
#        queue.finish()
#        
#        print "self.assertEqual"
#        self.assertEqual(foo, 12)

class TestDevice(unittest.TestCase):
    
    def _test_device_properties(self):
        
        device = ctx.devices[0]
        print 
        print "device_type", device.device_type
        print "name", device.name
        print "has_image_support", device.has_image_support
        print "has_native_kernel", device.has_native_kernel
        print "max_compute_units", device.max_compute_units
        print "max_work_item_dimension", device.max_work_item_dimensions
        print "max_work_item_sizes", device.max_work_item_sizes
        print "max_work_group_size", device.max_work_group_size
        print "max_clock_frequency", device.max_clock_frequency, 'MHz'
        print "address_bits", device.address_bits, 'bits'
        print "max_read_image_args", device.max_read_image_args
        print "max_write_image_args", device.max_write_image_args
        print "max_image2d_shape", device.max_image2d_shape
        print "max_image3d_shape", device.max_image3d_shape
        print "max_parameter_size", device.max_parameter_size, 'bytes'
        print "max_const_buffer_size", device.max_const_buffer_size, 'bytes'
        print "has_local_mem", device.has_local_mem
        print "local_mem_size", device.local_mem_size, 'bytes'
        print "host_unified_memory", device.host_unified_memory
        print "available", device.available
        print "compiler_available", device.compiler_available
        print "driver_version", device.driver_version
        print "device_profile", device.profile
        print "version", device.version
        print "extensions", device.extensions
        print 


class TestContext(unittest.TestCase):
    def test_properties(self):
        platform = get_platforms()[0]
        
        properties = ContextProperties()
        
        properties.platform = platform
                
        self.assertEqual(platform.name, properties.platform.name)
        
        ctx = Context(device_type=DEVICE_TYPE, properties=properties)

class TestProgram(unittest.TestCase):
        
    def test_program(self):
        
        program = Program(ctx, source=source)
        
        program.build()

    def test_source(self):
        
        program = Program(ctx, source=source)
        
        self.assertEqual(program.source, source)

    def test_binaries(self):
        
        program = Program(ctx, source=source)
        
        self.assertEqual(program.binaries, dict.fromkeys(ctx.devices))
        
        program.build()
        
        binaries = program.binaries
        self.assertIsNotNone(binaries[ctx.devices[0]])
        self.assertEqual(len(binaries[ctx.devices[0]]), program.binary_sizes[0])
        
        program2 = Program(ctx, binaries=binaries)
        
        self.assertIsNone(program2.source)
        
        self.assertEqual(program2.binaries, binaries)
        
    def test_constructor(self):
        
        with self.assertRaises(TypeError):
            Program(None, binaries=None)

        with self.assertRaises(TypeError):
            Program(ctx, binaries={None:None})
        
    def test_devices(self):
        
        program = Program(ctx, source=source)
        
        program.build()
        
class TestKernel(unittest.TestCase):
    
    def test_name(self):
        program = Program(ctx, source=source)
        
        program.build()
        
        generate_sin = program.kernel('generate_sin')
        
        self.assertEqual(generate_sin.name, 'generate_sin')
        
    def test_argtypes(self):

        program = Program(ctx, source=source)
        
        program.build()
        
        generate_sin = program.kernel('generate_sin')
        
        generate_sin.argtypes = [DeviceMemoryView, ctypes.c_float]
        
        with self.assertRaises(TypeError):
            generate_sin.argtypes = [DeviceMemoryView, ctypes.c_float, ctypes.c_float]

    def test_set_args(self):

        program = Program(ctx, source=source)
        
        program.build()
        
        generate_sin = program.kernel('generate_sin')
        
        generate_sin.argtypes = [global_memory(), ctypes.c_float]
        
        buf = empty(ctx, [10], ctype='ff')
        
        queue = Queue(ctx, ctx.devices[0])
        
        generate_sin.set_args(buf, 1.0)
        queue.enqueue_nd_range_kernel(generate_sin, 1, global_work_size=[buf.size])
        
        expected = np.zeros([10], dtype=[('x', np.float32), ('y', np.float32)])
        expected['x'] = np.arange(10)
        expected['y'] = np.sin(expected['x'] / 10)
        
        with buf.map(queue) as host:
            self.assertTrue(np.all(expected['x'] == np.asarray(host)['f0']))
            self.assertTrue(np.allclose(expected['y'], np.asarray(host)['f1']))

        generate_sin.argnames = ['a', 'scale']
        generate_sin.set_args(a=buf, scale=1.0)
        queue.enqueue_nd_range_kernel(generate_sin, 1, global_work_size=[buf.size])
        
        with buf.map(queue) as host:
            self.assertTrue(np.all(expected['x'] == np.asarray(host)['f0']))
            self.assertTrue(np.allclose(expected['y'], np.asarray(host)['f1']))
            
        with self.assertRaises(TypeError):
            generate_sin.set_args(a=buf)
            
        generate_sin.__defaults__ = [1.0]
        generate_sin.set_args(a=buf)
        
        queue.enqueue_nd_range_kernel(generate_sin, 1, global_work_size=[buf.size])
        
        with buf.map(queue) as host:
            self.assertTrue(np.all(expected['x'] == np.asarray(host)['f0']))
            self.assertTrue(np.allclose(expected['y'], np.asarray(host)['f1']))

    def test_call(self):

        expected = np.zeros([10], dtype=[('x', np.float32), ('y', np.float32)])
        expected['x'] = np.arange(10)
        expected['y'] = np.sin(expected['x'] / 10)
        
        program = Program(ctx, source=source)
        
        program.build()
        
        generate_sin = program.kernel('generate_sin')
        
        generate_sin.argtypes = [global_memory(), ctypes.c_float]
        
        buf = empty(ctx, [10], ctype='ff')
        
        queue = Queue(ctx, ctx.devices[0])
        
        size = [buf.size]
        with self.assertRaises(TypeError):
            generate_sin(queue, buf, 1.0)
        
        generate_sin(queue, buf, 1.0, global_work_size=size)
        
        with buf.map(queue) as host:
            self.assertTrue(np.all(expected['x'] == np.asarray(host)['f0']))
            self.assertTrue(np.allclose(expected['y'], np.asarray(host)['f1']))

        generate_sin.global_work_size = lambda a, scale: [a.size]
        
        generate_sin(queue, buf, 1.0)
        
        with buf.map(queue) as host:
            self.assertTrue(np.all(expected['x'] == np.asarray(host)['f0']))
            self.assertTrue(np.allclose(expected['y'], np.asarray(host)['f1']))

    def test_parse_args(self):
        
        arglist = parse_args('test', (1, 2, 3), dict(d=4, e=5), ('a', 'b', 'c', 'd', 'e'), ())
        self.assertEqual(arglist, (1, 2, 3, 4, 5))

        arglist = parse_args('test', (1, 2, 3), dict(), ('a', 'b', 'c', 'd', 'e'), (4, 5))
        self.assertEqual(arglist, (1, 2, 3, 4, 5))

        arglist = parse_args('test', (1, 2), dict(c=3), ('a', 'b', 'c', 'd', 'e'), (4, 5))
        self.assertEqual(arglist, (1, 2, 3, 4, 5))

        arglist = parse_args('test', (1, 2), dict(c=3, d=5), ('a', 'b', 'c', 'd', 'e'), (4, 5))
        self.assertEqual(arglist, (1, 2, 3, 5, 5))

        arglist = parse_args('test', (1, 2), dict(c=6, d=6), ('a', 'b', 'c', 'd', 'e'), (4, 5))
        self.assertEqual(arglist, (1, 2, 6, 6, 5))

        arglist = parse_args('test', (), dict(), ('a', 'b', 'c', 'd', 'e'), (1, 2, 3, 4, 5))
        self.assertEqual(arglist, (1, 2, 3, 4, 5))

        
        arglist = parse_args('test', (1, 2, 3, 4, 5), dict(), ('a', 'b', 'c', 'd', 'e'), ())
        self.assertEqual(arglist, (1, 2, 3, 4, 5))
        
        arglist = parse_args('test', (), dict(a=1, b=2, c=3, d=4, e=5), ('a', 'b', 'c', 'd', 'e'), ())
        self.assertEqual(arglist, (1, 2, 3, 4, 5))
        
        with self.assertRaises(TypeError):
            arglist = parse_args('test', (), dict(), ('a', 'b'), ())

        with self.assertRaises(TypeError):
            arglist = parse_args('test', (1), dict(a=1), ('a', 'b'), ())

        with self.assertRaises(TypeError):
            arglist = parse_args('test', (), dict(b=1), ('a', 'b'), (2))
            
        with self.assertRaises(TypeError):
            arglist = parse_args('test', (1, 2, 3), dict(), ('a', 'b'), ())
        
class TestBuffer(unittest.TestCase):
    
    def test_size(self):     
        buf = empty(ctx, [4])
        
        self.assertEqual(buf._refcount, 1)
        
        self.assertEqual(len(buf), 4 / buf.itemsize)
        self.assertEqual(buf.mem_size, 4)
        
        layout = buf.array_info
        
        self.assertEqual(layout[:4], [4, 0, 0, 4]) #shape
        self.assertEqual(layout[4:], [1, 0, 0, 0]) #strides
        
    def test_local_memory(self):
        a = np.array([[1, 2], [3, 4]])
        view_a = memoryview(a)
        clmem = DeviceMemoryView.from_host(ctx, a)
        
        self.assertEqual(clmem.format, view_a.format)
        self.assertEqual(clmem.shape, view_a.shape)
        self.assertEqual(clmem.strides, view_a.strides)
        
    def test_from_host(self):
        a = np.array([[1, 2], [3, 4]])
        view_a = memoryview(a)
        clmem = DeviceMemoryView.from_host(ctx, a)
        
        self.assertEqual(clmem.format, view_a.format)
        self.assertEqual(clmem.shape, view_a.shape)
        self.assertEqual(clmem.strides, view_a.strides)
        
    def test_read_write(self):
        a = np.array([[1, 2], [3, 4]])
        clbuf = DeviceMemoryView.from_host(ctx, a)
        
        queue = Queue(ctx, ctx.devices[0])
        
        out = np.zeros_like(a)
        
        clbuf.read(queue, out, blocking=True)
        
        self.assertTrue(np.all(out == a))
        
        clbuf.write(queue, a + 1, blocking=True)

        clbuf.read(queue, out, blocking=True)
        
        self.assertTrue(np.all(out == a + 1))
        
    def test_map(self):
        
        a = np.array([[1, 2], [3, 4]])
        view_a = memoryview(a)
        
        clbuf = DeviceMemoryView.from_host(ctx, a)
    
        queue = Queue(ctx, ctx.devices[0])
        
        self.assertEqual(clbuf._mapcount, 0)
        
        with clbuf.map(queue, writeable=False) as buf:
            self.assertEqual(clbuf._mapcount, 1)
        
            self.assertEqual(buf.format, view_a.format)
            self.assertEqual(buf.shape, view_a.shape)
            self.assertEqual(buf.strides, view_a.strides)
            
            b = np.asarray(buf)
            self.assertTrue(np.all(b == a))
        
            self.assertTrue(buf.readonly)
        
#        self.assertEqual(clbuf._mapcount, 0)
        
        with clbuf.map(queue, readable=False) as buf:
            self.assertEqual(clbuf._mapcount, 1)
            b = np.asarray(buf)
            b[::] = a[::-1]
            
            self.assertFalse(buf.readonly)
            
#        self.assertEqual(clbuf._mapcount, 0)
        
        with clbuf.map(queue, writeable=False) as buf:
            self.assertEqual(clbuf._mapcount, 1)
            b = np.asarray(buf)
            self.assertTrue(np.all(b == a[::-1]))
            
    def test_refcount(self):

        a = np.array([[1, 2], [3, 4]])
        
        clbuf = DeviceMemoryView.from_host(ctx, a)

        self.assertEqual(clbuf._refcount, 1)
        
        new_buf = clbuf[:, :-1]
        
        self.assertEqual(clbuf._refcount, 2)
        
        del new_buf
        gc.collect()
        
        self.assertEqual(clbuf._refcount, 1)
        
        self.assertEqual(clbuf.base, None)
        
        #create sub_buffer
        new_buf = clbuf[1, :]

        self.assertEqual(clbuf._refcount, 2)
        
        event = PyEvent()
        def callback():
            event.set()
            
        new_buf.add_destructor_callback(callback)
        
        del new_buf
        gc.collect()
        
        timed_out = not event.wait(2)
        
        self.assertFalse(timed_out)
        
        
        self.assertEqual(clbuf._refcount, 1)
        
        queue = Queue(ctx)
        with clbuf.map(queue) as host:
            self.assertEqual(clbuf._refcount, 1)
            
        self.assertEqual(clbuf._refcount, 2, "unmap increments the refcount")
        
        del host
        gc.collect()
        
        #GPU does not decrement the ref count
        #self.assertEqual(clbuf._refcount, 2, "")
            
    def test_get_slice(self):
        
        queue = Queue(ctx, ctx.devices[0])   
        a = np.array([1, 2, 3, 4])
        
        clbuf = DeviceMemoryView.from_host(ctx, a)

        self.assertEqual(clbuf._refcount, 1)
        
        new_buf = clbuf[::2]
        
        with new_buf.map(queue) as buf:
            b = np.asanyarray(buf)
            self.assertTrue(np.all(b == a[::2]))
            
        new_buf = clbuf[1::2]
        
        with new_buf.map(queue) as buf:
            b = np.asanyarray(buf)
            self.assertTrue(np.all(b == a[1::2]))

        new_buf = clbuf[::-1]
        
        with new_buf.map(queue) as buf:
            b = np.asanyarray(buf)
            self.assertTrue(np.all(b == a[::-1]))
            
        
    def test_dim_reduce(self):
        queue = Queue(ctx, ctx.devices[0])   
        a = np.array([[1, 2], [3, 4], [5, 6]])
    
        view = DeviceMemoryView.from_host(ctx, a)
        
        new_view = view[:, 0]
        
        self.assertEqual(new_view.ndim, 1)
        self.assertEqual(new_view.shape, (3,))
        self.assertEqual(new_view.base_offset, 0)
        self.assertEqual(new_view.strides, (8,))

        with new_view.map(queue) as buf:
            b = np.asarray(buf)
            self.assertTrue(np.all(b == a[:, 0]))

        new_view = view[:, 1]
        
        with new_view.map(queue) as buf:
            b = np.asarray(buf)
            self.assertTrue(np.all(b == a[:, 1]))

        new_view = view[0, :]
        
        with new_view.map(queue) as buf:
            b = np.asarray(buf)
            self.assertTrue(np.all(b == a[0, :]))

        new_view = view[1, :]
        
        with new_view.map(queue) as buf:
            b = np.asarray(buf)
            self.assertTrue(np.all(b == a[1, :]))

    def test_getitem(self):

        queue = Queue(ctx, ctx.devices[0])   
        a = np.array([[1, 2], [3, 4]])
        
        clbuf = DeviceMemoryView.from_host(ctx, a)

        with self.assertRaises(IndexError):
            clbuf[1, 1, 1]
        
        self.assertEqual(clbuf._refcount, 1)
        
        new_buf = clbuf[:, :-1]
        
        self.assertEqual(clbuf._refcount, 2)
        
        mapp = new_buf.map(queue)
        
        with mapp as buf:
            
            b = np.asanyarray(buf)
            self.assertTrue(np.all(b == a[:, :-1]))
        
        del buf
        del new_buf
        gc.collect()
        
        new_buf = clbuf[:, 1:]
        
        with new_buf.map(queue) as buf:
            b = np.asanyarray(buf)
            self.assertTrue(np.all(b == a[:, 1:]))

        new_buf = clbuf[1:, :]
        
        with new_buf.map(queue) as buf:
            b = np.asanyarray(buf)
            self.assertTrue(np.all(b == a[1:, :]))
        
    def test_is_contiguous(self):
        
        a = np.array([[1, 2], [3, 4]])
        
        clbuf = DeviceMemoryView.from_host(ctx, a)
        
        self.assertTrue(clbuf.is_contiguous)
        
        self.assertFalse(clbuf[:, 1:].is_contiguous)
        self.assertFalse(clbuf[::2, :].is_contiguous)
        self.assertFalse(clbuf[:, ::2].is_contiguous)
        
    def test_copy_contig(self):

        queue = Queue(ctx, ctx.devices[0])   
        a = np.array([[1, 2], [3, 4]])
        
        clbuf = DeviceMemoryView.from_host(ctx, a)
        
        copy_of = clbuf.copy(queue)
        queue.barrier()
        with copy_of.map(queue) as cpy:
            b = np.asarray(cpy)
            self.assertTrue(np.all(a == b))
            
    def test_copy_1D(self):
        
        queue = Queue(ctx, ctx.devices[0])   
        a = np.array([1, 2, 3, 4])
        
        clbuf = DeviceMemoryView.from_host(ctx, a)
        
        copy_of = clbuf[::2].copy(queue)
            
        with copy_of.map(queue) as cpy:
            b = np.asarray(cpy)
            self.assertTrue(np.all(a[::2] == b))
            
        copy_of = clbuf[1::2].copy(queue)
            
        with copy_of.map(queue) as cpy:
            b = np.asarray(cpy)
            self.assertTrue(np.all(a[1::2] == b))
            
        copy_of = clbuf[1:-1].copy(queue)
            
        with copy_of.map(queue) as cpy:
            b = np.asarray(cpy)
            self.assertTrue(np.all(a[1:-1] == b))

    def test_copy_2D(self):


        queue = Queue(ctx, ctx.devices[0])   
        a = np.arange(6 * 6).reshape([6, 6])
        
        clbuf = DeviceMemoryView.from_host(ctx, a)
        
        slices = [
                  (slice(None, None, 2), slice(None, None, 2)),
                  (slice(1, None, None), slice(1, None, None)),
                  (slice(None, None, None), slice(1, None, None)),
                  (slice(1, None, None), slice(None, None, None)),
                  
                  (slice(1, None, None), slice(0, None, 2)),
                  (slice(None, None, 2), slice(1, None, 2)),
                  (slice(1, None, 2), slice(None, None, 2)),
                  ]
        
        for idx0, idx1 in slices:
            
            expected = a[idx0, idx1]
            sub_buf = clbuf[idx0, idx1]
            copy_of = sub_buf.copy(queue)
        
            with copy_of.map(queue) as cpy:
                b = np.asarray(cpy)
                expected = a[idx0, idx1]
                
                self.assertTrue(np.all(expected == b), (idx0, idx1))
                
    @unittest.expectedFailure     
    def test_copy_2D_negative_stride(self):


        queue = Queue(ctx, ctx.devices[0])   
        a = np.arange(4 * 4).reshape([4, 4])
        
        clbuf = DeviceMemoryView.from_host(ctx, a)
        
        slices = [(slice(None, None, -2), slice(None, None, -2)),
                  
                  (slice(1, None, -1), slice(1, None, -1)),
                  (slice(None, None, None), slice(1, None, -1)),
                  (slice(1, None, -1), slice(None, None, -1)),
                  
                  (slice(1, None, -2), slice(1, None, -2)),
                  (slice(None, None, -2), slice(1, None, -2)),
                  (slice(1, None, -2), slice(None, None, -2)),
                  ]
        
        for idx0, idx1 in slices:
            copy_of = clbuf[idx0, idx1].copy(queue)
        
            with copy_of.map(queue) as cpy:
                b = np.asarray(cpy)
                expected = a[idx0, idx1]
                self.assertTrue(np.all(expected == b))

    def test_broadcast_0D(self):
        
        with self.assertRaises(TypeError):
            cl.broadcast(None, [1])
            
        one = cl.from_host(ctx, c_int(1))
        
        a = cl.broadcast(one, [10, 10])
        self.assertEqual(a.shape, (10, 10))
        self.assertEqual(a.strides, (0, 0))
        
        queue = cl.Queue(ctx)
        with a.map(queue) as view:
            b = np.asarray(view)
            self.assertEqual(b.shape, (10, 10))
            self.assertEqual(b.strides, (0, 0))

    def test_broadcast_2D(self):
        
        with self.assertRaises(TypeError):
            cl.broadcast(None, [1])
            
        npa = np.arange(10, dtype=c_float)
        z = np.zeros([10, 1])
        
        ten = cl.from_host(ctx, npa)
        
        a = cl.broadcast(ten, [10, 10])
        self.assertEqual(a.shape, (10, 10))
        self.assertEqual(a.strides, (0, sizeof(c_float)))
        
        queue = cl.Queue(ctx)
        with a.map(queue) as view:
            b = np.asarray(view)
            self.assertEqual(b.shape, (10, 10))
            self.assertEqual(b.strides, (0, sizeof(c_float)))
            self.assertTrue(np.all(b == z + npa))
            
            
class TestImage(unittest.TestCase):
    def test_supported_formats(self):
        image_format = cl.ImageFormat.supported_formats(ctx)[0]
        
        format_copy = cl.ImageFormat.from_ctype(image_format.ctype)
        
        self.assertEqual(image_format, format_copy)
        
    def test_empty(self):

        image_format = cl.ImageFormat('CL_RGBA', 'CL_UNSIGNED_INT8')
        
        image = cl.empty_image(ctx, [4, 4], image_format)
        
        self.assertEqual(image.type, cl.Image.IMAGE2D)
        
        self.assertEqual(image.image_format, image_format)
        self.assertEqual(image.image_width, 4)
        self.assertEqual(image.image_height, 4)
        self.assertEqual(image.image_depth, 1)

    def test_empty_3d(self):

        image_format = cl.ImageFormat('CL_RGBA', 'CL_UNSIGNED_INT8')
        
        image = cl.empty_image(ctx, [4, 4, 4], image_format)
        
        self.assertEqual(image.type, cl.Image.IMAGE3D)
        self.assertEqual(image.image_format, image_format)
        self.assertEqual(image.image_width, 4)
        self.assertEqual(image.image_height, 4)
        self.assertEqual(image.image_depth, 4)

        
    def test_map(self):

        image_format = cl.ImageFormat('CL_RGBA', 'CL_UNSIGNED_INT8')
        
        image = cl.empty_image(ctx, [4, 4], image_format)
        
        queue = Queue(ctx)   

        with image.map(queue) as img:
            self.assertEqual(img.format, 'T{B:r:B:g:B:b:B:a:}')
            self.assertEqual(img.ndim, 2)
            self.assertEqual(img.shape, (4, 4))
            
            array = np.asarray(img)
            array['r'] = 1
            
        with image.map(queue) as img:
            array = np.asarray(img)
            self.assertTrue(np.all(array['r'] == 1))
        
class TestEvent(unittest.TestCase):
    
    def test_status(self):
        
        event = UserEvent(ctx)
        
        self.assertEqual(event.status, Event.SUBMITTED)
        event.complete()
        self.assertEqual(event.status, Event.COMPLETE)
        
    def test_wait(self):
        
        event = UserEvent(ctx)

        queue = Queue(ctx, ctx.devices[0])
        
        queue.enqueue_wait_for_events(event)
        
        event2 = queue.marker()
        
        self.assertEqual(event.status, Event.SUBMITTED)
        self.assertEqual(event2.status, Event.QUEUED)
        
        event.complete()
        self.assertEqual(event.status, Event.COMPLETE)
        
        event2.wait()
        self.assertEqual(event2.status, Event.COMPLETE)

    def test_callback(self):
        self.callback_called = False
        self.py_event = PyEvent()
        
        def callback(event, status):
            self.callback_called = True
            self.py_event.set()
        
        event = UserEvent(ctx)

        queue = Queue(ctx, ctx.devices[0])
        
        queue.enqueue_wait_for_events(event)
        
        event2 = queue.marker()
        event2.add_callback(callback)
        
        self.assertEqual(event.status, Event.SUBMITTED)
        self.assertEqual(event2.status, Event.QUEUED)
        
        self.assertFalse(self.callback_called)
        event.complete()
        self.assertEqual(event.status, Event.COMPLETE)
        
        event2.wait()
        self.assertEqual(event2.status, Event.COMPLETE)
        
        event_is_set = self.py_event.wait(2)
        
        self.assertTrue(event_is_set, 'timed out waiting for callback')

        self.assertTrue(self.callback_called)

ctx = None
DEVICE_TYPE = cl.Device.DEFAULT

def setUpModule():
    global ctx, DEVICE_TYPE
    
    ctx = cl.Context(device_type=DEVICE_TYPE)
    print ctx.devices
        
if __name__ == '__main__':
    
    argv = list(sys.argv)
    
    if '--gpu' in argv:
        del argv[argv.index('--gpu')]
        DEVICE_TYPE = cl.Device.GPU
    elif '--cpu' in argv:
        del argv[argv.index('--cpu')]
        DEVICE_TYPE = cl.Device.CPU

    unittest.main(argv=argv)
