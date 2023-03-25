import blynklib
import blynktimer
import configparser
import acs400
import logging
import sys
import publisher

logger = logging.getLogger(__name__)

config = configparser.ConfigParser()
config.read("blynk_app.ini")


port = config['ACS400']['port']
if config['ACS400']['enable_writes'] == "True":
    enableWrites = True
else:
    enableWrites = False


fInv = acs400.ACS400(port=port, enableWrites=enableWrites)

publisher = publisher.Publisher()
publisher.open(port=22201)

timer = blynktimer.Timer()

# Map virtual pins to registers
#                   Vpin Register Description
VIRTUAL_PIN_MAP = [[[0, 2], "Speed"],
                   [[1, 3], "Freq"],
                   [[2, 4], "Current"],
                   [[3, 5], "Torque"],
                   [[4, 6], "Power"],
                   [[5, 16],"Appl blk output"],
                   [[6, 19],"AI2"],
                   [[7, 28],"Last fault"],
                   [[8, 29],"Previous fault"],
                   [[9, 30],"Oldest fault"],]

VRO1 = 21
VRO2 = 22
VDI1 = 31
VDI2 = 32
VDI3 = 33
VDI4 = 34
VDI5 = 35
VP = 50  # Pressure

# Writable pins
VP_REF = 100  # Pressure reference

# Limits
P_MIN = 0  # [bar] Minimum pressure
P_MAX = 4  # [bar] Maximum pressure

@timer.register(interval=4, run_once=False)
def write_to_virtual_pins():
    group = 1
    dictToPublish = {}
    dictToPublishBlynk2 = {}
    for (vpin_num, idx), desc in VIRTUAL_PIN_MAP:
        resultRaw, val = fInv.getRegisterFormat(group=group, idx=idx)
        if not resultRaw.isError():
            roundedValue = round(val, 3)
            dictToPublish[desc] = roundedValue
            dictToPublishBlynk2[vpin_num] = roundedValue
            logger.debug(f"{group:02}{idx:02}: {val}")
        else:
            logger.error(f"Error reading register {group:02}{idx:02} \'{resultRaw}\'")

    # Relays
    relays = fInv.getRelays()
    if relays:
        logger.debug(f"Relays: {relays}")
        dictToPublish["Relay 1"] = relays[0]
        dictToPublish["Relay 2"] = relays[1]

    # Digital inputs
    digitalInputs = fInv.getDigitalInputs()
    if digitalInputs:
        logger.debug(f"Digital inputs: {digitalInputs}")
        for idx, value in enumerate(digitalInputs):
            dictToPublish[f"Digital Input {idx+1}"] = value

    # Pressure
    pressure = fInv.getActualPressure()
    if pressure:
        logger.debug(f"Pressure: {pressure}")
        pressureRounded = round(pressure, 3)
        dictToPublish['pressure'] = pressureRounded

    # Publish if there is data
    if dictToPublish != {}:
        publisher.send({'acs400':dictToPublish})

    # Special publish for Blynk2
    if dictToPublishBlynk2 != {}:
        publisher.send({'acs400ForBlynk2':dictToPublishBlynk2})
        
if __name__ == "__main__":
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

    if enableWrites:
        logger.warning("Writes are enabled!")

    
        
    while True:
        timer.run()
