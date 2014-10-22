#!/usr/bin/python3

import RPi.GPIO as gpio
import atsci
import sys
import time

STABILIZE_MINS = 2

def calibrate(cmd, cond):
    print("place sensor in {} solution".format(cond))
    input("press enter when ready")

    print("entering continuous mode for {} minute(s)".format(STABILIZE_MINS))
    sensor.write("C,1")

    start = time.time()

    while True:
        elapsed = time.time() - start

        if elapsed > STABILIZE_MINS * 60:
            break

        print("{:4}s: {}".format(int(elapsed), sensor.read().decode("ascii")))
        time.sleep(1)

    print("calibrating for {}...".format(cond), end="")
    sensor.write("{},{}".format(cmd, cond))
    print("done")

    sensor.write("C,0")

try:
    probe = sys.argv[1]
    low = sys.argv[2]
    high = sys.argv[3]
except IndexError:
    print("Usage {} PROBE-K-VALUE LOW-SOLUTION HIGH-SOLUTION".format(
        sys.argv[0]))
    sys.exit(1)

with atsci.AtSciSensor() as sensor:
    print("letting temperature stabilize for {} minute(s)".format(
        STABILIZE_MINS))
    sensor.switch(atsci.TEMP)
    sensor.write("C")

    start = time.time()

    while True:
        elapsed = time.time() - start

        if elapsed > STABILIZE_MINS * 60:
            break;

        print("{:3}s: {}C".format(int(elapsed), float(sensor.read())))
        time.sleep(1)

    sensor.write("E")
    sensor.write("R")
    temp = float(sensor.read())

    # Leave continuous mode and clear calibration.
    sensor.switch(atsci.COND)
    sensor.write("C,0")
    sensor.write("Cal,clear");

    print("using probe {}".format(probe))
    sensor.write("K,{}".format(probe))

    print("adjusting temperature to {}°C".format(temp))
    sensor.write("T,{:.3}".format(temp))

    # calibrate for dry sensor.
    print("make sure the sensor is dry")
    input("press enter when ready")
    sensor.write("Cal,dry")

    calibrate("Cal,low", low)
    calibrate("Cal,high", high)
