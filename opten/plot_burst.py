import sys
import serial
import time
import threading
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QTimer

class SerialReader(threading.Thread):
    def __init__(self, serial_com):
        super().__init__()
        self.serialCom = serial_com
        self.x, self.y = 0, 0
        self.running = True

    def run(self):
        while self.running:
            if self.serialCom.inWaiting() > 0:
                input_line = self.serialCom.readline().decode('utf-8').strip()
                try:
                    dx, dy = map(int, input_line.split(' '))
                    self.x += dx
                    self.y -= dy
                except ValueError:
                    pass  # Ignore lines that don't parse correctly

    def stop(self):
        self.running = False

class SerialPlotter(QMainWindow):
    def __init__(self, serial_reader):
        super().__init__()
        self.serialReader = serial_reader

        # Set up the plot
        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)

        self.graphWidget.setBackground('w')
        self.graphWidget.setTitle("XY Position Stream")
        self.graphWidget.setLabel('left', 'Y Position')
        self.graphWidget.setLabel('bottom', 'X Position')
        self.graphWidget.setXRange(-5000, 5000)
        self.graphWidget.setYRange(-5000, 5000)
        self.graphWidget.setAspectLocked(True)
        self.graphWidget.showGrid(x=True, y=True)

        self.plotData = self.graphWidget.plot([], [], pen=None, symbol='o', symbolSize=10, symbolBrush=('r'))

        # Update the plot periodically
        self.timer = QTimer()
        self.timer.setInterval(50)  # Interval in milliseconds to update the plot
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

    def update_plot(self):
        self.plotData.setData([self.serialReader.x], [self.serialReader.y])
        QApplication.processEvents()  # Process any other Qt events

def main():
    # Check if the serial port is available
    try:
        serialCom = serial.Serial('COM4', 9600)
    except serial.SerialException:
        try:
            serialCom = serial.Serial('COM5', 9600)
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

if __name__ == "__main__":
    main()
