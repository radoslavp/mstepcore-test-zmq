import time
from ..mstep_lib import MstepLib

def module_run(context):
    LOG_FILE = "values.log"
    
    mstep = MstepLib(context)

    mstep.mkFile(LOG_FILE)
    print(f"Logging to {LOG_FILE}")

    while True:
        curr_pres = mstep.getVar('pres')
        curr_visi = mstep.getVar('visi')
        avg_pres = mstep.getVar('avg_pres')
        avg_visi = mstep.getVar('avg_visi')

        mstep.wrFile(LOG_FILE, f"Current pressure: {curr_pres}")
        print(f"logged curr_pres: {curr_pres}")
        mstep.wrFile(LOG_FILE, f"Current visibility: {curr_visi}")
        print(f"logged curr_visi: {curr_visi}")
        mstep.wrFile(LOG_FILE, f"Average pressure: {avg_pres}")
        print(f"logged avg_pres: {avg_pres}")
        mstep.wrFile(LOG_FILE, f"Average visibility: {avg_visi}")
        print(f"logged avg_visi: {avg_visi}")

        time.sleep(10)
