
import os
import time
from sync_dual import *


#### Main ####

dnx = Dynamixel()
dnx.open_port()

dnx.enable_torque(DXL1_ID)
dnx.enable_torque(DXL2_ID)





dnx.disable_torque(DXL1_ID)
dnx.disable_torque(DXL2_ID)
dnx.close_port()
