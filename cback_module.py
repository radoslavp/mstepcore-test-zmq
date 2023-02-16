import time
from mstepcore_test_zmq.mstep_lib import MstepLib

def cback(context):
    mstep = MstepLib(context)
    temp = mstep.getVar("temp")
    print(f"callback called! Current temperature is {temp}")
