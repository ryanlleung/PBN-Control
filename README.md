# PBN-Control
This repository contains code for controlling PBNs (programmable bevel-tip needles) using Dynamixel motors. The code is written in Python and uses the Dynamixel SDK Python API to communicate with the motors. The GUIs are written in Python using the PyQt5 library.

# Motors
## Dynamixel SDK Installation
Please follow the instructions here to install DynamixelSDK for Windows Python. Python 3.10 is used in this project.
https://github.com/ROBOTIS-GIT/DynamixelSDK
https://emanual.robotis.com/docs/en/software/dynamixel/dynamixel_sdk/library_setup/python_windows/#python-windows

## Motor IDs
Please change the Motor ID and reverse mode (if needed) using Dynamixel Wizard 2. Install from https://emanual.robotis.com/docs/en/software/dynamixel/dynamixel_wizard2/

A positive velocity should move the segment forwards. Set the reverse mode to True (address 10) if the segment moves backwards with a positive velocity.

## Device Configuration
Set ID and device name in config.json file.

For dual control:
- MOTOR1_ID: ID of the portside motor (default: 1)
- MOTOR2_ID: ID of the starboard motor (default: 2)

For quad control:
- MOTOR1_ID: ID of portside motor on the front drive set (default: 1)
- MOTOR2_ID: ID of starboard motor on the rear drive set (default: 2)
- MOTOR3_ID: ID of starboard motor on the front drive set (default: 3)
- MOTOR4_ID: ID of portside motor on the rear drive set (default: 4)

For clamp control:
- MOTOR1_ID: ID of portside motor on the front drive set (default: 1)
- MOTOR2_ID: ID of starboard motor on the rear drive set (default: 2)
- MOTOR3_ID: ID of starboard motor on the front drive set (default: 3)
- MOTOR4_ID: ID of portside motor on the rear drive set (default: 4)
- MOTOR5_ID: ID of the front clamp motor (default: 10)
- MOTOR6_ID: ID of the rear clamp motor (default: 11)

# Optical Sensors
## Arduino Library Installation
The optical encoders used are the PMW3360 Motion Sensor from Joe's Sensors and Sundry, available from https://www.tindie.com/products/citizenjoe/pmw3360-motion-sensor/. 

The optical encoders are controlled by Arduino Uno with Serial Peripheral Interface, using a library based on https://github.com/SunjunKim/PMW3360_Arduino. From this repository copy the opten/installation/AdvMouse/ to your Arduino library folder. Then load the .ino file onto the Arduino using the Arduino IDE.

The GUI interface is written in Python and uses the PySerial library to communicate with the Arduino.

https://github.com/ryanlleung/PBN-Control/blob/main/images/wiring.png

