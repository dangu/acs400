from pymodbus.client.sync import ModbusSerialClient
import time

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


if __name__=="__main__":
    acs400=ACS400(port="/dev/ttyUSB0")
    for i in range(5):
        acs400.printNPump()
        time.sleep(1)
