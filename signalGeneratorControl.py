#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  8 22:38:38 2020

@author: dillon
"""
from pylab import *
import serial

# setup serial 
scopeTTLdevice = '/dev/ttyUSB0'
endl = b'\r\n'
baudRate = 115200

testcmd = b':w23=170000,0.' # make a 1 KHz sin wave 
#testcmd = b'w23=25786,0.'

cmds = [b':w23=100000,0.',b':w23=200000,0.',b':w23=100000,0.',b':w21=1.',b':w21=3.',b':w21=0.']

# 8 databits, 1 stop bit, no parity
with serial.Serial(scopeTTLdevice,baudRate,timeout=1) as ser:
    for elm in cmds:
        ser.write(elm+endl)
        resp = ser.readline()
        print(resp)
        ser.flush()
        pause(3)