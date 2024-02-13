import serial
import time
import keyboard

# Open the serial port
serialCom = serial.Serial('COM4', 9600)

# Reset the Arduino
serialCom.setDTR(False)
time.sleep(1)
serialCom.flushInput()
serialCom.setDTR(True)

print("Press 'q' to exit")

try:
    while True:
        # Check if 'q' has been pressed without blocking
        if keyboard.is_pressed('q'):
            print("Quitting...")
            break  # Break out of the loop to end the programq

        if serialCom.inWaiting() > 0:
            input_line = serialCom.readline()
            print(input_line.decode('utf-8'))

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Ensure the serial port is closed on exit
    serialCom.close()
    print("Serial port closed.")