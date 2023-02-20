import time
import spidev
from mstepcore_test_zmq.mstep_lib import MstepLib

def module_run(context):
    mstep = MstepLib(context)

    variable_label = {  "temp": "temperature",
                        "hum": "humidity",
                        "pres": "pressure",
                        "visi": "visibility",
                        }

    temps_seq = []
    hums_seq = []
    pres_seq = []
    visi_seq = []

    def calc_value(var_name, var_value, var_seq):
        if  var_value and \
            var_value != "False":
            
            var_value = float(var_value)

            var_seq.append(var_value)
            if len(var_seq) >= 6:
                var_seq.pop(0)

            avg_var_value = sum(var_seq)/6

            avg_var_name = "avg_" + var_name
            mstep.setVar(avg_var_name, avg_var_value)
        else:
            print(f"No current {variable_label[var_name]}.")

    while True:
        curr_temp = mstep.getVar('temp')
        curr_hum = mstep.getVar('hum')
        curr_pres = mstep.getVar('pres')
        curr_visi = mstep.getVar('visi')

        calc_value("temp", curr_temp, temps_seq)
        calc_value("hum", curr_hum, hums_seq)
        calc_value("pres", curr_pres, pres_seq)
        calc_value("visi", curr_visi, visi_seq)

        time.sleep(10)
