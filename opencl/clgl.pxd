
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
    
    enum cl_gl_error:
        CL_INVALID_GL_OBJECT
        
    enum cl_gl_object_type:
        CL_GL_OBJECT_BUFFER
        CL_GL_OBJECT_TEXTURE2D
        CL_GL_OBJECT_TEXTURE3D
        CL_GL_OBJECT_RENDERBUFFER
        
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


    cl_int clGetGLObjectInfo(cl_mem memobj, cl_gl_object_type *gl_object_type,  GLuint *gl_object_name)
    
    cl_int clEnqueueAcquireGLObjects(cl_command_queue, cl_uint, cl_mem*, cl_uint, cl_event *, cl_event *)
    cl_int clEnqueueReleaseGLObjects(cl_command_queue, cl_uint, cl_mem*, cl_uint, cl_event *, cl_event *)
    
    