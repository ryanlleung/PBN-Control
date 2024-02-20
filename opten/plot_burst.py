import sys
import serial
import time
import threading
import pyqtgraph as pg

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtNetwork import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *

class SerialReader(threading.Thread):
    
    def __init__(self, serial_com):
        super().__init__()
        self.serialCom = serial_com
        self.x, self.y = 0, 0
        self.running = True

    def run(self):
        while self.running:
            if self.serialCom.inWaiting() > 0:
                try:
                    input_line = self.serialCom.readline().decode('utf-8').strip()
                except:
                    continue
                try:
                    dy, dx = map(int, input_line.split(' '))
                    self.x += dx * 25.4 / self.dpi
                    self.y += dy * 25.4 / self.dpi
                except:
                    if "DPI set to" in input_line:
                        self.dpi = int(input_line.split(' ')[-1])
                        print(f"{self.serialCom.name} DPI set to {self.dpi}")

    def stop(self):
        self.running = False

class SerialPlotter(QMainWindow):
    
    def __init__(self, serial_reader):
        super().__init__()
        self.serialReader = serial_reader

        # Set up the main widget and layout
        self.mainWidget = QWidget(self)
        self.setCentralWidget(self.mainWidget)
        self.layout = QVBoxLayout()
        self.mainWidget.setLayout(self.layout)

        # Set up the plot
        self.graphWidget = pg.PlotWidget()
        self.layout.addWidget(self.graphWidget)  # Add the plot widget to the layout

        self.graphWidget.setBackground('w')
        self.graphWidget.setTitle("XY Position Stream")
        self.graphWidget.setLabel('left', 'Y Position / mm')
        self.graphWidget.setLabel('bottom', 'X Position / mm')
        self.graphWidget.setXRange(-30.0, 30.0)
        self.graphWidget.setYRange(-50.0, 50.0)
        self.graphWidget.setAspectLocked(True)
        self.graphWidget.showGrid(x=True, y=True)

        self.plotData = self.graphWidget.plot([], [], pen=None, symbol='x', symbolSize=10, symbolBrush=('r'), name=self.serialReader.serialCom.name)

        # Add a button to reset x and y values
        self.resetButton = QPushButton("Reset Position")
        self.resetButton.clicked.connect(self.reset_position)
        self.layout.addWidget(self.resetButton)

        # Add labels to display x and y positions
        self.xLabel = QLabel(f"X Position: {round(self.serialReader.x, 2)} mm")
        self.yLabel = QLabel(f"Y Position: {round(self.serialReader.y, 2)} mm")
        self.layout.addWidget(self.xLabel)
        self.layout.addWidget(self.yLabel)

        # Update the plot periodically
        self.timer = QTimer()
        self.timer.setInterval(50)  # Interval in milliseconds to update the plot
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()
        
        QApplication.setStyle(QStyleFactory.create('Fusion'))
        self.setWindowTitle("GUI")
        self.show()

    def reset_position(self):
        self.serialReader.x, self.serialReader.y = 0, 0  # Reset x and y values to 0
        self.update_labels()  # Update the position labels

    def update_plot(self):
        self.plotData.setData([self.serialReader.x], [self.serialReader.y])
        self.update_labels()  # Update the position labels
        QApplication.processEvents()  # Process any other Qt events

    def update_labels(self):
        self.xLabel.setText(f"{self.serialReader.serialCom.name} X Position: {round(self.serialReader.x, 2)} mm")
        self.yLabel.setText(f"{self.serialReader.serialCom.name} Y Position: {round(self.serialReader.y, 2)} mm")


# Check if the serial port is available
try:
    serialCom = serial.Serial('COM4', 9600)
    print("Connected to COM4")
except serial.SerialException:
    try:
        serialCom = serial.Serial('COM5', 9600)
        print("Connected to COM5")
    except serial.SerialException:
        print("No serial port available")
        sys.exit(1)
        
serialCom.setDTR(False)
time.sleep(1)
serialCom.flushInput()
serialCom.setDTR(True)

app = QApplication(sys.argv)

serialReader = SerialReader(serialCom)
serialReader.start()  # Start the serial reader thread

plotter = SerialPlotter(serialReader)
plotter.show()

exit_code = app.exec_()
serialReader.stop()  # Stop the serial reader thread
serialReader.join()  # Wait for the serial reader thread to finish
serialCom.close()
print("Serial port closed.")
sys.exit(exit_code)
