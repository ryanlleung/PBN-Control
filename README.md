# PBN-Control
This repository contains code for controlling PBNs (programmable bevel-tip needles) using Dynamixel motors. The code is written in Python and uses the Dynamixel SDK Python API to communicate with the motors. The GUIs are written in Python using the PyQt5 library.

# Installation
1. Install Python 3.10 from https://www.python.org/downloads/ 
2. Clone the repository and setup your Python environment.
3. Navigate to your project folder and install the required packages using pip.
```bash
pip install -r requirements.txt
```

# Motors
## Dynamixel SDK Installation
Please follow the instructions here to install DynamixelSDK for Windows Python.
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

The optical encoders are controlled by Arduino Uno with Serial Peripheral Interface, using a library based on https://github.com/SunjunKim/PMW3360_Arduino by Kim Sunjun. From this repository copy the src/opt_ctrl/installation/AdvMouse/ to your Arduino library folder. Then load the .ino file onto the Arduino using the Arduino IDE.

This is the wiring diagram for the optical encoders with an Arduino Uno:
![alt text](https://github.com/ryanlleung/PBN-Control/blob/main/images/wiring.png "Wiring Diagram")


# Repository Structure
## Motor Control
In src/motor_ctrl:

Files beginning with sync_ contains low-level functions for controlling multiple motors simultaneously using the Dynamixel API.

- sync_dual.py: For 2-segment needle control
- sync_quad.py: For 4-segment needle control
- sync_clamp.py: For 4-segment needle with clamps control
- *sync_trio.py: Demo for catheter control with 3 motors

Before running the sync_ files, make sure the motors are powered and connected to the computer, the motor IDs and motor controller device name are set in src/motor_ctrl/config_<SETUP>.json.

## Optical Sensor Interfacing
The PySerial library to read serial output from the Arduino boards. Make sure the correct code is loaded onto the Arduino board when running the Python scripts.

In arduino/:

PMW3360DM_Burst/ contains code for the Arduino to read the optical sensors in burst mode. Burst mode outputs a serial line of "dx, dy" values for a sensor when movement is detected. 

PMW3360DM_Camera/ contains code for the Arduino to read the optical sensors in camera mode. Camera mode outputs continuously a serial line of ravelled pixel values for a sensor in the 36x36 sensor array.

In src/opten_ctrl:

Files beginning with opt_ contains low-level functions for reading the optical sensors using the Arduino.

read_burst.py reads an optical sensor in burst mode and prints the aggragated "dx, dy" values.

plot_camera.py reads the an optical sensor in camera mode and plots an image detected by the sensor array continuously, with a save image option.

## GUI
In src/ The files beginning with gui_ are for the GUI interface for monitoring and controlling the motors.

The GUI interface is written in Python and uses 

...



