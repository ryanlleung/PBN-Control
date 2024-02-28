
import os
import sys
import serial
import threading
import time

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pyqtgraph as pg

from opten_lib import *
from sync_dual import *
      
        
#### Motor Init ####

print("\nStarting motors initialisation")

dnx = Dynamixel()
dnx.open_port()

dnx.enable_torque(DXL1_ID)
dnx.enable_torque(DXL2_ID)

#### Opten Init ####

opt = OpticalDuo()
opt.start_burst()

####################################################################################################

time.sleep(2)




####################################################################################################

#### Opten Close ####

opt.close()

#### Motor Close ####

print("\nClosing motors")

dnx.disable_torque(DXL1_ID)
dnx.disable_torque(DXL2_ID)
dnx.close_port()
