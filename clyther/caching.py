import _ctypes
from inspect import isfunction, isclass
import pickle
import opencl as cl

class KernelCache(object):
    '''
    Basic Cache object.
    '''
    def generate_key(self, kwarg_types):
        '''
        create a hashable key from argument type dict.
        '''
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

    def __contains__(self, item):
        #ctx, func, cache_key = item
        raise NotImplementedError("This is an abstract class")
    
    def get(self, ctx, func, cache_key):
        raise NotImplementedError("This is an abstract class")
    
    def set(self, ctx, func, cache_key,
                  args, defaults, kernel_name, cly_meta, source,
                  binaries):
        raise NotImplementedError("This is an abstract class")

class NoFileCache(KernelCache):
    '''
    This is the default. It never caches a kernel's binary to disk. 
    '''
    
    def __contains__(self, item):
        #ctx, func, cache_key = item
        return False
    
    def get(self, ctx, func, cache_key):
        raise NotImplementedError("This object does not support caching use 'HDFCache' to cache to disk")
    
    def set(self, ctx, func, cache_key,
                  args, defaults, kernel_name, cly_meta, source,
                  binaries):
        pass
    

class HDFCache(NoFileCache):
    '''
    Cache a clyher.kernel to disk. 
    '''
    
    def __init__(self, kernel):
        # file://ff.h5.cly:/function_name/<hash of code obj>/<hash of arguments>/<device binary>
        try:
            import h5py
        except ImportError:
            raise NotImplementedError("import h5py failed. can not use HDFCache object")
        
        self.hf = h5py.File(kernel.db_filename)
    
    
    def __contains__(self, item):
        ctx, func, cache_key = item

        
        kgroup = self.hf.require_group(func.func_name)
        cgroup = kgroup.require_group(hex(hash(func.func_code)))
        tgroup = cgroup.require_group(hex(hash(cache_key)))
        
        have_compiled_version = all([device.name in tgroup.keys() for device in ctx.devices])
        
        return have_compiled_version

    
    def get(self, ctx, func, cache_key):
        
        kgroup = self.hf.require_group(func.func_name)
        cgroup = kgroup.require_group(hex(hash(func.func_code)))
        tgroup = cgroup.require_group(hex(hash(cache_key)))

#        source = cgroup.attrs['source']
        args = pickle.loads(tgroup.attrs['args'])
        defaults = pickle.loads(tgroup.attrs['defaults'])
        kernel_name = tgroup.attrs['kernel_name']

        binaries = {}
        for device in ctx.devices:
            binaries[device] = tgroup[device.name].value
            
        program = cl.Program(ctx, binaries=binaries)
        program.build()
        
        program, kernel_name, args, defaults
    
    def set(self, ctx, func, cache_key,
                  args, defaults, kernel_name, cly_meta, source,
                  binaries):
        
        kgroup = self.hf.require_group(func.func_name)
        cgroup = kgroup.require_group(hex(hash(func.func_code)))
        tgroup = cgroup.require_group(hex(hash(cache_key)))

        tgroup.attrs['args'] = pickle.dumps(args)
        tgroup.attrs['defaults'] = pickle.dumps(defaults)
        tgroup.attrs['kernel_name'] = kernel_name
        tgroup.attrs['meta'] = str(cly_meta)
        cgroup.attrs['source'] = source
        
        for device, binary in binaries.items():
            if device.name not in tgroup.keys():
                tgroup.create_dataset(device.name, data=binary)


