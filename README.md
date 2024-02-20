# PBN-Control

# Background
This repository contains code for controlling PBN (programmable bevel-tip needle) using Dynamixel motors. The code is written in Python and uses the Dynamixel SDK to communicate with the motors. 

# Motor Library Installation
https://github.com/ROBOTIS-GIT/DynamixelSDK
https://emanual.robotis.com/docs/en/software/dynamixel/dynamixel_sdk/library_setup/python_windows/#python-windows

Check the motor ID from Dynamixel Wizard
Change the motor ID there as well if needed

# Motor IDs
Looking from the front end of the PBN
- 1: Right segment
- 2: Top segment
- 3: Bottom segment
- 4: Left segment

# Optical Encoders Installation
The optical encoders used are the PMW3360 Motion Sensor from Joe's Sensors and Sundry, available from https://www.tindie.com/products/citizenjoe/pmw3360-motion-sensor/. 

The optical encoders are controlled by Arduino Uno with SPI, using a library based on https://github.com/SunjunKim/PMW3360_Arduino. From this repository copy the opten/installation/AdvMouse/ to your Arduino library folder. Then load the .ino file onto the Arduino using the Arduino IDE.

The GUI interface is written in Python and uses the PySerial library to communicate with the Arduino.
