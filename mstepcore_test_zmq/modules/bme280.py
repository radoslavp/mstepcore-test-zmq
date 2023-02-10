# sources: 
# https://github.com/rm-hull/bme280/blob/master/bme280/__init__.py
# https://github.com/rm-hull/bme280/blob/master/bme280/reader.py
# https://github.com/adafruit/Adafruit_BME280_Library/blob/master/Adafruit_BME280.cpp
# https://www.youtube.com/watch?v=MCi7dCBhVpQ

import spidev
import time
from ..mstep_lib import MstepLib

debug = False

spi = spidev.SpiDev()
spi.open(0,0)

def debugPrint(msg):
    if debug:
        print(f"Debug: {msg}")
        
def errorPrint(msg):
    print(f"Error: {msg}")

def read8(addr):
    return spi.xfer([addr, 0x00])[1]
    
def readS8(addr):
    val = read8(addr)
    return val if val < 0x80 else val - 0x100            
    
def read16(addr):
    val = spi.xfer([addr, 0x00, 0x00])
    return val[2] << 8 | val[1]

def readS16(addr):
    val = read16(addr)
    return val if val < 0x8000 else val - 0x10000

def module_run(context):
    mstep = MstepLib(context)

    chip_id = read8(0xd0)
    debugPrint(f"chip_id: {chip_id}")
    if chip_id == 0x60:
        spi.xfer([0x74, 0x37])	# todo: write
        ctrl_meas = read8(0xf4)
        debugPrint(f"ctrl_meas: {ctrl_meas}")
        if ctrl_meas == 0x37:
            print(f"Chip id: {chip_id}")

            # CALIBRATION VALUES
            # temperature
            dig_T1 = read16(0x88)
            dig_T2 = readS16(0x8A)
            dig_T3 = readS16(0x8C)

            # pressure
            dig_P1 = read16(0x8E)
            dig_P2 = readS16(0x90)
            dig_P3 = readS16(0x92)
            dig_P4 = readS16(0x94)
            dig_P5 = readS16(0x96)
            dig_P6 = readS16(0x98)
            dig_P7 = readS16(0x9A)
            dig_P8 = readS16(0x9C)
            dig_P9 = readS16(0x9E)        

            # humidity
            dig_H1 = read8(0xA1)
            dig_H2 = readS16(0xE1)
            dig_H3 = readS8(0xE3)
            e4 = readS8(0xE4) 
            e5 = readS8(0xE5)
            e6 = readS8(0xE6)
            dig_H4 = (e4 << 4) | (e5 & 0x0F)     
            dig_H5 = ((e5 >> 4) & 0x0F) | (e6 << 4)
            dig_H6 = readS8(0xE7)
         
            debugPrint(f"dig_T1: {dig_T1}")
            debugPrint(f"dig_T2: {dig_T2}")
            debugPrint(f"dig_T3: {dig_T3}")

            debugPrint(f"dig_P1: {dig_P1}")
            debugPrint(f"dig_P2: {dig_P2}")
            debugPrint(f"dig_P3: {dig_P3}")
            debugPrint(f"dig_P4: {dig_P4}")
            debugPrint(f"dig_P5: {dig_P5}")
            debugPrint(f"dig_P6: {dig_P6}")
            debugPrint(f"dig_P7: {dig_P7}")
            debugPrint(f"dig_P8: {dig_P8}")
            debugPrint(f"dig_P9: {dig_P9}")

            debugPrint(f"dig_H1: {dig_H1}")
            debugPrint(f"dig_H2: {dig_H2}")
            debugPrint(f"dig_H3: {dig_H3}")
            debugPrint(f"dig_H4: {dig_H4}")
            debugPrint(f"dig_H5: {dig_H5}")
            debugPrint(f"dig_H6: {dig_H6}")

            # measuring loop
            while True:
                # CURRENT VALUES
                curr_values = spi.xfer([0xF7, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
                debugPrint(f"Current values: {curr_values}")
            
                # pressure
                adc_P_msb = curr_values[1]
                adc_P_lsb = curr_values[2]
                adc_P_xlsb = curr_values[3] 
                # temperature
                adc_T_msb = curr_values[4]
                adc_T_lsb = curr_values[5]
                adc_T_xlsb = curr_values[6] 
                # humidity
                adc_H_msb = curr_values[7]
                adc_H_lsb = curr_values[8]
                
                # CALCULATIONS
                # temperature
                adc_T = adc_T_msb << 16 | adc_T_lsb << 8 | adc_T_xlsb
                debugPrint(f"adc_T: {adc_T}")

                adc_T >>= 4
                
                var1 = (adc_T / 16384.0 - dig_T1 / 1024.0) * dig_T2
                var2 = adc_T / 131072.0 - dig_T1 / 8192.0
                var2 = var2 * var2 * dig_T3
                t_fine = (var1 + var2)
                T = t_fine / 5120.0
                
                mstep.setVar('temp', T)
                
                # pressure            
                adc_P = adc_P_msb << 16 | adc_P_lsb << 8 | adc_P_xlsb
                debugPrint(f"adc_P: {adc_P}")            
                
                adc_P >>= 4
                
                var1 = t_fine / 2.0 - 64000.0
                var2 = var1 * var1 * dig_P6 / 32768.0
                var2 = var2 + var1 * dig_P5 * 2
                var2 = var2 / 4.0 + dig_P4 * 65536.0
                var1 = (dig_P3 * var1 * var1 / 524288.0 + dig_P2 * var1) / 524288.0
                var1 = (1.0 + var1 / 32768.0) * dig_P1
                pressure = 1048576.0 - adc_P
                pressure = (pressure - var2 / 4096.0) * 6250.0 / var1
                var1 = dig_P9 * pressure * pressure / 2147483648.0
                var2 = pressure * dig_P8 / 32768.0
                P = (pressure + (var1 + var2 + dig_P7) / 16.0) / 100.0
        
                mstep.setVar('pres', P)
                
                # humidity            
                adc_H = adc_H_msb << 8 | adc_H_lsb
                debugPrint(f"adc_H: {adc_H}")         
            
                var1 = t_fine - 76800.0
                var2 = dig_H4 * 64.0 + (dig_H5 / 16384.0) * var1
                var3 = adc_H - var2
                var4 = dig_H2 / 65536.0
                var5 = 1.0 + (dig_H3 / 67108864.0) * var1
                var6 = 1.0 + (dig_H6 / 67108864.0) * var1 * var5
                var6 = var3 * var4 * (var5 * var6)

                humidity = var6 * (1.0 - dig_H1 * var6 / 524288.0)
                H = max(0.0, min(100.0, humidity))
                
                mstep.setVar('hum', H)
                
                time.sleep(10)
