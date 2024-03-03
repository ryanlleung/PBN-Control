# Description: Synchronous control of two Dynamixel motors

from dynamixel_sdk import *                    # Uses Dynamixel SDK library


# Control table address
ADDR_OPERATING_MODE =         11
ADDR_CURRENT_LIMIT =          38

ADDR_TORQUE_ENABLE =          64
ADDR_LED =                    65
ADDR_STATUS_RETURN_LEVEL =    68
ADDR_REGISTERED_INSTRUCTION = 69
ADDR_HARDWARE_ERROR_STATUS =  70

ADDR_GOAL_PWM =               100
ADDR_GOAL_CURRENT =           102
ADDR_GOAL_VELOCITY =          104
ADDR_PROFILE_ACCELERATION =   108
ADDR_PROFILE_VELOCITY =       112
ADDR_GOAL_POSITION =          116

ADDR_MOVING =                 122
ADDR_MOVING_STATUS =          123

ADDR_PRESENT_PWM =            124
ADDR_PRESENT_CURRENT =        126
ADDR_PRESENT_VELOCITY =       128
ADDR_PRESENT_POSITION =       132
ADDR_PRESENT_INPUT_VOLTAGE =  144
ADDR_PRESENT_TEMPERATURE =    146

# Data Byte Length
LEN_CURRENT_LIMIT       = 2

LEN_GOAL_VELOCITY       = 4
LEN_PROFILE_ACCELERATION = 4
LEN_PROFILE_VELOCITY    = 4
LEN_GOAL_POSITION       = 4

LEN_PRESENT_CURRENT     = 2
LEN_PRESENT_VELOCITY    = 4
LEN_PRESENT_POSITION    = 4
LEN_PRESENT_INPUT_VOLTAGE = 2
LEN_PRESENT_TEMPERATURE = 2

# Protocol version
PROTOCOL_VERSION            = 2.0               # See which protocol version is used in the Dynamixel

# Device setting
DXL1_ID                     = 2                 # Dynamixel#1 ID : 1
DXL2_ID                     = 3                 # Dynamixel#1 ID : 2
BAUDRATE                    = 57600             # Dynamixel default baudrate : 57600
DEVICENAME                  = 'COM3'            # Check which port is being used on your controller
                                                # ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*"

#### Initialisation ####

