
import base64
import os
import time
import sys

from inputs import get_gamepad
from sync_dual import *

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtNetwork import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *


# Handle communication with the gamepad
class GamepadThread(QThread):
    
    def __init__(self, dnx, 
                 motor1_switch, motor1_vel_value,
                 motor2_switch, motor2_vel_value,):
        super().__init__()
        self.daemon = True
        self.dnx = dnx
        self.motor1_switch = motor1_switch
        self.motor1_vel_value = motor1_vel_value
        self.motor2_switch = motor2_switch
        self.motor2_vel_value = motor2_vel_value
        self.deadvel = 10
        
    def run(self):
        while True:
            events = get_gamepad()
            for event in events:
                if event.code == 'ABS_Y':
                    drive_value = int(-event.state / 500) ## change scaler here
                    if abs(drive_value) < self.deadvel:
                        drive_value = 0
                    self.motor1_vel_value.setText(str(drive_value))
                elif event.code == 'ABS_RY':
                    drive_value = int(event.state / 500) ## change scaler here
                    if abs(drive_value) < self.deadvel:
                        drive_value = 0
                    self.motor2_vel_value.setText(str(drive_value))
                elif event.code == 'BTN_START':
                    if event.state == 1:
                        self.motor1_switch.toggle()
                elif event.code == 'BTN_SELECT':
                    if event.state == 1:
                        self.motor2_switch.toggle()

# Handle communication with the Dynamixel motors                    
class CommsThread(QThread):
    
    def __init__(self, dnx, 
                 motor1_switch, 
                 motor1_vel_value, 
                 motor1_pos_value, 
                 motor1_current_value, 
                 motor1_temp_value,
                 motor2_switch,
                 motor2_vel_value,
                 motor2_pos_value,
                 motor2_current_value,
                 motor2_temp_value):
        super().__init__()
        self.daemon = True
        self.dnx = dnx
        self.motor1_switch = motor1_switch
        self.motor1_vel_value = motor1_vel_value
        self.motor1_pos_value = motor1_pos_value
        self.motor1_current_value = motor1_current_value
        self.motor1_temp_value = motor1_temp_value
        self.motor2_switch = motor2_switch
        self.motor2_vel_value = motor2_vel_value
        self.motor2_pos_value = motor2_pos_value
        self.motor2_current_value = motor2_current_value
        self.motor2_temp_value = motor2_temp_value
        
        self.motor1_switch_last = self.motor1_switch.isChecked()
        self.motor2_switch_last = self.motor2_switch.isChecked()
        
    def run(self):
        while True:
            if self.motor1_switch.isChecked() != self.motor1_switch_last:
                self.motor1_switch_last = self.motor1_switch.isChecked()
                if self.motor1_switch_last:
                    self.dnx.enable_torque(DXL1_ID)
                else:
                    self.dnx.disable_torque(DXL1_ID)
            if self.motor2_switch.isChecked() != self.motor2_switch_last:
                self.motor2_switch_last = self.motor2_switch.isChecked()
                if self.motor2_switch_last:
                    self.dnx.enable_torque(DXL2_ID)
                else:
                    self.dnx.disable_torque(DXL2_ID)
            self.dnx.set_velocity(DXL1_ID, int(self.motor1_vel_value.text()))
            self.dnx.set_velocity(DXL2_ID, int(self.motor2_vel_value.text()))
            self.motor1_pos_value.setText(str(self.dnx.get_position(DXL1_ID)))
            self.motor1_current_value.setText(str(self.dnx.get_current(DXL1_ID)))
            self.motor1_temp_value.setText(str(self.dnx.get_temperature(DXL1_ID)))
            self.motor2_pos_value.setText(str(self.dnx.get_position(DXL2_ID)))
            self.motor2_current_value.setText(str(self.dnx.get_current(DXL2_ID)))
            self.motor2_temp_value.setText(str(self.dnx.get_temperature(DXL2_ID)))
            time.sleep(1/60)

#### Main ####

