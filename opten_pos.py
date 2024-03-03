
import os
import threading
import time

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pyqtgraph as pg

from opten_lib import *
from sync_dual import *
from datetime import datetime
      
        
#### Motor Init ####

print("\nStarting motors initialisation")

dnx = Dynamixel()
dnx.open_port()

dnx.enable_torque(DXL1_ID)
dnx.enable_torque(DXL2_ID)

dnx.set_current_limit(DXL1_ID, 800)
dnx.set_current_limit(DXL2_ID, 800)

#### Opten Init ####

opt = OpticalDuo()
opt.start_burst()

####################################################################################################

class DataLogger(threading.Thread):
    
    def __init__(self, motor1_pos0, motor2_pos0):
        super().__init__()
        self.opt = opt
        self.dnx = dnx
        self.time_data = np.array([])
        self.time_start = time.time()
        self.motor1_pos0 = motor1_pos0
        self.motor2_pos0 = motor2_pos0
        self.motor1_apos_data, self.motor2_apos_data = np.array([]), np.array([])
        self.opten1_posx_data, self.opten1_posy_data = np.array([]), np.array([])
        self.opten2_posx_data, self.opten2_posy_data = np.array([]), np.array([])
        self.pause_poll = False
        self.running = True
    
    def run(self):
        while self.running:
            if not self.pause_poll:
                motor1_apos = (dnx.get_position(DXL1_ID) - motor1_pos0) / 52.5
                motor2_apos = (dnx.get_position(DXL2_ID) - motor2_pos0) / 52.5
                self.motor1_apos_data = np.append(self.motor1_apos_data, motor1_apos)
                self.motor2_apos_data = np.append(self.motor2_apos_data, motor2_apos)
                self.opten1_posx_data = np.append(self.opten1_posx_data, self.opt.serial_reader1.x)
                self.opten1_posy_data = np.append(self.opten1_posy_data, self.opt.serial_reader1.y)
                self.opten2_posx_data = np.append(self.opten2_posx_data, self.opt.serial_reader2.x)
                self.opten2_posy_data = np.append(self.opten2_posy_data, self.opt.serial_reader2.y)
                self.time_data = np.append(self.time_data, time.time() - self.time_start)
                time.sleep(0.08)
            else:
                time.sleep(0.01)
                
    def set_velocity(self, id, velocity):
        self.pause_poll = True
        time.sleep(0.05)
        dnx.set_velocity(id, velocity)
        time.sleep(0.05)
        self.pause_poll = False
        
    def set_2velocity(self, velocity1, velocity2):
        self.pause_poll = True
        time.sleep(0.05)
        dnx.set_velocity(DXL1_ID, -velocity1)
        time.sleep(0.05)
        dnx.set_velocity(DXL2_ID, velocity2)
        time.sleep(0.05)
        self.pause_poll = False
        
    def set_position(self, id, position):
        self.pause_poll = True
        time.sleep(0.05)
        dnx.set_position(id, position)
        time.sleep(0.05)
        self.pause_poll = False
            
    def save(self, filename=None):
        df = pd.DataFrame({'Time': np.round(self.time_data, 3),
                            'Motor1 Pos': np.round(self.motor1_apos_data, 3),
                            'Opten1 PosX': np.round(self.opten1_posx_data, 3),
                            'Opten1 PosY': np.round(self.opten1_posy_data, 3),
                            'Motor2 Pos': np.round(self.motor2_apos_data, 3),
                            'Opten2 PosX': np.round(self.opten2_posx_data, 3),
                            'Opten2 PosY': np.round(self.opten2_posy_data, 3)})
        os.makedirs('./exports', exist_ok=True)
        if not filename:
            filename = f"./exports/stream_{datetime.fromtimestamp(self.time_start).strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(filename, index=False)
        print(f"Data exported to {filename}")
        return filename
        
    def stop(self):
        self.running = False

motor1_pos0 = dnx.get_position(DXL1_ID)
motor2_pos0 = dnx.get_position(DXL2_ID)

dnx.set_mode(DXL1_ID, "extpos")
dnx.set_mode(DXL2_ID, "extpos")
dnx.set_profile_acceleration(DXL1_ID, 15)
dnx.set_profile_acceleration(DXL2_ID, 15)
dnx.set_profile_velocity(DXL1_ID, 500)
dnx.set_profile_velocity(DXL2_ID, 500)

logger = DataLogger(motor1_pos0, motor2_pos0)
logger.start()
print("Data logger started")

time.sleep(1)
for i in range(5):
    logger.set_position(DXL1_ID, motor1_pos0 - 1000)
    time.sleep(2)
    logger.set_position(DXL1_ID, motor1_pos0)
    time.sleep(2)
    
time.sleep(1)
for i in range(5):
    logger.set_position(DXL2_ID, motor2_pos0 - 1000)
    time.sleep(2)
    logger.set_position(DXL2_ID, motor2_pos0)
    time.sleep(2)

# time.sleep(1)
# for i in range(5):
#     logger.set_2velocity(50, 50)
#     time.sleep(1)
#     logger.set_2velocity(0, 0)
#     time.sleep(1)
#     logger.set_2velocity(-50, -50)
#     time.sleep(1)
#     logger.set_2velocity(0, 0)
#     time.sleep(1)


filename = logger.save()
logger.stop()
logger.join()


df_motor = pd.read_csv(filename)
time_motor = df_motor['Time'].values
x_motor1 = df_motor['Motor1 Pos'].values
x_opten1 = df_motor['Opten1 PosX'].values
y_opten1 = df_motor['Opten1 PosY'].values
x_motor2 = df_motor['Motor2 Pos'].values
x_opten2 = df_motor['Opten2 PosX'].values
y_opten2 = df_motor['Opten2 PosY'].values

fig, ax = plt.subplots(2, 1, figsize=(10, 10))
ax[0].plot(time_motor, x_motor1, label='Motor 1')
ax[0].plot(time_motor, x_opten1, label='Opten 1')
ax[1].plot(time_motor, x_motor2, label='Motor 2')
ax[1].plot(time_motor, x_opten2, label='Opten 2')
ax[0].set_title('Motor 1')
ax[1].set_title('Motor 2')
ax[0].set_xlabel('Time (s)')
ax[1].set_xlabel('Time (s)')
ax[0].set_ylabel('Position (mm)')
ax[1].set_ylabel('Position (mm)')
ax[0].legend()
ax[1].legend()
ax[0].grid()
ax[1].grid()
plt.show()

####################################################################################################

#### Opten Close ####

opt.close()

#### Motor Close ####

print("\nClosing motors")

dnx.disable_torque(DXL1_ID)
dnx.disable_torque(DXL2_ID)
dnx.close_port()
