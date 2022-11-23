import time
from ..mstep_lib import MstepLib

def module_run(context):
    LOG_FILE = "values.log"
    
    mstep = MstepLib(context)

    mstep.mkFile(LOG_FILE)
    print(f"Logging to {LOG_FILE}")

    while True:
        curr_temp = mstep.getVar('temp')
        curr_hum = mstep.getVar('hum')
        avg_temp = mstep.getVar('avg_temp')
        avg_hum = mstep.getVar('avg_hum')

        mstep.wrFile(LOG_FILE, f"Current temperature: {curr_temp}")
        print(f"logged curr_temp: {curr_temp}")
        mstep.wrFile(LOG_FILE, f"Current humidity: {curr_hum}")
        print(f"logged curr_hum: {curr_hum}")
        mstep.wrFile(LOG_FILE, f"Average temperature: {avg_temp}")
        print(f"logged avg_temp: {avg_temp}")
        mstep.wrFile(LOG_FILE, f"Average humidity: {avg_hum}")
        print(f"logged avg_hum: {avg_hum}")

        time.sleep(10)
