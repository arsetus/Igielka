aob64 = b"\x55\x41\x56\x41\x57\x48\x8D\xAC.....\x48\x81\xEC....\x48\x8B\x05....\x48\x33\xC4\x48\x89\x85....\x48\x8B\xF9"
aob32 = b"\x55\x41\x56\x41\x57\x48\x8D\xAC.....\x48\x81\xEC....\x48\x8B\x05....\x48\x33\xC4\x48\x89\x85....\x48\x8B\xF9"
my_stats_address = 0#xBABD80
my_x_address = 0x50 #static address
my_y_address = 0x54 #static address
my_z_address = 0x58 #static address
my_hp_offset = 0x710 #offset from localplayer
my_hp_max_offset = 0x718 #offset from localplayer
my_mapX_dest_offset = 0x5B8 #offset from localplayer
my_mapY_dest_offset = 0x5BB #offset from localplayer
my_mp_offset = 0x740 #offset from localplayer
my_mp_max_offset = 0x748 #offset from localplayer
my_rest_offset = 0x768 #offset from localplayer
my_name_offset = 0x250 #offset from localplayers
my_skinID_offset = 0xC4 #offset from localplayer
my_skin_offset = 0x148 #offset from localplayer
my_dir_offset = 0xBC #offset from localplayer

# Target Addresses
attack_address = 0#xBABD88
attack_address_offset = []
target_name_offset = 0x98 #offset from target attack address
target_x_offset = 0x50 #offset from target attack address
target_y_offset = 0x54 #offset from target attack address
target_z_offset = 0x58 #offset from target attack address
target_hp_offset = 0xB8 #offset from target attack address
