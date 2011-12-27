# IPython log file

import numpy as np
import opencl as cl
from PySide.QtGui import *
from PySide.QtOpenGL import *
from OpenGL import GL

app = QApplication([])
qgl = QGLWidget()
qgl.makeCurrent()

props = cl.ContextProperties()
cl.gl.set_opengl_properties(props)

ctx = cl.Context(device_type=cl.Device.DEFAULT, properties=props)

#print cl.ImageFormat.supported_formats(ctx)
print ctx.devices

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


iamge_format = cl.ImageFormat('CL_RGBA', 'CL_UNORM_INT8')

shape = 32, 32, 32

GL_FORMAT = cl.gl.get_gl_image_format(iamge_format)

#print "GL_FORMAT", GL_FORMAT
#print "GL.GL_RGBA", GL.GL_RGBA
#GL.glEnable(GL.GL_TEXTURE_2D)
#texture = GL.glGenTextures(1)
#GL.glBindTexture(GL.GL_TEXTURE_2D, texture)
#GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, 4, shape[0], shape[1], 0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, None)
#GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

image = cl.gl.empty_gl_image(ctx, shape, None)

print "image.shape"
print image.shape
print 
print 
with cl.gl.acquire(queue, image), image.map(queue) as buffer:
    array = np.asarray(buffer)
    array[:] = 0

with cl.gl.acquire(queue, image), image.map(queue) as buffer:
    array = np.asarray(buffer)
    print array

print image.image_format
print "done"

