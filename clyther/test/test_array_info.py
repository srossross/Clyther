'''
Created on Jan 9, 2012

@author: sean
'''
import clyther as cly
from clyther.array import CLArrayContext
import opencl as cl
import unittest
import math
import os
import numpy as np
import clyther.runtime as clrt


ca = None

def setUpModule():
    global ca
    
    
    DEVICE_TYPE_ATTR = os.environ.get('DEVICE_TYPE', 'DEFAULT')
    DEVICE_TYPE = getattr(cl.Device, DEVICE_TYPE_ATTR)
    
    ca = CLArrayContext(device_type=DEVICE_TYPE)
    
    print ca.devices

class Test(unittest.TestCase):

    def test_simple_func(self):
        
        @cly.global_work_size(lambda a:a.shape)
        @cly.kernel
        def test_kernel(a):
            idx = clrt.get_global_id(0)
            a[idx] = idx 
            
        a = ca.empty([10], ctype='f')
        
        test_kernel(a.queue, a)
        self.assertEqual(a[1].item().value, 1)
        self.assertEqual(a[2].item().value, 2)
        self.assertEqual(a[3].item().value, 3)

        test_kernel(a.queue, a[::2])
        
        self.assertEqual(a[1].item().value, 1)
        self.assertEqual(a[2].item().value, 1)
        self.assertEqual(a[3].item().value, 3)
        self.assertEqual(a[4].item().value, 2)

    def test_2Dsimple_func(self):
        
        @cly.global_work_size(lambda a:a.shape)
        @cly.kernel
        def test_kernel(a):
            idx0 = clrt.get_global_id(0)
            idx1 = clrt.get_global_id(1)
            a[idx0, idx1] = idx0 * 100 + idx1 
            
        a = ca.empty([10, 10], ctype='f')
        
        test_kernel(a.queue, a)
        self.assertEqual(a[1, 1].item().value, 101)
        self.assertEqual(a[2, 2].item().value, 202)
        self.assertEqual(a[3, 2].item().value, 302)

        test_kernel(a.queue, a[::2, ::3])
        
        self.assertEqual(a[1, 1].item().value, 101)
        self.assertEqual(a[2, 3].item().value, 101)
        self.assertEqual(a[2, 2].item().value, 202)
        self.assertEqual(a[3, 2].item().value, 302)
    
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_bcast']
    unittest.main()
