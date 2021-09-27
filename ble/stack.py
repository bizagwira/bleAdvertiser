import serial, time, datetime, struct

# define API commands we might use for this script
class BleStack(object):
    @staticmethod
    def ble_cmd_system_reset(p, boot_in_dfu):
        p.write(struct.pack('5B', 0, 1, 0, 0, boot_in_dfu))

    @staticmethod
    def ble_cmd_connection_disconnect(p, connection):
        p.write(struct.pack('5B', 0, 1, 3, 0, connection))
        
    @staticmethod
    def ble_cmd_gap_set_mode(p, discover, connect):
        p.write(struct.pack('6B', 0, 2, 6, 1, discover, connect))
        
    @staticmethod
    def ble_cmd_gap_end_procedure(p):
        p.write(struct.pack('4B', 0, 0, 6, 4))
        
    @staticmethod
    def ble_cmd_gap_set_adv_parameters(p, adv_interval_min, adv_interval_max, adv_channels):
        p.write(struct.pack('<4BHHB', 0, 5, 6, 8, adv_interval_min, adv_interval_max, adv_channels))
        
    @staticmethod
    def ble_cmd_gap_set_adv_data(p, set_scanrsp, adv_data):
        mystr = '<4BBB' + str(len(adv_data)) + 's'
        p.write(struct.pack(mystr.encode('utf8'), 0, 2 + len(adv_data), 6, 9, set_scanrsp, len(adv_data), bytes(adv_data)))