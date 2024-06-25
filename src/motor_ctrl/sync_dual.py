
import json
import time
from dynamixel_sdk import *  # Uses Dynamixel SDK library

# Load configuration from JSON file
with open('src/motor_ctrl/config.json', 'r') as config_file:
    config = json.load(config_file)

# Extract settings from the config dictionary
DXL1_ID = config['DXL1_ID']
DXL2_ID = config['DXL2_ID']
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
    "PRESENT_CURRENT": 2,
    "PRESENT_VELOCITY": 4,
    "PRESENT_POSITION": 4,
    "PRESENT_INPUT_VOLTAGE": 2,
    "PRESENT_TEMPERATURE": 2
}

PROTOCOL_VERSION = 2.0  # Protocol version used by the Dynamixel

class Dynamixel:
    def __init__(self):
        self.port_handler = PortHandler(DEVICENAME)
        self.packet_handler = PacketHandler(PROTOCOL_VERSION)
        self.init_sync_handlers()
        self.motor1_pos0 = 0
        self.motor2_pos0 = 0
        self.motor_modes = {DXL1_ID: None, DXL2_ID: None}
        
    def init_sync_handlers(self):
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
        
    def open_port(self):
        if not self.port_handler.openPort():
            raise IOError("Failed to open port")
        if not self.port_handler.setBaudRate(BAUDRATE):
            raise IOError("Failed to set baudrate")
        print("Port opened and baudrate set")

    def close_port(self):
        self.port_handler.closePort()
        print("Attempting to close port")

    def reboot(self, motor_id):
        comm_result, error = self.packet_handler.reboot(self.port_handler, motor_id)
        self.check_comm_status(comm_result, error, f"Rebooting motor ID {motor_id}")
        time.sleep(0.5)
        print(f"ID {motor_id} rebooted")

    def check_comm_status(self, comm_result, error, action):
        if comm_result != COMM_SUCCESS:
            print(f"{action} failed: {self.packet_handler.getTxRxResult(comm_result)}")
        elif error != 0:
            print(f"{action} error: {self.packet_handler.getRxPacketError(error)}")

    def _write_register(self, motor_id, address, value):
        comm_result, error = self.packet_handler.write1ByteTxRx(self.port_handler, motor_id, address, value)
        self.check_comm_status(comm_result, error, f"Writing to register {address} for ID {motor_id}")

    #### Torque & Modes ####

    def _set_torque(self, motor_id, enable):
        value = 1 if enable else 0
        self._write_register(motor_id, ADDR["TORQUE_ENABLE"], value)

    def enable_torque(self, motor_id):
        self._set_torque(motor_id, True)
        self.turn_LED_on(motor_id)
        print(f"ID {motor_id} torque enabled")

    def disable_torque(self, motor_id):
        self._set_torque(motor_id, False)
        self.turn_LED_off(motor_id)
        print(f"ID {motor_id} torque disabled")
    
    # Reads current limit (1 = 1 mA)
    def get_current_limit(self, motor_id):
        return self.read_sync_data(self.sync_read_current_limit, motor_id, ADDR["CURRENT_LIMIT"], LEN["CURRENT_LIMIT"])

    # Sets current limit (1 = 1 mA)
    def set_current_limit(self, motor_id, current):
        current = int(current)
        self.disable_torque(motor_id)  # Torque must be disabled to change current limit
        comm_result, error = self.packet_handler.write2ByteTxRx(self.port_handler, motor_id, ADDR["CURRENT_LIMIT"], current)
        self.check_comm_status(comm_result, error, f"Setting current limit for ID {motor_id}")
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

    def read_sync_data(self, sync_read, motor_id, address, length):
        sync_read.clearParam()
        if not sync_read.addParam(motor_id):
            raise RuntimeError(f"GroupSyncRead addparam failed for ID {motor_id}")
        comm_result = sync_read.txRxPacket()
        self.check_comm_status(comm_result, 0, f"Reading data from address {address} for ID {motor_id}")
        if not sync_read.isAvailable(motor_id, address, length):
            raise RuntimeError(f"GroupSyncRead getdata failed for ID {motor_id}")
        data = sync_read.getData(motor_id, address, length)
        if length == 2 and data > 32768:
            data -= 65536
        elif length == 4 and data > 2147483648:
            data -= 4294967296
        return data

    def get_current(self, motor_id):
        return self.read_sync_data(self.sync_read_current, motor_id, ADDR["PRESENT_CURRENT"], LEN["PRESENT_CURRENT"])
    
    def get_voltage(self, motor_id):
        return self.read_sync_data(self.sync_read_voltage, motor_id, ADDR["PRESENT_INPUT_VOLTAGE"], LEN["PRESENT_INPUT_VOLTAGE"])
    
    def get_temperature(self, motor_id):
        return self.read_sync_data(self.sync_read_temperature, motor_id, ADDR["PRESENT_TEMPERATURE"], LEN["PRESENT_TEMPERATURE"])
    
    #### Profile ####
    
    def get_profile_acceleration(self, motor_id):
        return self.read_sync_data(self.sync_read_profile_acceleration, motor_id, ADDR["PROFILE_ACCELERATION"], LEN["PROFILE_ACCELERATION"])
    
    def set_profile_acceleration(self, motor_id, acceleration):
        self.write_data(motor_id, ADDR["PROFILE_ACCELERATION"], acceleration, 4, "profile acceleration")
    
    def get_profile_velocity(self, motor_id):
        return self.read_sync_data(self.sync_read_profile_velocity, motor_id, ADDR["PROFILE_VELOCITY"], LEN["PROFILE_VELOCITY"])
    
    def set_profile_velocity(self, motor_id, velocity):
        self.write_data(motor_id, ADDR["PROFILE_VELOCITY"], velocity, 4, "profile velocity")

    def write_data(self, motor_id, address, data, length, description):
        data = int(data)
        write_method = {1: self.packet_handler.write1ByteTxRx, 2: self.packet_handler.write2ByteTxRx, 4: self.packet_handler.write4ByteTxRx}[length]
        comm_result, error = write_method(self.port_handler, motor_id, address, data)
        self.check_comm_status(comm_result, error, f"Setting {description} for ID {motor_id}")
    
    #### Position ####

    def get_position(self, motor_id):
        return self.read_sync_data(self.sync_read_position, motor_id, ADDR["PRESENT_POSITION"], LEN["PRESENT_POSITION"])
            
    def set_position(self, motor_id, position, mode="extpos"):
        if mode not in ["extpos", "curpos"]:
            raise ValueError("Invalid mode")
        self.set_mode(motor_id, mode)
        self.write_position(motor_id, position)

    def write_position(self, motor_id, position):
        position_byte = [DXL_LOBYTE(DXL_LOWORD(position)), DXL_HIBYTE(DXL_LOWORD(position)), DXL_LOBYTE(DXL_HIWORD(position)), DXL_HIBYTE(DXL_HIWORD(position))]
        self.sync_write_position.clearParam()
        if not self.sync_write_position.addParam(motor_id, position_byte):
            raise RuntimeError(f"GroupSyncWrite addparam failed for ID {motor_id}")
        comm_result = self.sync_write_position.txPacket()
        self.check_comm_status(comm_result, 0, f"Writing position for ID {motor_id}")

    def home_position(self, motor_id):
        if motor_id == DXL1_ID:
            self.motor1_pos0 = self.get_position(motor_id)
        elif motor_id == DXL2_ID:
            self.motor2_pos0 = self.get_position(motor_id)
        print(f"ID {motor_id} homed")

    #### Velocity ####

    def get_velocity(self, motor_id):
        return self.read_sync_data(self.sync_read_velocity, motor_id, ADDR["PRESENT_VELOCITY"], LEN["PRESENT_VELOCITY"])

    def set_velocity(self, motor_id, velocity):
        self.set_mode(motor_id, "vel")
        self.write_data(motor_id, ADDR["GOAL_VELOCITY"], velocity, 4, "velocity")
            
    #### Higher Level ####
    
    def set_dualpos(self, pos1, pos2, mode="curpos"):
        self.set_mode(DXL1_ID, mode)
        self.set_mode(DXL2_ID, mode)
        self.set_position(DXL1_ID, pos1 + self.motor1_pos0, mode)
        self.set_position(DXL2_ID, pos2 + self.motor2_pos0, mode)        
    
    def set_dualvel(self, vel1, vel2, dur, brake=True):
        BUFF = 0.2
        if dur < BUFF:
            print(f"Duration must be greater than {BUFF}s")
            self.stop_motors()
            return
        self.set_velocity(DXL1_ID, vel1)
        self.set_velocity(DXL2_ID, vel2)
        time.sleep(dur - BUFF)
        if brake:
            self.stop_motors()
        else:
            self.disable_torque(DXL1_ID)
            self.disable_torque(DXL2_ID)
            time.sleep(BUFF)
            self.enable_torque(DXL1_ID)
            self.enable_torque(DXL2_ID)
    
    def stop_motors(self):
        self.set_velocity(DXL1_ID, 0)
        self.set_velocity(DXL2_ID, 0)

#### Main ####

if __name__ == "__main__":
    dnx = Dynamixel()
    try:
        dnx.open_port()
        dnx.enable_torque(DXL1_ID)
        dnx.enable_torque(DXL2_ID)
        
        dnx.set_velocity(DXL2_ID, 20)
        time.sleep(2)
        dnx.set_velocity(DXL2_ID, 0)
        
    finally:
        dnx.disable_torque(DXL1_ID)
        dnx.disable_torque(DXL2_ID)
        dnx.close_port()
