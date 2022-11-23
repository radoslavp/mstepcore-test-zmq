import random
import time
from ..mstep_lib import MstepLib

def module_run(context):
    mstep = MstepLib(context)

    while True:
        random.random()
        mstep.setVar('temp', random.random() + 10)
        mstep.setVar('hum', random.random() + 55)
        time.sleep(10)
