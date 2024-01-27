
import os
import time
from inputs import get_gamepad
from sync_dual import *


#### Main ####

dnx = Dynamixel()
dnx.open_port()

dnx.enable_torque(DXL1_ID)
dnx.enable_torque(DXL2_ID)

last_check_time = time.time()
check_interval = 0  # Adjust the check interval as needed
last_values = {"ABS_Y": 0, "ABS_RY": 0}  # Initialize the last known values

def set_velocity(event, last_value, motor_id):
    if event.state != last_value:
        last_value = event.state
        drive_value = int(-event.state / 150) if motor_id == DXL1_ID else int(event.state / 150)
        if -10 < drive_value < 10:
            drive_value = 0
        print(f"Drive value: {drive_value}")
        dnx.set_velocity(motor_id, drive_value)

try:
    while True:
        current_time = time.time()
        if current_time - last_check_time >= check_interval:
            last_check_time = current_time
            events = get_gamepad()
            for event in events:
                if event.ev_type == "Absolute":
                    if event.code == "ABS_Y":
                        set_velocity(event, last_values["ABS_Y"], DXL1_ID)
                    elif event.code == "ABS_RY":
                        set_velocity(event, last_values["ABS_RY"], DXL2_ID)

except KeyboardInterrupt:
    print("Keyboard interrupt")

dnx.disable_torque(DXL1_ID)
dnx.disable_torque(DXL2_ID)
dnx.close_port()
