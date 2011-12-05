from inspect import isclass
import _ctypes
import struct
import numpy as np
import ctypes


def complex_type_format(any_type):
    pass

def type_format(any_type):
    if isclass(any_type):
        if issubclass(any_type, float):
            return 'd'
        elif issubclass(any_type, int):
            return 'i'
        elif issubclass(any_type, _ctypes._SimpleCData):
            return any_type._type_
        elif issubclass(any_type, _ctypes.Array):
            return '(%i)%s' % (any_type._length_, type_format(any_type._type_))
        elif issubclass(any_type, _ctypes.Structure):
            type_list = ['%s:%s:' % (type_format(ctype), name) for name, ctype in any_type._fields_]
            return 'T{%s}' % (''.join(type_list))
        elif issubclass(any_type, _ctypes._Pointer):
            return '&%s' % (any_type._type_)
        
    raise TypeError('Could not get type format from type %r' % (any_type))

def is_complex_type(format):
    return format in (list(struct_types) + ['ff', 'dd', 'ii'])

def is_pointer(format):
    return format.startswith('&')

def derefrence(format):
    assert format.startswith('&')
    return format[1:]

def refrence(format):
#    assert format.startswith('&')
    return '&' + format


struct_ctype_map = {
                   'c':ctypes.c_char,
                   'b':ctypes.c_byte,
                   'B':ctypes.c_ubyte,
                   '?':ctypes.c_ubyte,
                   'h':ctypes.c_short,
                   'H':ctypes.c_ushort,
                   'i':ctypes.c_int,
                   'I':ctypes.c_uint,
                   'l':ctypes.c_long,
                   'L':ctypes.c_ulong,
                   'q':ctypes.c_longlong,
                   'Q':ctypes.c_ulonglong,
                   'f':ctypes.c_float,
                   'd':ctypes.c_double,
                   's':ctypes.c_char_p,
                   'p':ctypes.c_char_p,
                   'P':ctypes.c_void_p,
                   }

struct_type_map = {
                   'c':'char',
                   'b':'char',
                   'B':'unsigned char',
                   '?':'unsigned char',
                   'h':'short',
                   'H':'unsigned short',
                   'i':'int',
                   'I':'unsigned int',
                   'l':'long',
                   'L':'unsigned long',
                   'q':'long long',
                   'Q':'unsigned long long',
                   'f':'float',
                   'd':'double',
                   's':'char*',
                   'p':'char*',
                   'P':'void*',
                   '(2)f':'float2',
                   'T{f:x:f:y:}':'float2',
                   '(4)f':'float4',
                   'T{f:x:f:y:f:z:f:w:}':'float4',
                   }

def cdefn(simple_format):
    if is_pointer(simple_format):
        return '%s*' % (cdefn(derefrence(simple_format)))
    else:
        return struct_type_map[simple_format]

def find_closing_brace(format, braces='{}'):
    count = 1
    for i, char in enumerate(format):
        if char == braces[0]:
            count += 1
        elif char == braces[1]:
            count -= 1
            
        if count == 0:
            return i
    else:
        raise Exception() 
    
struct_types = 'cbB?hHiIlLqQfdspP'

    
def _ctype_from_format(format):
    i = 0
    fields = []
    while i < len(format):
        char = format[i]
        
        if char in struct_types:
            fields.append(['', struct_ctype_map[char]])
            i += 1
        elif char == '&':
            rest = _ctype_from_format(format[i + 1:])
            rest[0] = [rest[0][0], ctypes.POINTER(rest[0][1])]
            fields.extend(rest)
            break
            
        elif char in '<>!':
            i += 1
        elif char == 'T':
            i += 2
            n = find_closing_brace(format[i:])
            cstruct = format[i:i + n]
            
            _fields_ = [(name, ctype) for name, ctype in _ctype_from_format(cstruct)]
            T = type('T', (ctypes.Structure,), {'_fields_':_fields_})
            fields.append(['', T])
            i += n + 1
            
        elif char == ':':
            n = format.find(':', i + 1)
            if n == -1: raise Exception("missing closing ':'")
            fields[-1][0] = format[i + 1:n]
            i = n + 1
        elif char == '(':
            n = format.find(')', i)
            rest = _ctype_from_format(format[n + 1:])
            r0 = rest[0][1]
            for s in format[i + 1:n].split(','):
                r0 = r0 * int(s)
            rest[0][1] = r0
            fields.extend(rest)
            break
        else:
            raise TypeError("can not handle character %r in format string" % (char,))
    
    return fields

def ctype_from_format(format):
    ctype_lst = _ctype_from_format(format)
    if len(ctype_lst) == 1:
        return ctype_lst[0][1]
    else:
        raise NotImplementedError("")

def descriptor_from_format(format):
    
    i = 0 
    fields = []
    while i < len(format):
        char = format[i]
        
        if char in struct_types:
            fields.append(('', char))
            i += 1
        elif char in '<>!':
            i += 1
        elif char == 'T':
            i += 2
            n = find_closing_brace(format[i:])
            cstruct = format[i:i + n]
            fields.append(descriptor_from_format(cstruct))
            i += n + 1
        elif char == ':':
            n = format.find(':', i + 1)
            if n == -1: raise Exception("missing closing ':'")
            fields[-1][0] = format[i + 1:n]
            i = n + 1
        elif char == '(':
            n = format.find(')', i)
            rest = descriptor_from_format(format[n + 1:])
            shape = tuple(int(s) for s in format[i + 1:n].split(','))
            rest[0] = rest[0][0], rest[0][1], shape
            fields.extend(rest)
            break
        else:
            raise TypeError("can not handle character %r in format string" % (char,))

    return fields

def _size_list_from_format(format):
    
    i = 0 
    sizes = []
    while i < len(format):
        char = format[i]
        
        if char in struct_types:
            sizes.append(struct.calcsize(char))
            i += 1
        elif char in '<>!':
            i += 1
        elif char == '&':
            rest = _size_list_from_format(format[i + 1:])
            rest[0] = struct.calcsize('P')
            sizes.extend(rest)
            break
        elif char == 'T':
            i += 2
            n = find_closing_brace(format[i:])
            cstruct = format[i:i + n]
            sizes.append(size_from_format(cstruct))
            i += n + 1
        elif char == ':':
            n = format.find(':', i + 1)
            if n == -1: raise Exception("missing closing ':'")
            i = n + 1
        elif char == '(':
            n = format.find(')', i)
            rest = _size_list_from_format(format[n + 1:])
            for s in format[i + 1:n].split(','):
                rest[0] = rest[0]*int(s)
            sizes.extend(rest)
            break
        else:
            raise TypeError("can not handle character %r in format string" % (char,))
        
    return sizes
            
def size_from_format(format):
    return sum(_size_list_from_format(format))


def main():
    format = 'T{f:x:f:y:}'
#    format = '&(2)f'
#    print size_from_format(format)
#    dtype = np.dtype(descriptor_from_format(format))
    
    ctype = ctype_from_format(format)
    
    print memoryview(ctype()).format

if __name__ == '__main__':
    main()
    
