#!/usr/bin/env python
import time
import os
from subprocess import call
import sys
import RPi.GPIO as GPIO
import eeml
 
from datetime import datetime

GPIO.setmode(GPIO.BCM)
DEBUG = 1
LOGGER = 1
TIMER_INTERVAL = 0.10

TEMP_F_MIN = -20
TEMP_F_MAX = 130

IMG_RATE = 10  # every N calls take a picture

current_count = 0

# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
        if ((adcnum > 7) or (adcnum < 0)):
                return -1
        GPIO.output(cspin, True)
 
        GPIO.output(clockpin, False)  # start clock low
        GPIO.output(cspin, False)     # bring CS low
 
        commandout = adcnum
        commandout |= 0x18  # start bit + single-ended bit
        commandout <<= 3    # we only need to send 5 bits here
        for i in range(5):
                if (commandout & 0x80):
                        GPIO.output(mosipin, True)
                else:   
                        GPIO.output(mosipin, False)
                commandout <<= 1
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)
 
        adcout = 0
        # read in one empty bit, one null bit and 10 ADC bits
        for i in range(12):
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)
                adcout <<= 1
                if (GPIO.input(misopin)):
                        adcout |= 0x1
 
        GPIO.output(cspin, True)
 
        adcout /= 2       # first bit is 'null' so drop it
        return adcout
 
# change these as desired - they're the pins connected from the
# SPI port on the ADC to the Cobbler
SPICLK = 22
SPIMISO = 23
SPIMOSI = 24
SPICS = 25
 
# set up the SPI interface pins
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)

class ButtonLed():
    def __init__(self):
        # Button / led output
        self.BUTTON_INPUT = 18
        self.LED_OUTPUT = 17

        GPIO.setup(self.BUTTON_INPUT, GPIO.IN)
        GPIO.setup(self.LED_OUTPUT, GPIO.OUT)

        self.vals = []
        self.target = 10
        self.count = 0
        self.last = None

    def read_button(self):
        pin22 = GPIO.input(self.BUTTON_INPUT)
        self.vals.append(pin22)

        if self.last is not None and pin22 != self.last and pin22 == False:
            self.count += 1
            print "count: {}".format(self.count)

        self.last = pin22

        self.vals = self.vals[-self.target:]                                       

    def set_led(self):
        if len(self.vals)>0:
            GPIO.output(self.LED_OUTPUT, self.vals[0])

    def on(self):
        GPIO.output(self.LED_OUTPUT, 1)

    def off(self):
        GPIO.output(self.LED_OUTPUT, 0)


 
# COSM variables. The API_KEY and FEED are specific to your COSM account and must be changed 
#API_KEY = '5RNOO3ShYJxYiq2V2sgSRtz3112SAKxFQjNDQmNXc0RScz0g'
#FEED = 68872
API_KEY = 'k9yVhNTEXxw0wSr5jNQl878NqdiSAKx1Rkc4clRNVUlqYz0g'
FEED = 102207
 
API_URL = '/v2/feeds/{feednum}.xml' .format(feednum = FEED)
 
# temperature sensor connected channel 0 of mcp3008
adcnum = 0
 

def adc_to_millivolts(adc):
    # convert analog reading to millivolts = ADC * ( 3300 / 1024 )
    millivolts = adc * ( 3300.0 / 1024.0)
    return millivolts

def millivolts_to_celcius(millivolts):
    # 10 mv per degree 
    return ((millivolts - 100.0) / 10.0) - 40.0

def celcius_to_fahrenheit(celcius):
    return  ( celcius * 9.0 / 5.0 ) + 32

def get_temp_strings(millivolts):
    temp_C = millivolts_to_celcius(millivolts)

    # convert celsius to fahrenheit 
    temp_F = celcius_to_fahrenheit(temp_C)

    # remove decimal point from millivolts
    millivolts = "%d" % millivolts

    # show only one decimal place for temprature and voltage readings
    temp_C = "%.1f" % temp_C
    temp_F = "%.1f" % temp_F

    return (millivolts, temp_C, temp_F)

def log_temps(pac, temps, d1, d2):
    if float(temps[2]) > TEMP_F_MIN and float(temps[2]) < TEMP_F_MAX:
        pac.update([eeml.Data(d1, temps[1], unit=eeml.Celsius())])
        pac.update([eeml.Data(d2, temps[2], unit=eeml.Fahrenheit())])
        print 'x'
    print 'xx'


def read_adc(bl=None):
    # read the analog pin (temperature sensor LM35)
    adc = [get_temp_strings(adc_to_millivolts(readadc(i, SPICLK, SPIMOSI, SPIMISO, SPICS))) for i in range(8)]

    millivolts1 = adc_to_millivolts(readadc(1, SPICLK, SPIMOSI, SPIMISO, SPICS))


    if DEBUG:
        print "Temperature: {}".format(datetime.now())
        for i in range(8):
            print "millivolts: {: >8} temp_C: {: >8} temp_F: {: >8}".format(*adc[i])
        print "Button count: {}".format(bl.count)

    if LOGGER:
        # open up your cosm feed
        pac = eeml.Pachube(API_URL, API_KEY)
        
        data_num = 0
        for i in range(8):
            if i == 0 or (i > 1 and i < 5):
                log_temps(pac, adc[i], data_num, data_num+1)
                data_num += 2 if i != 0 else 3
            
        pac.update([eeml.Data(2, millivolts1/1000.0, unit=eeml.Unit('Volt', type='basicSI', symbol='V'))])
        pac.update([eeml.Data(9, bl.count, unit=eeml.Unit('Button Count', symbol='^')) ])

        
        if bl is not None:
            bl.off()

        try:
            # send data to cosm
            r = pac.put()
            print "put: {}".format(r)
        except:
            print "ERROR: {}".format(sys.exc_info())

        if bl is not None:
            bl.on()


if __name__=='__main__':
    bl = ButtonLed()
    iteration = 0

    while True: 
        bl.read_button()
        bl.set_led()

        if iteration % 100 == 0:
            read_adc(bl)
            if current_count >= IMG_RATE:
                current_count = 0
                try:
                    call("raspistill -hf  -o /home/pi/work/temperature/imgs/{}.jpg".format(int(time.time())), shell=True)
                except:
                    print "camera call failed"
            current_count += 1
        # hang out and do nothing for 10 seconds, avoid flooding cosm

        iteration += 1
        time.sleep(TIMER_INTERVAL)
