import time
from mstepcore_test_zmq.mstep_lib import MstepLib

mstep = None

def cback():
    global mstep
    temp = mstep.getVar("temp")
    print(f"callback called! Current temperature is {temp}")

def initModule(context):
    global mstep
    
    mstep = MstepLib(context)
    mstep.regCback("event1", "cback_module", "cback")
    