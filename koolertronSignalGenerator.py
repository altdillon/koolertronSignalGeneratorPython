#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 10 13:39:34 2020

@author: dillon
"""

import serial

class KoolertronSig(object):
    
    def __init__(self,ttydev):
        #self.ttydevice = '/dev/ttyUSB0'
        self.ttydevice = ttydev
        self.baudRate = 115200
        self.endl = b'\r\n'
        
    def searchDevices(self):
        pass
    
    def sendCommand(self,strcmd):
        cmd = str.encode(strcmd)
        result = False
        #endl = b'\r\n'
        with serial.Serial(self.ttydevice,self.baudRate,timeout=1) as ser:
            ser.write(cmd+self.endl)
            resultCommand = ser.readline()
            # see if the result command works
            if(resultCommand == b':ok\r\n'):
                result = True
            
        return result
    
    # set the voltage level
    def setVoltageLevel(self,vlevel):
        pass
        
    # set wave form type,
    def setWave(self,wavetype,channel):
        # serial codes from wave forms 
        wavecommands = {
            "sin" : 0,
            "square" : 1,
            "pulse" : 2,
            "triangle" : 3,
            "partialsin" : 4,
            "CMOS" : 5,
            "DCLevel" : 6,
            "halfwave" : 7,
            "fullwave" : 8,
            "positive-step" : 9,
            "anti-step" : 10,
            "noise-wave" : 11,
            "index-rising" : 12,
            "index-reducing" : 13,
            "sinkpulse" : 15,
            "lortntzpulse" : 16
        }
        wavecode = wavecommands[wavetype]
        # build up the command
        if(channel < 2):
            strcmd = ':w2{}={}.'.format(channel,wavecode)
            self.sendCommand(strcmd)
    
    # set freq in Hz
    def setFreq(self,freq,channel):
        freq = freq * 100
        cmd = None 
        if(channel == 1):
            cmd = ':w23={},0.'.format(int(freq))
        elif(channel == 2):
            cmd = ':w24={},0.'.format(int(freq))
        # send the command back to the server 
        self.sendCommand(cmd)
    
    # set the phase in degrees.  ONly works for channel 2
    def setPhase(self,phase,channel):
        pass
    
    # set the duty cycle
    def setDuty(self,duty,channel):
        pass

    # set the offset voltage
    def setOffSet(self,offset,channel):
        offsetv = None
        # set the values for the offset
        if(offset >= 0):
            offsetcmd = "1{}".format(int(offset*1000))
        else:
            offsetvalue = 1000-offset
            offsetcmd = "{}".format(int(offsetvalue))
        # now build up and send the command
        

    # set the amplitude, amp given in volts 
    def setAmplitude(self,amp,channel):
        vamp = amp * 1000
        command = None
        if(channel == 1):
            command = ":w25={}.".format(vamp)
        elif(channel == 2):
            command = ":w26={}.".format(vamp)
        # send the command to the system
        self.sendCommand(command)
            
            

class KSchannel(KoolertronSig):
    pass
