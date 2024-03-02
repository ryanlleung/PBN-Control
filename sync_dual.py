# Description: Synchronous control of two Dynamixel motors

from dynamixel_sdk import *                    # Uses Dynamixel SDK library


# Control table address
ADDR_OPERATING_MODE =         11

ADDR_TORQUE_ENABLE =          64
ADDR_LED =                    65
ADDR_STATUS_RETURN_LEVEL =    68
ADDR_REGISTERED_INSTRUCTION = 69
ADDR_HARDWARE_ERROR_STATUS =  70

ADDR_GOAL_PWM =               100
ADDR_GOAL_CURRENT =           102
ADDR_GOAL_VELOCITY =          104
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
LEN_GOAL_POSITION       = 4
LEN_PRESENT_POSITION    = 4
LEN_GOAL_VELOCITY       = 4
LEN_PRESENT_VELOCITY    = 4
LEN_PRESENT_CURRENT     = 2
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
        self.op_mode = "vel"
        self.set_mode(DXL1_ID, "vel")
        self.set_mode(DXL2_ID, "vel")

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
        print(f"Torque enabled for ID {id}")

    def disable_torque(self, id):
        self._set_torque(id, False)
        self.turn_LED_off(id)
        print(f"Torque disabled for ID {id}")

    def set_mode(self, id, mode):
        if self.op_mode == mode:
            return
        self.disable_torque(id)
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
            print(f"{mode_description} mode set for ID {id}")
            self.op_mode = mode
        else:
            print("Invalid mode")
            quit()
        self.enable_torque(id)

    #### LED ####

    def _set_LED(self, id, enable):
        value = 1 if enable else 0
        self._write_register(id, ADDR_LED, value)

    def turn_LED_on(self, id):
        self._set_LED(id, True)

    def turn_LED_off(self, id):
        self._set_LED(id, False)
        
    ### Information ###
    
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
    
    # dnx.set_position(DXL2_ID, 0)
    # time.sleep(2)
    # print(f"Position: {dnx.get_position(DXL2_ID)}")
    
    # print("Starting")
    # dnx.set_position(DXL2_ID, 5000)
    # print(f"Position: {dnx.get_position(DXL2_ID)}")
    # time.sleep(2)
    # print(f"Position: {dnx.get_position(DXL2_ID)}")
    
    # dnx.set_velocity(DXL1_ID, 200)
    # time.sleep(2)
    # dnx.set_velocity(DXL1_ID, 0)
    
    # positions = [dnx.get_position(DXL1_ID), dnx.get_position(DXL2_ID)]
    # print(f"Positions: {positions}")
    # dnx.set_dualvel(200, 100, 1)
    # positions = [dnx.get_position(DXL1_ID), dnx.get_position(DXL2_ID)]
    # print(f"Positions: {positions}")
    # dnx.set_dualvel(-200, -100, 1)
    # positions = [dnx.get_position(DXL1_ID), dnx.get_position(DXL2_ID)]
    # print(f"Positions: {positions}")

    # dnx.set_dualvel(50, 50, 1)
    # dnx.set_dualvel(-50, -50, 1.05)
    # dnx.set_dualvel(50, 0, 1)
    # dnx.set_dualvel(-50, 0, 1.05)
    # dnx.set_dualvel(0, 50, 1)
    # dnx.set_dualvel(0, -50, 1.2)

    dnx.disable_torque(DXL1_ID)
    dnx.disable_torque(DXL2_ID)
    dnx.close_port()
