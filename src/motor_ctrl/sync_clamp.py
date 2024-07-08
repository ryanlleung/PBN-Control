
import json
import time
import threading
from dynamixel_sdk import *  # Uses Dynamixel SDK library

# Load configuration from JSON file
with open('src/motor_ctrl/config_clamp.json', 'r') as config_file:
    config = json.load(config_file)

# Extract settings from the config dictionary
MOTOR_IDS = {
    "MOTOR1_ID": config['MOTOR1_ID'],
    "MOTOR2_ID": config['MOTOR2_ID'],
    "MOTOR3_ID": config['MOTOR3_ID'],
    "MOTOR4_ID": config['MOTOR4_ID'],
    "MOTOR5_ID": config['MOTOR5_ID'],
    "MOTOR6_ID": config['MOTOR6_ID']
}
MOTOR1_ID = MOTOR_IDS["MOTOR1_ID"]
MOTOR2_ID = MOTOR_IDS["MOTOR2_ID"]
MOTOR3_ID = MOTOR_IDS["MOTOR3_ID"]
MOTOR4_ID = MOTOR_IDS["MOTOR4_ID"]
MOTOR5_ID = MOTOR_IDS["MOTOR5_ID"]
MOTOR6_ID = MOTOR_IDS["MOTOR6_ID"]

BAUDRATE = config['BAUDRATE']
DEVICENAME = config['DEVICENAME']

# Control table addresses and lengths
ADDR = {
    "OPERATING_MODE": 11,
    "CURRENT_LIMIT": 38,
    "TORQUE_ENABLE": 64,
    "LED": 65,
    "GOAL_VELOCITY": 104,
    "PROFILE_ACCELERATION": 108,
    "PROFILE_VELOCITY": 112,
    "GOAL_POSITION": 116,
    "MOVING_STATUS": 123,
    "PRESENT_CURRENT": 126,
    "PRESENT_VELOCITY": 128,
    "PRESENT_POSITION": 132,
    "PRESENT_INPUT_VOLTAGE": 144,
    "PRESENT_TEMPERATURE": 146
}

LEN = {
    "CURRENT_LIMIT": 2,
    "GOAL_VELOCITY": 4,
    "PROFILE_ACCELERATION": 4,
    "PROFILE_VELOCITY": 4,
    "GOAL_POSITION": 4,
    "MOVING_STATUS": 1,
    "PRESENT_CURRENT": 2,
    "PRESENT_VELOCITY": 4,
    "PRESENT_POSITION": 4,
    "PRESENT_INPUT_VOLTAGE": 2,
    "PRESENT_TEMPERATURE": 2
}

PROTOCOL_VERSION = 2.0  # Protocol version used by the Dynamixel

