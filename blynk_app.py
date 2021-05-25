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
VIRTUAL_PIN_MAP = [[0, 2], # Speed
                   [1, 3], # Freq
                   [1, 4], # Current
                   [1, 5], # Torque
                   [1, 6], # Power
                   [1, 12], # Ext ref 2
                   [1, 16], # Appl blk output
                   [2, 19],] # AI2

@timer.register(interval=4, run_once=False)
def write_to_virtual_pins():
    group = 1
    for vpin_num, idx in VIRTUAL_PIN_MAP:
        resultRaw, val = fInv.getRegisterFormat(group=group, idx=idx)
        if not resultRaw.isError():
            blynk.virtual_write(vpin_num, val)
            logger.debug(f"{group:02}{idx:02}: {val}")
        else:
            logger.error(f"Error reading register {group:02}{idx:02} \'{result}\'")


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

    logger.setLevel(logging.DEBUG)
    rootLogger.setLevel(logging.INFO)

    while True:
        blynk.run()
        timer.run()
