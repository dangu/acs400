import minimalmodbus


class Inverter(minimalmodbus.Instrument):
    """Instrument class for the three phase inverter
    Args:
        * port (str): port name
        * slaveaddress (int): slave address in the range 1 to 247"""
    def __init__(self, port, slaveaddress):
        """Init"""
        minimalmodbus.Instrument.__init__(self, port=port,
                                          slaveaddress=slaveaddress,
                                          debug=False)
        self.serial.baudrate = 9600
        

    def printNPump(self):
        """Try print pump speed"""
        nPump = self.read_register(101)
        print(f"nPump={nPump}")
        
        

if __name__ == "__main__":
    inverter = Inverter(port="/dev/ttyUSB0", slaveaddress=1)
    inverter.printNPump()
    # inverter.connect(port="/dev/ttyUSB0")