# Class for controlling 6 Dynamixel motors
# Methods starting with an underscore are helper methods, not meant to be called directly
class Dynamixel6:
    
    def __init__(self):
        self.port_handler = PortHandler(DEVICENAME)
        self.packet_handler = PacketHandler(PROTOCOL_VERSION)
        self._init_sync_handlers()
        self.motor_pos0 = {motor_id: 0 for motor_id in MOTOR_IDS.values()}
        self.motor_modes = {motor_id: "" for motor_id in MOTOR_IDS.values()}
        self.lock = threading.Lock()
        self.motor_threads = {motor_id: threading.Thread() for motor_id in MOTOR_IDS.values()}
        self.motor_arrived_events = {motor_id: threading.Event() for motor_id in MOTOR_IDS.values()}
        
        self.clamp1_pos0 = 0
        self.clamp2_pos0 = 0
        with open('src/motor_ctrl/clamp1_pos.json', 'r') as config_file:
            self.clamp1_pos = json.load(config_file)
        with open('src/motor_ctrl/clamp2_pos.json', 'r') as config_file:
            self.clamp2_pos = json.load(config_file)
        
    def _init_sync_handlers(self):
        self.sync_read_position = GroupSyncRead(self.port_handler, self.packet_handler, ADDR["PRESENT_POSITION"], LEN["PRESENT_POSITION"])
        self.sync_write_position = GroupSyncWrite(self.port_handler, self.packet_handler, ADDR["GOAL_POSITION"], LEN["GOAL_POSITION"])
        self.sync_read_velocity = GroupSyncRead(self.port_handler, self.packet_handler, ADDR["PRESENT_VELOCITY"], LEN["PRESENT_VELOCITY"])
        self.sync_write_velocity = GroupSyncWrite(self.port_handler, self.packet_handler, ADDR["GOAL_VELOCITY"], LEN["GOAL_VELOCITY"])
        self.sync_read_current = GroupSyncRead(self.port_handler, self.packet_handler, ADDR["PRESENT_CURRENT"], LEN["PRESENT_CURRENT"])
        self.sync_read_voltage = GroupSyncRead(self.port_handler, self.packet_handler, ADDR["PRESENT_INPUT_VOLTAGE"], LEN["PRESENT_INPUT_VOLTAGE"])
        self.sync_read_temperature = GroupSyncRead(self.port_handler, self.packet_handler, ADDR["PRESENT_TEMPERATURE"], LEN["PRESENT_TEMPERATURE"])
        self.sync_read_current_limit = GroupSyncRead(self.port_handler, self.packet_handler, ADDR["CURRENT_LIMIT"], LEN["CURRENT_LIMIT"])
        self.sync_read_profile_acceleration = GroupSyncRead(self.port_handler, self.packet_handler, ADDR["PROFILE_ACCELERATION"], LEN["PROFILE_ACCELERATION"])
        self.sync_read_profile_velocity = GroupSyncRead(self.port_handler, self.packet_handler, ADDR["PROFILE_VELOCITY"], LEN["PROFILE_VELOCITY"])
        self.sync_read_moving_status = GroupSyncRead(self.port_handler, self.packet_handler, ADDR["MOVING_STATUS"], LEN["MOVING_STATUS"])

    def _check_comm_status(self, comm_result, error, action):
        if comm_result != COMM_SUCCESS:
            print(f"{action} failed: {self.packet_handler.getTxRxResult(comm_result)}")
        elif error != 0:
            print(f"{action} error: {self.packet_handler.getRxPacketError(error)}")

    def _write_register(self, motor_id, address, value):
        with self.lock:
            comm_result, error = self.packet_handler.write1ByteTxRx(self.port_handler, motor_id, address, value)
        self._check_comm_status(comm_result, error, f"Writing to register {address} for ID {motor_id}")

    def _write_data(self, motor_id, address, data, length, description):
        data = int(data)
        write_method = {1: self.packet_handler.write1ByteTxRx, 
                        2: self.packet_handler.write2ByteTxRx, 
                        4: self.packet_handler.write4ByteTxRx}[length]
        comm_result, error = write_method(self.port_handler, motor_id, address, data)
        self._check_comm_status(comm_result, error, f"Setting {description} for ID {motor_id}")
    
    def _read_sync_data(self, sync_read, motor_id, address, length):
        with self.lock:
            sync_read.clearParam()
            if not sync_read.addParam(motor_id):
                raise RuntimeError(f"GroupSyncRead addparam failed for ID {motor_id}")
            comm_result = sync_read.txRxPacket()
        self._check_comm_status(comm_result, 0, f"Reading data from address {address} for ID {motor_id}")
        if not sync_read.isAvailable(motor_id, address, length):
            raise RuntimeError(f"GroupSyncRead getdata failed for ID {motor_id}")
        data = sync_read.getData(motor_id, address, length)
        if length == 2 and data > 32768:
            data -= 65536
        elif length == 4 and data > 2147483648:
            data -= 4294967296
        return data
    
    # Opens the port and sets the baudrate
    def open_port(self):
        with self.lock:
            if not self.port_handler.openPort():
                raise IOError("Failed to open port")
            if not self.port_handler.setBaudRate(BAUDRATE):
                raise IOError("Failed to set baudrate")
            print("Port opened and baudrate set")

    # Closes the port
    def close_port(self):
        with self.lock:
            self.port_handler.closePort()
            print("Attempting to close port")

    # Reboots the motor
    def reboot(self, motor_id):
        with self.lock:
            comm_result, error = self.packet_handler.reboot(self.port_handler, motor_id)
        self._check_comm_status(comm_result, error, f"Rebooting motor ID {motor_id}")
        time.sleep(0.5)
        print(f"ID {motor_id} rebooted")

    #### Torque & Modes ####

    def _set_torque(self, motor_id, enable):
        value = 1 if enable else 0
        self._write_register(motor_id, ADDR["TORQUE_ENABLE"], value)

    # Enables torque
    def enable_torque(self, motor_id):
        self._set_torque(motor_id, True)
        self.turn_LED_on(motor_id)
        print(f"ID {motor_id} torque enabled")

    # Disables torque
    def disable_torque(self, motor_id):
        self._set_torque(motor_id, False)
        self.turn_LED_off(motor_id)
        print(f"ID {motor_id} torque disabled")
    
    # Reads current limit (1 = 1 mA)
    def get_current_limit(self, motor_id):
        return self._read_sync_data(self.sync_read_current_limit, motor_id, ADDR["CURRENT_LIMIT"], LEN["CURRENT_LIMIT"])

    # Sets current limit (1 = 1 mA)
    def set_current_limit(self, motor_id, current):
        current = int(current)
        self.disable_torque(motor_id)  # Torque must be disabled to change current limit
        comm_result, error = self.packet_handler.write2ByteTxRx(self.port_handler, motor_id, ADDR["CURRENT_LIMIT"], current)
        self._check_comm_status(comm_result, error, f"Setting current limit for ID {motor_id}")
        self.reboot(motor_id)  # Reboot required for current limit to take effect
        self.enable_torque(motor_id)  # Re-enable torque after reboot

    # Sets mode
    def set_mode(self, motor_id, mode):
        if self.motor_modes[motor_id] == mode:
            return
        self.disable_torque(motor_id)  # Torque must be disabled to change mode
        mode_settings = {
            "pos": (3, "Position"),
            "extpos": (4, "Extended position"),
            "curpos": (5, "Current-based position"),
            "vel": (1, "Velocity"),
            "pwm": (16, "PWM"),
            "cur": (0, "Current")
        }
        if mode in mode_settings:
            register_value, mode_description = mode_settings[mode]
            self._write_register(motor_id, ADDR["OPERATING_MODE"], register_value)
            print(f"ID {motor_id} set to {mode_description} mode")
            self.motor_modes[motor_id] = mode
        else:
            raise ValueError("Invalid mode")
        self.enable_torque(motor_id)  # Re-enable torque after changing mode

    #### LED ####

    def _set_LED(self, motor_id, enable):
        value = 1 if enable else 0
        self._write_register(motor_id, ADDR["LED"], value)

    def turn_LED_on(self, motor_id):
        self._set_LED(motor_id, True)

    def turn_LED_off(self, motor_id):
        self._set_LED(motor_id, False)
        
    #### Information ####

    def get_current(self, motor_id):
        return self._read_sync_data(self.sync_read_current, motor_id, ADDR["PRESENT_CURRENT"], LEN["PRESENT_CURRENT"])
    
    def get_voltage(self, motor_id):
        return self._read_sync_data(self.sync_read_voltage, motor_id, ADDR["PRESENT_INPUT_VOLTAGE"], LEN["PRESENT_INPUT_VOLTAGE"])
    
    def get_temperature(self, motor_id):
        return self._read_sync_data(self.sync_read_temperature, motor_id, ADDR["PRESENT_TEMPERATURE"], LEN["PRESENT_TEMPERATURE"])
    
    #### Moving Monitoring ####
    
    def get_moving_status(self, motor_id):
        return self._read_sync_data(self.sync_read_moving_status, motor_id, ADDR["MOVING_STATUS"], LEN["MOVING_STATUS"])
    
    def has_arrived(self, motor_id):
        return self.get_moving_status(motor_id) & 0b01
    
    def _wait_for_motor(self, motor_id):
        while not self.motor_arrived_events[motor_id].is_set():
            time.sleep(0.1)
            self.motor1_arrived = self.has_arrived(motor_id)
            if self.motor1_arrived:
                self.motor_arrived_events[motor_id].set()
                print(f"ID {motor_id} has arrived")
    
    #### Profile ####

    def get_profile_acceleration(self, motor_id):
        return self._read_sync_data(self.sync_read_profile_acceleration, motor_id, ADDR["PROFILE_ACCELERATION"], LEN["PROFILE_ACCELERATION"])
    
    def set_profile_acceleration(self, motor_id, acceleration):
        self._write_data(motor_id, ADDR["PROFILE_ACCELERATION"], acceleration, 4, "profile acceleration")
    
    def get_profile_velocity(self, motor_id):
        return self._read_sync_data(self.sync_read_profile_velocity, motor_id, ADDR["PROFILE_VELOCITY"], LEN["PROFILE_VELOCITY"])
    
    def set_profile_velocity(self, motor_id, velocity):
        self._write_data(motor_id, ADDR["PROFILE_VELOCITY"], velocity, 4, "profile velocity")

    #### Position Control ####

    def _write_position(self, motor_id, position):
        position_byte = [DXL_LOBYTE(DXL_LOWORD(position)), DXL_HIBYTE(DXL_LOWORD(position)), DXL_LOBYTE(DXL_HIWORD(position)), DXL_HIBYTE(DXL_HIWORD(position))]
        self.sync_write_position.clearParam()
        if not self.sync_write_position.addParam(motor_id, position_byte):
            raise RuntimeError(f"GroupSyncWrite addparam failed for ID {motor_id}")
        comm_result = self.sync_write_position.txPacket()
        self._check_comm_status(comm_result, 0, f"Writing position for ID {motor_id}")

    # Returns the current position of the motor
    def get_position(self, motor_id):
        return self._read_sync_data(self.sync_read_position, motor_id, ADDR["PRESENT_POSITION"], LEN["PRESENT_POSITION"])
    
    # Sets the position of the motor, but does not wait for the motor to reach the position
    def set_position(self, motor_id, position, vel, mode="extpos"):
        if mode not in ["extpos", "curpos"]:
            raise ValueError("Invalid mode")
        self.set_mode(motor_id, mode)
        self.set_profile_velocity(motor_id, vel)
        self._write_position(motor_id, position)
    
    # Defines the current position as the new position 0
    def define_position0(self, motor_id):
        self.motor_pos0[motor_id] = self.get_position(motor_id)
        print(f"ID {motor_id} pos0 set to {self.motor_pos0[motor_id]}")
    
    # Defines the current positions as the new positions 0
    def define_quadpos0(self):
        for motor_id in MOTOR_IDS.values():
            self.define_position0(motor_id)
    
    # Moves the motor to the specified position and waits for it to reach the position
    def goto_position(self, motor_id, position, vel, mode="extpos"):
        self.set_position(motor_id, position, vel, mode)
        self.motor_arrived_events[motor_id].clear()
        self.motor_threads[motor_id] = threading.Thread(target=self._wait_for_motor, args=(motor_id,))
        self.motor_threads[motor_id].start()
        self.motor_threads[motor_id].join()
    
    # Moves the motors to the specified positions and waits for all motors to reach their positions
    def goto_quadpos(self, pos1, pos2, pos3, pos4, vel, mode="extpos"):
        for motor_id, pos in zip(MOTOR_IDS.values(), [pos1, pos2, pos3, pos4]):
            self.set_position(motor_id, pos, vel, mode)
        for motor_id in MOTOR_IDS.values():
            self.motor_arrived_events[motor_id].clear()
            self.motor_threads[motor_id] = threading.Thread(target=self._wait_for_motor, args=(motor_id,))
            self.motor_threads[motor_id].start()
        for motor_id in MOTOR_IDS.values():
            self.motor_threads[motor_id].join()
    
    # Moves the clamps to the specified positions and waits for all motors to reach their positions
    def _goto_clamppos(self, pos5, pos6, vel, mode="extpos"):
        for motor_id, pos in zip([MOTOR5_ID, MOTOR6_ID], [pos5, pos6]):
            self.set_position(motor_id, pos, vel, mode)
        for motor_id in [MOTOR5_ID, MOTOR6_ID]:
            self.motor_arrived_events[motor_id].clear()
            self.motor_threads[motor_id] = threading.Thread(target=self._wait_for_motor, args=(motor_id,))
            self.motor_threads[motor_id].start()
        for motor_id in [MOTOR5_ID, MOTOR6_ID]:
            self.motor_threads[motor_id].join()

    #### Velocity Control ####

    # Returns the current velocity of the motor
    def get_velocity(self, motor_id):
        return self._read_sync_data(self.sync_read_velocity, motor_id, ADDR["PRESENT_VELOCITY"], LEN["PRESENT_VELOCITY"])

    # Sets the velocity of the motor
    def set_velocity(self, motor_id, velocity):
        self.set_mode(motor_id, "vel")
        self._write_data(motor_id, ADDR["GOAL_VELOCITY"], velocity, 4, "velocity")
            
    #### Higher Level ####

    def set_dualvel(self, vel1, vel2, dur, brake=True):
        BUFF = 0.2
        if dur < BUFF:
            print(f"Duration must be greater than {BUFF}s")
            self.stop_motors()
            return
        self.set_velocity(MOTOR1_ID, vel1)
        self.set_velocity(MOTOR2_ID, vel2)
        time.sleep(dur - BUFF)
        if brake:
            self.stop_motors()
        else:
            self.disable_torque(MOTOR1_ID)
            self.disable_torque(MOTOR2_ID)
            time.sleep(BUFF)
            self.enable_torque(MOTOR1_ID)
            self.enable_torque(MOTOR2_ID)

    def set_quadvel(self, vel1, vel2, vel3, vel4, dur, brake=True):
        BUFF = 0.2
        if dur < BUFF:
            print(f"Duration must be greater than {BUFF}s")
            self.stop_motors()
            return
        self.set_velocity(MOTOR1_ID, vel1)
        self.set_velocity(MOTOR2_ID, vel2)
        self.set_velocity(MOTOR3_ID, vel3)
        self.set_velocity(MOTOR4_ID, vel4)
        time.sleep(dur - BUFF)
        if brake:
            self.stop_motors()
        else:
            self.disable_torque(MOTOR1_ID)
            self.disable_torque(MOTOR2_ID)
            self.disable_torque(MOTOR3_ID)
            self.disable_torque(MOTOR4_ID)
            time.sleep(BUFF)
            self.enable_torque(MOTOR1_ID)
            self.enable_torque(MOTOR2_ID)
            self.enable_torque(MOTOR3_ID)
            self.enable_torque(MOTOR4_ID)
    
    def stop_motors(self):
        self.set_velocity(MOTOR1_ID, 0)
        self.set_velocity(MOTOR2_ID, 0)
        self.set_velocity(MOTOR3_ID, 0)
        self.set_velocity(MOTOR4_ID, 0)
        
    #### Clamp Settings ####
    
    def define_homeclamp(self):
        self.clamp1_pos0 = self.get_position(MOTOR5_ID)
        self.clamp2_pos0 = self.get_position(MOTOR6_ID)
        
    def define_homeclamp1(self):
        self.clamp1_pos0 = self.get_position(MOTOR5_ID)
        
    def define_homeclamp2(self):
        self.clamp2_pos0 = self.get_position(MOTOR6_ID)
        
    def define_restclamp1(self):
        self.clamp1_pos["rest"] = self.get_position(MOTOR5_ID) - self.clamp1_pos0
        
    def define_restclamp2(self):
        self.clamp2_pos["rest"] = self.get_position(MOTOR6_ID) - self.clamp2_pos0
        
    def define_lightclamp1(self):     
        self.clamp1_pos["light"] = self.get_position(MOTOR5_ID) - self.clamp1_pos0
        
    def define_lightclamp2(self):
        self.clamp2_pos["light"] = self.get_position(MOTOR6_ID) - self.clamp2_pos0
        
    def define_mediumclamp1(self):
        self.clamp1_pos["medium"] = self.get_position(MOTOR5_ID) - self.clamp1_pos0
        
    def define_mediumclamp2(self):
        self.clamp2_pos["medium"] = self.get_position(MOTOR6_ID) - self.clamp2_pos0
        
    def define_heavyclamp1(self):
        self.clamp1_pos["heavy"] = self.get_position(MOTOR5_ID) - self.clamp1_pos0
        
    def define_heavyclamp2(self):
        self.clamp2_pos["heavy"] = self.get_position(MOTOR6_ID) - self.clamp2_pos0
        
    def save_clamp1pos(self):
        with open('src/motor_ctrl/clamp1_pos.json', 'w') as config_file:
            json.dump(self.clamp1_pos, config_file, indent=2)
            print("Clamp1 positions saved")
            
    def save_clamp2pos(self):
        with open('src/motor_ctrl/clamp2_pos.json', 'w') as config_file:
            json.dump(self.clamp2_pos, config_file, indent=2)
            print("Clamp2 positions saved")
        
    #### Clamp Control ####
        
    def goto_clamp1(self, desc, vel=1500, mode="extpos"):
        if desc not in self.clamp1_pos:
            raise ValueError("Invalid description")
        if desc in ["home", "rest"]:
            vel = 2000
        pos = self.clamp1_pos[desc]
        print(f"Setting clamp1 to {desc} at {self.clamp1_pos0 + pos}")
        self.goto_position(MOTOR5_ID, self.clamp1_pos0 + pos, vel, mode)
        
    def goto_clamp2(self, desc, vel=1500, mode="extpos"):
        if desc not in self.clamp2_pos:
            raise ValueError("Invalid description")
        if desc in ["home", "rest"]:
            vel = 2000
        pos = self.clamp2_pos[desc]
        print(f"Setting clamp2 to {desc} at {self.clamp2_pos0 + pos}")
        self.goto_position(MOTOR6_ID, self.clamp2_pos0 + pos, vel, mode)
        
    def goto_clamp(self, desc1, desc2, vel=1500, mode="extpos"):
        if desc1 not in self.clamp1_pos or desc2 not in self.clamp2_pos:
            raise ValueError("Invalid description")
        if desc1 in ["home", "rest"]:
           vel = 2000
        if desc2 in ["home", "rest"]:
            vel = 2000
        pos1 = self.clamp1_pos[desc1]
        pos2 = self.clamp2_pos[desc2]
        print(f"Setting clamp1 to {desc1} at {self.clamp1_pos0 + pos1}")
        print(f"Setting clamp2 to {desc2} at {self.clamp2_pos0 + pos2}")
        self._goto_clamppos(self.clamp1_pos0 + pos1, self.clamp2_pos0 + pos2, vel, mode)
        
    def goto_clamp_home(self):
        self.goto_clamp("home", "home")
        
    def goto_clamp_rest(self):
        self.goto_clamp("rest", "rest")    
        
    def moving_1or3(self):
        self.goto_clamp("heavy", "light")
        
    def moving_2or4(self):
        self.goto_clamp("light", "heavy")
        
    def moving_Halves(self):
        self.goto_clamp("medium", "medium")
        
    def moving_All(self):
        self.goto_clamp("medium", "medium")
    
    #### Autohome ####
    
    def home_clamp1(self, current_limit=35):
        while True:
            self.set_velocity(MOTOR5_ID, -50)
            current_current = abs(self.get_current(MOTOR5_ID))
            print(f"Current: {current_current}")
            if current_current >= current_limit:
                break
        self.set_velocity(MOTOR5_ID, 0)
        self.define_homeclamp1()
        print(f"Clamp1 homed at {self.clamp1_pos0}")
        
    def home_clamp2(self, current_limit=35):
        while True:
            self.set_velocity(MOTOR6_ID, -50)
            current_current = abs(self.get_current(MOTOR6_ID))
            print(f"Current: {current_current}")
            if current_current >= current_limit:
                break
        self.set_velocity(MOTOR6_ID, 0)
        self.define_homeclamp2()
        print(f"Clamp2 homed at {self.clamp2_pos0}")

