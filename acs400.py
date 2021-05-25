from pymodbus.client.sync import ModbusSerialClient
import time
import logging
import sys

logger = logging.getLogger(__name__)

class ACS400:
    def __init__(self,port):
        self.client = ModbusSerialClient(method='rtu',
                                         port=port,
                                         timeout=1,
                                         baudrate=9600)

    def printNPump(self):
        nPump=self.getNPump()
        if not nPump.isError():
            print(f"{nPump.registers[0]}")
        else:
            print(f"{nPump}")
            
    def getNPump(self):
        nPump = self.client.read_holding_registers(102-1,count=1,unit=1)
        return nPump

    def getRegister(self, reg):
        """Get register"""
        return self.client.read_holding_registers(reg-1,count=1,unit=1)

    def dumpAll(self):
        """Dump all parameters"""
        groups = [99,1,10,11,12,13,14,15,16,20]
        groups += [21,22,25,26,30,31,32,33,34,40,41]
        groups += [50,51,52,81]
        for group in groups:
            regs = [group*100+reg for reg in range(1,100)]
            for reg in regs:
                result = self.getRegister(reg)
                if not result.isError():
                    logger.info(f"{reg:04} {result.registers[0]:}")

if __name__=="__main__":
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
    acs400.dumpAll()
    # for i in range(5):
    #     acs400.printNPump()
    #     time.sleep(1)
