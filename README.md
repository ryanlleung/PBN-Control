# PBN-Control
This repository contains code for controlling PBN (programmable bevel-tip needle) using Dynamixel motors. The code is written in Python and uses the Dynamixel SDK Python API to communicate with the motors. The GUIs are written in Python using the PyQt5 library.

# Motors
## Dynamixel SDK Installation
Please follow the instructions here to install DynamixelSDK for Windows Python.
https://github.com/ROBOTIS-GIT/DynamixelSDK
https://emanual.robotis.com/docs/en/software/dynamixel/dynamixel_sdk/library_setup/python_windows/#python-windows

## Motor IDs
Please change the Motor ID and reverse mode (if needed) using Dynamixel Wizard. Install from https://emanual.robotis.com/docs/en/software/dynamixel/dynamixel_wizard2/

Looking from the rear end of the PBN:
- ID 1: Top segment (set to reverse mode, set Address 10 = 1)
- ID 2: Left segment (set to reverse mode, set Address 10 = 1)
- ID 3: Right segment (normal mode, set Address 10 = 0)
- ID 4: Bottom segment (normal mode, set Address 10 = 0)

## Device Configuration
Set ID and device name in config.json file.
- DXL1_ID: ID of portside motor on the first drive set (default: 2)
- DXL2_ID: ID of starboard motor on the first drive set (default: 3)
- DXL3_ID: ID of portside motor on the second drive set (default: 1)
- DXL4_ID: ID of starboard motor on the second drive set (default: 4)

# Optical Sensors
## Arduino Library Installation
The optical encoders used are the PMW3360 Motion Sensor from Joe's Sensors and Sundry, available from https://www.tindie.com/products/citizenjoe/pmw3360-motion-sensor/. 

The optical encoders are controlled by Arduino Uno with SPI, using a library based on https://github.com/SunjunKim/PMW3360_Arduino. From this repository copy the opten/installation/AdvMouse/ to your Arduino library folder. Then load the .ino file onto the Arduino using the Arduino IDE.

The GUI interface is written in Python and uses the PySerial library to communicate with the Arduino.
