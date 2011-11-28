//
// Created on Mar 15, 2010 by GeoSpin Inc
// @author: Sean Ross-Ross srossross@geospin.ca
// website: www.geospin.ca
//
//================================================================================//
// Copyright 2009 GeoSpin Inc.                                                    //
//                                                                                //
// Licensed under the Apache License, Version 2.0 (the "License");                //
// you may not use this file except in compliance with the License.               //
// You may obtain a copy of the License at                                        //
//                                                                                //
//      http://www.apache.org/licenses/LICENSE-2.0                                //
//                                                                                //
// Unless required by applicable law or agreed to in writing, software            //
// distributed under the License is distributed on an "AS IS" BASIS,              //
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.       //
// See the License for the specific language governing permissions and            //
// limitations under the License.                                                 //
//================================================================================//


#ifndef Py_OpenCL_H
#define Py_OpenCL_H

#ifdef __cplusplus
extern "C" {
#endif


#include <Python.h>
#include "structmember.h"

#ifdef __APPLE__
// if Mac 
#include <OpenCL/opencl.h>

#else
// else
#include <CL/cl.h>

#endif


typedef struct {
	PyObject_HEAD // ;
	cl_device_id devid;
} CyDeviceObject;

typedef struct {
    PyObject_HEAD // ;
    cl_context context;

    //PyObject *pfn_notify;
    PyObject *data;


} CyContextObject;

typedef struct {
    PyObject_HEAD // ;
    cl_program program;

} CyProgramObject;


typedef struct {
    PyObject_HEAD // ;
    cl_mem memory;
//    PyObject* host_buffer;

} CyMemBufferObject;

typedef struct {
    PyObject_HEAD // ;
    cl_event event;

} CyEventObject;


#define PyCLEvent_Check(ITEM) PyObject_TypeCheck( ITEM, (PyTypeObject*)(&_CyEventType) )
#define PyCLEvent_AsEvent(pevent) (((CyEventObject*)pevent)->event)

typedef struct {
    PyObject_HEAD // ;
    cl_kernel kernel;

} CyKernelObject;



typedef struct {
    PyObject_HEAD // ;
    cl_command_queue queue;

} CyQueueObject;


typedef struct {
    PyObject_HEAD // ;
    cl_platform_id plat;
} CyPlatformObject;



#define CyDeviceType_NUM 0
#define CyContextType_NUM 1
#define CyProgramType_NUM 2
#define CyMemBufferType_NUM 3
#define CyEventType_NUM 4
#define CyKernelType_NUM 5
#define CyQueueType_NUM 6
#define CyPlatType_NUM 7
#define CyError_NUM 8

#define ClytherAPI_pointers 9

#ifdef CLyther_MODULE


#define CyDeviceType 		((PyTypeObject*)&_CyDeviceType)
#define CyContextType 		((PyTypeObject*)&_CyContextType)
#define CyProgramType 		((PyTypeObject*)&_CyProgramType)
#define CyMemBufferType 		((PyTypeObject*)&_CyMemBufferType)
#define CyEventType 			((PyTypeObject*)&_CyEventType)
#define CyKernelType 		((PyTypeObject*)&_CyKernelType)
#define CyQueueType 	((PyTypeObject*)&_CyQueueType)
#define CyPlatType 			((PyTypeObject*)&_CyPlatType)


static cl_int CyError( cl_int err );




#else // External code


static void **CLyther_API;

#define CyDeviceType 		CLyther_API[0]
#define CyContextType 		CLyther_API[1]
#define CyProgramType 		CLyther_API[2]
#define CyMemBufferType 		CLyther_API[3]
#define CyEventType 			CLyther_API[4]
#define CyKernelType 		CLyther_API[5]
#define CyCommandQueueType 	CLyther_API[6]
#define CyPlatType 			CLyther_API[7]

#define CyError (*(cl_int (*) ( cl_int ) )  CLyther_API[8] )  ;

/* Return -1 and set exception on error, 0 on success. */
static int
import_opencl(void)
{
    PyObject *module = PyImport_ImportModule("opencl");

    if (module != NULL) {
        PyObject *c_api_object = PyObject_GetAttrString(module, "_C_API");
        if (c_api_object == NULL)
            return -1;
        if (PyCObject_Check(c_api_object))
        	CLyther_API = (void **)PyCObject_AsVoidPtr(c_api_object);
        Py_DECREF(c_api_object);
    }

    return 0;
}

#endif //CLyther_MODULE




#define CyDevice_Check( OBJ ) (PyObject_TypeCheck( OBJ, CyDeviceType ))
#define CyContext_Check( OBJ ) (PyObject_TypeCheck( OBJ, CyContextType ))
#define CyProgram_Check( OBJ ) (PyObject_TypeCheck( OBJ, CyProgramType ))
#define CyMemBuffer_Check( OBJ ) (PyObject_TypeCheck( OBJ, CyMemBufferType ))
#define CyEvent_Check( OBJ ) (PyObject_TypeCheck( OBJ, CyEventType ))
#define CyKernel_Check( OBJ ) (PyObject_TypeCheck( OBJ, CyKernelType ))
#define CyQueue_Check( OBJ ) (PyObject_TypeCheck( OBJ, CyCommandQueueType ))
#define CyPlat_Check( OBJ ) (PyObject_TypeCheck( OBJ, CyPlatType ))

#define CyDevice_AsDevice( OBJ ) (((CyDeviceObject *)OBJ)->devid)
#define CyContext_AsContext( OBJ ) (((CyContextObject *)OBJ)->context)
#define CyProgram_AsProgram( OBJ ) (((CyProgramObject *)OBJ)->program)
#define CyMemBuffer_AsMemBuffer( OBJ ) (((CyMemBufferObject *)OBJ)->memory)
#define CyEvent_AsEvent( OBJ ) (((CyEventObject *)OBJ)->event)
#define CyKernel_AsKernel( OBJ ) (((CyKernelObject *)OBJ)->kernel)
#define CyQueue_AsCommandQueue( OBJ ) (((CyQueueObject *)OBJ)->queue)
#define CyPlat_AsPlat( OBJ ) (((CyPlatformObject *)OBJ)->plat)


#ifdef __cplusplus
}
#endif


#endif // Py_OpenCL_H
