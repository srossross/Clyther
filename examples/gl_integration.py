# IPython log file

import numpy as np
import opencl as cl
from PySide.QtGui import *
from PySide.QtOpenGL import *

app = QApplication([])
qgl = QGLWidget()
qgl.makeCurrent()

props = cl.ContextProperties()
cl.gl.set_opengl_properties(props)

ctx = cl.Context(device_type=cl.Device.DEFAULT, properties=props)

view = cl.gl.empty_gl(ctx, [10], ctype='ff')
view2 = cl.empty(ctx, [10], ctype='ff')

view.shape

print view
queue = cl.Queue(ctx)

with cl.gl.acquire(queue, view), view.map(queue) as buffer:
    print np.asarray(buffer)

print
print 'cl.gl.is_gl_object: view2', cl.gl.is_gl_object(view2)
print 'cl.gl.is_gl_object: view ', cl.gl.is_gl_object(view)
print 'cl.gl.get_gl_name', cl.gl.get_gl_name(view)
print
print "done"

