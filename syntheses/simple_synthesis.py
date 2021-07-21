# Allows you to set delays
import time

# The pycont library is used to communicate with the pumps
import pycont.controller
import logging


# Set up our port constants, these indicate which port (starting from the left) that the reagents
# are connected to
WATER = '1'
ACETIC_ANHYDRIDE = '2'
SULPHURIC_ACID = '3'
WASTE = '4'
REACTOR = '6'

# start the logger
logging.basicConfig(level=logging.INFO)

# The JSON file contains the settings for the pumps. Don't forget to update the port!!
SETUP_CONFIG_FILE = "./simple_synthesis.json"

# Start up the controller
controller = pycont.controller.MultiPumpController.from_configfile(SETUP_CONFIG_FILE)
controller.smart_initialize()

# command to move 5ml water to reactor
controller.pumps["pump1"].transfer(5.0, from_valve=WATER, to_valve=REACTOR)

# delays the program by 10 seconds
time.sleep(10)

# command to move 2.5ml acetic anhydride to waste
controller.pumps["pump1"].transfer(2.5, from_valve=ACETIC_ANHYDRIDE, to_valve=WASTE)
