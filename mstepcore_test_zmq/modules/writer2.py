import random
import time
from ..mstep_lib import MstepLib

def module_run(context):
    mstep = MstepLib(context)

    while True:
        random.random()
        mstep.setVar('pres', random.random() + 20)
        mstep.setVar('visi', random.random() + 105)
        time.sleep(10)
