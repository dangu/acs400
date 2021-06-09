import blynklib
import blynktimer
import configparser
import acs400
import logging
import sys

logger = logging.getLogger(__name__)

config = configparser.ConfigParser()
config.read("blynk_app.ini")

BLYNK_AUTH = config['AUTH']['token'].strip('\"')
blynk = blynklib.Blynk(BLYNK_AUTH)

port = config['ACS400']['port']

fInv = acs400.ACS400(port=port)

timer = blynktimer.Timer()

# Map virtual pins to registers
VIRTUAL_PIN_MAP = [[0, 2],  # Speed
                   [1, 3],  # Freq
                   [2, 4],  # Current
                   [3, 5],  # Torque
                   [4, 6],  # Power
                   [5, 16],  # Appl blk output
                   [6, 19],  # AI2
                   [7, 28],  # Last fault
                   [8, 29],  # Previous fault
                   [9, 30],] # Oldest fault

VRO1 = 21
VRO2 = 22
VDI1 = 31
VDI2 = 32
VDI3 = 33
VDI4 = 34
VDI5 = 35

@timer.register(interval=4, run_once=False)
def write_to_virtual_pins():
    group = 1
    for vpin_num, idx in VIRTUAL_PIN_MAP:
        resultRaw, val = fInv.getRegisterFormat(group=group, idx=idx)
        if not resultRaw.isError():
            blynk.virtual_write(vpin_num, round(val,3))
            logger.debug(f"{group:02}{idx:02}: {val}")
        else:
            logger.error(f"Error reading register {group:02}{idx:02} \'{resultRaw}\'")

    # Relays
    relays = fInv.getRelays()
    if relays:
        logger.debug(f"Relays: {relays}")
        blynk.virtual_write(VRO1, relays[0]*255)
        blynk.virtual_write(VRO2, relays[1]*255)

    # Digital inputs
    digitalInputs = fInv.getDigitalInputs()
    if digitalInputs:
        logger.debug(f"Digital inputs: {digitalInputs}")
        blynk.virtual_write(VDI1, digitalInputs[0]*255)
        blynk.virtual_write(VDI2, digitalInputs[1]*255)
        blynk.virtual_write(VDI3, digitalInputs[2]*255)
        blynk.virtual_write(VDI4, digitalInputs[3]*255)
        blynk.virtual_write(VDI5, digitalInputs[4]*255)
            

if __name__ =="__main__":
    logFormatter = logging.Formatter("%(asctime)s [%(levelname)-7s][%(name)s] %(message)s")
    rootLogger = logging.getLogger()

    fileHandler = logging.FileHandler("blynk_app.log")
    fileHandler.setFormatter(logFormatter)
    fileHandler.setLevel(logging.WARNING)
    rootLogger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setFormatter(logFormatter)
    consoleHandler.setLevel(logging.DEBUG)
    rootLogger.addHandler(consoleHandler)

    logger.setLevel(logging.INFO)
    rootLogger.setLevel(logging.INFO)

    while True:
        blynk.run()
        timer.run()
