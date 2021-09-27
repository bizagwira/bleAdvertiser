import sys, optparse, time, datetime, re
from .optionformatter import OptionFormatter


class BleParsedArgs:
    def __init__(self, **entries):
        self.__dict__.update(entries)

    @staticmethod
    def toHexArray(hexstring):
        return [int(hexstring[i:i+2], 16) for i in range(0, len(hexstring), 2)]

class BleOptionParser(object):
    def __init__(self) -> None:
        """Generate BLE's command line parser.
        """
        # process script arguments
        self._parser = OptionFormatter(description='Bluetooth Smart iBeacon script for Bluegiga BLED112 v2014-09-24', epilog=
            """
            Examples:

                main.py

            \tDefault options (AirLocate UUID, 1/1 major/minor, 100ms interval)

                main.py -p /dev/ttyUSB0 -s -i 1000

            \tUse ttyUSB0, display scan requests, 1 second interval

                main.py -u f1b41cde-dbf5-4acf-8679-ecb8b4dca700 -j 5 -n 2

            \tUse custom UUID, major value of 5, minor value of 2

            """
        )
        # Add generic command line options to the parser
        self._add_default_options()

    def _add_default_options(self) -> None:
        # set all defaults for options
        self._parser.set_defaults(port="/dev/ttyACM0", baud=115200, interval=100, uuid="", major="0001", minor="0001", quiet=False, scanreq=False, duration=60, period=300)

        # create serial port options argument group
        serial_option_group = optparse.OptionGroup(self._parser, "Serial Port Options")
        serial_option_group.add_option('--port', '-p', type="string", help="Serial port device name (default /dev/ttyACM0)", metavar="PORT")
        serial_option_group.add_option('--baud', '-b', type="int", help="Serial port baud rate (default 115200)", metavar="BAUD")
        self._parser.add_option_group(serial_option_group)

        # create iBeacon options argument group
        ibeacon_option_group = optparse.OptionGroup(self._parser, "iBeacon Options")
        ibeacon_option_group.add_option('--uuid', '-u', type="string", help="iBeacon UUID (default AirLocate)", metavar="UUID")
        ibeacon_option_group.add_option('--major', '-j', type="string", help="iBeacon Major (default 0001)", metavar="MAJOR")
        ibeacon_option_group.add_option('--minor', '-n', type="string", help="iBeacon Minor (default 0001)", metavar="MINOR")
        ibeacon_option_group.add_option('--interval', '-i', type="int", help="Advertisement interval in ms (default 100, min 30, max 10230)", metavar="INTERVAL")
        ibeacon_option_group.add_option('--end', '-e', action="store_true", help="End beaconing advertisements", metavar="STOP")
        self._parser.add_option_group(ibeacon_option_group)

        # create output options argument group
        output_option_group = optparse.OptionGroup(self._parser, "Output Options")
        output_option_group.add_option('--scanreq', '-s', action="store_true", help="Display scan requests (Bluegiga enhanced broadcasting)", metavar="SCANREQ")
        output_option_group.add_option('--quiet', '-q', action="store_true", help="Quiet mode (suppress initial parameter display)")
        self._parser.add_option_group(output_option_group)

        # create duty cycle options argument group
        duty_cycle_option_group = optparse.OptionGroup(self._parser, "Duty cycle Options")
        duty_cycle_option_group.add_option('--duration', '-d', type="int", help="Advertisement activity duration in s (default 15 seconds)", metavar="INTERVAL")
        duty_cycle_option_group.add_option('--period', '-t', type="int", help="Advertisement activitionperiod in minute (default 300 seconds)", metavar="INTERVAL")
        self._parser.add_option_group(duty_cycle_option_group)

        
    def parse(self):
        """
            Parses all of the arguments.
        """
        options, arguments =self._parser.parse_args()
        args_option_dict = dict()

        args_option_dict["port"] = options.port
        args_option_dict["baudrate"] = options.baud
        args_option_dict["interval"] = options.interval
        args_option_dict["scanreq"] = options.scanreq
        args_option_dict["duration"] = options.duration
        args_option_dict["period"] = options.period

        # validate UUID if specified
        if len(options.uuid):
            if re.search('[^a-fA-F0-9:\\-]', options.uuid):
                self._parser.print_help()
                print("\n================================================================")
                print("Invalid UUID characters, must be 16 bytes in 0-padded hex form:")
                print("\t-u 0123456789abcdef0123456789abcdef")
                print("================================================================")
                exit(1)
            uuid_hex_string = options.uuid.replace(":", "").replace("-", "").upper()
            if len(uuid_hex_string) != 32:
                self._parser.print_help()
                print("\n================================================================")
                print("Invalid UUID length, must be 16 bytes in 0-padded hex form:")
                print("\t-u 0123456789abcdef0123456789abcdef")
                print("================================================================")
                exit(1)
            args_option_dict["uuid"] = BleParsedArgs.toHexArray(uuid_hex_string)

        # validate major value if specified
        if len(options.major):
            if re.search('[^a-fA-F0-9:\\-]', options.major):
                self._parser.print_help()
                print("\n================================================================")
                print("Invalid major characters, must be 2 bytes in 0-padded hex form:")
                print("\t-j 01cf")
                print("================================================================")
                exit(1)
            major =options.major.replace(":", "").replace("-", "").upper()
            if len(major) != 4:
                self._parser.print_help()
                print("\n================================================================")
                print("Invalid major length, must be 2 bytes in 0-padded hex form:")
                print("\t-j 01cf")
                print("================================================================")
                exit(1)
            args_option_dict["major"] = int(major[0:4], 16)
                
        # validate minor value if specified
        if len(options.minor):
            if re.search('[^a-fA-F0-9:\\-]', options.minor):
                self._parser.print_help()
                print("\n================================================================")
                print("Invalid minor characters, must be 2 bytes in 0-padded hex form:")
                print("\t-n 01cf")
                print("================================================================")
                exit(1)
            minor = options.minor.replace(":", "").replace("-", "").upper()
            if len(minor) != 4:
                self._parser.print_help()
                print("\n================================================================")
                print("Invalid minor length, must be 2 bytes in 0-padded hex form:")
                print("\t-n 01cf")
                print("================================================================")
                exit(1)
            args_option_dict["minor"] = int(minor[0:4], 16)
            
        # validate interval
        if options.interval < 30 or options.interval > 10230:
            self._parser.print_help()
            print("\n================================================================")
            print("Invalid advertisement interval, must be between 30 and 10230")
            print("================================================================")
            exit(1)
        else:
            adv_min = options.interval - 10
            adv_max = adv_min + 20
            args_option_dict["adv_min"] = options.interval - 10
            args_option_dict["adv_max"] = adv_min + 20

        args_option_dict["quiet"] = False if not(options.quiet) else True

        # Return the parsed parameters in BleParsedArgs object
        return BleParsedArgs(**args_option_dict)

        # display  parameter summary, if not in quiet mode
        if not(options.quiet):
            print("================================================================")
            print("BLED112 iBeacon for Python v%s" % __version__)
            print("================================================================")
            print("Serial port:\t%s" % options.port)
            print("Baud rate:\t%s" % options.baud)
            print("Beacon UUID:\t%s" % ''.join(['%02X' % b for b in uuid]))
            print("Beacon Major:\t%04X" % major)
            print("Beacon Minor:\t%04X" % minor)
            print("Adv. interval:\t%d ms" % options.interval)
            print("Scan requests:\t%s" % ['Disabled', 'Enabled'][options.scanreq])
            print("----------------------------------------------------------------")



