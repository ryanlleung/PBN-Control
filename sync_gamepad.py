
import os
import time
from dynamixel_sdk import *                    # Uses Dynamixel SDK library
from inputs import get_gamepad


# Control table address
CT_OPERATING_MODE =         11

CT_TORQUE_ENABLE =          64
CT_LED =                    65
CT_STATUS_RETURN_LEVEL =    68
CT_REGISTERED_INSTRUCTION = 69
CT_HARDWARE_ERROR_STATUS =  70

CT_GOAL_PWM =               100
CT_GOAL_CURRENT =           102
CT_GOAL_VELOCITY =          104
CT_GOAL_POSITION =          116

CT_MOVING =                 122
CT_MOVING_STATUS =          123

CT_PRESENT_PWM =            124
CT_PRESENT_CURRENT =        126
CT_PRESENT_VELOCITY =       128
CT_PRESENT_POSITION =       132
CT_PRESENT_INPUT_VOLTAGE =  144
CT_PRESENT_TEMPERATURE =    146

# Data Byte Length
LEN_GOAL_POSITION       = 4
LEN_PRESENT_POSITION    = 4
LEN_GOAL_VELOCITY       = 4
LEN_PRESENT_VELOCITY    = 4

# Protocol version
PROTOCOL_VERSION            = 2.0               # See which protocol version is used in the Dynamixel

# Device setting
DXL1_ID                     = 1                 # Dynamixel#1 ID : 1
DXL2_ID                     = 4                 # Dynamixel#1 ID : 2
BAUDRATE                    = 57600             # Dynamixel default baudrate : 57600
DEVICENAME                  = 'COM3'            # Check which port is being used on your controller
                                                # ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*"

#### Initialisation ####

