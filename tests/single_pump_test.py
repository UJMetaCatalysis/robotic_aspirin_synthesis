import time

import logging

import pycont.controller

logging.basicConfig(level=logging.INFO)

SETUP_CONFIG_FILE = "./single_pump_test.json"

controller = pycont.controller.MultiPumpController.from_configfile(SETUP_CONFIG_FILE)

controller.smart_initialize()

response = input("Next?")

controller.pumps['pump1'].go_to_volume(0.5, wait=True)


while response != "q":
    response = input("command?")
    if response in pycont.controller.VALVE_6WAY_LIST:
        controller.pumps['pump1'].set_valve_position(response)
    elif response == 'vol':
        response = input("where to?")
        try:
            response = int(response)
            controller.pumps['pump1'].go_to_volume(response)
        except ValueError:
            pass
