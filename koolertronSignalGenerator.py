#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 10 13:39:34 2020

@author: dillon
"""

import serial
import copy
import numpy as np


# basic helper functions for the arb waveform stuff
def makeStr(arr):
    sgStr=''
    for elem in arr:
        sgStr = sgStr + str(int(elem)) + ','
    return sgStr[:-1]

def vmap(x,in_min,in_max,out_min,out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

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
    
    def __init__(self,ttydev='/dev/ttyUSB0'):
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

    # set an apartray wave form
    # can take values between 1 and 60
    def setArb(self,arb,chan=1):
        # make sure that the arb between 1 and 60
        if arb < 1 or arb > 60:
            return None # at this point there's not point in running the function

        # convert the id to a string and add leading zeros if needed
        arbCmd = "{}".format(arb)
        if arb < 10:
            arbCmd = arbCmd.zfill(2)
        cmd = "1{}.".format(arbCmd)
        # set the channel
        chanCmd = ""
        if chan == 1:
            chanCmd = ":w21={}.".format(cmd)
        elif chan == 2:
            chanCmd = ":w22={}.".format(cmd)
        self.sendCommand(chanCmd)

    # take in a list of values to generate a multitone signal
    # https://stackoverflow.com/questions/29194588/python-gcd-for-list
    def multiTone(self,tones,channel=1):
        # do a type check
        # if it's not already a numpy array convert it to a numpy array
        if type(tones) != np.ndarray:
            tones = np.array(tones,dtype='float')
        # take in a value and devide it by the gcd 
        
        
        # add up the unit arb values 
        n = 2048
        t = np.linspace(start=-np.pi,stop=np.pi,num=n)
        for elem in tones:
            pass



    # set a value for the DDS table in an arbitary wave form
    # takes in a value with length 2048. Values will be normalized to -1 to 1
    def setArbValues(self,nArray,arb=1):
        # do some type checking to make sure that the stuff if formated correnctly
        #if type(nArray) != '<class \'numpy.ndarray\'>':
        #    return None
        # if everything works out then normalize and get started
        xnorm = nArray/nArray.max()
        xnmap = vmap(xnorm,-1,1,0,4095) # map to a value as seen in the datasheet
        xnmap_str = makeStr(xnmap)
        # add leading zeros to the arb function id
        arbId = ""
        if arb < 10:
            arbId = str(arb).zfill(2)
        else:
            arbId = str(arb)
        # fianlly build up the command
        
        cmd = ':a{}={}.'.format(arbId,xnmap_str)
        self.sendCommand(cmd)
    
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
    def setOffSet(self,offset,channel=1):
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
    
    def sinwave(self,freq,amp=1,phase=0,offset=0,chan=1):
        
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

    def squareWave(self,freq,amp=1,phase=0,offset=0,chan=1):
        if self.isConnected():
            self.setAmplitude(amp,chan)
            self.setFreq(freq,chan)
            self.setWave('square',chan)
            self.setOffSet(offset,chan)
            if chan == 2:
                self.setPhase(phase)
        else:
            return None
        return copy.copy(self.getState(chan))

    def pwm(self,freq,amp=1,phase=0,offset=0,chan=1,duty=0.5):
        if self.isConnected():
            self.setAmplitude(amp,chan)
            self.setFreq(freq,chan)
            self.setWave('CMOS',chan)
            self.setOffSet(offset,chan)
            self.setDuty(duty,chan)
            if chan == 2:
                self.setPhase(phase)
        else:
            return None
        return copy.copy(self.getState(chan))
        
class WaveForm:
    def __init__(self,wav,freq=1e3,dcoffset=0,phase=0,filepath=None):
        # do a dump oop thing and write the things to local values
        pass # TODO: add code here

class KSchannel(KoolertronSig):
    pass

class Servo(KoolertronSig):
    
    def __init__(self,ttydev,chan=1):
        self.channel = chan
        super().__init__(ttydev)
        
class Cli:

    def __init__(self):
        pass