class Dynamixel:

    def __init__(self):
        self.port_handler = PortHandler(DEVICENAME)
        self.packet_handler = PacketHandler(PROTOCOL_VERSION)
        self.current_mode = "pos"
        self.sync_read_position = GroupSyncRead(self.port_handler, self.packet_handler, 
                                                CT_PRESENT_POSITION, LEN_PRESENT_POSITION)
        self.sync_write_position = GroupSyncWrite(self.port_handler, self.packet_handler,
                                                CT_GOAL_POSITION, LEN_GOAL_POSITION)
        self.sync_read_velocity = GroupSyncRead(self.port_handler, self.packet_handler,
                                                CT_PRESENT_VELOCITY, LEN_PRESENT_VELOCITY)
        self.sync_write_velocity = GroupSyncWrite(self.port_handler, self.packet_handler,
                                                CT_GOAL_VELOCITY, LEN_GOAL_VELOCITY)

    def open_port(self, BAUDRATE=57600):
        if self.port_handler.openPort():
            print("Port opened successfully")
        else:
            print("Failed to open the port")
            quit()

        if self.port_handler.setBaudRate(BAUDRATE):
            print("Baudrate set successfully")
        else:
            print("Failed to set baudrate")
            quit()

    def close_port(self):
        self.port_handler.closePort()
        print("Port closed successfully")

    def _write_register(self, id, address, value):
        comm_result, error = self.packet_handler.write1ByteTxRx(self.port_handler, id, address, value)
        if comm_result != COMM_SUCCESS:
            print("%s" % self.packet_handler.getTxRxResult(comm_result))
        elif error != 0:
            print("%s" % self.packet_handler.getRxPacketError(error))        

    #### Torque & Mode ####

    def _set_torque(self, id, enable):
        value = 1 if enable else 0
        self._write_register(id, CT_TORQUE_ENABLE, value)

    def enable_torque(self, id):
        self._set_torque(id, True)
        print(f"Torque enabled for ID {id}")

    def disable_torque(self, id):
        self._set_torque(id, False)
        print(f"Torque disabled for ID {id}")

    def set_mode(self, id, mode):
        if self.current_mode == mode:
            return
        self.disable_torque(id)
        if mode == "pos":
            self._write_register(id, CT_OPERATING_MODE, 3)
            print(f"Position mode set for ID {id}")
            self.current_mode = "pos"
        elif mode == "vel":
            self._write_register(id, CT_OPERATING_MODE, 1)
            print(f"Velocity mode set for ID {id}")
            self.current_mode = "vel"
        elif mode == "cur":
            self._write_register(id, CT_OPERATING_MODE, 0)
            print(f"Current mode set for ID {id}")
            self.current_mode = "cur"
        else:
            print("Invalid mode")
            quit()
        self.enable_torque(id)

    #### LED ####

    def _set_LED(self, id, enable):
        value = 1 if enable else 0
        self._write_register(id, CT_LED, value)

    def turn_LED_on(self, id):
        self._set_LED(id, True)

    def turn_LED_off(self, id):
        self._set_LED(id, False)

    #### Position ####

    def get_position(self, id):
        self.sync_read_position.clearParam()
        add_param_result = self.sync_read_position.addParam(id)
        if add_param_result != True:
            print("[ID:%03d] groupSyncRead addparam failed" % id)
            quit()
        comm_result = self.sync_read_position.txRxPacket()
        if comm_result != COMM_SUCCESS:
            print("%s" % self.packet_handler.getTxRxResult(comm_result))
        getdata_result = self.sync_read_position.isAvailable(id, CT_PRESENT_POSITION, LEN_PRESENT_POSITION)
        if getdata_result != True:
            print("[ID:%03d] groupSyncRead getdata failed" % id)
            quit()
        position = self.sync_read_position.getData(id, CT_PRESENT_POSITION, LEN_PRESENT_POSITION)
        # Convert to signed int
        if position > 2147483648:
            position -= 4294967296
        return position

    def set_position(self, id, position):
        self.set_mode(id, "pos")
        self.sync_write_position.clearParam()
        position_byte = [DXL_LOBYTE(DXL_LOWORD(position)), DXL_HIBYTE(DXL_LOWORD(position)), 
                         DXL_LOBYTE(DXL_HIWORD(position)), DXL_HIBYTE(DXL_HIWORD(position))]
        add_param_result = self.sync_write_position.addParam(id, position_byte)
        if add_param_result != True:
            print("[ID:%03d] groupSyncWrite addparam failed" % id)
            quit()
        comm_result = self.sync_write_position.txPacket()
        if comm_result != COMM_SUCCESS:
            print("%s" % self.packet_handler.getTxRxResult(comm_result))

    #### Velocity ####

    def get_velocity(self, id):
        self.sync_read_velocity.clearParam()
        add_param_result = self.sync_read_velocity.addParam(id)
        if add_param_result != True:
            print("[ID:%03d] groupSyncRead addparam failed" % id)
            quit()
        comm_result = self.sync_read_velocity.txRxPacket()
        if comm_result != COMM_SUCCESS:
            print("%s" % self.packet_handler.getTxRxResult(comm_result))
        getdata_result = self.sync_read_velocity.isAvailable(id, CT_PRESENT_VELOCITY, LEN_PRESENT_VELOCITY)
        if getdata_result != True:
            print("[ID:%03d] groupSyncRead getdata failed" % id)
            quit()
        velocity = self.sync_read_velocity.getData(id, CT_PRESENT_VELOCITY, LEN_PRESENT_VELOCITY)
        # Convert to signed int
        if velocity > 2147483648:
            velocity -= 4294967296
        return velocity

    def set_velocity(self, id, velocity):
        self.set_mode(id, "vel")
        self.sync_write_velocity.clearParam()
        velocity_byte = [DXL_LOBYTE(DXL_LOWORD(velocity)), DXL_HIBYTE(DXL_LOWORD(velocity)), 
                         DXL_LOBYTE(DXL_HIWORD(velocity)), DXL_HIBYTE(DXL_HIWORD(velocity))]
        add_param_result = self.sync_write_velocity.addParam(id, velocity_byte)
        if add_param_result != True:
            print("[ID:%03d] groupSyncWrite addparam failed" % id)
            quit()
        comm_result = self.sync_write_velocity.txPacket()
        if comm_result != COMM_SUCCESS:
            print("%s" % self.packet_handler.getTxRxResult(comm_result))


#### Main ####

dnx = Dynamixel()
dnx.open_port()

dnx.enable_torque(DXL1_ID)
dnx.enable_torque(DXL2_ID)

try:
    breaker = False
    while True:
        events = get_gamepad()
        for event in events:
            if event.ev_type == "Key":
                if event.code == "BTN_SELECT":
                    breaker = True
                    break
            elif event.ev_type == "Absolute":
                if event.code == "ABS_Z":
                    dnx.set_velocity(DXL1_ID, int(-event.state*2))
                elif event.code == "ABS_RZ":
                    dnx.set_velocity(DXL2_ID, int(event.state*2))
        if breaker:
            break

except KeyboardInterrupt:
    pass

dnx.disable_torque(DXL1_ID)
dnx.disable_torque(DXL2_ID)
dnx.close_port()
