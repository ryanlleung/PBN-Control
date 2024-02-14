import serial
import time
import keyboard

# Open the serial port
serialCom1 = serial.Serial('COM4', 9600)

# Reset the Arduino
serialCom1.setDTR(False)
time.sleep(1)
serialCom1.flushInput()
serialCom1.setDTR(True)

# Open the second serial port
serialCom2 = serial.Serial('COM5', 9600)

# Reset the Arduino
serialCom2.setDTR(False)
time.sleep(1)
serialCom2.flushInput()
serialCom2.setDTR(True)

print("Press 'q' to exit")

try:
    while True:
        # Check if 'q' has been pressed without blocking
        if keyboard.is_pressed('q'):
            print("Quitting...")
            break  # Break out of the loop to end the programq

        if serialCom1.inWaiting() > 0:
            input_line = serialCom1.readline()
            print(input_line.decode('utf-8'))
            
        if serialCom2.inWaiting() > 0:
            input_line = serialCom2.readline()
            print(input_line.decode('utf-8'))

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Ensure the serial port is closed on exit
    serialCom1.close()
    serialCom2.close()
    print("Serial port closed.")