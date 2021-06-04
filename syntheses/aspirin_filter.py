import time
from progress.bar import Bar

import logging

import pycont.controller

WATER = '1'
ACETIC_ANHYDRIDE = '2'
SULPHURIC_ACID = '3'
FILTER_TOP = '4'
FILTER_BOT = '5'
REACTOR = '6'


def validate_input(input_query, int_val=False):
    answer = input(input_query)
    try:
        if int_val:
            answer = int(answer)
        else:
            answer = float(answer)
    except ValueError:
        print("Please enter a number")
        validate_input(input_query, int_val)
    if answer > 0:
        return answer
    else:
        print("Please enter a number greater than 0")
        validate_input(input_query)


default_parameters = [5.0, 900, 10.0]
cool_time = 900
parameters = []

logging.basicConfig(level=logging.INFO)

SETUP_CONFIG_FILE = "./aspirin_filter.json"

controller = pycont.controller.MultiPumpController.from_configfile(SETUP_CONFIG_FILE)

controller.smart_initialize()
last_increment = 0

while True:
    print(" Enter R to change reaction parameters\n", "Enter S to begin aspirin synthesis\n",
          "Press P to prime the tubing\n",
          "Enter F to flush port 1 with acetic anhydride\n",
          "Enter Q to quit\n")
    response = input()
    response = response.capitalize()
    if response == "S":
        if not parameters:
            parameters = default_parameters
        acetic = parameters[0]
        heat_time = parameters[1]
        water = parameters[2]
        acetic_first = acetic - 0.5

        print(f"Transferring 4ml of acetic anhyrdride to reactor")
        controller.pumps["pump1"].transfer(acetic_first, from_valve=ACETIC_ANHYDRIDE, to_valve=REACTOR)

        print("Transferring 0.1ml of sulphuric acid to reactor")
        controller.pumps["pump1"].transfer(0.1, from_valve=SULPHURIC_ACID, to_valve=REACTOR)

        print("Transferring 1ml of acetic anhydride to reactor")
        controller.pumps["pump1"].transfer(0.5, from_valve=ACETIC_ANHYDRIDE, to_valve=REACTOR)
        # Flush out dead volume of acetic acid (~0.4ml) with water
        controller.pumps["pump1"].transfer(0.3, from_valve=WATER, to_valve=REACTOR)

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
        controller.pumps["pump1"].transfer(0.5, from_valve=WATER, to_valve=REACTOR)

        print("Priming filter unit with water")
        controller.pumps["pump1"].transfer(4.0, from_valve=WATER, to_valve=FILTER_BOT)

        remaining_water = water - 0.5

        print(f"Transferring {remaining_water}ml of water to reactor")
        controller.pumps['pump1'].transfer(remaining_water, from_valve=WATER, to_valve=REACTOR)

        total_volume = acetic_first + 0.1 + 0.5 + remaining_water + 5.0

        print("Transferring contents of flask to filter unit")
        controller.pumps["pump1"].transfer(total_volume, from_valve=REACTOR, to_valve=FILTER_TOP)

        print("Flushing filter line with 1ml of water")
        controller.pumps["pump1"].transfer(1.0, from_valve=WATER, to_valve=FILTER_TOP)

        print("Flushing filter line with 1ml of water")
        controller.pumps["pump1"].transfer(1.0, from_valve=WATER, to_valve=FILTER_TOP)

        start_time = time.time()
        input("Press any key after crystallisation occurs")
        finish_time = time.time()
        print(f"The crystallisation took {start_time - finish_time} seconds")

        input("Place the reactor line (port 1) into the waste container and press any key")

        print("Emptying filter unit")
        controller.pumps['pump1'].transfer(total_volume + 5, from_valve=FILTER_BOT, to_valve=REACTOR)

        # print("Cooling for 10 min")
        # last_increment = 0
        # start_time = time.time()
        # time_elapsed = time.time() - start_time
        # with Bar("   Cooling", fill="#", suffix="%(percent).1f%%") as bar:
        #     while time_elapsed < cool_time + 2:
        #         if time_elapsed - (last_increment * 6) > 6:
        #             bar.next()
        #             last_increment += 1
        #         time.sleep(0.1)
        #         time_elapsed = time.time() - start_time
        # print("Synthesis complete")

    elif response == "R":
        parameters = []
        acetic_ml = validate_input("How many mL of acetic anhydride?\n")
        parameters.append(acetic_ml)
        heat_time = validate_input("How many minutes should the reaction heat for?\n", int_val=True)
        parameters.append(heat_time*60)
        water_ml = validate_input("How many mL of water?\n")
        parameters.append(water_ml)
    elif response == "P":
        print("The tubing only needs to be primed once.", "Please move the reactor line, ",
              REACTOR, ", to the waste container.")
        response = input("Continue (Y/N)?")
        if response.capitalize() == "Y":
            # Port 1
            print("Priming port" + WATER + "with water")
            controller.pumps["pump1"].transfer(1.5, from_valve=WATER, to_valve=REACTOR)
            # Port 3
            print("Priming port " + SULPHURIC_ACID + " with conc. sulphuric acid")
            controller.pumps["pump1"].transfer(1.5, from_valve=SULPHURIC_ACID, to_valve=REACTOR)
            # Port 5
            print("Priming port " + FILTER_BOT + " with water")
            controller.pumps["pump1"].transfer(1.5, from_valve=WATER, to_valve=REACTOR)
            # Port 2
            print("Priming port " + ACETIC_ANHYDRIDE + " with Acetic anhydride")
            controller.pumps["pump1"].transfer(1.5, from_valve=ACETIC_ANHYDRIDE, to_valve=REACTOR)

    elif response == "F":
        print("Route reactor tube, port " + REACTOR + " into waste container.")
        response = input("press F to continue")
        if response.capitalize() == "F":
            controller.pumps["pump1"].transfer(2.0, from_valve=ACETIC_ANHYDRIDE, to_valve=REACTOR)
    elif response == "Q":
        print("End of program")
        break

