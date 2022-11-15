import zmq
import sys
import time
import random

class Publisher:
    """ZMQ publisher"""
    def __init__(self):
        """Init"""
        pass

    def open(self, port):
        """Bind to a specific port"""
        context = zmq.Context()
        self._socket = context.socket(zmq.PUB)
        bind_address = f"tcp://127.0.0.1:{port}"
        print(f"Binding to {bind_address} ...")
        self._socket.bind(bind_address)

    def send(self, data):
        """Send data"""
        self._socket.send_pyobj(data)
        #self._socket.send(data)

def run():
    """Run main functionality"""
    publisher = Publisher()
    publisher.open(port=22201)

#    while True:
#        topic = random.randrange(9999,10005)
#        messagedata = random.randrange(1,215) - 80
#        print(f"{topic}, {messagedata}")
#        publisher.send(f"{topic} {messagedata}".encode("UTF8"))
#        time.sleep(1)
    
    for x in range(100):
        publisher.send(f"{x}")

    print("Mitt")
    for y in ["A","B","C"]:
        publisher.send(y)
        time.sleep(1)
        
    for x in range(100):
        publisher.send(f"{x}")

if __name__=='__main__':
    run()

