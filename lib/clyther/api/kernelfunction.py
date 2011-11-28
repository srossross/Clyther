'''
Created on Mar 05, 2010 by GeoSpin Inc
@author: Sean Ross-Ross srossross@geospin.ca
website: www.geospin.ca
'''


#================================================================================#
# Copyright 2009 GeoSpin Inc.                                                     #
#                                                                                # 
# Licensed under the Apache License, Version 2.0 (the "License");                #
# you may not use this file except in compliance with the License.               #
# You may obtain a copy of the License at                                        #
#                                                                                #
#      http://www.apache.org/licenses/LICENSE-2.0                                #
#                                                                                #
# Unless required by applicable law or agreed to in writing, software            #
# distributed under the License is distributed on an "AS IS" BASIS,              #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.       #
# See the License for the specific language governing permissions and            #
# limitations under the License.                                                 #
#================================================================================#

import copencl as cl #@UnresolvedImport IGNORE:F0401

from clyther.api.ast.astoptimize import ASTOptimize
from clyther.api.ast.astgen import ASTConvert 
from clyther.api.ast.codegen import ASTWrite


from clyther.api.cltypes import cltype, rtte
from clyther.api.util import create_local_dict
#import astOpenCL
import inspect
import compiler
from clyther.static import get_context, get_queue, get_profile
import ctypes
from clyther.memory import shared_array_type, global_array_type
import pdb
import time
from warnings import warn
from clyther.device_objects import device_object
from clyther.disasembler import ast_from_function


class MapCountWarning(RuntimeWarning):
    pass

class OpenCLFunctionFactory(rtte):
    decorator_map = {'kernel':'__kernel' , 'device':'', 'task':'__kernel' }
    _is_function = True
    
    
    def __init__(self, func , _ftype):
        
        
        self.inst_count = 0
        
        if get_profile():
            self.profile = {} 
            self.profile['init'] = time.time()
            self.profile['optimize'] = {}
        else:
            self.profile = None
            
            
        self._ftype = _ftype
        self.__cl_constants__ = []
        self.function_dict = {}


        if hasattr(func, '__cl_constants__'):
            self.__cl_constants__ = func.__cl_constants__ 
        else:
            self.__cl_constants__ = []
            
            
        if hasattr(func, '__cl_bind__'):
            self.__cl_bind__ = func.__cl_bind__ 
        else:
            self.__cl_bind__ = []
        
        self.func = func
        source = inspect.getsource(func)
        
        stripcount = 0
        sourcelines = source.splitlines()
        for line in sourcelines:
            if not len(line.strip()):
                continue
            else:
                for item in line:
                    if item in ' \t':
                        stripcount += 1
                break
        
        source = "\n".join([ line[stripcount:] for line in sourcelines ])
        
        self.source = source
        
#        func_ast = compiler.parse( self.source )
        func_ast = ast_from_function(func)

#        print func_ast
#        self.ast = func_ast.node.nodes[0]
        self.ast = func_ast
        
        _, self._lineno = inspect.getsourcelines(self.func)
        self._filename = inspect.getfile(self.func)


        
        
        opencl_gen = ASTConvert(func, self._filename, self._lineno, self.source, decorator=self.decorator_map[self._ftype])
        
        compiler.visitor.walk(self.ast, opencl_gen, opencl_gen, verbose=True)
        
        self.opencl_module = opencl_gen.module
        
        if get_profile():
            self.profile['init_done'] = time.time()
#    def _get_return_type(self):
#        return self.opencl_module.return_type
#    return_type = property( _get_return_type )
    
    def _get_name(self):
        return self.func.__name__
    
    name = property(_get_name)
    def __repr__(self):
        return "<OpenCL %s factory '%s'>" % (self._ftype, self.func.__name__)
    
    def create_cl_code(self, cl_types , namespace, local_names):
        
