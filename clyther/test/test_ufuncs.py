'''
Created on Dec 24, 2011

@author: sean
'''
import clyther as cly
from clyther.array import CLArrayContext
import opencl as cl
import unittest
import math
import os
import numpy as np

ca = None

def setUpModule():
    global ca
    
    
    DEVICE_TYPE_ATTR = os.environ.get('DEVICE_TYPE', 'DEFAULT')
    DEVICE_TYPE = getattr(cl.Device, DEVICE_TYPE_ATTR)
    
    ca = CLArrayContext(device_type=DEVICE_TYPE)
    
    print ca.devices

class Test(unittest.TestCase):


    def test_arange(self):
        a = ca.arange(5, ctype='f')
        npa = np.arange(5, dtype='f')
        
        with a.map() as view:
            self.assertTrue(np.allclose(view, npa))
        
    def test_add_scalar(self):
        
        a = ca.arange(5, ctype='f')
        a1 = ca.add(a, 5)

        b = np.arange(5, dtype='f')
        b1 = np.add(b, 5)
        
        self.assertEqual(a1.shape, b1.shape)
        
        with a1.map() as arr:
            self.assertTrue(np.allclose(arr, b1))
            
    def test_add_vector(self):
        
        a = ca.arange(5, ctype='f')
        x = ca.arange(5, ctype='f')
        
        a1 = ca.add(a, x)

        b = np.arange(5, dtype='f')
        y = np.arange(5, dtype='f')
        
        b1 = np.add(b, y)
        
        self.assertEqual(a1.shape, b1.shape)
        
        with a1.map() as arr:
            self.assertTrue(np.allclose(arr, b1))
            
    def test_add_vector_outer(self):
        
        a = ca.arange(5, ctype='f')
        x = ca.arange(5, ctype='f').reshape([5, 1])
        
        a1 = ca.add(a, x)

        b = np.arange(5, dtype='f')
        y = np.arange(5, dtype='f').reshape([5, 1])
        
        b1 = np.add(b, y)
        
        self.assertEqual(a1.shape, b1.shape)
        
        with a1.map() as arr:
            self.assertTrue(np.allclose(arr, b1))
        
    def test_sum(self):
        
        
        a = ca.arange(5, ctype='f')
        a1 = ca.sum(a)

        b = np.arange(5, dtype='f')
        b1 = np.sum(b)
        
        self.assertEqual(a1.size, b1.size)
        
        with a1.map() as arr:
            self.assertTrue(np.allclose(arr, b1))
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_add']
    unittest.main()
