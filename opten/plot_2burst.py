
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
    
    def __init__(self, serial_com, flip_x=False, flip_y=False):
        super().__init__()
        self.serialCom = serial_com
        self.x, self.y = 0, 0
        self.flip_x = flip_x
        self.flip_y = flip_y
        self.running = True
        self.initialised = False
        self.lock = threading.Lock()

    def run(self):
        while self.running:
            if self.serialCom.inWaiting() > 0:
                input_line = ""
                try:
                    input_line = self.serialCom.readline().decode('utf-8').strip()
                except Exception as e:
                    print(f"{self.serialCom.name}: {e} - {input_line}")
                else:
                    self.process_input(input_line)
                
    def process_input(self, input_line):
        if "DPI set to" in input_line:
            self.dpi = int(input_line.split(' ')[-1])
            print(f"{self.serialCom.name} DPI set to {self.dpi}")
        elif "Optical Chip Initialised" in input_line:
            if not hasattr(self, 'dpi'):
                raise ValueError(f"DPI not retrieved for {self.serialCom.name}")
            self.initialised = True
            print(f"{self.serialCom.name} initialised")
            return
            
        if self.initialised:
            dy, dx = map(int, input_line.split(' '))
            if self.flip_x:
                dx = -dx
            if self.flip_y:
                dy = -dy
            with self.lock:
                self.x += dx * 25.4 / self.dpi
                self.y += dy * 25.4 / self.dpi

    def stop(self):
        self.running = False

class SerialPlotter(QMainWindow):
    
    def __init__(self, serial_reader1, serial_reader2):
        super().__init__()
        self.serialReader1 = serial_reader1
        self.serialReader2 = serial_reader2

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
        # self.graphWidget.setAspectLocked(True)
        self.graphWidget.showGrid(x=True, y=True)
        self.graphWidget.addLegend()

        self.plotData1 = self.graphWidget.plot([], [], pen=None, symbol='x', symbolSize=10, symbolBrush=('r'), name="COM4")
        self.plotData2 = self.graphWidget.plot([], [], pen=None, symbol='x', symbolSize=10, symbolBrush=('b'), name="COM5")
        
        # Add a button to reset x and y values
        self.resetButton = QPushButton("Reset Position")
        self.resetButton.clicked.connect(self.reset_position)
        self.layout.addWidget(self.resetButton)

        # Add labels to display x and y positions
        self.COMBox = QHBoxLayout()
        self.layout.addLayout(self.COMBox)
        
        self.COM4Box = QVBoxLayout()
        self.xLabel1 = QLabel(f"COM4 X Position: {round(self.serialReader1.x, 2)} mm")
        self.yLabel1 = QLabel(f"COM4 Y Position: {round(self.serialReader1.y, 2)} mm")
        self.COM4Box.addWidget(self.xLabel1)
        self.COM4Box.addWidget(self.yLabel1)
        self.COMBox.addLayout(self.COM4Box)
        
        self.COM5Box = QVBoxLayout()
        self.xLabel2 = QLabel(f"COM5 X Position: {round(self.serialReader2.x, 2)} mm")
        self.yLabel2 = QLabel(f"COM5 Y Position: {round(self.serialReader2.y, 2)} mm")
        self.COM5Box.addWidget(self.xLabel2)
        self.COM5Box.addWidget(self.yLabel2)
        self.COMBox.addLayout(self.COM5Box)

        # Update the plot periodically
        self.timer = QTimer()
        self.timer.setInterval(50)  # Interval in milliseconds to update the plot
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()
        
        QApplication.setStyle(QStyleFactory.create('Fusion'))
        self.setWindowTitle("GUI")
        self.show()

    def reset_position(self):
        self.serialReader1.x, self.serialReader1.y = 0, 0
        self.serialReader2.x, self.serialReader2.y = 0, 0
        self.update_labels()  # Update the position labels

    def update_plot(self):
        self.plotData1.setData([self.serialReader1.x], [self.serialReader1.y])
        self.plotData2.setData([self.serialReader2.x], [self.serialReader2.y])
        self.update_labels()  # Update the position labels
        QApplication.processEvents()  # Process any other Qt events

    def update_labels(self):
        self.xLabel1.setText(f"COM4 X Position: {round(self.serialReader1.x, 2)} mm")
        self.yLabel1.setText(f"COM4 Y Position: {round(self.serialReader1.y, 2)} mm")
        self.xLabel2.setText(f"COM5 X Position: {round(self.serialReader2.x, 2)} mm")
        self.yLabel2.setText(f"COM5 Y Position: {round(self.serialReader2.y, 2)} mm")
        
try:
    serialCom1 = serial.Serial('COM4', 9600)
    print("Connected to COM4")
except serial.SerialException:
    print("COM4 not available")
    sys.exit(1)
try:
    serialCom2 = serial.Serial('COM5', 9600)
    print("Connected to COM5")
except serial.SerialException:
    print("COM5 not available")
    sys.exit(1)
            
            
serialCom1.setDTR(False)
time.sleep(1)
serialCom1.flushInput()
serialCom1.setDTR(True)
print("COM4 reset")

serialCom2.setDTR(False)
time.sleep(1)
serialCom2.flushInput()
serialCom2.setDTR(True)
print("COM5 reset")


app = QApplication(sys.argv)

serialReader1 = SerialReader(serialCom1)
serialReader1.start()  # Start the serial reader thread

serialReader2 = SerialReader(serialCom2, flip_x=True)
serialReader2.start()  # Start the serial reader thread

plotter = SerialPlotter(serialReader1, serialReader2)
plotter.show()

exit_code = app.exec_()

serialReader1.stop()  # Stop the serial reader thread
serialReader1.join()  # Wait for the serial reader thread to finish
serialCom1.close()
print("COM4 closed")

serialReader2.stop()  # Stop the serial reader thread
serialReader2.join()  # Wait for the serial reader thread to finish
serialCom2.close()
print("COM5 closed")

sys.exit(exit_code)
