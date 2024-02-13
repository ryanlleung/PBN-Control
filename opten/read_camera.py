import serial
import time
import keyboard
import numpy as np
import matplotlib.pyplot as plt

# Open the serial port
serialCom = serial.Serial('COM4', 9600)

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
                raw = input_line.split(' ')
                if len(raw) != 1297:
                    continue
                pixels = np.array(raw[1:]).reshape((36, 36)).astype(np.uint8)
                plt.imshow(pixels, cmap='gray')
                plt.show()
            except:
                pass

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Ensure the serial port is closed on exit
    serialCom.close()
    print("Serial port closed.")