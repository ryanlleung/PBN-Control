
import serial
import time

import numpy as np
import pyqtgraph as pg
from PyQt5.QtCore import QThread


OPT1 = 'COM4'
OPT2 = 'COM5'
BAUDRATE = 9600


class SerialReader(QThread):
    
    def __init__(self, serial_com, mode="burst", flip_x=False, flip_y=False):
        super().__init__()
        self.serialCom = serial_com
        self.x, self.y = 0, 0
        self.flip_x = flip_x
        self.flip_y = flip_y
        self.pixels = None
        if mode not in ["burst", "camera"]:
            raise ValueError(f"Mode {mode} not recognised, must be 'burst' or 'camera'")
        self.mode = mode
        self.running = True
        self.initialised = False
        # self.lock = threading.Lock()

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
                    
    def check_initialised(self, input_line):
        
        if "DPI set to" in input_line:
            self.dpi = int(input_line.split(' ')[-1])
            print(f"{self.serialCom.name} DPI set to {self.dpi}")
        elif "Optical Chip Initialised" in input_line:
            if not hasattr(self, 'dpi'):
                raise ValueError(f"DPI not retrieved for {self.serialCom.name}")
            self.initialised = True
            print(f"{self.serialCom.name} initialised")
                
    def process_input(self, input_line):
        
        if not self.initialised:
            self.check_initialised(input_line)
        else:
            if self.mode == "burst":
                dy, dx = map(int, input_line.split(' '))
                if self.flip_x:
                    dx = -dx
                if self.flip_y:
                    dy = -dy
                    
                # with self.lock:
                self.x += dx * 25.4 / self.dpi
                self.y += dy * 25.4 / self.dpi
                
            elif self.mode == "camera":
                raw = input_line.split(' ')
                if len(raw) == 1297:
                    self.pixels = np.array(raw[:-1]).reshape((36, 36)).astype(np.uint8)

    def stop(self):
        self.running = False
        
        
class OpticalDuo:
    
    def __init__(self):
        self.port1 = OPT1
        self.port2 = OPT2
        self.baudrate = BAUDRATE

    def connect(self):
        try:
            self.serial_com1 = serial.Serial(self.port1, self.baudrate)
            print(f"Connected to {self.port1}")
        except serial.SerialException:
            raise Exception(f"{self.port1} not available")
        else:
            self.serial_com1.setDTR(False)
            time.sleep(1)
            self.serial_com1.flushInput()
            self.serial_com1.setDTR(True)
            print(f"{self.port1} reset")
        
        try:
            self.serial_com2 = serial.Serial(self.port2, self.baudrate)
            print(f"Connected to {self.port2}")
        except serial.SerialException:
            raise Exception(f"{self.port2} not available")
        else:
            self.serial_com2.setDTR(False)
            time.sleep(1)
            self.serial_com2.flushInput()
            self.serial_com2.setDTR(True)
            print(f"{self.port2} reset")
            
    def start_burst(self):
        
        print("\nStarting optical encoders in burst mode")
        self.connect()
        
        self.serial_reader1 = SerialReader(self.serial_com1, mode="burst")
        self.serial_reader1.start()
        
        self.serial_reader2 = SerialReader(self.serial_com2, mode="burst", flip_x=True)
        self.serial_reader2.start()
        
        while self.serial_reader1.initialised is False or self.serial_reader2.initialised is False:
            time.sleep(0.1)
        time.sleep(1.5)
        print("Optical encoders ready\n")
            
    def start_camera(self):
        
        print("\nStarting optical encoders in camera mode")
        self.connect()
        
        self.serial_reader1 = SerialReader(self.serial_com1, mode="camera")
        self.serial_reader1.start()
        
        self.serial_reader2 = SerialReader(self.serial_com2, mode="camera")
        self.serial_reader2.start()
        
        while self.serial_reader1.initialised is False or self.serial_reader2.initialised is False:
            time.sleep(0.1)
        time.sleep(1.5)
        print("Optical encoders ready\n")
        
    def close(self):
        
        print("\nClosing optical encoders")
        self.serial_reader1.stop()
        self.serial_reader1.wait()
        self.serial_com1.close()
        print(f"{self.port1} closed")
        
        self.serial_reader2.stop()
        self.serial_reader2.wait()
        self.serial_com2.close()
        print(f"{self.port2} closed")
        
        
if __name__ == "__main__":
    opt = OpticalDuo()
    opt.start_burst()
    time.sleep(2)
    opt.close()
