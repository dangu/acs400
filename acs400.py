from pymodbus.client.sync import ModbusSerialClient
# import time
import logging
import sys

logger = logging.getLogger(__name__)

# Register table: [index, resolution, name, unit]
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
                  [37, 1, "MWh Counter", "MWh"], ]],
             40: ["PID Control",
                  [[20, 0.1, "Internal setpoint", "%"], ]]}

REGISTER_RELAY = 121  # Relay register
REGISTER_DI1_4 = 117
REGISTER_DI5 = 121

# Pressure sensor 4-20 mA data
SENSOR_PRESSURE_MAX = 10   # [bar] Sensor max pressure
SENSOR_SIGNAL_MIN = 20    # [%] Sensor min current
SENSOR_SIGNAL_MAX = 100   # [%] Sensor max current

P_REF_MIN = 0             # [bar] Minimum reference pressure
P_REF_MAX = 4             # [bar] Maximum reference pressure


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

    def getActualPressure(self):
        """Get actual pressure value by using the
        4-20 mA current output of the pressure sensor"""
        pressure = None
        result, value = self.getRegisterFormat(group=1, idx=19)
        if not result.isError():
            k = SENSOR_PRESSURE_MAX/(SENSOR_SIGNAL_MAX-SENSOR_SIGNAL_MIN)
            signal = value-SENSOR_SIGNAL_MIN
            pressure = signal*k
        return pressure

    def setReferencePressure(self, pressureRef):
        """Set reference pressure"""
        if P_REF_MIN <= pressureRef <= P_REF_MAX:
            k = (SENSOR_SIGNAL_MAX-SENSOR_SIGNAL_MIN)/SENSOR_PRESSURE_MAX
            signal = pressureRef*k + SENSOR_SIGNAL_MIN
            registerValue = round(signal/0.1)
            logger.info(f"Would set {registerValue}")

    def getRegisterFormat(self, group, idx):
        """Get register formatted"""
        value = None
        result = None
        if group in REGISTERS:
            groupData = REGISTERS[group]
            registers = groupData[1]
            register = [reg for reg in registers if reg[0] == idx]

            if register:
                idx, fact, name, unit = register[0]
                reg = group*100 + idx
                result = self.getRegister(reg)
                if not result.isError():
                    value = result.registers[0]*fact
                else:
                    logger.error(f"Could not read register {group}{idx}")
            else:
                logger.error(f"Register {group:02}{idx:02} not found")
        else:
            logger.error(f"Register {group:02}{idx:02} not found")
        return result, value

    def getRelays(self):
        """Get status of relays"""
        relays = None
        result = self.getRegister(REGISTER_RELAY)
        if not result.isError():
            raw = result.registers[0]
            relay1Status = raw & 0x01
            relay2Status = (raw & 0x02) >> 1
            relays = [relay1Status, relay2Status]
        else:
            logger.error(f"Could not read relays ({result})")
        return relays

    def getDigitalInputs(self):
        """Get status of DI1-DI5"""
        resultDI1_4 = self.getRegister(REGISTER_DI1_4)
        resultDI5 = self.getRegister(REGISTER_DI5)

        digitalInputs = None
        if not (resultDI1_4.isError() or resultDI5.isError()):
            val1_4 = resultDI1_4.registers[0]
            val5 = resultDI5.registers[0]
            DI1 = (val1_4 >> 0) & 0x01
            DI2 = (val1_4 >> 1) & 0x01
            DI3 = (val1_4 >> 2) & 0x01
            DI4 = (val1_4 >> 3) & 0x01
            DI5 = (val5 >> 3) & 0x01
            digitalInputs = [DI1, DI2, DI3, DI4, DI5]
        else:
            logger.error(f"Could not read digital inputs {resultDI1_4} {resultDI5}")
        return digitalInputs

    def dumpGroup(self,  group):
        """Dump specific group of parameters"""
        if group in REGISTERS:
            groupData = REGISTERS[group]
            # groupName = groupData[0]
            registers = groupData[1]
            for idx in registers:
                result, value = self.getRegisterFormat(group, idx)
                if not result.isError():
                    logger.info(f"{group:02}{idx:02} {value}")
                else:
                    logger.error(f"Could not read register {group:02}{idx:02}")
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

    def getPFCStatus(self):
        """Get status of PFC (Pump and Fan Control) values
Important values PID
------------------
4006 Actual Val Sel: PID controller (actual) signal selection
1: ACT1
4007 ACT1 input selection
2: (AI2)
4009 ACT1 MINIMUM
Analogue minimum value
3010 ACT1 MAXIMUM
Analogue maximum
4019 Set Point Selection: Sets the reference signal
1: Internal. Process referencs is a constant value set with 4020
44.0

Important values PFC
-----------------------
8109 Start freq 1: When exceeding Start freq + 1 Hz the start delay starts
counting
8109: 53.0
8112 Low freq 1: When below low freq -1 stop delay starts
8112: 5.0
8117 Relay outputs. RO1 and RO2 are used if 8117==1
8118 [0.1h] Autochange interval
8120 Interlocks

"""
        interlocks = self.getRegister(8120)
        numOfExtraMotors = self.getRegister(8117)
        if interlocks == 4 and numOfExtraMotors == 1:
            # DI4 is Motor 1
            # DI5 is Motor 2
            digitalInputs = self.getDigitalInputs()
            
            
                    
if __name__ =="__main__":
    logFormatter = logging.Formatter("%(asctime)s [%(levelname)-7s][%(name)s] %(message)s")
    rootLogger = logging.getLogger()

    fileHandler = logging.FileHandler("acs400.log")
    fileHandler.setFormatter(logFormatter)
    fileHandler.setLevel(logging.WARNING)
    rootLogger.addHandler(fileHandler)
    
    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)
    
    rootLogger.setLevel(logging.INFO)
    acs400 = ACS400(port="/dev/ttyUSB1")
    #acs400.dumpGroup(1)
    logger.info(f"Relays: {acs400.getRelays()}")
    #logger.info(f"{acs400.getRegisterFormat(group=1, idx=5)}")
    logger.info(f"{acs400.getDigitalInputs()}")
    # for i in range(5):
    #     acs400.printNPump()
    #     time.sleep(1)
