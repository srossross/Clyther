'''
Created on Dec 7, 2011

@author: sean
'''
import opencl as cl

DMAP = {cl.Device.CPU:'CPU', cl.Device.GPU:'GPU'}
def main():
    
    for platform in cl.get_platforms():
        print "Platform %r version: %s" % (platform.name, platform.version)
        
        for device in platform.devices():
            print " ++  %s Device %r" % (DMAP[device.type], device.name) 
            
            print "     | global_mem_size", device.global_mem_size / (1024 ** 2), 'Mb'
            print "     | local_mem_size", device.local_mem_size / (1024 ** 1), 'Kb'
            print "     | max_mem_alloc_size", device.max_mem_alloc_size / (1024 ** 2), 'Mb'
            print "     | has_image_support", device.has_image_support
            print "     | has_native_kernel", device.has_native_kernel
            print "     | max_compute_units", device.max_compute_units
            print "     | max_work_item_dimension", device.max_work_item_dimensions
            print "     | max_work_item_sizes", device.max_work_item_sizes
            print "     | max_work_group_size", device.max_work_group_size
            print "     | max_clock_frequency", device.max_clock_frequency, 'MHz'
            print "     | address_bits", device.address_bits, 'bits'
            print "     | max_read_image_args", device.max_read_image_args
            print "     | max_write_image_args", device.max_write_image_args
            print "     | max_image2d_shape", device.max_image2d_shape
            print "     | max_image3d_shape", device.max_image3d_shape
            print "     | max_parameter_size", device.max_parameter_size, 'bytes'
            print "     | max_const_buffer_size", device.max_const_buffer_size, 'bytes'
            print "     | has_local_mem", device.has_local_mem
            print "     | host_unified_memory", device.host_unified_memory
            print "     | available", device.available
            print "     | compiler_available", device.compiler_available
            print "     | driver_version", device.driver_version
            print "     | device_profile", device.profile
            print "     | version", device.version
#            print "     | extensions", device.extensions
            print 




if __name__ == '__main__':
    main()
    
