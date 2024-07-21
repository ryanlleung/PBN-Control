
import json
import serial
import threading
import time

import numpy as np
from PyQt5.QtCore import QThread

# Load configuration from JSON file
with open('src/opten_ctrl/opten_config.json', 'r') as config_file:
    config = json.load(config_file)

# Extract settings from the config dictionary
OPTEN_IDS = {
    "OPTEN1_ID": config['OPTEN1_ID'],
    "OPTEN2_ID": config['OPTEN2_ID'],
    "OPTEN3_ID": config['OPTEN3_ID'],
    "OPTEN4_ID": config['OPTEN4_ID']
}
OPTEN1_ID = OPTEN_IDS["OPTEN1_ID"]
OPTEN2_ID = OPTEN_IDS["OPTEN2_ID"]
OPTEN3_ID = OPTEN_IDS["OPTEN3_ID"]
OPTEN4_ID = OPTEN_IDS["OPTEN4_ID"]

BAUDRATE = 9600

class SerialReader(QThread):
    
    def __init__(self, serial_com, mode="burst", flip_x=False, flip_y=False):
        super().__init__()
        self.serialCom = serial_com
        self.x, self.y = 0, 0
        self.flip_x = flip_x
        self.flip_y = flip_y
        self.pixels = np.zeros((36, 36), dtype=np.uint8)
        if mode not in ["burst", "camera"]:
            raise ValueError(f"Mode {mode} not recognised, must be 'burst' or 'camera'")
        self.mode = mode
        self.running = True
        self.initialised = False
        self.lock = threading.Lock()

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
                with self.lock:
                    self.x += dx * 25.4 / self.dpi
                    self.y += dy * 25.4 / self.dpi
                    
            elif self.mode == "camera":
                raw = input_line.split(' ')
                if len(raw) == 1297:
                    self.pixels = np.array(raw[:-1]).reshape((36, 36)).astype(np.uint8)

    def stop(self):
        self.running = False
        
        
