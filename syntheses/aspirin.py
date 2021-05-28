import time
from progress.bar import Bar

import logging

import pycont.controller

logging.basicConfig(level=logging.INFO)

SETUP_CONFIG_FILE = "./aspirin.json"

controller = pycont.controller.MultiPumpController.from_configfile(SETUP_CONFIG_FILE)

controller.smart_initialize()
heat_time = 900  # Heat for 15 min
cool_time = 600  # cool for 10 min
precip_time = 900
last_increment = 0

while True:
    print("Enter S to begin aspirin synthesis",
          "Enter F to flush port 1",
          "Enter Q to quit")
    response = input()
    response.capitalize()
    if response == "S":
        print("Transferring 4ml of acetic anhyrdride to reactor")
        controller.pumps["pump1"].transfer(4.0, from_valve='4', to_valve='1')

        print("Transferring 0.1ml of sulphuric acid to reactor")
        controller.pumps["pump1"].transfer(0.1, from_valve='3', to_valve='1')

        print("Transferring 1ml of acetic anhydride to reactor")
        controller.pumps["pump1"].transfer(0.6, from_valve='4', to_valve='1')
        # Flush out dead volume (~0.4ml) with water
        controller.pumps["pump1"].transfer(0.3, from_valve='5', to_valve='1')

        print("Heating for 15 minutes")
        start_time = time.time()
        time_elapsed = time.time() - start_time
        with Bar('   Heating', fill='#', suffix="%(percent).1f%%") as bar:
            while time_elapsed < heat_time + 2:
                if time_elapsed - (last_increment * 9) > 9:
                    bar.next()
                    last_increment += 1
                time.sleep(0.1)
                time_elapsed = time.time() - start_time

        print("Transferring 0.5ml of water to reactor")
        controller.pumps["pump1"].transfer(0.5, from_valve='5', to_valve='1')

        print("Transferring 10ml of water to reactor")
        controller.pumps['pump1'].transfer(9.5, from_valve='5', to_valve='1')

        print("Place reactor in an ice bath")

        print("Cooling for 10 min")
        last_increment = 0
        start_time = time.time()
        time_elapsed = time.time() - start_time
        with Bar("   Cooling", fill="#", suffix="%(percent).1f%%") as bar:
            while time_elapsed < cool_time + 2:
                if time_elapsed - (last_increment * 6) > 6:
                    bar.next()
                    last_increment += 1
                time.sleep(0.1)
                time_elapsed = time.time() - start_time
        print("Synthesis complete")
    elif response == "F":
        response = input("Route reactor tube (port 1) into waste container, press F to continue")
        if response == "F":
            controller.pumps["pump1"].transfer(2.0, from_valve='4', to_valve='1')
    elif response == "Q":
        print("End of program")
        break

