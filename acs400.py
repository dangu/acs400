from pymodbus.client.sync import ModbusSerialClient
import time

class ACS400:
    def __init__(self):
        self.client = ModbusSerialClient(method='rtu',
                                         port='/dev/ttyUSB1',
                                         timeout=1,
                                         baudrate=9600)

    def printNPump(self):
        nPump = self.client.read_holding_registers(102-1,count=2,unit=1)
        print(f"Va? {nPump.registers}")


if __name__=="__main__":
    acs400=ACS400()
    for i in range(5):
        acs400.printNPump()
        time.sleep(1)