class Optical4:
    
    def __init__(self):
        self.port1 = OPTEN1_ID
        self.port2 = OPTEN2_ID
        self.port3 = OPTEN3_ID
        self.port4 = OPTEN4_ID
        self.baudrate = BAUDRATE
        self.serial_reader1, self.serial_reader2, self.serial_reader3, self.serial_reader4 = None, None, None, None
        self.serial_com1, self.serial_com2, self.serial_com3, self.serial_com4 = None, None, None, None
        self.connections = {self.port1: False, 
                            self.port2: False,
                            self.port3: False,
                            self.port4: False}
        
    def connect_serial(self, port):
        try:
            serial_com = serial.Serial(port, self.baudrate)
            print(f"Connected to {port}")
        except serial.SerialException as e:
            print(f"{port} not available")
            return None
        else:
            serial_com.setDTR(False)
            time.sleep(1)
            serial_com.flushInput()
            serial_com.setDTR(True)
            print(f"{port} is reset")
            return serial_com

    def connect(self):
        
        self.serial_com1 = self.connect_serial(self.port1)
        self.serial_com2 = self.connect_serial(self.port2)
        self.serial_com3 = self.connect_serial(self.port3)
        self.serial_com4 = self.connect_serial(self.port4)
        
        if self.serial_com1 is not None:
            self.connections[self.port1] = True
        if self.serial_com2 is not None:
            self.connections[self.port2] = True
        if self.serial_com3 is not None:
            self.connections[self.port3] = True
        if self.serial_com4 is not None:
            self.connections[self.port4] = True
            
        return self.connections[self.port1], self.connections[self.port2], self.connections[self.port3], self.connections[self.port4]
            
    def start_burst(self):
        print("\nStarting optical encoders in burst mode")
        
        self.connect()
        if not self.connections[self.port1] and not self.connections[self.port2] and not self.connections[self.port3] and not self.connections[self.port4]:
            print("No optical encoders available")
            return False
        
        if self.connections[self.port1]:
            self.serial_reader1 = SerialReader(self.serial_com1, mode="burst")
            self.serial_reader1.start()
        if self.connections[self.port2]:
            self.serial_reader2 = SerialReader(self.serial_com2, mode="burst", flip_x=True, flip_y=True)
            self.serial_reader2.start()
        if self.connections[self.port3]:
            self.serial_reader3 = SerialReader(self.serial_com3, mode="burst")
            self.serial_reader3.start()
        if self.connections[self.port4]:
            self.serial_reader4 = SerialReader(self.serial_com4, mode="burst", flip_x=True, flip_y=True)
            self.serial_reader4.start()
            
        if self.connections[self.port1]:
            while self.serial_reader1.initialised is False:
                time.sleep(0.1)
        if self.connections[self.port2]:
            while self.serial_reader2.initialised is False:
                time.sleep(0.1)
        if self.connections[self.port3]:
            while self.serial_reader3.initialised is False:
                time.sleep(0.1)
        if self.connections[self.port4]:
            while self.serial_reader4.initialised is False:
                time.sleep(0.1)
        time.sleep(1.5)
        
        if self.connections[self.port1]:
            print(f"{self.port1} optical encoder ready")
        if self.connections[self.port2]:
            print(f"{self.port2} optical encoder ready")
        if self.connections[self.port3]:
            print(f"{self.port3} optical encoder ready")
        if self.connections[self.port4]:
            print(f"{self.port4} optical encoder ready")
        print("")
            
    def start_camera(self):
        print("\nStarting optical encoders in camera mode")
        
        self.connect()
        if not self.connections[self.port1] and not self.connections[self.port2]:
            print("No optical encoders available")
            return False
        
        if self.connections[self.port1]:
            self.serial_reader1 = SerialReader(self.serial_com1, mode="camera")
            self.serial_reader1.start()
        if self.connections[self.port2]:
            self.serial_reader2 = SerialReader(self.serial_com2, mode="camera")
            self.serial_reader2.start()
        if self.connections[self.port3]:
            self.serial_reader3 = SerialReader(self.serial_com3, mode="camera")
            self.serial_reader3.start()
        if self.connections[self.port4]:
            self.serial_reader4 = SerialReader(self.serial_com4, mode="camera")
            self.serial_reader4.start()
            
        if self.connections[self.port1]:
            while self.serial_reader1.initialised is False:
                time.sleep(0.1)
        if self.connections[self.port2]:
            while self.serial_reader2.initialised is False:
                time.sleep(0.1)
        if self.connections[self.port3]:
            while self.serial_reader3.initialised is False:
                time.sleep(0.1)
        if self.connections[self.port4]:
            while self.serial_reader4.initialised is False:
                time.sleep(0.1)
        time.sleep(1.5)
        
        if self.connections[self.port1]:
            print(f"{self.port1} optical encoder ready")
        if self.connections[self.port2]:
            print(f"{self.port2} optical encoder ready")
        if self.connections[self.port3]:
            print(f"{self.port3} optical encoder ready")
        if self.connections[self.port4]:
            print(f"{self.port4} optical encoder ready")
        print("")
        
    def close(self):
        
        if not self.connections[self.port1] and not self.connections[self.port2] and not self.connections[self.port3] and not self.connections[self.port4]:
            return
        
        print("\nClosing optical encoders")
        if self.connections[self.port1]:
            self.serial_reader1.stop()
            self.serial_reader1.wait()
            self.serial_com1.close()
            print(f"{self.port1} closed")
        if self.connections[self.port2]:
            self.serial_reader2.stop()
            self.serial_reader2.wait()
            self.serial_com2.close()
            print(f"{self.port2} closed")
        if self.connections[self.port3]:
            self.serial_reader3.stop()
            self.serial_reader3.wait()
            self.serial_com3.close()
            print(f"{self.port3} closed")
        if self.connections[self.port4]:
            self.serial_reader4.stop()
            self.serial_reader4.wait()
            self.serial_com4.close()
            print(f"{self.port4} closed")
        
        
if __name__ == "__main__":
    opt = Optical4()
    opt.start_burst()
    time.sleep(2)
    opt.close()
