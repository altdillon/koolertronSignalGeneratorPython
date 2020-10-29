#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 11 00:01:40 2020

@author: dillon
"""

# test the signal generator
from koolertronSignalGenerator import *
import numpy as np

kst = KoolertronSig('/dev/ttyUSB0')
testfreq = 60e3
#testfreq = testfreq * 100
kst.setFreq(testfreq,1)
kst.setWave('sin',1)
kst.setAmplitude(7,1)
#a = ':w23={},0.'.format(int(testfreq))
#kst.sendCommand(a)
#kst.sendCommand(':w23=1000,1.')

# setup a test sin wave 
t = np.linspace(0,2*np.pi,1000)
x1 = np.sin(t)