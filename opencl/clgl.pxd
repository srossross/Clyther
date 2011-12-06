
from _cl cimport *

cdef extern from "OpenCL/cl_gl_ext.h":
    enum gl_context_properties:
        CL_CONTEXT_PROPERTY_USE_CGL_SHAREGROUP_APPLE

cdef extern from "OpenGL/gl.h":
    void* CGLGetCurrentContext()
    void* CGLGetShareGroup(void*)
    
    ctypedef unsigned GLuint
    ctypedef void GLvoid
    ctypedef size_t GLsizeiptr
    
    enum GLenum:
        GL_ARRAY_BUFFER
        GL_STATIC_DRAW
        GL_NO_ERROR
    
    void glGenBuffers(size_t, GLuint*)
    void glBindBuffer(GLenum, GLuint)
    void glBufferData(GLenum, GLsizeiptr, GLvoid*, GLenum)
    
    GLenum glGetError() 

cdef extern from "OpenCL/cl_gl.h":
    
    cl_mem clCreateFromGLBuffer(cl_context, cl_mem_flags, unsigned, cl_int*)
