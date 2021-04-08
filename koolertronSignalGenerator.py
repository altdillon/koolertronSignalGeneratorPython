#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 10 13:39:34 2020

@author: dillon
"""

import serial
import copy

# stories 
class KoolertronState(object):
    
    def __init__(self,freq=None,amplitude=None,offset=None,phase=None,wavetype=None,dutycycle=None):
        self._freq = freq # hertz
        self._amplitude = amplitude # volts 
        self._offSet = offset # volts 
        self._phase = phase # in radians 
        self._waveType = wavetype 
        self._dutycycle = dutycycle
        

# base class for the koolertron
class KoolertronSig(object):
    
    def __init__(self,ttydev):
        #self.ttydevice = '/dev/ttyUSB0'
        self.ttydevice = ttydev
        self.baudRate = 115200 # baud rate dosn't change 
        self.endl = b'\r\n'
        # calles for the states of the channelas
        self.chan1State = KoolertronState()
        self.chan2State = KoolertronState()
        
    def searchDevices(self):
        pass
    
    def setState(self,state):
        if(type(state) == '__main__.KoolertronState'):
            pass
    
    # method for sending a command to the ktron
    def sendCommand(self,strcmd):
        cmd = str.encode(strcmd)
        result = None
        #endl = b'\r\n'
        with serial.Serial(self.ttydevice,self.baudRate,timeout=1) as ser:
            ser.write(cmd+self.endl)
            resultCommand = ser.readline()
            # see if the result command works
            if(resultCommand == b':ok\r\n'):
                result = 'ok'
            else:
                result = resultCommand
            
        return result
    
    # may've been superseeded by set offset method
    # set the voltage level
    def setVoltageLevel(self,vlevel):
        pass
        
    # set wave form type,
    def setWave(self,wavetype,channel=1):
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
        strcmd = ':w2{}={}.'.format(channel,wavecode)
        self.sendCommand(strcmd)
        # update the state object 
        if channel == 1:
            self.chan1State.waveType = wavecommands[wavetype]
        elif channel == 2:
            self.chan2State.waveType = wavecommands[wavetype]
    
    # set freq in Hz
    def setFreq(self,freq,channel=1):
        freq = freq * 100
        cmd = None 
        if(channel == 1):
            cmd = ':w23={},0.'.format(int(freq))
            self.chan1State.freq = freq
        elif(channel == 2):
            cmd = ':w24={},0.'.format(int(freq))
            self.chan2State.freq = freq
        # send the command back to the server 
        self.sendCommand(cmd)
    
    # set the phase in degrees.  ONly works for channel 2
    # phase is a value defined from 
    def setPhase(self,phase):
        phaseValue = phase * 100 
        cmd = ':w31={}.'.format(phaseValue)
        self.sendCommand(cmd)
        self.chan2State.phase = phase # only chan 2 has a phase relitive to phase 1
           
    # make the truth wave
    # for testing digital stuff
    # basicly make the ktron into a 2 bit counter, assuing 3.3 volts ttl
    def makeTruthWave(self,lspPer,amp=3.3):
        # figure out the freqency
        freqCh1 = 1/lspPer 
        freqCh2 = 2*freqCh1
        # set the amplitude 
        self.setAmplitude(amp,1)
        self.setAmplitude(amp,2)
        # set the wave type
        self.setWave("CMOS",1)
        self.setWave("CMOS",2)
        # set the freq
        self.setFreq(freqCh2,1)
        self.setFreq(freqCh1,2)
 
        
    
    # set the duty cycle
    # takes in a value between 0.0 - 1.0
    def setDuty(self,duty,channel=1):
        if(duty <= 1):
            dutycycle = int(duty * 1000)
            cmd = None
            if(channel == 1):
                cmd = ':w29={}.'.format(dutycycle)
                self.chan1State.dutycycle = dutycycle
            elif(channel == 2):
                cmd = ':w30={}.'.format(dutycycle)
                self.chan2State.dutycycle = dutycycle
            self.sendCommand(cmd)

    # set the offset voltage
    def setOffSet(self,offset,channel):
        offsetcmd = None
        offsetvalue = int(offset*100)
        # set the values for the offset
        if(offset > 0):
            offsetcmd = "1{}".format(str(offsetvalue).zfill(3))
        elif(offset < 0):
            offsetvalueN = 1000-abs(offsetvalue)
            offsetcmd = "{}".format(str(offsetvalueN).zfill(3))
        else:
            offsetcmd = "1000" # one to make the value zero and positive
        # now build up and send the command
        command = None
        if(channel == 1):
            command = ":w27=" + offsetcmd + "."
            self.chan1State.offSet = offsetcmd
        elif(channel == 2):
            command = ":w28=" + offsetcmd + "."
            self.chan2State.offSet = offsetcmd
            
        self.sendCommand(command)
        
    def pulse(self,amp,highTime,offset=0,phase=0,channel=1):
        pass

    # set the amplitude, amp given in volts 
    def setAmplitude(self,amp,channel=1):
        vamp = amp * 1000
        command = None
        if(channel == 1):
            command = ":w25={}.".format(vamp)
            self.chan1State.amplitude = vamp
        elif(channel == 2):
            command = ":w26={}.".format(vamp)
            self.chan2State.amplitude = vamp
        # send the command to the system
        self.sendCommand(command)
            
    def getState(self,channel=1):
        if channel == 1:
            return self.chan1State
        elif channel == 2:
            return self.chan2State
        
    def isConnected(self):
        cmd = ":r01=0."
        res = self.sendCommand(cmd)
        if len(res) > 3:
            return True 
        else:
            return False
    
    # helpers for making diffrent functions
    
    def sinwave(self,freq,amp,phase=0,offset=0,chan=1):
        
        if self.isConnected(): # see if we're connected
            self.setAmplitude(amp,chan)
            self.setFreq(freq,chan)
            self.setWave('sin',chan)
            self.setOffSet(offset,chan)
            if chan == 2:
                self.setPhase(phase)
        else:
            return None
        
        return copy.copy(self.getState(chan))

class KSchannel(KoolertronSig):
    pass

class Servo(KoolertronSig):
    
    def __init__(self,ttydev,chan=1):
        self.channel = chan
        super().__init__(ttydev)
        
    