#        print self.opencl_module
        
        opt = ASTOptimize(self.func, self._filename, self._lineno, self.source, cl_types , namespace=namespace)
        
        compiler.visitor.walk(self.opencl_module, opt, opt, verbose=True)

#        print self,opt.local_names.keys()

        local_names.update(opt.local_names)
        
        opencl_gen = ASTWrite(self.func, self._filename, self._lineno, self.source)
        
        compiler.visitor.walk(opt.result , opencl_gen, opencl_gen, verbose=True)
        
        return opt.node_name, opencl_gen.code, opt.args
    
            
    def arg_dict(self, args, kwargs):
        
        argspec = inspect.getargspec(self.func)
        
        return create_local_dict(argspec, args, kwargs)
        
    def argtypes(self, *args, **kwargs):
        
        if get_profile():
            t1 = time.time()

#        if get_emulate( ):
#            return EmulateKernelFunction( self.func )
        
        context = kwargs.pop('context', None)
        if context is None:
            context = get_context()
        
        namespace = kwargs.pop('__namespace__', dict())
        
        argspec = inspect.getargspec(self.func)
        
        arglocals = create_local_dict(argspec, args, kwargs)
        
        for key, value in arglocals.items():
            
            if not cltype.is_const(value):
                arglocals[key] = cltype.ctype(value)
        
        index = hash(tuple(arglocals.items()))
        
        if index in self.function_dict:
#            print "returning function from memory", self.function_dict[index]
            kernelfunc = self.function_dict[index]
        else:
            local_names = {}
            node_name, source, argnames = self.create_cl_code(arglocals, namespace, local_names)
            
            if self._ftype == 'kernel':
#                name = "%s%i" % (self.func.__name__,self.inst_count)
                kernelfunc = KernelFunction(node_name , source , argnames, arglocals, self.func, self.__cl_bind__, context, local_names=local_names)
                self.inst_count += 1
            elif self._ftype == 'task':
                kernelfunc = TaskFunction(node_name , source , argnames, arglocals, self.func, self.__cl_bind__, context, local_names=local_names)
            elif self._ftype == 'device':
                kernelfunc = DeviceFunction(node_name , source , argnames, arglocals, self.func, self.__cl_bind__, context, local_names=local_names)
            else:
                raise Exception("can not define opencl function with type %r. must be one of ['kernel','task']" % (self._ftype))
            
            self.function_dict[index] = kernelfunc
        
        if get_profile():
            self.profile['optimize'][index] = (t1, time.time()) 

        return kernelfunc
    
    def get_restype(self, arg_types):
        
        argspec = inspect.getargspec(self.func)
        
        arglocals = create_local_dict(argspec, arg_types, {})
        
#        pdb.set_trace( )
        for argdec in self.func_ast.argnames:
            argdec.type.set_type(arglocals[argdec.name])
        
        result = self.func_ast.return_type.resolve()
        return result
        
    
    def _get_func_ast(self):
        return self.opencl_module.node.nodes[0]
    
    func_ast = property(_get_func_ast)
    
    def __call__(self, *args, **kwargs):
        
        context = kwargs.pop('context', None)
        if context is None:
            context = get_context()

        argspec = inspect.getargspec(self.func)
        
        arglocals = create_local_dict(argspec, args, kwargs)
        
        
        argtypes = {}
        for argname in argspec[0]:
            
            # if the argument is constant then pass in the value
            # not the type
            if argname not in self.__cl_constants__:
                ctype = cltype.ctype(arglocals[argname])
                argtypes[argname] = ctype
            else:
                argtypes[argname] = arglocals[argname]
                
            
        
        argtypes['context'] = context
        
        kernelfunc = self.argtypes(**argtypes)
        
        return kernelfunc(**arglocals)
    
    def print_full_profile(self):
        if self.profile is None: raise Exception("Profiling not enabled from clyther.init()")
            
        print "PROFILE"
        print "*" * 40
        print "host init: %7.4f" % (self.profile['init_done'] - self.profile['init'])
        print "-" * 50
        for key in self.function_dict:
            func = self.function_dict[key]
            print func.cdef() 
            start, stop = self.profile['optimize'][key]
            print "host opt:  %7.4f" % (stop - start)
            
            total = 0
            num = len(func.profile['call'])
            totals = []
            
            print "              num   |   avg   |   min   |   max   | total "
            
            for start, stop in  func.profile['call']:
                totals.append(stop - start)
            total = sum(totals)
            
            
            print "host call:  %7i | %7.4f | %7.4f | %7.4f | %7.4f" % (num, total / float(num), min(totals), max(totals), total)
            
            totals = []
            for work_sizes, events in  func.profile['events'].items():
                print "global_work_size=%r local_work_size=%r" % work_sizes
                for event in events:
                    diff = 1e-9 * (event.profile_end - event.profile_start)
                    totals.append(diff)
                    total = sum(totals)
                print " +device :  %7i | %7.4f | %7.4f | %7.4f | %7.4f" % (num, total / float(num), min(totals), max(totals), total)
    
    
