import sys
import time

from inputs import get_gamepad
from motor_ctrl.sync_dual import Dynamixel, DXL1_ID, DXL2_ID

from PyQt5.QtCore import QThread, QTimer, Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QLineEdit, QStyleFactory

class GamepadThread(QThread):

    def __init__(self, dnx, motor1_switch, motor1_vel_value, motor2_switch, motor2_vel_value):
        super().__init__()
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
                    drive_value = int(event.state / 500)  # Adjust scaling factor here
                    if abs(drive_value) < self.deadvel:
                        drive_value = 0
                    self.motor1_vel_value.setText(str(drive_value))
                elif event.code == 'ABS_RY':
                    drive_value = int(event.state / 500)  # Adjust scaling factor here
                    if abs(drive_value) < self.deadvel:
                        drive_value = 0
                    self.motor2_vel_value.setText(str(drive_value))
                elif event.code == 'BTN_START' and event.state == 1:
                    self.motor1_switch.toggle()
                elif event.code == 'BTN_SELECT' and event.state == 1:
                    self.motor2_switch.toggle()


class MainWindow(QWidget):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.dnx = Dynamixel()
        self.dnx.open_port()
        self.dnx.enable_torque(DXL1_ID)
        self.dnx.enable_torque(DXL2_ID)

        self.motor1_switch = QCheckBox()
        self.motor1_vel_value = QLineEdit('0')
        self.motor2_switch = QCheckBox()
        self.motor2_vel_value = QLineEdit('0')

        self.initUI()
        if self.have_gamepad():
            self.gamepad_thread = GamepadThread(
                self.dnx, self.motor1_switch, self.motor1_vel_value, self.motor2_switch, self.motor2_vel_value)
            self.gamepad_thread.start()

    def initUI(self):
        motor_box = QHBoxLayout()

        self.motor1_layout = self.create_motor_layout("Motor 1", DXL1_ID, self.motor1_switch, self.motor1_vel_value)
        self.motor2_layout = self.create_motor_layout("Motor 2", DXL2_ID, self.motor2_switch, self.motor2_vel_value)
        
        motor_box.addLayout(self.motor1_layout)
        motor_box.addLayout(self.motor2_layout)

        box = QVBoxLayout(self)
        box.addLayout(motor_box)
        self.setLayout(box)

        self.timer = QTimer()
        self.timer.setInterval(100)  # Interval in milliseconds
        self.timer.timeout.connect(self.update_values)
        self.timer.start()

        QApplication.setStyle(QStyleFactory.create('Fusion'))
        self.setWindowTitle("2-DoF Control GUI")
        self.show()

    def create_motor_layout(self, label_text, motor_id, motor_switch, motor_vel_value):
        motor_box = QVBoxLayout()

        label_box = QHBoxLayout()
        label = QLabel(label_text)
        label.setStyleSheet("font-size: 10pt")
        motor_switch.setChecked(True)
        label_box.addWidget(label)
        label_box.addStretch(1)
        label_box.addWidget(motor_switch)

        vel_box = QHBoxLayout()
        vel_label = QLabel("Set Velocity")
        vel_label.setFixedWidth(80)
        motor_vel_value.setReadOnly(True)
        vel_box.addWidget(vel_label)
        vel_box.addWidget(motor_vel_value)

        pos_box = QHBoxLayout()
        pos_label = QLabel("Position")
        pos_label.setFixedWidth(80)
        pos_value = QLineEdit(str(self.dnx.get_position(motor_id)))
        pos_value.setReadOnly(True)
        pos_box.addWidget(pos_label)
        pos_box.addWidget(pos_value)
        if motor_id == DXL1_ID:
            self.motor1_pos_value = pos_value
        else:
            self.motor2_pos_value = pos_value

        voltage_box = QHBoxLayout()
        voltage_label = QLabel("Voltage / V")
        voltage_label.setFixedWidth(80)
        voltage_value = QLineEdit(str(self.dnx.get_voltage(motor_id)))
        voltage_value.setReadOnly(True)
        voltage_box.addWidget(voltage_label)
        voltage_box.addWidget(voltage_value)
        if motor_id == DXL1_ID:
            self.motor1_voltage_value = voltage_value
        else:
            self.motor2_voltage_value = voltage_value

        current_box = QHBoxLayout()
        current_label = QLabel("Current / mA")
        current_label.setFixedWidth(80)
        current_value = QLineEdit(str(self.dnx.get_current(motor_id)))
        current_value.setReadOnly(True)
        current_box.addWidget(current_label)
        current_box.addWidget(current_value)
        if motor_id == DXL1_ID:
            self.motor1_current_value = current_value
        else:
            self.motor2_current_value = current_value

        temp_box = QHBoxLayout()
        temp_label = QLabel("Temp / °C")
        temp_label.setFixedWidth(80)
        temp_value = QLineEdit(str(self.dnx.get_temperature(motor_id)))
        temp_value.setReadOnly(True)
        temp_box.addWidget(temp_label)
        temp_box.addWidget(temp_value)
        if motor_id == DXL1_ID:
            self.motor1_temp_value = temp_value
        else:
            self.motor2_temp_value = temp_value

        motor_box.addLayout(label_box)
        motor_box.addLayout(vel_box)
        motor_box.addLayout(pos_box)
        motor_box.addLayout(voltage_box)
        motor_box.addLayout(current_box)
        motor_box.addLayout(temp_box)

        return motor_box

    def have_gamepad(self):
        try:
            get_gamepad()
        except:
            print("No gamepad found")
            return False
        return True

    def update_values(self):
        if self.motor1_switch.isChecked() != getattr(self, 'motor1_switch_last', None):
            self.motor1_switch_last = self.motor1_switch.isChecked()
            if self.motor1_switch_last:
                self.dnx.enable_torque(DXL1_ID)
            else:
                self.dnx.disable_torque(DXL1_ID)
        if self.motor2_switch.isChecked() != getattr(self, 'motor2_switch_last', None):
            self.motor2_switch_last = self.motor2_switch.isChecked()
            if self.motor2_switch_last:
                self.dnx.enable_torque(DXL2_ID)
            else:
                self.dnx.disable_torque(DXL2_ID)

        self.dnx.set_velocity(DXL1_ID, int(self.motor1_vel_value.text()))
        self.dnx.set_velocity(DXL2_ID, int(self.motor2_vel_value.text()))

        self.motor1_pos_value.setText(str(self.dnx.get_position(DXL1_ID)))
        self.motor1_voltage_value.setText(str(self.dnx.get_voltage(DXL1_ID)))
        self.motor1_current_value.setText(str(self.dnx.get_current(DXL1_ID)))
        self.motor1_temp_value.setText(str(self.dnx.get_temperature(DXL1_ID)))
        self.motor2_pos_value.setText(str(self.dnx.get_position(DXL2_ID)))
        self.motor2_voltage_value.setText(str(self.dnx.get_voltage(DXL2_ID)))
        self.motor2_current_value.setText(str(self.dnx.get_current(DXL2_ID)))
        self.motor2_temp_value.setText(str(self.dnx.get_temperature(DXL2_ID)))

    def keyPressEvent(self, event):
        boost_multiplier = 3 if event.modifiers() & Qt.ShiftModifier else 1

        if event.key() == Qt.Key_Q:
            self.motor1_vel_value.setText(str(-17 * boost_multiplier))
        elif event.key() == Qt.Key_W:
            self.motor1_vel_value.setText(str(17 * boost_multiplier))
        elif event.key() == Qt.Key_S:
            self.motor2_vel_value.setText(str(17 * boost_multiplier))
        elif event.key() == Qt.Key_A:
            self.motor2_vel_value.setText(str(-17 * boost_multiplier))
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
if app is None:
    app = QApplication([])
app.setStyleSheet(stylesheet)
window = MainWindow()
app.exec_()
