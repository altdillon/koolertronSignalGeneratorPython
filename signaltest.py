#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 11 00:01:40 2020

@author: dillon
"""

# test the signal generator
from koolertronSignalGenerator import *
import numpy as np
from pylab import *

kst = KoolertronSig('/dev/ttyUSB0')
# make a wave form

kst.setOffSet(0.5,1)
kst.setOffSet(-3,1)

#kst.setPhase(90)