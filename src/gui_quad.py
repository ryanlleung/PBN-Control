
import sys
import time

from inputs import get_gamepad
from motor_ctrl.sync_quad import Dynamixel, DXL1_ID, DXL2_ID, DXL3_ID, DXL4_ID

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class GamepadThread(QThread):

    def __init__(self, dnx, motor_switches, motor_vel_values):
        super().__init__()
        self.dnx = dnx
        self.motor_switches = motor_switches
        self.motor_vel_values = motor_vel_values
        self.deadvel = 10

    def run(self):
        while True:
            events = get_gamepad()
            for event in events:
                if event.code == 'ABS_Y':
                    drive_value = int(event.state / 500)
                    if abs(drive_value) < self.deadvel:
                        drive_value = 0
                    self.motor_vel_values[0].setText(str(drive_value))
                elif event.code == 'ABS_RY':
                    drive_value = int(event.state / 500)
                    if abs(drive_value) < self.deadvel:
                        drive_value = 0
                    self.motor_vel_values[1].setText(str(drive_value))
                elif event.code == 'ABS_X':
                    drive_value = int(event.state / 500)
                    if abs(drive_value) < self.deadvel:
                        drive_value = 0
                    self.motor_vel_values[2].setText(str(drive_value))
                elif event.code == 'ABS_RX':
                    drive_value = int(event.state / 500)
                    if abs(drive_value) < self.deadvel:
                        drive_value = 0
                    self.motor_vel_values[3].setText(str(drive_value))
                elif event.code == 'BTN_START' and event.state == 1:
                    self.motor_switches[0].toggle()
                elif event.code == 'BTN_SELECT' and event.state == 1:
                    self.motor_switches[1].toggle()
                elif event.code == 'BTN_MODE' and event.state == 1:
                    self.motor_switches[2].toggle()
                elif event.code == 'BTN_THUMBL' and event.state == 1:
                    self.motor_switches[3].toggle()


