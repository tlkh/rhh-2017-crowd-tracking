import serial
import time

arduino = serial.Serial("/dev/ttyACM0", 9600, timeout=.1)
time.sleep(1)

print("all stop")
arduino.write("<" + str(0) + "," + str(0) + ">")
time.sleep(0.5)
raw_input("Press Enter to continue...")

print("begining stress test")
for i in range(0,100):
	arduino.write("<" + str(35) + "," + str(20) + ">")
	time.sleep(0.02)
	arduino.write("<" + str(25) + "," + str(25) + ">")
	time.sleep(0.02)
	arduino.write("<" + str(20) + "," + str(35) + ">")
	time.sleep(0.02)

print("backwards")
arduino.write("<" + str(-30) + "," + str(-30) + ">")
time.sleep(1.5)

arduino.write("<" + str(-20) + "," + str(-20) + ">")
time.sleep(0.5)

print("spinning")
arduino.write("<" + str(-35) + "," + str(35) + ">")
time.sleep(1.5)

arduino.write("<" + str(35) + "," + str(-35) + ">")
time.sleep(1.5)

print("all stop")
arduino.write("<" + str(0) + "," + str(0) + ">")
