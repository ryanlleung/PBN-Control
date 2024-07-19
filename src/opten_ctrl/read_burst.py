
"""
Script to read the output of the Arduino and print aggregated the x and y values.
Make sure PMW3360DM_Burst is uploaded to the Arduino before running this script.
Change the PORT_NAME to match the device name of the Arduino.
Press 'q' to exit the program.
"""

import serial
import time
import keyboard

# Open the serial port
PORT_NAME = 'COM10' # Change the COM port to match your Arduino
serialCom = serial.Serial(PORT_NAME, 9600)

# Reset the Arduino
serialCom.setDTR(False)
time.sleep(1)
serialCom.flushInput()
serialCom.setDTR(True)

print("Press 'q' to exit")

x, y = 0, 0
try:
    while True:
        # Check if 'q' has been pressed without blocking
        if keyboard.is_pressed('q'):
            print("Quitting...")
            break  # Break out of the loop to end the programq

        if serialCom.inWaiting() > 0:
            input_line = serialCom.readline().decode('utf-8')
            try:
                dx, dy = input_line.split(' ')
                x += int(dx)
                y += int(dy)
                print(f"x: {x}, y: {y}")
            except:
                pass

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Ensure the serial port is closed on exit
    serialCom.close()
    print("Serial port closed.")
    