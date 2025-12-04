from re import X
from tkinter import Y
import win32api
import win32con
import win32security
import ctypes as c
import pymem
import pymem.process
from context import *

def _buffer_size_for_option(option: int) -> int:
    # size to read for each type
    if option in (2, 3):   # u64 / double
        return 8
    if option in (1, 4):   # int / short
        return 4 if option == 1 else 2
    if option == 7:        # byte
        return 1
    if option == 5:        # string (assume small fixed/zero-terminated)
        return 64          # adjust if your game uses larger names
    return 8               # default raw

def _cast_buffer(buffer: c.Array, option: int):
    match option:
        case 1:  # int32
            return c.cast(buffer, c.POINTER(c.c_int)).contents.value
        case 2:  # uint64
            return c.cast(buffer, c.POINTER(c.c_ulonglong)).contents.value
        case 3:  # double
            return c.cast(buffer, c.POINTER(c.c_double)).contents.value
        case 4:  # int16
            return c.cast(buffer, c.POINTER(c.c_short)).contents.value
        case 5:  # utf-8 zstr
            try:
                raw = bytes(buffer)
                end = raw.find(b"\x00")
                if end == -1:
                    end = len(raw)
                return raw[:end].decode("utf-8", errors="replace")
            except Exception:
                return "*"
        case 7:  # byte
            return c.cast(buffer, c.POINTER(c.c_ubyte)).contents.value
        case _:
            return bytes(buffer)

def _rpm(handle, address_int: int, option: int, *, debug_label: str = ""):
    buf_size = _buffer_size_for_option(option)
    buffer = c.create_string_buffer(buf_size)
    bytes_read = c.c_size_t(0)
    addr = c.c_void_p(address_int)
    ok = c.windll.kernel32.ReadProcessMemory(
        handle, addr, buffer, buf_size, c.byref(bytes_read)
    )
    if not ok:
        return None
    return _cast_buffer(buffer, option)

def write_memory(handle, address, value, value_type="int"):

    if value_type == "int":
        buffer = c.c_int(value)
        size = c.sizeof(buffer)

    elif value_type == "float":
        buffer = c.c_float(value)
        size = c.sizeof(buffer)

    elif value_type == "double":
        buffer = c.c_double(value)
        size = c.sizeof(buffer)

    elif value_type == "short":
        buffer = c.c_short(value)
        size = c.sizeof(buffer)

    elif value_type == "byte":
        buffer = c.c_byte(value)
        size = c.sizeof(buffer)

    elif value_type == "string":
        buffer = c.create_string_buffer(value.encode("utf-8"))
        size = len(buffer)

    else:
        raise ValueError(f"Unsupported value_type: {value_type}")

    written = c.c_size_t(0)
    result = c.windll.kernel32.WriteProcessMemory(
        handle,
        c.c_void_p(address),
        c.byref(buffer),
        size,
        c.byref(written)
    )

    if not result:
        raise OSError(f"WriteProcessMemory failed at {hex(address)}")
    return True

def read_direct(handle, absolute_address: int, field_offset: int, option: int, *, label=""):
    return _rpm(handle, absolute_address + field_offset, option, debug_label=label)

def read_memory_address(handle, module_base: int, rva: int, offset: int, option: int, *, label=""):
    absolute = module_base + rva + offset
    return _rpm(handle, absolute, option, debug_label=label)

def read_pointer_address(handle, module_base: int, rva: int, offsets: list[int], option: int, *, label=""):
    cur_ptr = read_memory_address(handle, module_base, rva, 0, 2, label=label + ":base_ptr")
    if cur_ptr is None:
        return None
    for ofs in offsets:
        nxt = _rpm(handle, cur_ptr + ofs, 2, debug_label=label + f":ptr+{hex(ofs)}")
        if nxt is None:
            return None
        cur_ptr = nxt
    return _rpm(handle, cur_ptr, option, debug_label=label + ":final")

def read_targeting_status(handle, context):
    return read_direct(handle, context.attackPointer, 0, 2, label="attack_ptr")

def read_my_stats(handle, context):
    x        = read_direct(handle, context.playerPointer, context.Addresses.my_x_address, 1, label="my_x")
    y        = read_direct(handle, context.playerPointer, context.Addresses.my_y_address, 1, label="my_y")
    z        = read_direct(handle, context.playerPointer, context.Addresses.my_z_address, 7, label="my_z")
    hp       = read_direct(handle, context.playerPointer, context.Addresses.my_hp_offset, 3, label="my_hp")
    hp_max   = read_direct(handle, context.playerPointer, context.Addresses.my_hp_max_offset, 3, label="my_hp_max")
    mp       = read_direct(handle, context.playerPointer, context.Addresses.my_mp_offset, 3, label="my_mp")
    mp_max   = read_direct(handle, context.playerPointer, context.Addresses.my_mp_max_offset, 3, label="my_mp_max")
    rest     = read_direct(handle, context.playerPointer, context.Addresses.my_rest_offset, 3, label="my_rest")
    return x, y, z, hp, hp_max, mp, mp_max, rest

def read_target_info(handle, target, context):
    tx = read_direct(handle, target, context.Addresses.target_x_offset, 1, label="target_x")
    ty = read_direct(handle, target, context.Addresses.target_y_offset, 1, label="target_y")
    tz = read_direct(handle, target, context.Addresses.target_z_offset, 7, label="target_y")
    name = read_direct(handle, target, context.Addresses.target_name_offset, 5, label="target_name")
    hp = read_direct(handle, target, context.Addresses.target_hp_offset, 7, label="target_hp")

    return tx, ty, tz, name, hp

def enable_debug_privilege_pywin32():
    try:
        hToken = win32security.OpenProcessToken(
            win32api.GetCurrentProcess(),
            win32con.TOKEN_ADJUST_PRIVILEGES | win32con.TOKEN_QUERY
        )
        privilege_id = win32security.LookupPrivilegeValue(None, win32security.SE_DEBUG_NAME)
        win32security.AdjustTokenPrivileges(hToken, False, [(privilege_id, win32con.SE_PRIVILEGE_ENABLED)])
        return True
    except Exception as e:
        print("Błąd przy włączaniu przywileju debugowania:", e)
        return False

def getBaseModuleName(modules):
    lowest_base_address = -1
    for module in modules:
        if lowest_base_address == -1 or module.lpBaseOfDll < lowest_base_address:
            lowest_base_address = module.lpBaseOfDll
            module
            return module

def AOB_Scan(process_handle, module_name, signature):
    try:
        module = pymem.process.module_from_name(process_handle, module_name)
        found_address = pymem.pattern.pattern_scan_module(process_handle, module, signature)
        if found_address:
            return found_address
        else:
            print("AOB signature not found.")
 
    except Exception as e:
        print(f"An error occurred during module loading or AOB scan: {e}")