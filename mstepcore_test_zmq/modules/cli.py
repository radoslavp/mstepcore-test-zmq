import serial
import re
from ..mstep_lib import MstepLib

ser = serial.Serial('/dev/ttyGS0') 

def ser_write(msg):
    ser.write(msg + b'\r\n')

def module_run(context):
    mstep = MstepLib(context)
    buff = b''
    
    ser.write(b'> ')
    while True:
        c = ser.read(1)

        if c == b'\r':
            ser.write(b'\r\n')
        
            if buff == b'help':
                ser_write(b'Mstep CLI help:')
                ser_write(b'\tdevid - prints device id')
            elif buff == b'devid':
                ser_write(b'devid = 1')
            elif re.match(b'get', buff):
                var = buff.split(b' ')[1].decode("utf-8")
                val = bytes(mstep.getVar(var), "utf-8")
                ser_write(val)

            buff = b''
            ser.write(b'> ')
                
        else:
            ser.write(c)
            buff = buff + c
