
import time
from motor_ctrl.sync_dual import Dynamixel2, MOTOR1_ID, MOTOR2_ID

"""
Change configuration in in motor_ctrl/config_dual.json
Make sure the Dynamixel port is not occupied by another software.
Check motor_ctrl/sync_dual.py for more info.
"""

#### DONT CHANGE START ####
dnx = Dynamixel2()
dnx.open_port()
dnx.enable_torque(MOTOR1_ID)
dnx.enable_torque(MOTOR2_ID)
##### DONT CHANGE END #####


#### Position Control Demo ####

# Set the mode and velocity during motion
dnx.set_mode(MOTOR1_ID, "extpos")
dnx.set_mode(MOTOR2_ID, "extpos")
dnx.set_profile_velocity(MOTOR1_ID, 33) # Set the profile velocity of the motor, 1 mm/s ~= 3.33 unit/s
dnx.set_profile_velocity(MOTOR2_ID, 33) # Set the profile velocity of the motor, 1 mm/s ~= 3.33 unit/s
dnx.define_position0(MOTOR1_ID) # Define the current position as 0
dnx.define_position0(MOTOR2_ID) # Define the current position as 0

## Demo ##
print(f"\nAbsolute Positions Demo \nInitial Abs Positions: {dnx.motor_pos0[MOTOR1_ID]}, {dnx.motor_pos0[MOTOR2_ID]}")
time.sleep(1)
motor1_pos1 = dnx.motor_pos0[MOTOR1_ID] + 520   # 1 mm ~= 52 units
motor2_pos1 = dnx.motor_pos0[MOTOR2_ID] + 520   # 1 mm ~= 52 units
dnx.goto_dualpos(motor1_pos1, motor2_pos1)
print(f"Moving to Abs Positions: {motor1_pos1}, {motor2_pos1}")

motor1_pos2 = dnx.motor_pos0[MOTOR1_ID]
motor2_pos2 = dnx.motor_pos0[MOTOR2_ID] + 520
dnx.goto_dualpos(motor1_pos2, motor2_pos2)
print(f"Moving to Abs Positions: {motor1_pos2}, {motor2_pos2}")


##### DONT CHANGE START #####
dnx.disable_torque(MOTOR1_ID)
dnx.disable_torque(MOTOR2_ID)
dnx.close_port()
##### DONT CHANGE END #####
