
import sys

import pyqtgraph as pg
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from opten_lib import Optical4


class SerialPlotter(QMainWindow):
    
    def __init__(self, opt):
        super().__init__()
        self.opt = opt
        self.serial_reader1 = opt.serial_reader1
        self.serial_reader2 = opt.serial_reader2
        self.serial_reader3 = opt.serial_reader3
        self.serial_reader4 = opt.serial_reader4

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

        if self.serial_reader1 is not None:
            self.plotData1 = self.graphWidget.plot([], [], pen=None, symbol='x', symbolSize=10, symbolBrush=('r'), name="COM5")
        if self.serial_reader2 is not None:
            self.plotData2 = self.graphWidget.plot([], [], pen=None, symbol='x', symbolSize=10, symbolBrush=('b'), name="COM6")
        if self.serial_reader3 is not None:
            self.plotData3 = self.graphWidget.plot([], [], pen=None, symbol='x', symbolSize=10, symbolBrush=('g'), name="COM7")
        if self.serial_reader4 is not None:
            self.plotData4 = self.graphWidget.plot([], [], pen=None, symbol='x', symbolSize=10, symbolBrush=('y'), name="COM8")
        
        # Add a button to reset x and y values
        self.resetButton = QPushButton("Reset Position")
        self.resetButton.clicked.connect(self.reset_position)
        self.layout.addWidget(self.resetButton)

        # Add labels to display x and y positions
        self.OPTENBox = QHBoxLayout()
        self.layout.addLayout(self.OPTENBox)
        
        if self.serial_reader1 is not None:
            self.OPTEN1Box = QVBoxLayout()
            self.xLabel1 = QLabel(f"{self.serial_reader1.serialCom.name} X Position: {round(self.serial_reader1.x, 2)} mm")
            self.yLabel1 = QLabel(f"{self.serial_reader1.serialCom.name} Y Position: {round(self.serial_reader1.y, 2)} mm")
            self.OPTEN1Box.addWidget(self.xLabel1)
            self.OPTEN1Box.addWidget(self.yLabel1)
            self.OPTENBox.addLayout(self.OPTEN1Box)
        
        if self.serial_reader2 is not None:
            self.OPTEN2Box = QVBoxLayout()
            self.xLabel2 = QLabel(f"COM6 X Position: {round(self.serial_reader2.x, 2)} mm")
            self.yLabel2 = QLabel(f"COM6 Y Position: {round(self.serial_reader2.y, 2)} mm")
            self.OPTEN2Box.addWidget(self.xLabel2)
            self.OPTEN2Box.addWidget(self.yLabel2)
            self.OPTENBox.addLayout(self.OPTEN2Box)
        
        if self.serial_reader3 is not None:
            self.OPTEN3Box = QVBoxLayout()
            self.xLabel3 = QLabel(f"COM7 X Position: {round(self.serial_reader3.x, 2)} mm")
            self.yLabel3 = QLabel(f"COM7 Y Position: {round(self.serial_reader3.y, 2)} mm")
            self.OPTEN3Box.addWidget(self.xLabel3)
            self.OPTEN3Box.addWidget(self.yLabel3)
            self.OPTENBox.addLayout(self.OPTEN3Box)
        
        if self.serial_reader4 is not None:
            self.OPTEN4Box = QVBoxLayout()
            self.xLabel4 = QLabel(f"COM8 X Position: {round(self.serial_reader4.x, 2)} mm")
            self.yLabel4 = QLabel(f"COM8 Y Position: {round(self.serial_reader4.y, 2)} mm")
            self.OPTEN4Box.addWidget(self.xLabel4)
            self.OPTEN4Box.addWidget(self.yLabel4)
            self.OPTENBox.addLayout(self.OPTEN4Box)
        
        # Update the plot periodically
        self.timer = QTimer()
        self.timer.setInterval(50)  # Interval in milliseconds to update the plot
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()
        
        QApplication.setStyle(QStyleFactory.create('Fusion'))
        self.setWindowTitle("Optical Encoder Position Plotter")
        self.show()

    def reset_position(self):
        if self.serial_reader1 is not None:
            self.serial_reader1.x, self.serial_reader1.y = 0, 0
        if self.serial_reader2 is not None:
            self.serial_reader2.x, self.serial_reader2.y = 0, 0
        if self.serial_reader3 is not None:
            self.serial_reader3.x, self.serial_reader3.y = 0, 0
        if self.serial_reader4 is not None:
            self.serial_reader4.x, self.serial_reader4.y = 0, 0
        self.update_labels()  # Update the position labels

    def update_plot(self):
        if self.serial_reader1 is not None:
           self.plotData1.setData([self.serial_reader1.x], [self.serial_reader1.y])
        if self.serial_reader2 is not None:    
            self.plotData2.setData([self.serial_reader2.x], [self.serial_reader2.y])
        if self.serial_reader3 is not None:
            self.plotData3.setData([self.serial_reader3.x], [self.serial_reader3.y])
        if self.serial_reader4 is not None:
            self.plotData4.setData([self.serial_reader4.x], [self.serial_reader4.y])
        self.update_labels()  # Update the position labels
        QApplication.processEvents()  # Process any other Qt events

    def update_labels(self):
        if self.serial_reader1 is not None:
            self.xLabel1.setText(f"{self.serial_reader1.serialCom.name} X Position: {round(self.serial_reader1.x, 2)} mm")
            self.yLabel1.setText(f"{self.serial_reader1.serialCom.name} Y Position: {round(self.serial_reader1.y, 2)} mm")
        if self.serial_reader2 is not None:
            self.xLabel2.setText(f"{self.serial_reader2.serialCom.name} X Position: {round(self.serial_reader2.x, 2)} mm")
            self.yLabel2.setText(f"{self.serial_reader2.serialCom.name} Y Position: {round(self.serial_reader2.y, 2)} mm")
        if self.serial_reader3 is not None:
            self.xLabel3.setText(f"{self.serial_reader3.serialCom.name} X Position: {round(self.serial_reader3.x, 2)} mm")
            self.yLabel3.setText(f"{self.serial_reader3.serialCom.name} Y Position: {round(self.serial_reader3.y, 2)} mm")
        if self.serial_reader4 is not None:
            self.xLabel4.setText(f"{self.serial_reader4.serialCom.name} X Position: {round(self.serial_reader4.x, 2)} mm")
            self.yLabel4.setText(f"{self.serial_reader4.serialCom.name} Y Position: {round(self.serial_reader4.y, 2)} mm")
    
    def closeEvent(self, event):
        opt.close()
        event.accept()
        
if "__main__" == __name__:
    opt = Optical4()
    opt.start_burst()
    app = QApplication(sys.argv)
    spl = SerialPlotter(opt)
    sys.exit(app.exec_())