#### Main ####

if __name__ == "__main__":
    dnx = Dynamixel6()
    try:
        dnx.open_port()
        dnx.enable_torque(MOTOR1_ID)
        dnx.enable_torque(MOTOR2_ID)
        dnx.enable_torque(MOTOR3_ID)
        dnx.enable_torque(MOTOR4_ID)
        dnx.enable_torque(MOTOR5_ID)
        dnx.enable_torque(MOTOR6_ID)
        
        dnx.define_quadpos0()
        dnx.define_homeclamp1()
        dnx.define_homeclamp2()
        
        m1p0 = dnx.motor_pos0[MOTOR1_ID]
        m2p0 = dnx.motor_pos0[MOTOR2_ID]
        m3p0 = dnx.motor_pos0[MOTOR3_ID]
        m4p0 = dnx.motor_pos0[MOTOR4_ID]
        
        dnx.goto_clamp_rest()
        
        response = input("Press enter to start")
        if response == "":

            EXTEN = 1000
            EXVEL = 33
        
            dnx.moving_1or3()
            time.sleep(0.5)
            dnx.goto_quadpos(m1p0+EXTEN, m2p0, m3p0, m4p0, vel=EXVEL)
            time.sleep(0.5)
            dnx.goto_quadpos(m1p0, m2p0, m3p0, m4p0, vel=EXVEL)
            time.sleep(0.5)
            dnx.goto_quadpos(m1p0, m2p0, m3p0+EXTEN, m4p0, vel=EXVEL)
            time.sleep(0.5)
            dnx.goto_quadpos(m1p0, m2p0, m3p0, m4p0, vel=EXVEL)
            time.sleep(0.5)
            
            dnx.moving_2or4()
            time.sleep(0.5)
            dnx.goto_quadpos(m1p0, m2p0, m3p0, m4p0+EXTEN, vel=EXVEL)
            time.sleep(0.5)
            dnx.goto_quadpos(m1p0, m2p0, m3p0, m4p0, vel=EXVEL)
            time.sleep(0.5)
            dnx.goto_quadpos(m1p0, m2p0+EXTEN, m3p0, m4p0, vel=EXVEL)
            time.sleep(0.5)
            dnx.goto_quadpos(m1p0, m2p0, m3p0, m4p0, vel=EXVEL)
            time.sleep(0.5)
            
            dnx.moving_Halves()
            time.sleep(0.5)
            
            dnx.goto_quadpos(m1p0, m2p0, m3p0+EXTEN, m4p0+EXTEN, vel=EXVEL)
            time.sleep(0.5)
            dnx.goto_quadpos(m1p0, m2p0, m3p0, m4p0, vel=EXVEL)
            time.sleep(0.5)
            dnx.goto_quadpos(m1p0+EXTEN, m2p0+EXTEN, m3p0, m4p0, vel=EXVEL)
            time.sleep(0.5)
            dnx.goto_quadpos(m1p0, m2p0, m3p0, m4p0, vel=EXVEL)
            time.sleep(0.5)

            dnx.goto_quadpos(m1p0+EXTEN, m2p0, m3p0, m4p0+EXTEN, vel=EXVEL)
            time.sleep(0.5)
            dnx.goto_quadpos(m1p0, m2p0, m3p0, m4p0, vel=EXVEL)
            time.sleep(0.5)
            dnx.goto_quadpos(m1p0, m2p0+EXTEN, m3p0+EXTEN, m4p0, vel=EXVEL)
            time.sleep(0.5)
            dnx.goto_quadpos(m1p0, m2p0, m3p0, m4p0, vel=EXVEL)
            time.sleep(0.5)     
            
            dnx.moving_All()
            time.sleep(0.5)
            dnx.goto_quadpos(m1p0+EXTEN, m2p0+EXTEN, m3p0+EXTEN, m4p0+EXTEN, vel=EXVEL)
            time.sleep(0.5)
            dnx.goto_quadpos(m1p0, m2p0, m3p0, m4p0, vel=EXVEL)
            time.sleep(0.5)
        
        dnx.goto_clamp_home()

        
    finally:
        dnx.disable_torque(MOTOR1_ID)
        dnx.disable_torque(MOTOR2_ID)
        dnx.disable_torque(MOTOR3_ID)
        dnx.disable_torque(MOTOR4_ID)
        dnx.disable_torque(MOTOR5_ID)
        dnx.disable_torque(MOTOR6_ID)
        for motor_id in MOTOR_IDS.values():
            if dnx.motor_threads[motor_id].is_alive():
                dnx.motor_arrived_events[motor_id].set()
                dnx.motor_threads[motor_id].join()
        dnx.close_port()
