import logging
import os
import json
import pycont.controller as pc

HERE = os.path.dirname(__file__)

logging.basicConfig(level=logging.INFO)

with open(os.path.join(HERE, "multipump_test.json")) as file:
    pump_config = json.load(file)

p1_config = pump_config["pump1"]
p2_config = pump_config["pump2"]

pump1IO = pc.PumpIO.from_config(p1_config['io'])
pump2IO = pc.PumpIO.from_config(p2_config['io'])
pump1 = pc.C3000Controller.from_config(pump1IO, 'pump1', p1_config['default'])
pump2 = pc.C3000Controller.from_config(pump2IO, 'pump2', p2_config['default'])
pump1.smart_initialize()
pump1.wait_until_idle()
pump2.smart_initialize()
pump2.wait_until_idle()
pc.transfer_between(pump1, '1', '6', pump2, '1', '2', 10)