from ble.role import BleRole
from ble.stack import BleStack
from ble.optionparser import BleParsedArgs

class BleAdvertiser(BleRole):
    def __init__(self, connection, params, name=None):
        super().__init__(connection, params)
        self._name = name
        # self._name = name.encode("utf-8").hex()

    def _get_name(self):
        # lname = [ 0x09, 0x09]
        # lname.extend(BleParsedArgs.toHexArray(self._name))
        # return lname
        return self._name

    def _set_name(self, name):
        self._name = name

    def start(self):
        self.stop()

        """ Build main ad packet"""
        ibeacon_adv = [ 0x02, 0x01, 0x06, 0x1a, 0xff, 0x4c, 0x00, 0x02, 0x15,
                        0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
                        self.params.major & 0xFF, self.params.major >> 8,
                        self.params.minor & 0xFF, self.params.minor >> 8,
                        0xC6 ]
                        
        """ Set UUID specifically"""
        ibeacon_adv[9:25] = self.params.uuid[0:16]

        """ Set advertisement (min/max interval + all three ad channels)"""
        BleStack.ble_cmd_gap_set_adv_parameters(self.serial, int(self.params.adv_min * 0.625), int(self.params.adv_max * 0.625), 7)
        response = self.serial.read(6) # 6-byte response
        #for b in response: print '%02X' % ord(b),
        
        """ Set beacon data (advertisement packet)"""
        BleStack.ble_cmd_gap_set_adv_data(self.serial, 0, ibeacon_adv)
        response = self.serial.read(6) # 6-byte response
        #for b in response: print '%02X' % ord(b),
        
        """ Set local name (scan response packet)"""
        # BleStack.ble_cmd_gap_set_adv_data(self.serial, 1, [ 0x09, 0x09, 0x50, 0x69, 0x42, 0x65, 0x61, 0x63, 0x6f, 0x6e ])
        BleStack.ble_cmd_gap_set_adv_data(self.serial, 1, [0x09, 0x09, 0x4d, 0x4f, 0x42, 0x2d, 0x31, 0x34, 0x34, 0x33])
        response = self.serial.read(6) # 6-byte response
        #for b in response: print '%02X' % ord(b),

        """ Start advertising as non-connectable with userdata and enhanced broadcasting"""
        print ("Entering advertisement mode...")
        BleStack.ble_cmd_gap_set_mode(self.serial, 0x84, 0x03)
        response = self.serial.read(6) # 6-byte response
        #for b in response: print '%02X' % ord(b),

    def stop(self):
        """Flush the serial buffers"""
        #print ("Flushing serial I/O buffers...")
        self.serial.flushInput()
        self.serial.flushOutput()

        """ Disconnect if we are connected already"""
        #print ("Disconnecting if connected...")
        BleStack.ble_cmd_connection_disconnect(self.serial, 0)
        response = self.serial.read(7) # 7-byte response
        #for b in response: print ('%02X' % ord(b))

        """ Stop advertising if we are advertising already """
        #print ("Exiting advertising mode if advertising...")
        BleStack.ble_cmd_gap_set_mode(self.serial, 0, 0)
        response = self.serial.read(6) # 6-byte response
        #for b in response: print '%02X' % ord(b),

        """ Stop scanning if we are scanning already"""
        #print ("Exiting scanning mode if scanning...")
        BleStack.ble_cmd_gap_end_procedure(self.serial)
        response = self.serial.read(6) # 6-byte response
        #for b in response: print ('%02X' % ord(b))
    name = property(_get_name, _set_name)


