
import os
import sys
import serial
import threading
import time

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pyqtgraph as pg

from sync_dual import *


class SerialReader(threading.Thread):
    
    def __init__(self, serial_com, flip_x=False, flip_y=False):
        super().__init__()
        self.serialCom = serial_com
        self.x, self.y = 0, 0
        self.flip_x = flip_x
        self.flip_y = flip_y
        self.running = True
        self.initialised = False
        # self.lock = threading.Lock()
        
        self.theta = 0
        if self.serialCom.name == 'COM4':
            self.theta = 0
        elif self.serialCom.name == 'COM5':
            self.theta = 0

    def run(self):
        while self.running:
            if self.serialCom.inWaiting() > 0:
                input_line = ""
                try:
                    input_line = self.serialCom.readline().decode('utf-8').strip()
                except Exception as e:
                    print(f"{self.serialCom.name}: {e} - {input_line}")
                else:
                    self.process_input(input_line)
                
    def process_input(self, input_line):
        if "DPI set to" in input_line:
            self.dpi = int(input_line.split(' ')[-1])
            print(f"{self.serialCom.name} DPI set to {self.dpi}")
        elif "Optical Chip Initialised" in input_line:
            if not hasattr(self, 'dpi'):
                raise ValueError(f"DPI not retrieved for {self.serialCom.name}")
            self.initialised = True
            print(f"{self.serialCom.name} initialised")
            return
            
        if self.initialised:
            dy, dx = map(int, input_line.split(' '))
            if self.flip_x:
                dx = -dx
            if self.flip_y:
                dy = -dy
                
            # with self.lock:
            dx_rot = dx * np.cos(np.deg2rad(self.theta)) - dy * np.sin(np.deg2rad(self.theta))
            dy_rot = dx * np.sin(np.deg2rad(self.theta)) + dy * np.cos(np.deg2rad(self.theta))
            
            self.x += dx_rot * 25.4 / self.dpi
            self.y += dy_rot * 25.4 / self.dpi

    def stop(self):
        self.running = False


#### Motor Init ####

dnx = Dynamixel()
dnx.open_port()

dnx.enable_torque(DXL1_ID)
dnx.enable_torque(DXL2_ID)

#### Opten Init ####
try:
    serialCom = serial.Serial('COM4', 9600)
    print("Connected to COM4")
except serial.SerialException:
    try:
        serialCom = serial.Serial('COM5', 9600)
        print("Connected to COM5")
    except serial.SerialException:
        print("No serial port available")
        sys.exit(1)
        
serialCom.setDTR(False)
time.sleep(1)
serialCom.flushInput()
serialCom.setDTR(True)

sr = SerialReader(serialCom)
sr.start()  # Start the serial reader thread

while sr.initialised is False:
    time.sleep(0.1)
time.sleep(2)
print("Opten initialised")

#### Main ####

motorpos = []
serialpos = []
times = []
time0 = time.time()
mpos0 = dnx.get_position(DXL2_ID)

def capture_positions(duration, interval=0.01):
    end_time = time.time() + duration
    while time.time() < end_time:
        mpos = dnx.get_position(DXL2_ID)-mpos0
        spos = [sr.x, sr.y]
        times.append(time.time() - time0)
        motorpos.append(mpos)
        serialpos.append(spos)
        time.sleep(interval)
        

for i in range(5):
    
    dnx.set_velocity(DXL2_ID, 35)
    duration = .3
    capture_thread = threading.Thread(target=capture_positions, args=(duration,))
    capture_thread.start()
    time.sleep(duration)
    capture_thread.join()

    dnx.set_velocity(DXL2_ID, 15)
    duration = .5
    capture_thread = threading.Thread(target=capture_positions, args=(duration,))
    capture_thread.start()
    time.sleep(duration)
    capture_thread.join()
    
    dnx.set_velocity(DXL2_ID, 25)
    duration = .5
    capture_thread = threading.Thread(target=capture_positions, args=(duration,))
    capture_thread.start()
    time.sleep(duration)
    capture_thread.join()
    
    dnx.set_velocity(DXL2_ID, 0)
    duration = 1.5
    capture_thread = threading.Thread(target=capture_positions, args=(duration,))
    capture_thread.start()
    time.sleep(duration)
    capture_thread.join()
    
    dnx.set_velocity(DXL2_ID, -55)
    duration = .3
    capture_thread = threading.Thread(target=capture_positions, args=(duration,))
    capture_thread.start()
    time.sleep(duration)
    capture_thread.join()

    dnx.set_velocity(DXL2_ID, -15)
    duration = .5
    capture_thread = threading.Thread(target=capture_positions, args=(duration,))
    capture_thread.start()
    time.sleep(duration)
    capture_thread.join()
    
    dnx.set_velocity(DXL2_ID, -35)
    duration = .5
    capture_thread = threading.Thread(target=capture_positions, args=(duration,))
    capture_thread.start()
    time.sleep(duration)
    capture_thread.join()
    
    dnx.set_velocity(DXL2_ID, 0)
    duration = 1.5
    capture_thread = threading.Thread(target=capture_positions, args=(duration,))
    capture_thread.start()
    time.sleep(duration)
    capture_thread.join()
    
dnx.set_velocity(DXL2_ID, 0)

#### Opten Close ####
sr.stop()  # Stop the serial reader thread
sr.join()  # Wait for the serial reader thread to finish
serialCom.close()
print("Serial port closed.")

#### Motor Close ####
dnx.disable_torque(DXL1_ID)
dnx.disable_torque(DXL2_ID)
dnx.close_port()

####################################################################################################

motorpos = np.array(motorpos)
serialpos = np.array(serialpos)
times = np.array(times)
delay = 0.075

mag = np.sqrt(serialpos[:, 0]**2 + serialpos[:, 1]**2)

plt.plot(times, motorpos/57.5, label="Motor")
plt.plot(times-delay, serialpos[:, 0], label="Opten")
plt.plot(times-delay, serialpos[:, 1], label="Opten")

plt.legend()
plt.grid()
plt.show()

# Export data
df = pd.DataFrame({'Time': times, 'Motor': motorpos, 'OptenX': serialpos[:, 0], 'OptenY': serialpos[:, 1]})
df.to_csv("./calib/ctr.csv", index=False)




# print(sr.x, sr.y)

# xx = []
# tt = []
# time0 = time.time()

# target_x = -5
# sum_error = 0
# last_error = 0
# while True:
    
#     error = target_x - sr.x
#     sum_error += error
#     d_error = error - last_error
    
#     kp, ki, kd = 3, 0.02, 0
#     vel = kp*error + ki*sum_error + kd*d_error
    
#     print(f"X: {round(sr.x, 2)} mm, Y: {round(sr.y, 2)} mm, Vel: {round(vel, 2)} mm/s")
    
#     dnx.set_velocity(DXL2_ID, vel)
#     xx += [sr.x]
#     tt += [time.time() - time0]
#     if not (3360 > dnx.get_position(DXL2_ID) > 2000):
#         dnx.set_dualvel(0, 0, 0.5)
#         print("Out of bounds, stopping")
#         break
    
#     if abs(error) < 0.05:
#         print("Reached target")
#         break
    
#     last_error = error
    
# time.sleep(1)
