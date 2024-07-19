"""
Script to plot the camera data from the Arduino on a PyQt window.
Make sure PMW3360DM_Camera is uploaded to the Arduino before running this script.
Change the PORT_NAME to match the device name of the Arduino.
"""

import os
import sys
import serial
import numpy as np
import threading
import pyqtgraph as pg
from datetime import datetime

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

PORT_NAME = 'COM5' # Change the COM port to match your Arduino
SAVE_IMAGE_DIR = 'exports/camera' # Change the directory to save the images if needed

class SerialReader(threading.Thread):
    def __init__(self, serial_port):
        super().__init__()
        self.serial_port = serial_port
        self.running = True
        self.latest_data = None

    def run(self):
        while self.running:
            if self.serial_port.inWaiting() > 0:
                input_line = self.serial_port.readline().decode('utf-8').strip()
                try:
                    raw = input_line.split(' ')
                    if len(raw) == 1297:  # Ensure the data format is correct
                        pixels = np.array(raw[:-1]).reshape((36, 36)).astype(np.uint8)
                        self.latest_data = pixels
                except Exception as e:
                    print(f"An error occurred in the serial reading thread: {e}")

    def stop(self):
        self.running = False

class SerialImagePlotter(QMainWindow):
    def __init__(self, serial_reader):
        super().__init__()
        self.serial_reader = serial_reader
        self.COM = self.serial_reader.serial_port.name

        # Main widget and layout
        mainWidget = QWidget(self)
        mainLayout = QVBoxLayout(mainWidget)  # Create a QVBoxLayout
        mainWidget.setLayout(mainLayout)  # Set the QVBoxLayout on the main widget
        self.setCentralWidget(mainWidget)

        # Set up the plot with white background
        self.imageItem = pg.ImageItem(border='w')
        self.graphWidget = pg.GraphicsLayoutWidget()
        self.graphWidget.setBackground('w')  # Set background to white
        self.view = self.graphWidget.addViewBox()
        self.view.setAspectLocked(True)
        self.view.addItem(self.imageItem)

        # Add the plot to the layout
        mainWidget.layout().addWidget(self.graphWidget)

        # Button to save the image
        self.saveButton = QPushButton("Save Image")
        self.saveButton.clicked.connect(self.save_image)
        mainWidget.layout().addWidget(self.saveButton)  # Add the button to the layout

        # Update the plot periodically
        self.timer = QTimer()
        self.timer.setInterval(10)  # Interval in milliseconds to update the plot
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

        QApplication.setStyle(QStyleFactory.create('Fusion'))
        self.setWindowTitle("Camera Plotter")
        self.show()

    def update_plot(self):
        if self.serial_reader.latest_data is not None:
            self.imageItem.setImage(self.serial_reader.latest_data)
            self.serial_reader.latest_data = None  # Reset the data after plotting

    def save_image(self):
        pixmap = self.graphWidget.grab()
        os.makedirs(SAVE_IMAGE_DIR, exist_ok=True)
        filename = f"{SAVE_IMAGE_DIR}/{self.COM}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"
        pixmap.save(filename, 'PNG')
        print(f"Image saved as {filename}")
        
def main():
    app = QApplication(sys.argv)

    # Open the serial port
    try:
        serial_port = serial.Serial(PORT_NAME, 9600)
        print(f"Connected to {PORT_NAME}")
    except serial.SerialException:
        print(f"Failed to connect to {PORT_NAME}")

    # Start the serial reader thread
    serial_reader = SerialReader(serial_port)
    serial_reader.start()

    # Start the PyQt application
    plotter = SerialImagePlotter(serial_reader)
    plotter.show()

    exit_code = app.exec_()
    serial_reader.stop()  # Stop the serial reader thread
    serial_reader.join()  # Wait for the thread to finish
    serial_port.close()
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
