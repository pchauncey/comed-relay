#!/usr/bin/env python

import json
import logging
import requests
import signal
import RPi.GPIO as GPIO
from sys import exit
from time import sleep
from requests.exceptions import HTTPError


def get_config(key):
    with open('config.json', 'r') as file:
        data = json.load(file)
    file.close()
    return data[key]


def initialize_gpio():
    global relay_pin
    relay_pin = get_config("relay_pin")
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(relay_pin, GPIO.OUT)


def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)


def get_rate():
    global comed_api_url
    comed_api_url = get_config("comed_api_url")
    rates = requests.get(comed_api_url)
    rates = rates.json()
    rateset = []
    for i in range(12):
        rateset.append(float(rates[i]['price']))
    return round(mean(rateset), 1)


def set_relay(state):
    if state:
        GPIO.output(relay_pin, GPIO.LOW)
    else:
        GPIO.output(relay_pin, GPIO.HIGH)
    return state


def cleanup(signal, frame):
    logging.warning("shutting down.")
    GPIO.cleanup()
    exit(0)


def main():
    # catch these termination signals:
    signal.signal(signal.SIGTERM, cleanup)
    signal.signal(signal.SIGINT, cleanup)
    # initialization:
    initialize_gpio()
    state = "new"

    while True:
        # allow these to be changes during loop
        rate_limit = get_config("rate_limit")
        loop_seconds = get_config("loop_seconds")
        try:
            current = get_rate()
        except HTTPError as http_error:
            # sleep out a timeout / lookup error:
            print(f'HTTP error occurred: {http_error}')
            sleep(loop_seconds)
            continue

        if current > rate_limit:
            # rate is high:
            if state is not False:
                logging.warning("disabling, rate is " + str(current) + " cents per kWh, and limit is " + str(rate_limit))
                state = set_relay(False)
        else:
            # rate is low:
            if state is not True:
                logging.warning("enabling, rate is " + str(current) + " cents per kWh, and limit is " + str(rate_limit))
                state = set_relay(True)

        sleep(loop_seconds)


if __name__ == '__main__':
    main()
