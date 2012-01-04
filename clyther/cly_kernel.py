'''
Created on Dec 4, 2011

@author: sean
'''

from clyther.clast import cast
from clyther.pipeline import create_kernel_source
from clyther.queue_record import EventRecord
from clyther.rttt import typeof
from inspect import isfunction
from tempfile import mktemp
import ast
import opencl as cl
from clyther.caching import NoFileCache

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
    
def developer(func):
    '''
    Kernel decorator to enable developer tracebacks.
    '''
    func._development_mode = True
    func._no_cache = True

    return func

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
        self._file_cacher = NoFileCache()
        self._use_cache_file = False
    

    def clear_cache(self):
        '''
        Clear the binary cache in memory.
        '''
        self._cache.clear()
        
    def run_kernel(self, cl_kernel, queue, kernel_args, kwargs):
        '''
        Run a kernel this method is subclassable for the task class.
        '''
        event = cl_kernel(queue, global_work_size=kwargs.get('global_work_size'),
                                 global_work_offset=kwargs.get('global_work_offset'),
                                 local_work_size=kwargs.get('local_work_size'),
                                 **kernel_args)
        
        return event
    
    
    def _unpack(self, argnames, arglist, kwarg_types):
        '''
        Unpack memobject structure into two arguments. 
        '''
        kernel_args = {}
        for name, arg  in zip(argnames, arglist):
            
            if is_const(arg):
                continue
            
            arg_type = kwarg_types[name]
            if isinstance(arg_type, cl.contextual_memory):
                if kwarg_types[name].ndim != 0:
                    kernel_args['cly_%s_info' % name] = arg_type._get_array_info(arg)
            kernel_args[name] = arg
        return kernel_args

    def __call__(self, queue_or_context, *args, **kwargs):
        '''
        Call this kernel as a function.
        
        :param queue_or_context: a queue or context. if this is a context a queue is created and finish is called before return.
        
        :return: an OpenCL event.
        '''
        if isinstance(queue_or_context, cl.Context):
            queue = cl.Queue(queue_or_context)
        else:
            queue = queue_or_context
             
        argnames = self.func.func_code.co_varnames[:self.func.func_code.co_argcount]
        defaults = self.func.func_defaults
        
        kwargs_ = kwargs.copy()
        kwargs_.pop('global_work_size', None)
        kwargs_.pop('global_work_offset', None)
        kwargs_.pop('local_work_size', None)
        
        arglist = cl.kernel.parse_args(self.func.__name__, args, kwargs_, argnames, defaults)
        
        kwarg_types = {argnames[i]:typeof(queue.context, arglist[i]) for i in range(len(argnames))}
        
        cl_kernel = self.compile(queue.context, **kwarg_types)
        
        kernel_args = self._unpack(argnames, arglist, kwarg_types)
            
        event = self.run_kernel(cl_kernel, queue, kernel_args, kwargs)
        
        #FIXME: I don't like that this breaks encapsulation
        if isinstance(event, EventRecord):
            event.set_kernel_args(kernel_args)
            
        if isinstance(queue_or_context, cl.Context):
            queue.finish()
        
        return event
    
    def compile(self, ctx, source_only=False, cly_meta=None, **kwargs):
        '''
        Compile a kernel or lookup in cache.
        
        :param ctx: openCL context
        :param cly_meta: meta-information for inspecting the cache. (does nothing)
        :param kwargs: All other keyword arguments are used for type information.
        
        :return: An OpenCL kernel 
        '''
        cache = self._cache.setdefault(ctx, {})
        
        cache_key = tuple(sorted(kwargs.viewitems(), key=lambda item:item[0]))
        
        #Check for in memory cache
        if cache_key not in cache or self._no_cache:
            cl_kernel = self.compile_or_cly(ctx, source_only=source_only, cly_meta=cly_meta, **kwargs)
            
            cache[cache_key] = cl_kernel

        return cache[cache_key] 
    
    def source(self, ctx, *args, **kwargs):
        '''
        Get the source that would be compiled for specific argument types.
        
        .. note:: 
            
            This is meant to have a similar signature to the function call.
            i.e::
                 
                 print func.source(queue.context, arg1, arg2) 
                 func(queue, arg1, arg2)
        
        '''
        
        argnames = self.func.func_code.co_varnames[:self.func.func_code.co_argcount]
        defaults = self.func.func_defaults
        
        arglist = cl.kernel.parse_args(self.func.__name__, args, kwargs, argnames, defaults)
        
        kwarg_types = {argnames[i]:typeof(ctx, arglist[i]) for i in range(len(argnames))}
        
        return self.compile_or_cly(ctx, source_only=True, **kwarg_types)

    
    @property
    def db_filename(self):
        '''
        get the filename that the binaries can be cached to
        '''
        from os.path import splitext
        base = splitext(self.func.func_code.co_filename)[0]
        return base + '.h5.cly'
     
    def compile_or_cly(self, ctx, source_only=False, cly_meta=None, **kwargs):
        '''
        internal
        '''
        cache_key = self._file_cacher.generate_key(kwargs)

        if (ctx, self.func, cache_key) in self._file_cacher:
            program, kernel_name, args, defaults = self._file_cacher.get(ctx, self.func, cache_key)
        else:
            args, defaults, kernel_name, source = self.translate(ctx, **kwargs)
            
            program = self._compile(ctx, args, defaults, kernel_name, source)
            
            self._file_cacher.set(ctx, self.func, cache_key,
                                  args, defaults, kernel_name, cly_meta, source,
                                  program.binaries)

            
        cl_kernel = program.kernel(kernel_name)
        
        cl_kernel.global_work_size = self.global_work_size
        cl_kernel.local_work_size = self.local_work_size
        cl_kernel.global_work_offset = self.global_work_offset
        cl_kernel.argtypes = [arg[1] for arg in args]
        cl_kernel.argnames = [arg[0] for arg in args]
        cl_kernel.__defaults__ = defaults
        
        return cl_kernel
    
    def translate(self, ctx, **kwargs):
        '''
        Translate this func into a tuple of (args, defaults, kernel_name, source)  
        '''
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
        '''
        Compile a kernel without cache lookup. 
        '''
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

    def emulate(self, ctx, *args, **kwargs):
        '''
        Run this function in emulation mode.
        '''
        return self.func(*args, **kwargs)
    
    def run_kernel(self, cl_kernel, queue, kernel_args, kwargs):
        '''
        Run the kernel as a single thread task.
        '''
        #have to keep args around OpenCL refrence count is not incremented until enqueue_task is called
        args = cl_kernel.set_args(**kernel_args)
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

def cache(chache_obj):
    '''
    Set the caching type for a kernel binaries to file. (default is :class:`clyther.caching.NoFileCache`)
    Use cache as a decorator::
        
        @cache(HDFCache)
        @cly.kernel
        def foo(...):
            ...
    
    
    :param chache_obj: Cache object 
    
    
    '''
    def decorator(func):
        func._file_cacher = chache_obj
        return func
    return decorator