class KernelFunctionBase(object):
    cdef_decorator = "__kernel"
    
    def __init__(self, name, source, argnames, argtypes , func, bind, context, local_names):
        
        if get_profile():
            self.profile = {}
            self.profile['build_start'] = time.time()
            self.profile['call'] = []
            self.profile['events'] = {}
        else:
            self.profile = None
              

        self.__cl_bind__ = bind
        self.func = func
        self.source = source
        self.name = name 
        self.context = context
        self.argnames = argnames
        self.argtypes = argtypes
        
        
        self.prog = cl.Program(context, source)
        try:
            self.prog.build()
        except:
            print "build log"
            
            lines = [ "%4i :  %s" % (i + 1, line) for (i, line) in enumerate(self.source.splitlines())]
            print "\n".join(lines)
            print 
            print 
            print self.prog.build_log(context.devices[0])
            raise
        
        self.kernel = cl.Kernel(self.prog, self.name)
        
        if len(self.argnames) != self.kernel.num_args :
            raise TypeError("Developer error kernel %s() takes takes exactly %i arguments (python calculated %i )" % (self.name, self.kernel.num_args, len(self.argnames)))

        if get_profile():
            self.profile['build_end'] = time.time()

    def __repr__(self):
        return "<kernel function '%s'>" % (self.name,)
    
    def cdef(self):
        
        return "%s %s( %s );" % (self.cdef_decorator, self.name, ", ".join([cltype.cdef(ctype) for ctype in self.argtypes.values()]))
    
    def set_args(self, argdict):
        
        for idx, arg in enumerate(self.argnames):
            value = argdict[arg]
            ctype = self.argtypes[arg]
            
            
            new_ctype = cltype.ctype(ctype)
            
            
            if isinstance(new_ctype, (rtte)):
                if isinstance(new_ctype, shared_array_type):
                    self.kernel.set_arg(idx, None , value.nbytes)
                elif isinstance(new_ctype, global_array_type):
                    map_count = getattr(value, 'map_count' , 0)
                    if map_count != 0:
                        message = "map_count of device memory object is not 0. This could mean that there are un-written chenges"
                        warn(message, category=MapCountWarning, stacklevel=2)
                        
                    self.kernel.set_arg(idx, value)
                else:
                    raise Exception("can not handle this type yet")
                
            elif isinstance(value, (device_object,)):
                
                address = ctypes.addressof(value._container)
                size = ctypes.sizeof(value._container)
#                    print "calling self.kernel.set_arg_ptr"
                self.kernel.set_arg_ptr(idx, size , address)
                
            elif hasattr(new_ctype, 'from_param'):
                    
                cvalue = new_ctype(value)
#                    cvalue = value 
                
                address = ctypes.addressof(cvalue)
                size = ctypes.sizeof(cvalue)
#                    print "calling self.kernel.set_arg_ptr"
                self.kernel.set_arg_ptr(idx, size , address)
