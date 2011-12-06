from opencl.errors import OpenCLException

from _cl cimport *
from opencl.copencl cimport clPlatformFromPyPlatform, clPlatformAs_PyPlatform
from opencl.copencl cimport DeviceIDFromPyDevice, DeviceIDAsPyDevice
from libc.stdlib cimport malloc, free 

cdef class ContextProperties:

    cdef public object properties_dict
    
    def __cinit__(self):
        self.properties_dict = {}
        
    property platform:
        def __get__(self):
            cdef cl_platform_id platform_id = NULL
            
            if 'platform' in self.properties_dict:
                plat = <size_t>self.properties_dict['platform'][1]
                platform_id = <cl_platform_id> plat
                return clPlatformAs_PyPlatform(<cl_platform_id>plat)
            else:
                return None

        def __set__(self, value):
            cdef cl_platform_id platform_id = clPlatformFromPyPlatform(value)
            self.properties_dict['platform'] = (< size_t > CL_CONTEXT_PLATFORM, <size_t> platform_id)

    def set_property(self, name, size_t property, size_t value):
        self.properties_dict['name'] = (property, value)
    
    def as_dict(self):
        return self.properties_dict
    
    cdef cl_context_properties * context_properties(self):
        
        nprops = len(self.properties_dict)
        
        cdef cl_context_properties * props = NULL
            
        if nprops == 0:
            return NULL
            
        props = < cl_context_properties *> malloc(sizeof(cl_context_properties) * (1 + 2 * nprops))

        cdef size_t property
        cdef size_t value
        cdef int i
        for i, (property, value) in enumerate(self.properties_dict.values()):
            props[i*2] = <cl_context_properties> property
            props[i*2+1] = <cl_context_properties> value

        props[nprops*2] = <cl_context_properties> NULL
        
        return props
    
    def __repr__(self):
        items = ['%s=%r' % (key, value[1]) for (key, value) in self.properties_dict.items()]
        
        return '<ContextProperties %s>' % (' '.join(items))


_context_errors = {
                       CL_INVALID_PLATFORM : ('Properties is NULL and no platform could be selected or if ' 
                                              'platform value specified in properties is not a valid platform.'),
                   CL_INVALID_PROPERTY: ('Context property name in properties is not a supported ' 
                                         'property name, if the value specified for a supported property name is not valid, or if the ' 
                                         'same property name is specified more than once.'),
                   CL_INVALID_VALUE: 'pfn_notify is NULL but user_data is not NULL.',
                   CL_INVALID_DEVICE_TYPE :'device_type is not a valid value.',
                   CL_DEVICE_NOT_AVAILABLE : ('No devices that match device_type and property values' 
                                              'specified in properties are currently available.'),
                                               
                   CL_DEVICE_NOT_FOUND: ('No devices that match device_type and property values ' 
                                        'specified in properties were found.'),
                   CL_OUT_OF_RESOURCES: ('There is a failure to allocate resources required by the ' 
                                         'OpenCL implementation on the device.'),
                   CL_OUT_OF_HOST_MEMORY :('There is a failure to allocate resources required by the ' 
                                           'OpenCL implementation on the host'),
                   }
cdef class Context:
    cdef cl_context context_id
    
    def __cinit__(self):
        self.context_id = NULL
        
    def __init__(self, devices=(), device_type=CL_DEVICE_TYPE_DEFAULT, ContextProperties properties=None):
        
        cdef cl_context_properties * props = NULL
        
        if properties is not None:
            props = properties.context_properties()
        
        cdef cl_device_type dtype
        cdef cl_int err_code
        cdef cl_uint num_devices
        cdef cl_device_id * _devices = NULL

        if devices:
            num_devices = len(devices)
            _devices = < cl_device_id *> malloc(num_devices * sizeof(cl_device_id))
            for i in range(num_devices): 
                _devices[i] = DeviceIDFromPyDevice(devices[i])
                 
            self.context_id = clCreateContext(props, num_devices, _devices, NULL, NULL, & err_code)
            
            if _devices != NULL:
                free(_devices)

            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code, _context_errors)
        else:
            dtype = < cl_device_type > device_type
            self.context_id = clCreateContextFromType(props, dtype, NULL, NULL, & err_code)
    
            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code, _context_errors)

    
    def __dealloc__(self):
        if self.context_id != NULL:
            clReleaseContext(self.context_id)
        self.context_id = NULL
        
    def __repr__(self):
        return '<opencl.Context>'
    
    def retain(self):
        clRetainContext(self.context_id)

    def release(self):
        clReleaseContext(self.context_id)
    
    property ref_count:
        def __get__(self):
            pass
        
    property num_devices:
        def __get__(self):
            
            cdef cl_int err_code
            cdef cl_uint num_devices
            err_code = clGetContextInfo (self.context_id, CL_CONTEXT_NUM_DEVICES, sizeof(cl_uint), &num_devices, NULL)
            
            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code)
            
            return num_devices
            
    property devices:
        def __get__(self):
            
            cdef cl_int err_code
            cdef size_t num_devices = self.num_devices
            cdef cl_device_id * _devices
    
            _devices = < cl_device_id *> malloc(num_devices * sizeof(cl_device_id))
    
            err_code = clGetContextInfo(self.context_id, CL_CONTEXT_DEVICES, num_devices*sizeof(cl_device_id), _devices, NULL)
    
            if err_code != CL_SUCCESS:
                free(_devices)
                raise OpenCLException(err_code)
            
            devices = []
            for i in range(num_devices): 
                device_id = _devices[i]
                device = DeviceIDAsPyDevice(device_id)
                devices.append(device) 
                
            free(_devices)
            
            return devices

#===============================================================================
# API
#===============================================================================

cdef api cl_context ContextFromPyContext(object pycontext):
    cdef Context context = < Context > pycontext
    return context.context_id

cdef api object ContextAsPyContext(cl_context context):
    ctx = < Context > Context.__new__(Context)
    clRetainContext(context)
    ctx.context_id = context
    return ctx

cdef api int PyContext_Check(object context):
    return isinstance(context, Context) 