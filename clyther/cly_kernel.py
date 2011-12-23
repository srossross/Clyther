'''
Created on Dec 4, 2011

@author: sean
'''

from clyther.clast import cast
import opencl as cl
from opencl import global_memory
from clyther.queue_record import  EventRecord
import ast
from inspect import isfunction, isclass
import ctypes
from tempfile import mktemp
import pickle
import h5py
import _ctypes
from clyther.pipeline import create_kernel_source

class ClytherKernel(object):
    pass

class CLComileError(Exception):
    def __init__(self, lines, prog):
        Exception.__init__(self, lines)
        self.prog = prog
        

def is_const(obj):
    if isfunction(obj):
        return True
    else:
        return False
    
def typeof(obj):
    if isinstance(obj, cl.MemoryObject):
        return global_memory(obj.format, len(obj.shape), obj.shape)
    elif isinstance(obj, cl.local_memory):
        return obj
    elif isfunction(obj):
        return obj
    
    elif isinstance(obj, int):
        return ctypes.c_int
    elif isinstance(obj, float):
        return ctypes.c_float
    else:
        return type(obj)
    
def developer(func):
    func._development_mode = True
    func._no_cache = True

    return func

def create_key(kwarg_types):
    
    arlist = []
    for key, value in sorted(kwarg_types.viewitems(), key=lambda item:item[0]):
        CData = _ctypes._SimpleCData.mro()[1]
        if isfunction(value):
            value = (value.func_name, hash(value.func_code.co_code))
        elif isclass(value) and issubclass(value, CData):
            value = hash(pickle.dumps(value))
        else:
            value = hash(value)
            
        arlist.append((key, value))
    
    return hash(tuple(arlist))