#                    print "called kernel.set_arg_ptr"
            else:
                raise Exception("can not handle this type yet")
        
    def get_args(self, args, kwargs):
        
        argspec = inspect.getargspec(self.func)
        argdict = create_local_dict(argspec, args, kwargs, only_use=self.argnames)
        
        mylocals = self.argtypes.copy()
        mylocals.update(argdict)
        for name, bind_expr in self.__cl_bind__:
            if name not in kwargs:
                kwargs[name] = self.eval_bind(name, bind_expr, mylocals)
                argdict[name] = kwargs[name]
                
        return argdict

    def eval_bind(self, name, bind_expr, arglocals):
        if isinstance(bind_expr, str):
            return eval(bind_expr , globals(), arglocals)
        elif inspect.isroutine(bind_expr):
            return bind_expr(**arglocals)
        else:
            return bind_expr


class KernelFunction(KernelFunctionBase):
    cdef_decorator = "__kernel"
    
    def __call__(self, *args, **kwargs):
        
        if get_profile():
            t1 = time.time()

        queue = kwargs.pop('queue', None)
        
        if queue is None:
            queue = get_queue()
        
        argdict = self.get_args(args, kwargs)
        self.set_args(argdict)

                    
        global_work_size = kwargs.pop('global_work_size', [1, 1, 1])
        local_work_size = kwargs.pop('local_work_size', [1, 1, 1])

        if not isinstance(global_work_size, (list, tuple)):
            global_work_size = [global_work_size, 1, 1]
        elif len(global_work_size) < 3:
            global_work_size = tuple(global_work_size + [1] * (3 - len(global_work_size)))
    
        if not isinstance(local_work_size, (list, tuple)):
            local_work_size = [local_work_size, 1, 1]
        elif len(local_work_size) < 3:
            local_work_size = tuple(local_work_size + [1] * (3 - len(local_work_size)))


        event = queue.enqueue_kernel(self.kernel, global_work_size, local_work_size)
        
        
        if get_profile():
            self.profile['call'].append((t1, time.time()))
            key = (tuple(global_work_size), tuple(local_work_size))
            lst = self.profile['events'].setdefault(key, [])
            lst.append(event) 

        return event
        

class DeviceFunction(KernelFunctionBase):
    cdef_decorator = ""
    
    def __init__(self, name, source, argnames, argtypes , func, bind, context, local_names):

        self.__cl_bind__ = bind
        self.func = func
        self.source = source
        self.name = name 
        self.context = context
        self.argnames = argnames
        self.argtypes = argtypes
        self.local_names = local_names
        
        
class TaskFunction(KernelFunctionBase):
    cdef_decorator = "__kernel"
    
    def __call__(self, *args, **kwargs):
        
        if get_profile():
            t1 = time.time()

        queue = kwargs.pop('queue', None)
        
        if queue is None:
            queue = get_queue()
        
        argdict = self.get_args(args, kwargs)
        self.set_args(argdict)

                    
        global_work_size = kwargs.pop('global_work_size', [1, 1, 1])
        local_work_size = kwargs.pop('local_work_size', [1, 1, 1])

        if not isinstance(global_work_size, (list, tuple)):
            global_work_size = [global_work_size, 1, 1]
        elif len(global_work_size) < 3:
            global_work_size = tuple(global_work_size + [1] * (3 - len(global_work_size)))
    
        if not isinstance(local_work_size, (list, tuple)):
            local_work_size = [local_work_size, 1, 1]
        elif len(local_work_size) < 3:
            local_work_size = tuple(local_work_size + [1] * (3 - len(local_work_size)))


        event = queue.enqueue_task(self.kernel)
        
        if get_profile():
            self.profile['call'].append((t1, time.time()))
            key = (tuple(global_work_size), tuple(local_work_size))
            lst = self.profile['events'].setdefault(key, [])
            lst.append(event) 

        return event
        

        
