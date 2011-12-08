'''
Created on Dec 8, 2011

@author: sean
'''

from OpenGL.GL import *
from OpenGL.GLUT import *
import opencl as cl
from ctypes import c_float
from clyther.types import float2
import clyther as cly
import clyther.runtime as clrt
import numpy as np


@cly.global_work_size(lambda a: [a.size])
@cly.kernel
def generate_sin(a):
    gid = clrt.get_global_id(0)
    n = clrt.get_global_size(0)
    r = c_float(gid) / c_float(n)
    
    x = r * c_float(16.0) * c_float(3.1415)
    
    a[gid].x = c_float(r * 2.0) - c_float(1.0)
    a[gid].y = clrt.native_sin(x)

n_vertices = 100
coords_dev = None

def initialize():
    global coords_dev, n_vertices
    
    ctx = cl.gl.context()

    coords_dev = cl.gl.empty_gl(ctx, [n_vertices], ctype=float2)
    
    glClearColor(1, 1, 1, 1)
    glColor(0, 0, 1)
    
    queue = cl.Queue(ctx)
    
    with cl.gl.acquire(queue, coords_dev):
        generate_sin(queue, coords_dev)
        
    glEnableClientState(GL_VERTEX_ARRAY)
    
def display():
    global coords_dev, n_vertices

    glClear(GL_COLOR_BUFFER_BIT)
    
    vbo = cl.gl.get_gl_name(coords_dev)
    
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glVertexPointer(2, GL_FLOAT, 0, None)
    glDrawArrays(GL_LINE_STRIP, 0, n_vertices)
    
    glFlush()

def reshape(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glMatrixMode(GL_MODELVIEW)

if __name__ == '__main__':
    import sys
    glutInit(sys.argv)
    if len(sys.argv) > 1:
        n_vertices = int(sys.argv[1])
    glutInitWindowSize(800, 160)
    glutInitWindowPosition(0, 0)
    glutCreateWindow('OpenCL/OpenGL Interop Tutorial: Sin Generator')
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    initialize()
    glutMainLoop()