class Dynamixel:

    def __init__(self):
        self.port_handler = PortHandler(DEVICENAME)
        self.packet_handler = PacketHandler(PROTOCOL_VERSION)
        self.sync_read_position = GroupSyncRead(self.port_handler, self.packet_handler, 
                                                ADDR_PRESENT_POSITION, LEN_PRESENT_POSITION)
        self.sync_write_position = GroupSyncWrite(self.port_handler, self.packet_handler,
                                                  ADDR_GOAL_POSITION, LEN_GOAL_POSITION)
        self.sync_read_velocity = GroupSyncRead(self.port_handler, self.packet_handler,
                                                ADDR_PRESENT_VELOCITY, LEN_PRESENT_VELOCITY)
        self.sync_write_velocity = GroupSyncWrite(self.port_handler, self.packet_handler,
                                                  ADDR_GOAL_VELOCITY, LEN_GOAL_VELOCITY)
        self.sync_read_current = GroupSyncRead(self.port_handler, self.packet_handler,
                                                  ADDR_PRESENT_CURRENT, LEN_PRESENT_CURRENT)
        self.sync_read_voltage = GroupSyncRead(self.port_handler, self.packet_handler,
                                               ADDR_PRESENT_INPUT_VOLTAGE, LEN_PRESENT_INPUT_VOLTAGE)
        self.sync_read_temperature = GroupSyncRead(self.port_handler, self.packet_handler,
                                                   ADDR_PRESENT_TEMPERATURE, LEN_PRESENT_TEMPERATURE)
        self.sync_read_current_limit = GroupSyncRead(self.port_handler, self.packet_handler,
                                                        ADDR_CURRENT_LIMIT, LEN_CURRENT_LIMIT)
        self.sync_read_profile_acceleration = GroupSyncRead(self.port_handler, self.packet_handler,
                                                            ADDR_PROFILE_ACCELERATION, LEN_PROFILE_ACCELERATION)
        self.sync_read_profile_velocity = GroupSyncRead(self.port_handler, self.packet_handler,
                                                        ADDR_PROFILE_VELOCITY, LEN_PROFILE_VELOCITY)
        self.motor1_pos0 = 0
        self.motor2_pos0 = 0
        self.motor1_mode = None
        self.motor2_mode = None
        
    def open_port(self):
        if self.port_handler.openPort():
            print("Attempting to open port")
        else:
            print("Failed to open port")
            quit()

        if self.port_handler.setBaudRate(BAUDRATE):
            print("Attempting to set baudrate")
        else:
            print("Failed to set baudrate")
            quit()

    def close_port(self):
        self.port_handler.closePort()
        print("Attempting to close port")
        
    def reboot(self, id):
        comm_result, error = self.packet_handler.reboot(self.port_handler, id)
        if comm_result != COMM_SUCCESS:
            print("%s" % self.packet_handler.getTxRxResult(comm_result))
        elif error != 0:
            print("%s" % self.packet_handler.getRxPacketError(error))
        time.sleep(0.5)
        print(f"ID {id} rebooted")

    def _write_register(self, id, address, value):
        comm_result, error = self.packet_handler.write1ByteTxRx(self.port_handler, id, address, value)
        if comm_result != COMM_SUCCESS:
            print("%s" % self.packet_handler.getTxRxResult(comm_result))
            # raise Exception(f"Failed to write register {address} for ID {id}")
        elif error != 0:
            print("%s" % self.packet_handler.getRxPacketError(error))
            # raise Exception(f"Failed to write register {address} for ID {id}")
        return comm_result, error

    #### Torque & Modes ####

    def _set_torque(self, id, enable):
        value = 1 if enable else 0
        self._write_register(id, ADDR_TORQUE_ENABLE, value)

    def enable_torque(self, id):
        self._set_torque(id, True)
        self.turn_LED_on(id)
        print(f"ID {id} torque enabled")

    def disable_torque(self, id):
        self._set_torque(id, False)
        self.turn_LED_off(id)
        print(f"ID {id} torque disabled")
    
    # Reads current limit (1 = 1 mA)
    def get_current_limit(self, id):
        self.sync_read_current_limit.clearParam()
        add_param_result = self.sync_read_current_limit.addParam(id)
        if add_param_result != True:
            print("[ID:%03d] groupSyncRead addparam failed" % id)
            quit()
        comm_result = self.sync_read_current_limit.txRxPacket()
        if comm_result != COMM_SUCCESS:
            print("%s" % self.packet_handler.getTxRxResult(comm_result))
        getdata_result = self.sync_read_current_limit.isAvailable(id, ADDR_CURRENT_LIMIT, LEN_CURRENT_LIMIT)
        if getdata_result != True:
            print("[ID:%03d] groupSyncRead getdata failed" % id)
            quit()
        self.current_limit = self.sync_read_current_limit.getData(id, ADDR_CURRENT_LIMIT, LEN_CURRENT_LIMIT)
        return self.current_limit
        
    # Sets current limit (1 = 1 mA)
    def set_current_limit(self, id, current):
        self.get_current_limit(id)
        if current == self.current_limit:
            return
        self.disable_torque(id) # Torque must be disabled to change current limit
        current = int(current)
        comm_result, error = self.packet_handler.write2ByteTxRx(self.port_handler, id, ADDR_CURRENT_LIMIT, current)
        if comm_result != COMM_SUCCESS:
            print("%s" % self.packet_handler.getTxRxResult(comm_result))
        elif error != 0:
            print("%s" % self.packet_handler.getRxPacketError(error))
        else:
            print(f"ID {id} current limit set to {current}")
        self.reboot(id) # Reboot required for current limit to take effect
        self.enable_torque(id) # Re-enable torque after reboot

    # Sets mode
    def set_mode(self, id, mode):
        if id == DXL1_ID and self.motor1_mode == mode:
            return
        if id == DXL2_ID and self.motor2_mode == mode:
            return
        self.disable_torque(id) # Torque must be disabled to change mode
        mode_settings = {
            "pos": (3, "Position"), # Not useful
            "extpos": (4, "Extended position"),
            "curpos": (5, "Current-based position"),
            "vel": (1, "Velocity"),
            "pwm": (16, "PWM"),
            "cur": (0, "Current")
        }
        if mode in mode_settings:
            register_value, mode_description = mode_settings[mode]
            self._write_register(id, ADDR_OPERATING_MODE, register_value)
            print(f"ID {id} set to {mode_description} mode")
            if id == DXL1_ID:
                self.motor1_mode = mode
            elif id == DXL2_ID:
                self.motor2_mode = mode
        else:
            print("Invalid mode")
            quit()
        self.enable_torque(id) # Re-enable torque after changing mode

    #### LED ####

    def _set_LED(self, id, enable):
        value = 1 if enable else 0
        self._write_register(id, ADDR_LED, value)

    def turn_LED_on(self, id):
        self._set_LED(id, True)

    def turn_LED_off(self, id):
        self._set_LED(id, False)
        
    #### Information ####
    
    # Reads present current (1 = 1 mA)
    def get_current(self, id):
        self.sync_read_current.clearParam()
        add_param_result = self.sync_read_current.addParam(id)
        if add_param_result != True:
            print("[ID:%03d] groupSyncRead addparam failed" % id)
            quit()
        comm_result = self.sync_read_current.txRxPacket()
        if comm_result != COMM_SUCCESS:
            print("%s" % self.packet_handler.getTxRxResult(comm_result))
        getdata_result = self.sync_read_current.isAvailable(id, ADDR_PRESENT_CURRENT, LEN_PRESENT_CURRENT)
        if getdata_result != True:
            print("[ID:%03d] groupSyncRead getdata failed" % id)
            quit()
        current = self.sync_read_current.getData(id, ADDR_PRESENT_CURRENT, LEN_PRESENT_CURRENT)
        # Convert to signed int
        if current > 32768:
            current -= 65536
        return current
    
    # Reads present input voltage (1 = 0.1V)
    def get_voltage(self, id):
        self.sync_read_voltage.clearParam()
        add_param_result = self.sync_read_voltage.addParam(id)
        if add_param_result != True:
            print("[ID:%03d] groupSyncRead addparam failed" % id)
            quit()
        comm_result = self.sync_read_voltage.txRxPacket()
        if comm_result != COMM_SUCCESS:
            print("%s" % self.packet_handler.getTxRxResult(comm_result))
        getdata_result = self.sync_read_voltage.isAvailable(id, ADDR_PRESENT_INPUT_VOLTAGE, LEN_PRESENT_INPUT_VOLTAGE)
        if getdata_result != True:
            print("[ID:%03d] groupSyncRead getdata failed" % id)
            quit()
        voltage = self.sync_read_voltage.getData(id, ADDR_PRESENT_INPUT_VOLTAGE, LEN_PRESENT_INPUT_VOLTAGE)
        return voltage
    
    # Reads present temperature (1 = 1°C)
    def get_temperature(self, id):
        self.sync_read_temperature.clearParam()
        add_param_result = self.sync_read_temperature.addParam(id)
        if add_param_result != True:
            print("[ID:%03d] groupSyncRead addparam failed" % id)
            quit()
        comm_result = self.sync_read_temperature.txRxPacket()
        if comm_result != COMM_SUCCESS:
            print("%s" % self.packet_handler.getTxRxResult(comm_result))
        getdata_result = self.sync_read_temperature.isAvailable(id, ADDR_PRESENT_TEMPERATURE, LEN_PRESENT_TEMPERATURE)
        if getdata_result != True:
            print("[ID:%03d] groupSyncRead getdata failed" % id)
            quit()
        temperature = self.sync_read_temperature.getData(id, ADDR_PRESENT_TEMPERATURE, LEN_PRESENT_TEMPERATURE)
        return temperature
    
    #### Profile ####
    
    # Reads profile acceleration (1 = 214.577 rpm/m = 0.3745 rad/s^2)
    def get_profile_acceleration(self, id):
        self.sync_read_profile_acceleration.clearParam()
        add_param_result = self.sync_read_profile_acceleration.addParam(id)
        if add_param_result != True:
            print("[ID:%03d] groupSyncRead addparam failed" % id)
            quit()
        comm_result = self.sync_read_profile_acceleration.txRxPacket()
        if comm_result != COMM_SUCCESS:
            print("%s" % self.packet_handler.getTxRxResult(comm_result))
        getdata_result = self.sync_read_profile_acceleration.isAvailable(id, ADDR_PROFILE_ACCELERATION, LEN_PROFILE_ACCELERATION)
        if getdata_result != True:
            print("[ID:%03d] groupSyncRead getdata failed" % id)
            quit()
        acceleration = self.sync_read_profile_acceleration.getData(id, ADDR_PROFILE_ACCELERATION, LEN_PROFILE_ACCELERATION)
        return acceleration
    
    # Sets profile acceleration (1 = 214.577 rpm/m = 0.3745 rad/s^2)
    # !!! Resets after changing mode !!!
    def set_profile_acceleration(self, id, acceleration):
        acceleration = int(acceleration)
        comm_result, error = self.packet_handler.write4ByteTxRx(self.port_handler, id, ADDR_PROFILE_ACCELERATION, acceleration)
        if comm_result != COMM_SUCCESS:
            print("%s" % self.packet_handler.getTxRxResult(comm_result))
        elif error != 0:
            print("%s" % self.packet_handler.getRxPacketError(error))
        else:
            print(f"ID {id} profile acceleration set to {acceleration}")
    
    # Reads profile velocity (1 = 0.229 rpm = 0.02398 rad/s)
    def get_profile_velocity(self, id):
        self.sync_read_profile_velocity.clearParam()
        add_param_result = self.sync_read_profile_velocity.addParam(id)
        if add_param_result != True:
            print("[ID:%03d] groupSyncRead addparam failed" % id)
            quit()
        comm_result = self.sync_read_profile_velocity.txRxPacket()
        if comm_result != COMM_SUCCESS:
            print("%s" % self.packet_handler.getTxRxResult(comm_result))
        getdata_result = self.sync_read_profile_velocity.isAvailable(id, ADDR_PROFILE_VELOCITY, LEN_PROFILE_VELOCITY)
        if getdata_result != True:
            print("[ID:%03d] groupSyncRead getdata failed" % id)
            quit()
        velocity = self.sync_read_profile_velocity.getData(id, ADDR_PROFILE_VELOCITY, LEN_PROFILE_VELOCITY)
        return velocity
    
    # Sets profile velocity (1 = 0.229 rpm = 0.02398 rad/s)
    # !!! Resets after changing mode !!!
    def set_profile_velocity(self, id, velocity):
        velocity = int(velocity)
        comm_result, error = self.packet_handler.write4ByteTxRx(self.port_handler, id, ADDR_PROFILE_VELOCITY, velocity)
        if comm_result != COMM_SUCCESS:
            print("%s" % self.packet_handler.getTxRxResult(comm_result))
        elif error != 0:
            print("%s" % self.packet_handler.getRxPacketError(error))
        else:
            print(f"ID {id} profile velocity set to {velocity}")

    #### Position ####

    # Reads present position (1 = 0.088° = 0.00153 rad)
    def get_position(self, id):
        self.sync_read_position.clearParam()
        add_param_result = self.sync_read_position.addParam(id)
        if add_param_result != True:
            print("[ID:%03d] groupSyncRead addparam failed" % id)
            quit()
        comm_result = self.sync_read_position.txRxPacket()
        if comm_result != COMM_SUCCESS:
            print("%s" % self.packet_handler.getTxRxResult(comm_result))
        getdata_result = self.sync_read_position.isAvailable(id, ADDR_PRESENT_POSITION, LEN_PRESENT_POSITION)
        if getdata_result != True:
            print("[ID:%03d] groupSyncRead getdata failed" % id)
            quit()
        position = self.sync_read_position.getData(id, ADDR_PRESENT_POSITION, LEN_PRESENT_POSITION)
        # Convert to signed int
        if position > 2147483648:
            position -= 4294967296
        return position
            
    # Writes goal position in extended position or current-based position mode (1 = 0.088° = 0.00153 rad)
    def set_position(self, id, position, mode="extpos"):
        if mode not in ["extpos", "curpos"]:
            raise ValueError("Invalid mode")
        self.set_mode(id, mode)
        position = int(position)
        position_byte = [DXL_LOBYTE(DXL_LOWORD(position)), DXL_HIBYTE(DXL_LOWORD(position)), 
                         DXL_LOBYTE(DXL_HIWORD(position)), DXL_HIBYTE(DXL_HIWORD(position))]
        self.sync_write_position.clearParam()
        add_param_result = self.sync_write_position.addParam(id, position_byte)
        if add_param_result != True:
            print("[ID:%03d] groupSyncWrite addparam failed" % id)
            quit()
        comm_result = self.sync_write_position.txPacket()
        if comm_result != COMM_SUCCESS:
            print("%s" % self.packet_handler.getTxRxResult(comm_result))
    
    # Homes motor and sets home position
    def home_position(self, id):
        if id == DXL1_ID:
            self.motor1_pos0 = self.get_position(id)
        elif id == DXL2_ID:
            self.motor2_pos0 = self.get_position(id)
        print(f"ID {id} homed")

    #### Velocity ####

    # Reads present velocity (1 = 0.229 rpm = 0.02398 rad/s)
    def get_velocity(self, id):
        self.sync_read_velocity.clearParam()
        add_param_result = self.sync_read_velocity.addParam(id)
        if add_param_result != True:
            print("[ID:%03d] groupSyncRead addparam failed" % id)
            quit()
        comm_result = self.sync_read_velocity.txRxPacket()
        if comm_result != COMM_SUCCESS:
            print("%s" % self.packet_handler.getTxRxResult(comm_result))
        getdata_result = self.sync_read_velocity.isAvailable(id, ADDR_PRESENT_VELOCITY, LEN_PRESENT_VELOCITY)
        if getdata_result != True:
            print("[ID:%03d] groupSyncRead getdata failed" % id)
            quit()
        velocity = self.sync_read_velocity.getData(id, ADDR_PRESENT_VELOCITY, LEN_PRESENT_VELOCITY)
        # Convert to signed int
        if velocity > 2147483648:
            velocity -= 4294967296
        return velocity

    # Writes goal velocity (1 = 0.229 rpm = 0.02398 rad/s)
    def set_velocity(self, id, velocity):
        self.set_mode(id, "vel")
        velocity = int(velocity)
        velocity_byte = [DXL_LOBYTE(DXL_LOWORD(velocity)), DXL_HIBYTE(DXL_LOWORD(velocity)), 
                         DXL_LOBYTE(DXL_HIWORD(velocity)), DXL_HIBYTE(DXL_HIWORD(velocity))]
        self.sync_write_velocity.clearParam()
        add_param_result = self.sync_write_velocity.addParam(id, velocity_byte)
        if add_param_result != True:
            print("[ID:%03d] groupSyncWrite addparam failed" % id)
            quit()
        comm_result = self.sync_write_velocity.txPacket()
        if comm_result != COMM_SUCCESS:
            print("%s" % self.packet_handler.getTxRxResult(comm_result))
            
    #### Higher Level ####
    
    def set_dualpos(self, pos1, pos2, mode="curpos"):
        self.set_mode(DXL1_ID, mode)
        self.set_mode(DXL2_ID, mode)
        self.set_position(DXL1_ID, -pos1 + self.motor1_pos0, mode)
        self.set_position(DXL2_ID, pos2 + self.motor1_pos0, mode)        
    
    def set_dualvel(self, vel1, vel2, dur, brake=True):
        BUFF = 0.2
        if dur < BUFF:
            print(f"Time must be greater than {BUFF}s")
            self.set_velocity(DXL1_ID, 0)
            self.set_velocity(DXL2_ID, 0)
            return
        self.set_velocity(DXL1_ID, -vel1)
        self.set_velocity(DXL2_ID, vel2)
        time.sleep(dur-BUFF)
        if brake:
            self.set_velocity(DXL1_ID, 0)
            self.set_velocity(DXL2_ID, 0)
            time.sleep(BUFF)
        else:
            self.disable_torque(DXL1_ID)
            self.disable_torque(DXL2_ID)
            time.sleep(BUFF)
            self.enable_torque(DXL1_ID)
            self.enable_torque(DXL2_ID)

