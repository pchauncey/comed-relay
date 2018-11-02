#!/usr/bin/env python

import json
from time import sleep
from urllib2 import urlopen
import RPi.GPIO as GPIO

comed_api = "https://hourlypricing.comed.com/api?type=5minutefeed"
relay_pin = 25
loop_seconds = 60

# limit in cents per kwh, above this level relay is disabled
rate_limit = 3.5

def initialize_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(relay_pin, GPIO.OUT)
    GPIO.output(relay_pin, GPIO.HIGH)

def get_rate():
    rates = json.load(urlopen(comed_api))
    # current rate in cents per kwh:
    return float(rates[0]['price'])

def set_relay(state):
    if state == True:
        GPIO.output(relay_pin, GPIO.HIGH)
    else:
        GPIO.output(relay_pin, GPIO.LOW)
    return state

def main_loop():

    state = "new"

    # loop begins
    while True:

        # pull current rate
        current = get_rate()

        # rate is high:
        if (current > rate_limit):

            if (state != False):
                print "disabling, rate is " + str(current) + "cents per kWh."
                state = set_relay(False)

        # rate is low:
        else:

            if (state != True):
                print "enabling, rate is " + str(current) + "cents per kWh."
                state = set_relay(True)

        sleep(loop_seconds)


if __name__ == '__main__':
    try:
        initialize_gpio()
        main_loop()
    except KeyboardInterrupt:
        print "Cleaning up."
        GPIO.cleanup()
