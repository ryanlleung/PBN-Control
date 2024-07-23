
import time
from motor_ctrl.sync_quad import Dynamixel4, MOTOR1_ID, MOTOR2_ID, MOTOR3_ID, MOTOR4_ID
from opten_ctrl.opten_lib import Optical4

"""
Change configuration in in motor_ctrl/config_dual.json
Make sure the Dynamixel port is not occupied by another software.
Check motor_ctrl/sync_dual.py for more info.
"""

#### DONT CHANGE START ####
opt = Optical4()
opt.start_burst()

dnx = Dynamixel4()
dnx.open_port()
dnx.enable_torque(MOTOR1_ID)
dnx.enable_torque(MOTOR2_ID)
dnx.enable_torque(MOTOR3_ID)
dnx.enable_torque(MOTOR4_ID)
##### DONT CHANGE END #####


#### Closed-loop Position Control Test ####

# Set the mode and velocity during motion
dnx.set_mode(MOTOR1_ID, "vel")
dnx.set_mode(MOTOR2_ID, "vel")
dnx.set_mode(MOTOR3_ID, "vel")
dnx.set_mode(MOTOR4_ID, "vel")

dnx.define_quadpos0() # Define the current position as the origin

## Test ##
print ("Test Starting...")

SETPOINT_1 = 25.4 # mm
KP, KI, KD = 6., 0.01, 1.

integral = 0
last_error = 0
while True:
    error = SETPOINT_1 - opt.serial_reader1.y
    integral += error
    control = KP * error + KI * integral + KD * (error - last_error)
    dnx.set_velocity(MOTOR1_ID, control)
    last_error = error
    if abs(error) < 0.1:
        print(f"Motor 1 reached the setpoint: {SETPOINT_1} | Optical Encoder 1: {opt.serial_reader1.y}")
        break
dnx.set_velocity(MOTOR1_ID, 0)
time.sleep(0.5)


##### DONT CHANGE START #####
opt.close()

dnx.disable_torque(MOTOR1_ID)
dnx.disable_torque(MOTOR2_ID)
dnx.disable_torque(MOTOR3_ID)
dnx.disable_torque(MOTOR4_ID)
dnx.close_port()
##### DONT CHANGE END #####
