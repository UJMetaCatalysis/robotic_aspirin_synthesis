import time
from progress.bar import Bar

import logging

import pycont.controller

WATER = '1'
ACETIC_ANHYDRIDE = '2'
SULPHURIC_ACID = '3'
WASTE = '4'
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

SETUP_CONFIG_FILE = "./aspirin.json"

controller = pycont.controller.MultiPumpController.from_configfile(SETUP_CONFIG_FILE)

controller.smart_initialize()
last_increment = 0

while True:
    print(" Enter R to change reaction parameters\n", "Enter S to begin aspirin synthesis\n",
          "Press P to prime the tubing\n",
          "Enter F to flush port 1 with acetic anhydride\n",
          "Enter Z to zero the pump\n",
          "Enter Q to quit\n")
    response = input()
    response = response.capitalize()
    if response == "S":
        print("Before beginning, please check the connections, port 1 is the left-most port on the valve:\n", "Port 1: Water\n", "Port 2: Acetic anhydride\n", "Port 3: Conc. sulphuric acid\n", "Port 4: Waste bottle\n", "Port 6: Reactor\n")
        print("Please make sure the reagent bottles are filled and the tubing can reach the reagents. Make sure that 5g of salicyclic acid is present in the reactor. \n")
        print("Turn on the stirrer hotplate. Set temperature to 70°C and stirring to 500 rpm")
        cont = input("Continue? (Y/N")
        if cont.upper() == "Y":
            pass
        elif cont.upper() == "N":
            continue
        if not parameters:
            parameters = default_parameters
        acetic = parameters[0]
        heat_time = parameters[1]
        water = parameters[2]
        acetic_first = acetic - 0.5

        print(f"Transferring {acetic_first}ml of acetic anhyrdride to reactor")
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

        print("Transferring 10ml of water to reactor")
        controller.pumps['pump1'].transfer(water - 0.5, from_valve=WATER, to_valve=REACTOR)

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
    elif response == "R":
        parameters = []
        acetic_ml = validate_input("How many mL of acetic anhydride?\n")
        parameters.append(acetic_ml)
        heat_time = validate_input("How many minutes should the reaction heat for?\n", int_val=True)
        parameters.append(heat_time*60)
        water_ml = validate_input("How many mL of water?\n")
        parameters.append(water_ml)
    elif response == "P":
        response = input("The tubing only needs to be primed once. Continue (Y/N)?")
        if response.capitalize() == "Y":
            print("Priming port " + SULPHURIC_ACID + " with conc. sulphuric acid")
            controller.pumps["pump1"].transfer(1.5, from_valve=SULPHURIC_ACID, to_valve=WASTE)
            print("Priming port " + WATER + " with water")
            controller.pumps["pump1"].transfer(1.5, from_valve=WATER, to_valve=WASTE)
            print("Priming port " + ACETIC_ANHYDRIDE + " with acetic anhydride")
            controller.pumps["pump1"].transfer(1.5, from_valve=ACETIC_ANHYDRIDE, to_valve=REACTOR)
    elif response == "F":
        print("Route reactor tube, port " + REACTOR + " into waste container.")
        response = input("Press F to continue")
        if response == "F":
            controller.pumps["pump1"].transfer(2.0, from_valve=ACETIC_ANHYDRIDE, to_valve=REACTOR)
    elif response == "Z":
        print("Zeroing the pump")
        controller.pumps['pump1'].go_to_volume(0)
    elif response == "Q":
        print("End of program")
        break