#### Main ####

if __name__ == "__main__":

    dnx = Dynamixel()
    dnx.open_port()
    
    dnx.enable_torque(DXL1_ID)
    dnx.enable_torque(DXL2_ID)

    # #### Extended Position and Current Position Demo ####
    # dnx.set_current_limit(DXL2_ID, 50)
    # dnx.set_position(DXL2_ID, 0)
    # time.sleep(2)
    # print(f"Position: {dnx.get_position(DXL2_ID)}")
    
    # print("Starting")
    # dnx.set_position(DXL2_ID, 5000, "curpos")
    # print(f"Position: {dnx.get_position(DXL2_ID)}")
    # time.sleep(2)
    # dnx.set_position(DXL2_ID, 0, "curpos")
    # time.sleep(2)
    # print(f"Position: {dnx.get_position(DXL2_ID)}")
    
    # #### Velocity Demo ####    
    # dnx.set_velocity(DXL2_ID, 200)
    # time.sleep(2)
    # dnx.set_velocity(DXL2_ID, 0)
    
    #### Profile velocity and acceleration Demo ####
    
    dnx.set_mode(DXL1_ID, "extpos")
    dnx.set_mode(DXL2_ID, "extpos")
    
    dnx.set_profile_acceleration(DXL1_ID, 20)
    dnx.set_profile_acceleration(DXL2_ID, 20)
    dnx.set_profile_velocity(DXL1_ID, 200)
    dnx.set_profile_velocity(DXL2_ID, 200)
    
    dnx.set_position(DXL1_ID, 1000)
    time.sleep(5)
    print(f"Position 1: {dnx.get_position(DXL1_ID)-dnx.motor1_pos0}, Position 2: {dnx.get_position(DXL2_ID)-dnx.motor2_pos0}")
    dnx.set_position(DXL1_ID, 0)
    time.sleep(5)
    print(f"Position 1: {dnx.get_position(DXL1_ID)-dnx.motor1_pos0}, Position 2: {dnx.get_position(DXL2_ID)-dnx.motor2_pos0}")
    
    #### Dualpos Demo ####
    # dnx.set_current_limit(DXL1_ID, 800)
    # dnx.set_current_limit(DXL2_ID, 800)
    
    # dnx.set_profile_acceleration(DXL1_ID, 1)
    # dnx.set_profile_acceleration(DXL2_ID, 1)
    # dnx.set_profile_velocity(DXL1_ID, 10)
    # dnx.set_profile_velocity(DXL2_ID, 10)
    
    # dnx.home_position(DXL1_ID)
    # dnx.home_position(DXL2_ID)
    
    # dnx.set_dualpos(500, 0, "extpos")
    # time.sleep(5)
    # print(f"Position 1: {dnx.get_position(DXL1_ID)-dnx.motor1_pos0}, Position 2: {dnx.get_position(DXL2_ID)-dnx.motor2_pos0}")
    
    # dnx.set_dualpos(0, 0, "extpos")
    # time.sleep(5)
    # print(f"Position 1: {dnx.get_position(DXL1_ID)-dnx.motor1_pos0}, Position 2: {dnx.get_position(DXL2_ID)-dnx.motor2_pos0}")

    # #### Dualvel Demo ####
    # dnx.set_dualvel(50, 50, 1)
    # dnx.set_dualvel(-50, -50, 1.05)
    # dnx.set_dualvel(50, 0, 1)
    # dnx.set_dualvel(-50, 0, 1.05)
    # dnx.set_dualvel(0, 50, 1)
    # dnx.set_dualvel(0, -50, 1.2)

    dnx.disable_torque(DXL1_ID)
    dnx.disable_torque(DXL2_ID)
    dnx.close_port()
