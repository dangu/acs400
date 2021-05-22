import blynklib
import blynktimer
import configparser
import acs400


#BLYNK_AUTH = 'YourAuthToken'  # insert your Auth Token here
config = configparser.ConfigParser()
config.read("blynk_app.ini")

BLYNK_AUTH = config['AUTH']['token'].strip('\"')
blynk = blynklib.Blynk(BLYNK_AUTH)

# create timers dispatcher instance
timer = blynktimer.Timer()

WRITE_EVENT_PRINT_MSG = "[WRITE_VIRTUAL_WRITE] Pin: V{} Value: '{}'"

fInv = acs400.ACS400(port="/dev/ttyUSB1")

# Code below: register two timers for different pins with different intervals
# run_once flag allows to run timers once or periodically
@timer.register(vpin_num=0, interval=4, run_once=False)
def write_to_virtual_pin(vpin_num=1):
    value = fInv.getNPump()
    print(WRITE_EVENT_PRINT_MSG.format(vpin_num, value))
    blynk.virtual_write(vpin_num, value)



print(BLYNK_AUTH)
    

while True:
    blynk.run()
    timer.run()
