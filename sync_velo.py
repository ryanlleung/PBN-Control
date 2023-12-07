
import os
import time
import msvcrt
from dynamixel_sdk import *                    # Uses Dynamixel SDK library

def getch():
    return msvcrt.getch().decode()

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

# Default setting
DXL1_ID                     = 1                 # Dynamixel#1 ID : 1
DXL2_ID                     = 4                 # Dynamixel#1 ID : 2
BAUDRATE                    = 57600             # Dynamixel default baudrate : 57600
DEVICENAME                  = 'COM3'            # Check which port is being used on your controller
                                                # ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*"

# TORQUE_ENABLE               = 1                 # Value for enabling the torque
# TORQUE_DISABLE              = 0                 # Value for disabling the torque
# DXL_MINIMUM_POSITION_VALUE  = 100               # Dynamixel will rotate between this value
# DXL_MAXIMUM_POSITION_VALUE  = 4000              # and this value (note that the Dynamixel would not move when the position value is out of movable range. Check e-manual about the range of the Dynamixel you use.)
# DXL_MOVING_STATUS_THRESHOLD = 20                # Dynamixel moving status threshold


#### Initialisation ####

class Dynamixel:

    def __init__(self):
        self.port_handler = PortHandler(DEVICENAME)
        self.packet_handler = PacketHandler(PROTOCOL_VERSION)
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

    def set_mode(self, id, mode="position"):
        self.disable_torque(id)
        if mode == "position":
            comm_result, error = self.packet_handler.write1ByteTxRx(self.port_handler, id, CT_OPERATING_MODE, 3)
        elif mode == "velocity":
            comm_result, error = self.packet_handler.write1ByteTxRx(self.port_handler, id, CT_OPERATING_MODE, 1)
        elif mode == "current":
            comm_result, error = self.packet_handler.write1ByteTxRx(self.port_handler, id, CT_OPERATING_MODE, 0)
        else:
            print("Invalid mode")
            quit()
        if comm_result != COMM_SUCCESS:
            print("%s" % self.packet_handler.getTxRxResult(comm_result))
        elif error != 0:
            print("%s" % self.packet_handler.getRxPacketError(error))
        self.enable_torque(id)

    def enable_torque(self, id):
        comm_result, error = self.packet_handler.write1ByteTxRx(self.port_handler, id, CT_TORQUE_ENABLE, 1)
        if comm_result != COMM_SUCCESS:
            print("%s" % self.packet_handler.getTxRxResult(comm_result))
        elif error != 0:
            print("%s" % self.packet_handler.getRxPacketError(error))
        else:
            print("Dynamixel#%d has been successfully connected" % id)

    def disable_torque(self, id):
        comm_result, error = self.packet_handler.write1ByteTxRx(self.port_handler, id, CT_TORQUE_ENABLE, 0)
        if comm_result != COMM_SUCCESS:
            print("%s" % self.packet_handler.getTxRxResult(comm_result))
        elif error != 0:
            print("%s" % self.packet_handler.getRxPacketError(error))
        else:
            print("Dynamixel#%d has been successfully disconnected" % id)

    def turn_led_on(self, id):
        comm_result, error = self.packet_handler.write1ByteTxRx(self.port_handler, id, CT_LED, 1)
        if comm_result != COMM_SUCCESS:
            print("%s" % self.packet_handler.getTxRxResult(comm_result))
        elif error != 0:
            print("%s" % self.packet_handler.getRxPacketError(error))

    def turn_led_off(self, id):
        comm_result, error = self.packet_handler.write1ByteTxRx(self.port_handler, id, CT_LED, 0)
        if comm_result != COMM_SUCCESS:
            print("%s" % self.packet_handler.getTxRxResult(comm_result))
        elif error != 0:
            print("%s" % self.packet_handler.getRxPacketError(error))

    def get_present_position(self, id):
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
        return position

    def set_goal_position(self, id, position):
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

    def get_present_velocity(self, id):
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
        return velocity

    def set_goal_velocity(self, id, velocity):
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

dnx.set_mode(DXL2_ID, "velocity")
dnx.set_goal_velocity(DXL2_ID, 200)
t0 = time.time()
while True:
    print(dnx.get_present_velocity(DXL2_ID), dnx.get_present_position(DXL2_ID))
    time.sleep(0.1)

dnx.set_goal_velocity(DXL2_ID, 0)

dnx.disable_torque(DXL1_ID)
dnx.disable_torque(DXL2_ID)
dnx.close_port()
