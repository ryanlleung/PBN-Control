
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
LEN_PRO_GOAL_POSITION       = 4
LEN_PRO_PRESENT_POSITION    = 4

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

open_port()
set_baudrate()
enable_torque(DXL1_ID)
enable_torque(DXL2_ID)



turn_led_on(DXL1_ID)
time.sleep(1)
turn_led_on(DXL2_ID)
time.sleep(1)
turn_led_off(DXL1_ID)
time.sleep(1)
turn_led_off(DXL2_ID)



disable_torque(DXL1_ID)
disable_torque(DXL2_ID)
close_port()
