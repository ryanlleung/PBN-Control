
import os
import time
import msvcrt
from dynamixel_sdk import *                    # Uses Dynamixel SDK library

def getch():
    return msvcrt.getch().decode()

# Control table address
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
port_handler = PortHandler(DEVICENAME)
packet_handler = PacketHandler(PROTOCOL_VERSION)

def open_port():
    if port_handler.openPort():
        print("Succeeded to open the port")
    else:
        print("Failed to open the port")
        print("Press any key to terminate...")
        getch()
        quit()

def set_baudrate():
    if port_handler.setBaudRate(BAUDRATE):
        print("Succeeded to change the baudrate")
    else:
        print("Failed to change the baudrate")
        print("Press any key to terminate...")
        getch()
        quit()

def close_port():
    port_handler.closePort()

def enable_torque(id):
    dxl_comm_result, dxl_error = packet_handler.write1ByteTxRx(port_handler, id, CT_TORQUE_ENABLE, 1)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packet_handler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packet_handler.getRxPacketError(dxl_error))
    else:
        print("Dynamixel#%d has been successfully connected" % id)

def disable_torque(id):
    dxl_comm_result, dxl_error = packet_handler.write1ByteTxRx(port_handler, id, CT_TORQUE_ENABLE, 0)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packet_handler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packet_handler.getRxPacketError(dxl_error))
    else:
        print("Dynamixel#%d has been successfully disconnected" % id)

def turn_led_on(id):
    dxl_comm_result, dxl_error = packet_handler.write1ByteTxRx(port_handler, id, CT_LED, 1)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packet_handler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packet_handler.getRxPacketError(dxl_error))

def turn_led_off(id):
    dxl_comm_result, dxl_error = packet_handler.write1ByteTxRx(port_handler, id, CT_LED, 0)
    if dxl_comm_result != COMM_SUCCESS:
        print("%s" % packet_handler.getTxRxResult(dxl_comm_result))
    elif dxl_error != 0:
        print("%s" % packet_handler.getRxPacketError(dxl_error))

sync_read_position = GroupSyncRead(port_handler, packet_handler, 
                                   CT_PRESENT_POSITION, LEN_PRESENT_POSITION)
def read_present_position(id):
    sync_read_position.clearParam()

    addparam_result = sync_read_position.addParam(id)
    if addparam_result != True:
        print("[ID:%03d] groupSyncRead addparam failed" % id)
        quit()

    comm_result = sync_read_position.txRxPacket()
    if comm_result != COMM_SUCCESS:
        print("%s" % packet_handler.getTxRxResult(comm_result))

    getdata_result = sync_read_position.isAvailable(id, CT_PRESENT_POSITION, LEN_PRESENT_POSITION)
    if getdata_result != True:
        print("[ID:%03d] groupSyncRead getdata failed" % id)
        quit()

    dxl_present_position = sync_read_position.getData(id, CT_PRESENT_POSITION, LEN_PRESENT_POSITION)
    return dxl_present_position

sync_write_position = GroupSyncWrite(port_handler, packet_handler, 
                                     CT_GOAL_POSITION, LEN_GOAL_POSITION)
def write_goal_position(id, pos):
    sync_write_position.clearParam()

    goal_position = [DXL_LOBYTE(DXL_LOWORD(pos)), DXL_HIBYTE(DXL_LOWORD(pos)), 
                     DXL_LOBYTE(DXL_HIWORD(pos)), DXL_HIBYTE(DXL_HIWORD(pos))]
    addparam_result = sync_write_position.addParam(id, goal_position)
    if addparam_result != True:
        print("[ID:%03d] groupSyncWrite addparam failed" % id)
        quit()

    comm_result = sync_write_position.txPacket()
    if comm_result != COMM_SUCCESS:
        print("%s" % packet_handler.getTxRxResult(comm_result))

    
#### Main ####

open_port()
set_baudrate()
enable_torque(DXL1_ID)
enable_torque(DXL2_ID)

pos1 = read_present_position(DXL1_ID)
pos2 = read_present_position(DXL2_ID)
print(f"pos1: {pos1}, pos2: {pos2}")

write_goal_position(DXL1_ID, pos1 + 100)
write_goal_position(DXL2_ID, pos2 + 100)
time.sleep(5)

pos1 = read_present_position(DXL1_ID)
pos2 = read_present_position(DXL2_ID)
print(f"pos1: {pos1}, pos2: {pos2}")

disable_torque(DXL1_ID)
disable_torque(DXL2_ID)
close_port()
