import sys
import serial
import time
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
import threading

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
                        pixels = np.array(raw[1:]).reshape((36, 36)).astype(np.uint8)
                        self.latest_data = pixels
                except Exception as e:
                    print(f"An error occurred in the serial reading thread: {e}")

    def stop(self):
        self.running = False

class SerialImagePlotter(QMainWindow):
    def __init__(self, serial_reader):
        super().__init__()
        self.serial_reader = serial_reader

        # Set up the plot
        self.imageItem = pg.ImageItem(border='w')
        self.graphWidget = pg.GraphicsLayoutWidget()
        self.view = self.graphWidget.addViewBox()
        self.view.setAspectLocked(True)
        self.view.addItem(self.imageItem)

        self.setCentralWidget(self.graphWidget)

        # Update the plot periodically
        self.timer = QTimer()
        self.timer.setInterval(100)  # Interval in milliseconds to update the plot
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

    def update_plot(self):
        if self.serial_reader.latest_data is not None:
            self.imageItem.setImage(self.serial_reader.latest_data)
            self.serial_reader.latest_data = None  # Reset the data after plotting

def main():
    app = QApplication(sys.argv)

    # Open the serial port
    try:
        serial_port = serial.Serial('COM4', 9600)
    except serial.SerialException as e:
        print(f"Could not open serial port: {e}")
        sys.exit(1)

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