class kernel(object):
    '''
    Create an OpenCL kernel from a Python function.
    
    This class can be used as a decorator::
    
        @kernel
        def foo(a):
            ...
    '''
    
    def __init__(self, func):
        self.func = func
        self.__doc__ = self.func.__doc__ 
        self.global_work_size = None
        self.local_work_size = None
        self.global_work_offset = None
        self._cache = {}
        
        self._development_mode = False
        self._no_cache = False
        

    def run_kernel(self, cl_kernel, queue, kernel_args, kwargs):
        event = cl_kernel(queue, global_work_size=kwargs.get('global_work_size'),
                                 global_work_offset=kwargs.get('global_work_offset'),
                                 local_work_size=kwargs.get('local_work_size'),
                                 **kernel_args)
        
        return event
    
    
    def __call__(self, queue, *args, **kwargs):
        
        argnames = self.func.func_code.co_varnames[:self.func.func_code.co_argcount]
        defaults = self.func.func_defaults
        
        kwargs_ = kwargs.copy()
        kwargs_.pop('global_work_size', None)
        kwargs_.pop('global_work_offset', None)
        kwargs_.pop('local_work_size', None)
        
        arglist = cl.kernel.parse_args(self.func.__name__, args, kwargs_, argnames, defaults)
        
        kwarg_types = {argnames[i]:typeof(arglist[i]) for i in range(len(argnames))}
        
        cl_kernel = self.compile(queue.context, **kwarg_types)
        
        kernel_args = {}
        for name, arg  in zip(argnames, arglist):
            
            if is_const(arg):
                continue
            
            kernel_args[name] = arg
            if isinstance(arg, cl.DeviceMemoryView):
                kernel_args['cly_%s_info' % name] = arg.array_info
            if isinstance(arg, cl.local_memory):
                kernel_args['cly_%s_info' % name] = arg.local_info
        
        event = self.run_kernel(cl_kernel, queue, kernel_args, kwargs)
        
        #FIXME: I don't like that this breaks encapsulation
        if isinstance(event, EventRecord):
            event.set_kernel_args(kernel_args)
            
        return event
    
    def compile(self, ctx, source_only=False, cly_meta=None, **kwargs):
        cache = self._cache.setdefault(ctx, {})
        
        cache_key = tuple(sorted(kwargs.viewitems(), key=lambda item:item[0]))
        
        if cache_key not in cache or self._no_cache:
            cl_kernel = self.compile_or_cly(ctx, source_only=source_only, cly_meta=cly_meta, **kwargs)
            
            cache[cache_key] = cl_kernel

        return cache[cache_key] 
    
    def source(self, ctx, *args, **kwargs):
        
        argnames = self.func.func_code.co_varnames[:self.func.func_code.co_argcount]
        defaults = self.func.func_defaults
        
        arglist = cl.kernel.parse_args(self.func.__name__, args, kwargs, argnames, defaults)
        
        kwarg_types = {argnames[i]:typeof(arglist[i]) for i in range(len(argnames))}
        
        return self.compile_or_cly(ctx, source_only=True, **kwarg_types)

    
    @property
    def db_filename(self):
        from os.path import splitext
        base = splitext(self.func.func_code.co_filename)[0]
        return base + '.h5.cly'
     
    def compile_or_cly(self, ctx, source_only=False, cly_meta=None, **kwargs):
        
        cache_key = create_key(kwargs) 
        # file://ff.h5.cly:/function_name/<hash of code obj>/<hash of arguments>/<device binary>

        hf = h5py.File(self.db_filename)
        kgroup = hf.require_group(self.func.func_name)
        cgroup = kgroup.require_group(hex(hash(self.func.func_code)))
        tgroup = cgroup.require_group(hex(hash(cache_key)))
        
        have_compiled_version = all([device.name in tgroup.keys() for device in ctx.devices])
        
        if not have_compiled_version:
            args, defaults, kernel_name, source = self.translate(ctx, **kwargs)
            tgroup.attrs['args'] = pickle.dumps(args)
            tgroup.attrs['defaults'] = pickle.dumps(defaults)
            tgroup.attrs['kernel_name'] = kernel_name
            tgroup.attrs['meta'] = str(cly_meta)
            cgroup.attrs['source'] = source
            
            if source_only:
                return source
            
            program = self._compile(ctx, args, defaults, kernel_name, source)
            
            for device, binary in program.binaries.items():
                if device.name not in tgroup.keys():
                    tgroup.create_dataset(device.name, data=binary)
            
                    
        else:
            #args, defaults, program, kernel_name, source = self._compile(ctx, source_only=source_only, **kwargs)
            source = cgroup.attrs['source']
            args = pickle.loads(tgroup.attrs['args'])
            defaults = pickle.loads(tgroup.attrs['defaults'])
            kernel_name = tgroup.attrs['kernel_name']
            
            if source_only:
                return source

            binaries = {}
            for device in ctx.devices:
                binaries[device] = tgroup[device.name].value
                
            program = cl.Program(ctx, binaries=binaries)
            program.build()
            
        cl_kernel = program.kernel(kernel_name)
        
        cl_kernel.global_work_size = self.global_work_size
        cl_kernel.local_work_size = self.local_work_size
        cl_kernel.global_work_offset = self.global_work_offset
        cl_kernel.argtypes = [arg[1] for arg in args]
        cl_kernel.argnames = [arg[0] for arg in args]
        cl_kernel.__defaults__ = defaults
        
        return cl_kernel
    
    def translate(self, ctx, **kwargs):
        
        try:
            args, defaults, source, kernel_name = create_kernel_source(self.func, kwargs)
        except cast.CError as error:
            if self._development_mode: raise
            
            redirect = ast.parse('raise error.exc(error.msg)')
            redirect.body[0].lineno = error.node.lineno
            filename = self.func.func_code.co_filename
            redirect_error_to_function = compile(redirect, filename, 'exec')
            eval(redirect_error_to_function) #use the @cly.developer function decorator to turn this off and see stack trace ...
            
        return args, defaults, kernel_name, source
        
    
    def _compile(self, ctx, args, defaults, kernel_name, source):
        
        tmpfile = mktemp('.cl', 'clyther_')
        program = cl.Program(ctx, ('#line 1 "%s"\n' % (tmpfile)) + source)
        
        try:
            program.build()
        except cl.OpenCLException:
            log_lines = []
            for device, log in program.logs.items():
                log_lines.append(repr(device))
                log_lines.append(log)
            
            with open(tmpfile, 'w') as fp:
                fp.write(source)
                
            raise CLComileError('\n'.join(log_lines), program)
        
        for device, log in program.logs.items():
            if log: print log
            
        return program

class task(kernel):
    '''
    Create an OpenCL kernel from a Python function.
    
    Calling this object will enqueue a task.
    
    This class can be used as a decorator::
    
        @task
        def foo(a):
            ...
    '''

    def run_kernel(self, cl_kernel, queue, kernel_args, kwargs):
        
        cl_kernel.set_args(**kernel_args)
        event = queue.enqueue_task(cl_kernel)
        
#        event = cl_kernel(queue, global_work_size=kwargs.get('global_work_size'),
#                                 global_work_offset=kwargs.get('global_work_offset'),
#                                 local_work_size=kwargs.get('local_work_size'),
#                                 **kernel_args)
        
        return event
    
def global_work_size(arg):
    '''
    Bind the global work size of an nd range kernel to a arguments.
    
    :param arg: can be either a list of integers or a function with the same signature as the python
        kernel.
    '''
    def decorator(func):
        func.global_work_size = arg
        return func
    return decorator

def local_work_size(arg):
    '''
    Bind the local work size of an nd range kernel to a arguments.
    
    :param arg: can be either a list of integers or a function with the same signature as the python
        kernel.
    '''
    def decorator(func):
        func.local_work_size = arg
        return func
    return decorator

def global_work_offset(arg):
    '''
    Bind the local work size of an nd range kernel to a arguments.
    
    :param arg: can be either a list of integers or a function with the same signature as the python
        kernel.
    '''
    def decorator(func):
        func.global_work_offset = arg
        return func
    return decorator

