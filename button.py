
from time import sleep
import os
import RPi.GPIO as GPIO
 
GPIO.setmode(GPIO.BCM)
GPIO.setup(22, GPIO.IN)
GPIO.setup(17, GPIO.OUT)

vals = []
target = 10
count = 0
last = None

while True:
    pin22 = GPIO.input(22)
    vals.append(pin22)


    if last is not None and pin22 != last and pin22 == False:
        count += 1
        print "count: {}".format(count)

    last = pin22

    if len(vals)>target:
        del vals[0]
    
    if len(vals)>0:
        GPIO.output(17, vals[0])



    #print pin22
    sleep(0.1);