class MainWindow(QWidget):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.dnx = Dynamixel()
        self.dnx.open_port()
        self.dnx.enable_torque(DXL1_ID)
        self.dnx.enable_torque(DXL2_ID)
        self.dnx.enable_torque(DXL3_ID)
        self.dnx.enable_torque(DXL4_ID)

        self.motor_switches = [QCheckBox() for _ in range(4)]
        self.motor_vel_values = [QLineEdit('0') for _ in range(4)]

        self.initUI()
        if self.have_gamepad():
            self.gamepad_thread = GamepadThread(
                self.dnx, self.motor_switches, self.motor_vel_values)
            self.gamepad_thread.start()

    def initUI(self):
        motor_box = QHBoxLayout()

        self.motor_layouts = [
            self.create_motor_layout("Motor 1", DXL1_ID, self.motor_switches[0], self.motor_vel_values[0]),
            self.create_motor_layout("Motor 2", DXL2_ID, self.motor_switches[1], self.motor_vel_values[1]),
            self.create_motor_layout("Motor 3", DXL3_ID, self.motor_switches[2], self.motor_vel_values[2]),
            self.create_motor_layout("Motor 4", DXL4_ID, self.motor_switches[3], self.motor_vel_values[3])
        ]

        for layout in self.motor_layouts:
            motor_box.addLayout(layout)

        box = QVBoxLayout(self)
        box.addLayout(motor_box)

        speed_box = QHBoxLayout()
        speed_label = QLabel("Keyboard Speed")
        self.speed_input = QSpinBox()
        self.speed_input.setValue(17)
        self.speed_input.setRange(1, 100)
        self.speed_input.setFixedWidth(50)
        
        speed_box.addWidget(speed_label)
        speed_box.addWidget(self.speed_input)
        speed_box.setContentsMargins(0, 15, 0, 0)

        box.addLayout(speed_box)
        self.setLayout(box)

        self.timer = QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_values)
        self.timer.start()

        QApplication.setStyle(QStyleFactory.create('Fusion'))
        self.setWindowTitle("4-DoF Control GUI")
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
        elif motor_id == DXL2_ID:
            self.motor2_pos_value = pos_value
        elif motor_id == DXL3_ID:
            self.motor3_pos_value = pos_value
        else:
            self.motor4_pos_value = pos_value

        voltage_box = QHBoxLayout()
        voltage_label = QLabel("Voltage / V")
        voltage_label.setFixedWidth(80)
        voltage_value = QLineEdit(str(self.dnx.get_voltage(motor_id)))
        voltage_value.setReadOnly(True)
        voltage_box.addWidget(voltage_label)
        voltage_box.addWidget(voltage_value)
        if motor_id == DXL1_ID:
            self.motor1_voltage_value = voltage_value
        elif motor_id == DXL2_ID:
            self.motor2_voltage_value = voltage_value
        elif motor_id == DXL3_ID:
            self.motor3_voltage_value = voltage_value
        else:
            self.motor4_voltage_value = voltage_value

        current_box = QHBoxLayout()
        current_label = QLabel("Current / mA")
        current_label.setFixedWidth(80)
        current_value = QLineEdit(str(self.dnx.get_current(motor_id)))
        current_value.setReadOnly(True)
        current_box.addWidget(current_label)
        current_box.addWidget(current_value)
        if motor_id == DXL1_ID:
            self.motor1_current_value = current_value
        elif motor_id == DXL2_ID:
            self.motor2_current_value = current_value
        elif motor_id == DXL3_ID:
            self.motor3_current_value = current_value
        else:
            self.motor4_current_value = current_value

        temp_box = QHBoxLayout()
        temp_label = QLabel("Temp / °C")
        temp_label.setFixedWidth(80)
        temp_value = QLineEdit(str(self.dnx.get_temperature(motor_id)))
        temp_value.setReadOnly(True)
        temp_box.addWidget(temp_label)
        temp_box.addWidget(temp_value)
        if motor_id == DXL1_ID:
            self.motor1_temp_value = temp_value
        elif motor_id == DXL2_ID:
            self.motor2_temp_value = temp_value
        elif motor_id == DXL3_ID:
            self.motor3_temp_value = temp_value
        else:
            self.motor4_temp_value = temp_value

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
        for i, motor_id in enumerate([DXL1_ID, DXL2_ID, DXL3_ID, DXL4_ID]):
            switch = self.motor_switches[i]
            if switch.isChecked() != getattr(self, f'motor{i+1}_switch_last', None):
                setattr(self, f'motor{i+1}_switch_last', switch.isChecked())
                if switch.isChecked():
                    self.dnx.enable_torque(motor_id)
                else:
                    self.dnx.disable_torque(motor_id)

            self.dnx.set_velocity(motor_id, int(self.motor_vel_values[i].text()))

            pos_value = getattr(self, f'motor{i+1}_pos_value')
            voltage_value = getattr(self, f'motor{i+1}_voltage_value')
            current_value = getattr(self, f'motor{i+1}_current_value')
            temp_value = getattr(self, f'motor{i+1}_temp_value')

            pos_value.setText(str(self.dnx.get_position(motor_id)))
            voltage_value.setText(str(self.dnx.get_voltage(motor_id)))
            current_value.setText(str(self.dnx.get_current(motor_id)))
            temp_value.setText(str(self.dnx.get_temperature(motor_id)))

    def keyPressEvent(self, event):
        try:
            speed_value = int(self.speed_input.text())
        except ValueError:
            speed_value = 17

        boost_multiplier = 3 if event.modifiers() & Qt.ShiftModifier else 1
        adjusted_speed = int(speed_value * boost_multiplier)

        if event.key() == Qt.Key_Q:
            self.motor_vel_values[0].setText(str(-adjusted_speed))
        elif event.key() == Qt.Key_W:
            self.motor_vel_values[0].setText(str(adjusted_speed))
        elif event.key() == Qt.Key_S:
            self.motor_vel_values[1].setText(str(adjusted_speed))
        elif event.key() == Qt.Key_A:
            self.motor_vel_values[1].setText(str(-adjusted_speed))
        elif event.key() == Qt.Key_R:
            self.motor_vel_values[2].setText(str(adjusted_speed))
        elif event.key() == Qt.Key_E:
            self.motor_vel_values[2].setText(str(-adjusted_speed))
        elif event.key() == Qt.Key_F:
            self.motor_vel_values[3].setText(str(adjusted_speed))
        elif event.key() == Qt.Key_D:
            self.motor_vel_values[3].setText(str(-adjusted_speed))
        elif event.key() == Qt.Key_M:
            self.motor_vel_values[0].setText(str(-adjusted_speed))
            self.motor_vel_values[1].setText(str(-adjusted_speed))
            self.motor_vel_values[2].setText(str(-adjusted_speed))
            self.motor_vel_values[3].setText(str(-adjusted_speed))
        elif event.key() == Qt.Key_N:
            self.motor_vel_values[0].setText(str(adjusted_speed))
            self.motor_vel_values[1].setText(str(adjusted_speed))
            self.motor_vel_values[2].setText(str(adjusted_speed))
            self.motor_vel_values[3].setText(str(adjusted_speed))
        elif event.key() == Qt.Key_T:
            self.motor_switches[0].toggle()
        elif event.key() == Qt.Key_Y:
            self.motor_switches[1].toggle()
        elif event.key() == Qt.Key_U:
            self.motor_switches[2].toggle()
        elif event.key() == Qt.Key_I:
            self.motor_switches[3].toggle()
        elif event.key() == Qt.Key_Escape:
            QApplication.quit()

    def keyReleaseEvent(self, event):
        if event.key() in [Qt.Key_Q, Qt.Key_W]:
            self.motor_vel_values[0].setText('0')
        elif event.key() in [Qt.Key_A, Qt.Key_S]:
            self.motor_vel_values[1].setText('0')
        elif event.key() in [Qt.Key_E, Qt.Key_R]:
            self.motor_vel_values[2].setText('0')
        elif event.key() in [Qt.Key_D, Qt.Key_F]:
            self.motor_vel_values[3].setText('0')
        elif event.key() in [Qt.Key_M, Qt.Key_N]:
            self.motor_vel_values[0].setText('0')
            self.motor_vel_values[1].setText('0')
            self.motor_vel_values[2].setText('0')
            self.motor_vel_values[3].setText('0')

    def closeEvent(self, event):
        if self.have_gamepad():
            self.gamepad_thread.terminate()
        self.dnx.disable_torque(DXL1_ID)
        self.dnx.disable_torque(DXL2_ID)
        self.dnx.disable_torque(DXL3_ID)
        self.dnx.disable_torque(DXL4_ID)
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