class MainWindow(QWidget):
    
    def __init__(self):
        super(MainWindow, self).__init__()
        self.dnx = Dynamixel()
        self.dnx.open_port()
        self.dnx.enable_torque(DXL1_ID)
        self.dnx.enable_torque(DXL2_ID)
        self.initUI()
        if self.have_gamepad():
            self.gamepad_thread = GamepadThread(self.dnx,
                                                self.motor1_switch,
                                                self.motor1_vel_value,
                                                self.motor2_switch,
                                                self.motor2_vel_value)
            self.gamepad_thread.start()
        self.comms_thread = CommsThread(self.dnx,
                                        self.motor1_switch,
                                        self.motor1_vel_value,
                                        self.motor1_pos_value,
                                        self.motor1_current_value,
                                        self.motor1_temp_value,
                                        self.motor2_switch,
                                        self.motor2_vel_value,
                                        self.motor2_pos_value,
                                        self.motor2_current_value,
                                        self.motor2_temp_value,)
        self.comms_thread.start()

    def initUI(self):
        
        motor_box = QHBoxLayout()
       
        motor1_box = QVBoxLayout()
        motor1_label_box = QHBoxLayout()
        motor1_label = QLabel("Motor 1")
        motor1_label.setStyleSheet("font-size: 10pt")
        self.motor1_switch = QCheckBox()
        self.motor1_switch.setChecked(True)
        motor1_label_box.addWidget(motor1_label)
        motor1_label_box.addStretch(1)
        motor1_label_box.addWidget(self.motor1_switch)
        
        motor1_vel_box = QHBoxLayout()
        motor1_vel_label = QLabel("Set Velocity")
        motor1_vel_label.setFixedWidth(80)
        self.motor1_vel_value = QLineEdit('0')
        self.motor1_vel_value.setReadOnly(True)
        motor1_vel_box.addWidget(motor1_vel_label)
        motor1_vel_box.addWidget(self.motor1_vel_value)
        
        motor1_pos_box = QHBoxLayout()
        motor1_pos_label = QLabel("Position")
        motor1_pos_label.setFixedWidth(80)
        self.motor1_pos_value = QLineEdit(str(self.dnx.get_position(DXL1_ID)))
        self.motor1_pos_value.setReadOnly(True)
        motor1_pos_box.addWidget(motor1_pos_label)
        motor1_pos_box.addWidget(self.motor1_pos_value)
        
        motor1_current_box = QHBoxLayout()
        motor1_current_label = QLabel("Current / mA")
        motor1_current_label.setFixedWidth(80)
        self.motor1_current_value = QLineEdit(str(self.dnx.get_current(DXL1_ID)))
        self.motor1_current_value.setReadOnly(True)
        motor1_current_box.addWidget(motor1_current_label)
        motor1_current_box.addWidget(self.motor1_current_value)
        
        motor1_temp_box = QHBoxLayout()
        motor1_temp_label = QLabel("Temp / °C")
        motor1_temp_label.setFixedWidth(80)
        self.motor1_temp_value = QLineEdit(str(self.dnx.get_temperature(DXL1_ID)))
        self.motor1_temp_value.setReadOnly(True)
        motor1_temp_box.addWidget(motor1_temp_label)
        motor1_temp_box.addWidget(self.motor1_temp_value)
        
        motor1_box.addLayout(motor1_label_box)
        motor1_box.addLayout(motor1_vel_box)
        motor1_box.addLayout(motor1_pos_box)
        motor1_box.addLayout(motor1_current_box)
        motor1_box.addLayout(motor1_temp_box)
        
        motor2_box = QVBoxLayout()
        motor2_label_box = QHBoxLayout()
        motor2_label = QLabel("Motor 2")
        motor2_label.setStyleSheet("font-size: 10pt")
        self.motor2_switch = QCheckBox()
        self.motor2_switch.setChecked(True)
        motor2_label_box.addWidget(motor2_label)
        motor2_label_box.addStretch(1)
        motor2_label_box.addWidget(self.motor2_switch)
        
        motor2_vel_box = QHBoxLayout()
        motor2_vel_label = QLabel("Set Velocity")
        motor2_vel_label.setFixedWidth(80)
        self.motor2_vel_value = QLineEdit('0')
        self.motor2_vel_value.setReadOnly(True)
        motor2_vel_box.addWidget(motor2_vel_label)
        motor2_vel_box.addWidget(self.motor2_vel_value)
        
        motor2_pos_box = QHBoxLayout()
        motor2_pos_label = QLabel("Position")
        motor2_pos_label.setFixedWidth(80)
        self.motor2_pos_value = QLineEdit(str(self.dnx.get_position(DXL2_ID)))
        self.motor2_pos_value.setReadOnly(True)
        motor2_pos_box.addWidget(motor2_pos_label)
        motor2_pos_box.addWidget(self.motor2_pos_value)
        
        motor2_current_box = QHBoxLayout()
        motor2_current_label = QLabel("Current / mA")
        motor2_current_label.setFixedWidth(80)
        self.motor2_current_value = QLineEdit(str(self.dnx.get_current(DXL2_ID)))
        self.motor2_current_value.setReadOnly(True)
        motor2_current_box.addWidget(motor2_current_label)
        motor2_current_box.addWidget(self.motor2_current_value)
        
        motor2_temp_box = QHBoxLayout()
        motor2_temp_label = QLabel("Temp / °C")
        motor2_temp_label.setFixedWidth(80)
        self.motor2_temp_value = QLineEdit(str(self.dnx.get_temperature(DXL2_ID)))
        self.motor2_temp_value.setReadOnly(True)
        motor2_temp_box.addWidget(motor2_temp_label)
        motor2_temp_box.addWidget(self.motor2_temp_value)
        
        motor2_box.addLayout(motor2_label_box)
        motor2_box.addLayout(motor2_vel_box)
        motor2_box.addLayout(motor2_pos_box)
        motor2_box.addLayout(motor2_current_box)
        motor2_box.addLayout(motor2_temp_box)
        
        motor_box.addLayout(motor1_box)
        motor_box.addLayout(motor2_box)

        box = QVBoxLayout(self)
        box.addLayout(motor_box)
        self.setLayout(box)

        icon_bytes = base64.b64decode(b'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')
        icon = QImage.fromData(icon_bytes)
        icon_pixmap = QPixmap.fromImage(icon)
        self.setWindowIcon(QIcon(icon_pixmap))

        QApplication.setStyle(QStyleFactory.create('Fusion'))
        self.setWindowTitle("GUI")
        self.show()

    def have_gamepad(self):
        try:
            events = get_gamepad()
        except:
            print("No gamepad found")
            return False
        return True
        
    def keyPressEvent(self, event):
        boost_multiplier = 2 if event.modifiers() & Qt.ShiftModifier else 1

        if event.key() == Qt.Key_Q:
            self.motor1_vel_value.setText(str(50 * boost_multiplier))
        elif event.key() == Qt.Key_W:
            self.motor1_vel_value.setText(str(-50 * boost_multiplier))
        elif event.key() == Qt.Key_S:
            self.motor2_vel_value.setText(str(50 * boost_multiplier))
        elif event.key() == Qt.Key_A:
            self.motor2_vel_value.setText(str(-50 * boost_multiplier))
        elif event.key() == Qt.Key_T:
            self.motor1_switch.toggle()
        elif event.key() == Qt.Key_Y:
            self.motor2_switch.toggle()
        elif event.key() == Qt.Key_Escape:
            QApplication.quit()

    def keyReleaseEvent(self, event):
        if event.key() in [Qt.Key_Q, Qt.Key_W]:
            self.motor1_vel_value.setText('0')
        elif event.key() in [Qt.Key_A, Qt.Key_S]:
            self.motor2_vel_value.setText('0')
    
    def closeEvent(self, event):
        self.comms_thread.terminate()
        if self.have_gamepad():
            self.gamepad_thread.terminate()
        self.dnx.disable_torque(DXL1_ID)
        self.dnx.disable_torque(DXL2_ID)
        self.dnx.close_port()
        QApplication.quit()


stylesheet = """
        QCheckBox::indicator {
            width: 40px;
            height: 20px;
        }
        QCheckBox::indicator:checked {
            background-color: #34b4eb;
            border-radius: 10px;
        }
        QCheckBox::indicator:unchecked {
            background-color: #ccc;
            border-radius: 10px;
        }
    """
app = QApplication.instance()
if app is None: app = QApplication([])
app.setStyleSheet(stylesheet)
window = MainWindow()
app.exec_()

