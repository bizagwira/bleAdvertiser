#!/usr/bin/env python3
# -*- coding: utf-8 -*

import serial, signal, schedule, sys
import time, datetime
import csv
from pathlib import Path

"""
*
* @brief Implementation of the ble dongle services
* @author Honoré BIZAGWIRA
* Contact devios.honore@gmail.com
*
*
"""
__version__ = "2021-09-24"
RESOURCE_DIR="resources"

from ble.optionparser import BleOptionParser
from ble.advertiser import BleAdvertiser


"""
 Example: ./main.py -u 504f4c45-5354-4152-4d4f-422d31343433 -j 2341 -n 1245 -p /dev/ttyUSB0 -d 45 -t 360
"""

def mkdir(dirpath):
    Path(dirpath).mkdir(parents=True, exist_ok=True)

# Gracefully exit without a big exception message if possible
def ctrl_c_handler(signal, frame):
    print ('Goodbye, cruel world!')
    exit(0)

def append_list_as_row(file_name, list_of_elem):
    # Open file in append mode
    with open(file_name, 'a+', newline='') as write_obj:
        # Create a writer object from csv module
        csv_writer = csv.writer(write_obj)
        # Add contents of list as last row in the csv file
        csv_writer.writerow(list_of_elem)

def writeCSV(status="Start", filepath="resources/wakeup.csv"):
    row_contents = [datetime.datetime.now(), status]
    # Append a list as new line to an old csv file
    append_list_as_row(filepath, row_contents)


def writeCSVHeader(filepath="resources/wakeup.csv"):
    with open(filepath, 'w', newline='') as outcsv:
        writer = csv.DictWriter(outcsv, fieldnames = ["Date", "Status"])
        writer.writeheader()

def doTask(bletask):
    bletask.start()
    if not bletask.params.quiet:
        writeCSV("Start")
        print(f"-> [{datetime.datetime.now()}] iBeacon advertisements started")
        time.sleep(bletask.params.duration)
    bletask.stop()
    writeCSV("Stop")
    print(f"<- [{datetime.datetime.now()}] iBeacon advertisements stopped")

def main():
    mkdir(RESOURCE_DIR)
    options = BleOptionParser()
    params = options.parse()
    # display  parameter summary, if not in quiet mode
    if not(params.quiet):
        print("================================================================")
        print("BLED112 iBeacon for Python v%s" % __version__)
        print("================================================================")
        print("Serial port:\t%s" % params.port)
        print("Baud rate:\t%s" % params.baudrate)
        print("Beacon UUID:\t%s" % ''.join(['%02X' % b for b in params.uuid]))
        print("Beacon Major:\t%04X" % params.major)
        print("Beacon Minor:\t%04X" % params.minor)
        print("Adv. interval:\t%d ms" % params.interval)
        print("Adv. duty cycle duration:\t%d s" % params.duration)
        print("Adv. duty cycle period :\t%d s" % params.period)
        print("Scan requests:\t%s" % ['Disabled', 'Enabled'][params.scanreq])
        print("----------------------------------------------------------------")

    """
        Open the serial port on which the dongle is connected
    """
    try:
        writeCSVHeader()
        ser = serial.Serial(port=params.port, baudrate=params.baudrate, timeout=1)
    except serial.SerialException as e:
        print("\n================================================================")
        print("Port error (name='%s', baud='%ld'): %s" % (params.port, params.baudrate, e))
        print("================================================================")
        exit(2)

    # Create the ble advertiser task
    advertiser_task = BleAdvertiser(ser, params)

    schedule.every(params.period).seconds.do(doTask, bletask=advertiser_task)
    doTask(advertiser_task) # Run now
    while True:
        schedule.run_pending()
        time.sleep(1)


signal.signal(signal.SIGINT, ctrl_c_handler)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"{e.args}\nPlease, run \"./main.py -h\" for more options!")