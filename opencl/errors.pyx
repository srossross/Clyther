
from _cl cimport *

all_opencl_errors = {
CL_SUCCESS: 'CL_SUCCESS',
CL_INVALID_VALUE: 'CL_INVALID_VALUE',
CL_INVALID_BINARY: 'CL_INVALID_BINARY',
CL_INVALID_BUFFER_SIZE: 'CL_INVALID_BUFFER_SIZE',
CL_INVALID_BUILD_OPTIONS: 'CL_INVALID_BUILD_OPTIONS',
CL_INVALID_CONTEXT: 'CL_INVALID_CONTEXT',
CL_INVALID_DEVICE: 'CL_INVALID_DEVICE',
CL_INVALID_EVENT: 'CL_INVALID_EVENT',
CL_INVALID_HOST_PTR: 'CL_INVALID_HOST_PTR',
CL_INVALID_KERNEL_NAME: 'CL_INVALID_KERNEL_NAME',
CL_INVALID_OPERATION: 'CL_INVALID_OPERATION',
CL_INVALID_KERNEL_NAME: 'CL_INVALID_KERNEL_NAME',
CL_INVALID_COMMAND_QUEUE: 'CL_INVALID_COMMAND_QUEUE',
CL_INVALID_CONTEXT: 'CL_INVALID_CONTEXT',
CL_INVALID_MEM_OBJECT: 'CL_INVALID_MEM_OBJECT',
CL_INVALID_EVENT_WAIT_LIST: 'CL_INVALID_EVENT_WAIT_LIST',
CL_INVALID_PROPERTY: 'CL_INVALID_PROPERTY',
CL_INVALID_DEVICE_TYPE: 'CL_INVALID_DEVICE_TYPE',
CL_INVALID_PROGRAM: 'CL_INVALID_PROGRAM',
CL_INVALID_PROGRAM_EXECUTABLE: 'CL_INVALID_PROGRAM_EXECUTABLE',
CL_INVALID_PLATFORM: 'CL_INVALID_PLATFORM',
CL_INVALID_KERNEL: 'CL_INVALID_KERNEL',
CL_INVALID_KERNEL_ARGS: 'CL_INVALID_KERNEL_ARGS',
CL_INVALID_WORK_DIMENSION: 'CL_INVALID_WORK_DIMENSION',
CL_INVALID_GLOBAL_WORK_SIZE: 'CL_INVALID_GLOBAL_WORK_SIZE',
CL_INVALID_GLOBAL_OFFSET: 'CL_INVALID_GLOBAL_OFFSET',
CL_INVALID_WORK_GROUP_SIZE: 'CL_INVALID_WORK_GROUP_SIZE',
CL_INVALID_WORK_ITEM_SIZE: 'CL_INVALID_WORK_ITEM_SIZE',
CL_INVALID_IMAGE_SIZE: 'CL_INVALID_IMAGE_SIZE',
CL_INVALID_ARG_INDEX: 'CL_INVALID_ARG_INDEX',
CL_INVALID_ARG_VALUE: 'CL_INVALID_ARG_VALUE',
CL_INVALID_SAMPLER: 'CL_INVALID_SAMPLER',
CL_INVALID_ARG_SIZE: 'CL_INVALID_ARG_SIZE',
CL_INVALID_KERNEL_DEFINITION: 'CL_INVALID_KERNEL_DEFINITION',
CL_MISALIGNED_SUB_BUFFER_OFFSET: 'CL_MISALIGNED_SUB_BUFFER_OFFSET',
CL_MEM_OBJECT_ALLOCATION_FAILURE: 'CL_MEM_OBJECT_ALLOCATION_FAILURE',
CL_DEVICE_NOT_AVAILABLE: 'CL_DEVICE_NOT_AVAILABLE',
CL_COMPILER_NOT_AVAILABLE: 'CL_COMPILER_NOT_AVAILABLE',
CL_BUILD_PROGRAM_FAILURE: 'CL_BUILD_PROGRAM_FAILURE',
CL_INVALID_OPERATION: 'CL_INVALID_OPERATION',
CL_OUT_OF_HOST_MEMORY: 'CL_OUT_OF_HOST_MEMORY',
CL_OUT_OF_RESOURCES: 'CL_OUT_OF_RESOURCES',
CL_DEVICE_NOT_FOUND: 'CL_DEVICE_NOT_FOUND',
CL_EXEC_STATUS_ERROR_FOR_EVENTS_IN_WAIT_LIST: 'CL_EXEC_STATUS_ERROR_FOR_EVENTS_IN_WAIT_LIST',
}

OpenCLErrorStrings = {
                
    CL_INVALID_CONTEXT: 'Context is not a valid context.',
    CL_INVALID_BUFFER_SIZE: 'size is 0',
    
    CL_INVALID_EVENT:'Event objects specified in event_list are not valid event objects',
    
    CL_INVALID_HOST_PTR : '''if host_ptr is NULL and CL_MEM_USE_HOST_PTR or  
CL_MEM_COPY_HOST_PTR are set in flags or if host_ptr is not NULL but 
CL_MEM_COPY_HOST_PTR or CL_MEM_USE_HOST_PTR are not set in flags.''',
    CL_MEM_OBJECT_ALLOCATION_FAILURE :"There is a failure to allocate memory for buffer object.",
    CL_OUT_OF_RESOURCES : "There is a failure to allocate resources required by the OpenCL implementation on the device.",
    CL_OUT_OF_HOST_MEMORY : "There is a failure to allocate resources required by the OpenCL implementation on the host",
    CL_INVALID_PROGRAM :'Program is not a valid program object.',
    CL_INVALID_VALUE: 'CL_INVALID_VALUE: this one should have been caught by python!',
    CL_INVALID_DEVICE : 'OpenCL devices listed in device_list are not in the list of devices associated with program.',
    CL_INVALID_BINARY:  'program is created with clCreateWithProgramBinary and devices listed in device_list do not have a valid program binary loaded.',
    CL_INVALID_BUILD_OPTIONS :'The build options specified by options are invalid.',
    CL_INVALID_OPERATION: 'The build of a program executable for any of the devices listed in device_list by a previous call to clBuildProgram for program has not  completed.',
    CL_COMPILER_NOT_AVAILABLE: 'Program is created with clCreateProgramWithSource and a compiler is not available' ,
    CL_BUILD_PROGRAM_FAILURE: '''if there is a failure to build the program executable.  
This error will be returned if clBuildProgram does not return until the build has 
completed. 
''',
    CL_INVALID_OPERATION: 'There are kernel objects attached to program.',
    CL_OUT_OF_HOST_MEMORY : 'if there is a failure to allocate resources required by the OpenCL implementation on the host.',
    
    CL_EXEC_STATUS_ERROR_FOR_EVENTS_IN_WAIT_LIST: 'The execution status of any of the events in event_list is a negative integer value',
    
    CL_INVALID_PROGRAM_EXECUTABLE : 'there is no successfully built executable for program',
    
    CL_INVALID_KERNEL_NAME : ' kernel_name is not found in program.',
    
    CL_INVALID_KERNEL_DEFINITION : ('The function definition for __kernel  function ' 
                                    'given by kernel_name such as the number of arguments, the argument types are not the' 
                                    'same for all devices for which the program executable has been built'),
                }


class OpenCLException(Exception):
    def __init__(self, err_code, mapping=None):
        if mapping is None:
            mapping = OpenCLErrorStrings
        Exception.__init__(self, err_code, all_opencl_errors.get(err_code, 'CL_ERROR'), mapping.get(err_code, 'Uknown OpenCL error'))
