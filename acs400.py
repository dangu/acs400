from pymodbus.client.sync import ModbusSerialClient
import time
import logging
import sys

logger = logging.getLogger(__name__)

REGISTERS = {1: ["Operating data",
                 [[2, 1, "Speed", "rpm"],
                  [3, 0.1, "Output Freq", "Hz"],
                  [4, 0.1, "Current", "A"],
                  [5, 0.1, "Torque", "%"],
                  [6, 0.1, "Power", "kW"],
                  [7, 0.1, "DC Bus Voltage", "V"],
                  [9, 0.1, "Output Voltage", "V"],
                  [10, 0.1, "ACS400 Temp", "degC"],
                  [11, 0.1, "External Ref 1", "Hz"],
                  [12, 0.1, "External Ref 2", "%"],
                  [13, 1, "Ctrl Location", "-"],
                  [14, 1, "Run Time", "h"],
                  [15, 1, "kWh Counter", "kWh"],
                  [16, 0.1, "Appl Blk Output", "%"],
                  [17, 1, "DI1-DI4 Status", "-"],
                  [18, 0.1, "AI1", "%"],
                  [19, 0.1, "AI2", "%"],
                  [21, 1, "DI5 & Relays", "-"],
                  [22, 0.1, "AO", "mA"],
                  [24, 0.1, "Actual Value 1", "%"],
                  [25, 0.1, "Actual Value 2", "%"],
                  [26, 0.1, "Control Dev", "%"],
                  [27, 0.1, "PID Act Value", "%"],
                  [28, 1, "Last Fault", "-"],
                  [29, 1, "Previous Fault", "-"],
                  [30, 1, "Oldest Fault", "-"],
                  [31, 1, "Ser Link Data 1", "-"],
                  [32, 1, "Ser Link Data 2", "-"],
                  [33, 1, "Ser Link Data 3", "-"],
                  [34, 1, "Process Var 1", "-"],
                  [35, 1, "Process Var 2", "-"],
                  [36, 0.01, "Run Time", "kh"],
                  [37, 1, "MWh Counter", "MWh"], ]]}


class ACS400:
    def __init__(self, port):
        self.client = ModbusSerialClient(method='rtu',
                                         port=port,
                                         timeout=1,
                                         baudrate=9600)

    def printNPump(self):
        nPump = self.getNPump()
        if not nPump.isError():
            print(f"{nPump.registers[0]}")
        else:
            print(f"{nPump}")

    def getNPump(self):
        nPump = self.client.read_holding_registers(102-1, count=1, unit=1)
        return nPump

    def getRegister(self,  reg):
        """Get register"""
        return self.client.read_holding_registers(reg-1, count=1, unit=1)

    def dumpGroup(self,  group):
        """Dump specific group of parameters"""
        if group in REGISTERS:
            groupData = REGISTERS[group]
            groupName = groupData[0]
            registers = groupData[1]
            for idx, fact, name, unit in registers:
                reg = group*100 + idx
                result = self.getRegister(reg)
                if not result.isError():
                    value = result.registers[0]*fact
                    logger.info(f"{group:02}{idx:02}: {value} {unit} ({name})")
                else:
                    logger.error(f"Could not read register {group}{idx}")
        else:
            logger.error(f"Group '{group}' not found")
    
    def dumpAll(self):
        """Dump all parameters"""
        groups = [99, 1, 10, 11, 12, 13, 14, 15, 16, 20]
        groups += [21, 22, 25, 26, 30, 31, 32, 33, 34, 40, 41]
        groups += [50, 51, 52, 81]
        for group in groups:
            regs = [group*100+reg for reg in range(1, 100)]
            for reg in regs:
                result = self.getRegister(reg)
                if not result.isError():
                    logger.info(f"{reg:04} {result.registers[0]:}")

if __name__ =="__main__":
    logFormatter = logging.Formatter("%(asctime)s [%(levelname)-7s][%(name)s] %(message)s")
    rootLogger = logging.getLogger()

    fileHandler = logging.FileHandler("acs400.log")
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)
    
    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)
    
    rootLogger.setLevel(logging.INFO)
    acs400 = ACS400(port="/dev/ttyUSB1")
    acs400.dumpGroup(1)
    # for i in range(5):
    #     acs400.printNPump()
    #     time.sleep(1)
