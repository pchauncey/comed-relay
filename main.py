#!/usr/bin/env python

import json
from time import sleep
from urllib2 import urlopen
from urllib2 import URLError
import RPi.GPIO as GPIO
import datetime

comed_api = "https://hourlypricing.comed.com/api?type=5minutefeed"
relay_pin = 26
loop_seconds = 60

# limit in cents per kwh, above this level relay is disabled
rate_limit = 2.5


def initialize_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(relay_pin, GPIO.OUT)


def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)


def get_rate():
    rates = json.load(urlopen(comed_api))
    rateset = []
    for i in range(12):
        rateset.append(float(rates[i]['price']))
    return round(mean(rateset),1)


def set_relay(state):
    if state:
        GPIO.output(relay_pin, GPIO.LOW)
    else:
        GPIO.output(relay_pin, GPIO.HIGH)
    return state


def main_loop():
    state = "new"
    while True:
        try:
            current = get_rate()
        except URLError:
            sleep(loop_seconds)
            continue

        timestamp = datetime.datetime.now()
        # rate is high:
        if (current > rate_limit):
            if (state != False):
                print str(timestamp) + ": disabling, rate is " + str(current) + " cents per kWh."
                state = set_relay(False)
        # rate is low:
        else:
            if (state != True):
                print str(timestamp) + ": enabling, rate is " + str(current) + " cents per kWh."
                state = set_relay(True)
        sleep(loop_seconds)

if __name__ == '__main__':
    try:
        initialize_gpio()
        main_loop()
    except KeyboardInterrupt:
        print str(timestamp) + ": Cleaning up."
        GPIO.cleanup()
