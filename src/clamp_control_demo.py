
import time
from motor_ctrl.sync_clamp import Dynamixel6, DXL1_ID, DXL2_ID, DXL3_ID, DXL4_ID, DXL5_ID, DXL6_ID

"""
Change configuration in in motor_ctrl/config.json
Make sure the Dynamixel port is not occupied by another software.
Check motor_ctrl/sync_dual.py for more info.
"""

#### DONT CHANGE START ####
dnx = Dynamixel6()
dnx.open_port()
dnx.enable_torque(DXL1_ID)
dnx.enable_torque(DXL2_ID)
dnx.enable_torque(DXL3_ID)
dnx.enable_torque(DXL4_ID)
dnx.enable_torque(DXL5_ID)
dnx.enable_torque(DXL6_ID)
##### DONT CHANGE END #####


#### Profile Velocity Demo ####
"""
Position mode where the motor moves to a specified position.
Set the profile velocity and acceleration of the motor when moving to a position.
"""
# Set the mode and velocity during motion
dnx.set_mode(DXL1_ID, "extpos")
dnx.set_mode(DXL2_ID, "extpos")
dnx.set_mode(DXL3_ID, "extpos")
dnx.set_mode(DXL4_ID, "extpos")
dnx.set_mode(DXL5_ID, "extpos")
dnx.set_mode(DXL6_ID, "extpos")

dnx.set_profile_velocity(DXL1_ID, 33) # Set the profile velocity of the motor, 1 mm/s = 3.33 unit/s
dnx.set_profile_velocity(DXL2_ID, 33) # Set the profile velocity of the motor, 1 mm/s = 3.33 unit/s
dnx.set_profile_velocity(DXL3_ID, 33) # Set the profile velocity of the motor, 1 mm/s = 3.33 unit/s
dnx.set_profile_velocity(DXL4_ID, 33) # Set the profile velocity of the motor, 1 mm/s = 3.33 unit/s

dnx.home_position(DXL1_ID)
dnx.home_position(DXL2_ID)
dnx.home_position(DXL3_ID)
dnx.home_position(DXL4_ID)

## Using absolute positions ##
print(f"\nAbsolute Positions Demo \nInitial Abs Positions: {dnx.motor1_pos0}, {dnx.motor2_pos0}")
time.sleep(1)

motor1_pos1 = dnx.motor_pos0[DXL1_ID] + 520
motor2_pos1 = dnx.motor_pos0[DXL2_ID] + 520
dnx.set_dualpos(motor1_pos1, motor2_pos1)
print(f"Moving to Abs Positions: {motor1_pos1}, {motor2_pos1}")
time.sleep(5)

motor1_pos2 = dnx.motor_pos0[DXL1_ID] - 520
motor2_pos2 = dnx.motor_pos0[DXL2_ID] - 520
dnx.set_dualpos(motor1_pos2, motor2_pos2)
print(f"Moving to Abs Positions: {motor1_pos2}, {motor2_pos2}")
time.sleep(5)

## Using relative positions ##
print(f"\nRelative Positions Demo \nInitial Abs Positions: {dnx.motor1_pos0}, {dnx.motor2_pos0}")
time.sleep(1)

motor1_rpos1 = 200/52.5
motor2_rpos1 = 200
dnx.set_dualrpos(motor1_rpos1, motor2_rpos1)
print(f"Moving to Rel Positions: {motor1_rpos1}, {motor2_rpos1}")
time.sleep(5)

motor1_rpos2 = 250
motor2_rpos2 = 750
dnx.set_dualrpos(motor1_rpos2, motor2_rpos2)
print(f"Moving to Rel Positions: {motor1_rpos2}, {motor2_rpos2}")
time.sleep(5)

motor1_rpos3 = 500
motor2_rpos3 = 500
dnx.set_dualrpos(motor1_rpos3, motor2_rpos3)
print(f"Moving to Rel Positions: {motor1_rpos3}, {motor2_rpos3}")
time.sleep(5)

motor1_rpos4 = -(motor1_rpos1 + motor1_rpos2 + motor1_rpos3)
motor2_rpos4 = -(motor2_rpos1 + motor2_rpos2 + motor2_rpos3)
dnx.set_dualrpos(motor1_rpos4, motor2_rpos4)
print(f"Moving to Rel Positions: {motor1_rpos4}, {motor2_rpos4}")
time.sleep(5)

print("\nDemo completed")

##### DONT CHANGE START #####
dnx.disable_torque(DXL1_ID)
dnx.disable_torque(DXL2_ID)
dnx.disable_torque(DXL3_ID)
dnx.disable_torque(DXL4_ID)
dnx.disable_torque(DXL5_ID)
dnx.disable_torque(DXL6_ID)
dnx.close_port()
##### DONT CHANGE END #####
