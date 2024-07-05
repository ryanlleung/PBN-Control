
import sys
import time

from inputs import get_gamepad
from motor_ctrl.sync_clamp import Dynamixel6, DXL1_ID, DXL2_ID, DXL3_ID, DXL4_ID, DXL5_ID, DXL6_ID

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

DEFAULT_KEY_SPEED = 33
CLAMP_KEY_SPEED = 150
GAMEPAD_SCALER = 1/500

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
                    drive_value = int(event.state * GAMEPAD_SCALER)
                    if abs(drive_value) < self.deadvel:
                        drive_value = 0
                    self.motor_vel_values[0].setText(str(drive_value))
                elif event.code == 'ABS_RY':
                    drive_value = int(event.state * GAMEPAD_SCALER)
                    if abs(drive_value) < self.deadvel:
                        drive_value = 0
                    self.motor_vel_values[1].setText(str(drive_value))
                elif event.code == 'ABS_X':
                    drive_value = int(event.state * GAMEPAD_SCALER)
                    if abs(drive_value) < self.deadvel:
                        drive_value = 0
                    self.motor_vel_values[2].setText(str(drive_value))
                elif event.code == 'ABS_RX':
                    drive_value = int(event.state * GAMEPAD_SCALER)
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
        self.dnx = Dynamixel6()
        self.dnx.open_port()
        self.dnx.enable_torque(DXL1_ID)
        self.dnx.enable_torque(DXL2_ID)
        self.dnx.enable_torque(DXL3_ID)
        self.dnx.enable_torque(DXL4_ID)
        self.dnx.enable_torque(DXL5_ID)
        self.dnx.enable_torque(DXL6_ID)
        self.dnx.define_homeclamp()

        self.motor_switches = [QCheckBox() for _ in range(6)]
        self.motor_vel_values = [QLineEdit('0') for _ in range(6)]
        self.clamp1_keymove = False
        self.clamp2_keymove = False

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
            self.create_motor_layout("Motor 4", DXL4_ID, self.motor_switches[3], self.motor_vel_values[3]),
            self.create_motor_layout("Motor 5", DXL5_ID, self.motor_switches[4], self.motor_vel_values[4]),
            self.create_motor_layout("Motor 6", DXL6_ID, self.motor_switches[5], self.motor_vel_values[5])
        ]

        for layout in self.motor_layouts:
            motor_box.addLayout(layout)

        ## Keyboard Speed Box ##

        box = QVBoxLayout(self)
        box.addLayout(motor_box)

        speed_box = QHBoxLayout()
        speed_label = QLabel("Keyboard Speed")
        self.speed_input = QSpinBox()
        self.speed_input.setValue(DEFAULT_KEY_SPEED)
        self.speed_input.setRange(1, 100)
        self.speed_input.setFixedWidth(50)
        
        speed_box.addWidget(speed_label)
        speed_box.addWidget(self.speed_input)
        speed_box.setContentsMargins(0, 15, 0, 0)

        ## Clamping Controls ##
        
        clamp_box = QHBoxLayout()
                
        clamp1_box = QVBoxLayout()
        clamp1_label = QLabel("Clamp 1")
        clamp1_label.setFixedWidth(80)
        clamp1_label.setStyleSheet("font-size: 10pt")
        
        clamp1_restpos_box = QHBoxLayout()
        clamp1_restpos_label = QLabel("Rest Position")
        clamp1_restpos_label.setFixedWidth(100)
        self.clamp1_restpos_value = QLineEdit(str(self.dnx.clamp1_pos["rest"]))
        self.clamp1_restpos_value.setReadOnly(True)
        self.clamp1_absrestpos_value = QLineEdit(str(self.dnx.clamp1_pos["rest"] + self.dnx.clamp1_pos0))
        self.clamp1_absrestpos_value.setFixedWidth(60)
        self.clamp1_absrestpos_value.setReadOnly(True)
        clamp1_restpos_setbutton = QPushButton("Set")
        clamp1_restpos_setbutton.clicked.connect(lambda: self.dnx.define_restclamp1())
        clamp1_restpos_goto_button = QPushButton("Go To")
        clamp1_restpos_goto_button.clicked.connect(lambda: self.dnx.set_clamp1("rest"))
        clamp1_restpos_box.addWidget(clamp1_restpos_label)
        clamp1_restpos_box.addWidget(self.clamp1_restpos_value)
        clamp1_restpos_box.addWidget(self.clamp1_absrestpos_value)
        clamp1_restpos_box.addWidget(clamp1_restpos_setbutton)
        clamp1_restpos_box.addWidget(clamp1_restpos_goto_button)        
        
        clamp1_lightpos_box = QHBoxLayout()
        clamp1_lightpos_label = QLabel("Light Position")
        clamp1_lightpos_label.setFixedWidth(100)
        self.clamp1_lightpos_value = QLineEdit(str(self.dnx.clamp1_pos["light"]))
        self.clamp1_lightpos_value.setReadOnly(True)
        self.clamp1_abslightpos_value = QLineEdit(str(self.dnx.clamp1_pos["light"] + self.dnx.clamp1_pos0))
        self.clamp1_abslightpos_value.setFixedWidth(60)
        self.clamp1_abslightpos_value.setReadOnly(True)
        clamp1_lightpos_setbutton = QPushButton("Set")
        clamp1_lightpos_setbutton.clicked.connect(lambda: self.dnx.define_lightclamp1())
        clamp1_lightpos_goto_button = QPushButton("Go To")
        clamp1_lightpos_goto_button.clicked.connect(lambda: self.dnx.set_clamp1("light"))
        clamp1_lightpos_box.addWidget(clamp1_lightpos_label)
        clamp1_lightpos_box.addWidget(self.clamp1_lightpos_value)
        clamp1_lightpos_box.addWidget(self.clamp1_abslightpos_value)
        clamp1_lightpos_box.addWidget(clamp1_lightpos_setbutton)
        clamp1_lightpos_box.addWidget(clamp1_lightpos_goto_button)
        
        clamp1_mediumpos_box = QHBoxLayout()
        clamp1_mediumpos_label = QLabel("Medium Position")
        clamp1_mediumpos_label.setFixedWidth(100)
        self.clamp1_mediumpos_value = QLineEdit(str(self.dnx.clamp1_pos["medium"]))
        self.clamp1_mediumpos_value.setReadOnly(True)
        self.clamp1_absmediumpos_value = QLineEdit(str(self.dnx.clamp1_pos["medium"] + self.dnx.clamp1_pos0))
        self.clamp1_absmediumpos_value.setFixedWidth(60)
        self.clamp1_absmediumpos_value.setReadOnly(True)
        clamp1_mediumpos_setbutton = QPushButton("Set")
        clamp1_mediumpos_setbutton.clicked.connect(lambda: self.dnx.define_mediumclamp1())
        clamp1_mediumpos_goto_button = QPushButton("Go To")
        clamp1_mediumpos_goto_button.clicked.connect(lambda: self.dnx.set_clamp1("medium"))
        clamp1_mediumpos_box.addWidget(clamp1_mediumpos_label)
        clamp1_mediumpos_box.addWidget(self.clamp1_mediumpos_value)
        clamp1_mediumpos_box.addWidget(self.clamp1_absmediumpos_value)
        clamp1_mediumpos_box.addWidget(clamp1_mediumpos_setbutton)
        clamp1_mediumpos_box.addWidget(clamp1_mediumpos_goto_button)
        
        clamp1_heavypos_box = QHBoxLayout()
        clamp1_heavypos_label = QLabel("Heavy Position")
        clamp1_heavypos_label.setFixedWidth(100)
        self.clamp1_heavypos_value = QLineEdit(str(self.dnx.clamp1_pos["heavy"]))
        self.clamp1_heavypos_value.setReadOnly(True)
        self.clamp1_absheavypos_value = QLineEdit(str(self.dnx.clamp1_pos["heavy"] + self.dnx.clamp1_pos0))
        self.clamp1_absheavypos_value.setFixedWidth(60)
        self.clamp1_absheavypos_value.setReadOnly(True)
        clamp1_heavypos_setbutton = QPushButton("Set")
        clamp1_heavypos_setbutton.clicked.connect(lambda: self.dnx.define_heavyclamp1())
        clamp1_heavypos_goto_button = QPushButton("Go To")
        clamp1_heavypos_goto_button.clicked.connect(lambda: self.dnx.set_clamp1("heavy"))
        clamp1_heavypos_box.addWidget(clamp1_heavypos_label)
        clamp1_heavypos_box.addWidget(self.clamp1_heavypos_value)
        clamp1_heavypos_box.addWidget(self.clamp1_absheavypos_value)
        clamp1_heavypos_box.addWidget(clamp1_heavypos_setbutton)
        clamp1_heavypos_box.addWidget(clamp1_heavypos_goto_button)
        
        clamp1_savepos_box = QHBoxLayout()
        clamp1_savepos_button = QPushButton("Save Positions")
        clamp1_savepos_button.clicked.connect(lambda: self.dnx.save_clamp1pos())
        clamp1_savepos_box.addWidget(clamp1_savepos_button)
        
        clamp1_homepos_box = QHBoxLayout()
        clamp1_homepos_button = QPushButton("Perform Homing Routine")
        clamp1_homepos_button.clicked.connect(lambda: self.dnx.home_clamp1())
        clamp1_gohome_button = QPushButton("Go Home")
        clamp1_gohome_button.clicked.connect(lambda: self.dnx.set_clamp1("home"))
        clamp1_homepos_box.addWidget(clamp1_homepos_button)
        clamp1_homepos_box.addWidget(clamp1_gohome_button)
        
        clamp1_go_box = QHBoxLayout()
        clamp1_tighten45_button = QPushButton("Tighten 45°")
        clamp1_tighten45_button.clicked.connect(lambda: self.dnx.set_position(DXL5_ID, self.dnx.get_position(DXL5_ID) + 512))
        clamp1_loosen45_button = QPushButton("Loosen 45°")
        clamp1_loosen45_button.clicked.connect(lambda: self.dnx.set_position(DXL5_ID, self.dnx.get_position(DXL5_ID) - 512))
        clamp1_tightin23_button = QPushButton("Tighten 23°")
        clamp1_tightin23_button.clicked.connect(lambda: self.dnx.set_position(DXL5_ID, self.dnx.get_position(DXL5_ID) + 256))
        clamp1_loosen23_button = QPushButton("Loosen 23°")
        clamp1_loosen23_button.clicked.connect(lambda: self.dnx.set_position(DXL5_ID, self.dnx.get_position(DXL5_ID) - 256))
        clamp1_go_box.addWidget(clamp1_tighten45_button)
        clamp1_go_box.addWidget(clamp1_loosen45_button)
        clamp1_go_box.addWidget(clamp1_tightin23_button)
        clamp1_go_box.addWidget(clamp1_loosen23_button)
    
        clamp1_box.addWidget(clamp1_label)
        clamp1_box.addLayout(clamp1_restpos_box)
        clamp1_box.addLayout(clamp1_lightpos_box)
        clamp1_box.addLayout(clamp1_mediumpos_box)
        clamp1_box.addLayout(clamp1_heavypos_box)
        clamp1_box.addLayout(clamp1_savepos_box)
        clamp1_box.addLayout(clamp1_homepos_box)
        clamp1_box.addLayout(clamp1_go_box)
        
        clamp2_box = QVBoxLayout()
        clamp2_label = QLabel("Clamp 2")
        clamp2_label.setFixedWidth(80)
        clamp2_label.setStyleSheet("font-size: 10pt")
        
        clamp2_restpos_box = QHBoxLayout()
        clamp2_restpos_label = QLabel("Rest Position")
        clamp2_restpos_label.setFixedWidth(100)
        self.clamp2_restpos_value = QLineEdit(str(self.dnx.clamp2_pos["rest"]))
        self.clamp2_restpos_value.setReadOnly(True)
        self.clamp2_absrestpos_value = QLineEdit(str(self.dnx.clamp2_pos["rest"] + self.dnx.clamp2_pos0))
        self.clamp2_absrestpos_value.setFixedWidth(60)
        self.clamp2_absrestpos_value.setReadOnly(True)
        clamp2_restpos_setbutton = QPushButton("Set")
        clamp2_restpos_setbutton.clicked.connect(lambda: self.dnx.define_restclamp2())
        clamp2_restpos_goto_button = QPushButton("Go To")
        clamp2_restpos_goto_button.clicked.connect(lambda: self.dnx.set_clamp2("rest"))
        clamp2_restpos_box.addWidget(clamp2_restpos_label)
        clamp2_restpos_box.addWidget(self.clamp2_restpos_value)
        clamp2_restpos_box.addWidget(self.clamp2_absrestpos_value)
        clamp2_restpos_box.addWidget(clamp2_restpos_setbutton)
        clamp2_restpos_box.addWidget(clamp2_restpos_goto_button)
        
        clamp2_lightpos_box = QHBoxLayout()
        clamp2_lightpos_label = QLabel("Light Position")
        clamp2_lightpos_label.setFixedWidth(100)
        self.clamp2_lightpos_value = QLineEdit(str(self.dnx.clamp2_pos["light"]))
        self.clamp2_lightpos_value.setReadOnly(True)
        self.clamp2_abslightpos_value = QLineEdit(str(self.dnx.clamp2_pos["light"] + self.dnx.clamp2_pos0))
        self.clamp2_abslightpos_value.setFixedWidth(60)
        self.clamp2_abslightpos_value.setReadOnly(True)
        clamp2_lightpos_setbutton = QPushButton("Set")
        clamp2_lightpos_setbutton.clicked.connect(lambda: self.dnx.define_lightclamp2())
        clamp2_lightpos_goto_button = QPushButton("Go To")
        clamp2_lightpos_goto_button.clicked.connect(lambda: self.dnx.set_clamp2("light"))
        clamp2_lightpos_box.addWidget(clamp2_lightpos_label)
        clamp2_lightpos_box.addWidget(self.clamp2_lightpos_value)
        clamp2_lightpos_box.addWidget(self.clamp2_abslightpos_value)
        clamp2_lightpos_box.addWidget(clamp2_lightpos_setbutton)
        clamp2_lightpos_box.addWidget(clamp2_lightpos_goto_button)
        
        clamp2_mediumpos_box = QHBoxLayout()
        clamp2_mediumpos_label = QLabel("Medium Position")
        clamp2_mediumpos_label.setFixedWidth(100)
        self.clamp2_mediumpos_value = QLineEdit(str(self.dnx.clamp2_pos["medium"]))
        self.clamp2_mediumpos_value.setReadOnly(True)
        self.clamp2_absmediumpos_value = QLineEdit(str(self.dnx.clamp2_pos["medium"] + self.dnx.clamp2_pos0))
        self.clamp2_absmediumpos_value.setFixedWidth(60)
        self.clamp2_absmediumpos_value.setReadOnly(True)
        clamp2_mediumpos_setbutton = QPushButton("Set")
        clamp2_mediumpos_setbutton.clicked.connect(lambda: self.dnx.define_mediumclamp2())
        clamp2_mediumpos_goto_button = QPushButton("Go To")
        clamp2_mediumpos_goto_button.clicked.connect(lambda: self.dnx.set_clamp2("medium"))
        clamp2_mediumpos_box.addWidget(clamp2_mediumpos_label)
        clamp2_mediumpos_box.addWidget(self.clamp2_mediumpos_value)
        clamp2_mediumpos_box.addWidget(self.clamp2_absmediumpos_value)
        clamp2_mediumpos_box.addWidget(clamp2_mediumpos_setbutton)
        clamp2_mediumpos_box.addWidget(clamp2_mediumpos_goto_button)
        
        clamp2_heavypos_box = QHBoxLayout()
        clamp2_heavypos_label = QLabel("Heavy Position")
        clamp2_heavypos_label.setFixedWidth(100)
        self.clamp2_heavypos_value = QLineEdit(str(self.dnx.clamp2_pos["heavy"]))
        self.clamp2_heavypos_value.setReadOnly(True)
        self.clamp2_absheavypos_value = QLineEdit(str(self.dnx.clamp2_pos["heavy"] + self.dnx.clamp2_pos0))
        self.clamp2_absheavypos_value.setFixedWidth(60)
        self.clamp2_absheavypos_value.setReadOnly(True)
        clamp2_heavypos_setbutton = QPushButton("Set")
        clamp2_heavypos_setbutton.clicked.connect(lambda: self.dnx.define_heavyclamp2())
        clamp2_heavypos_goto_button = QPushButton("Go To")
        clamp2_heavypos_goto_button.clicked.connect(lambda: self.dnx.set_clamp2("heavy"))
        clamp2_heavypos_box.addWidget(clamp2_heavypos_label)
        clamp2_heavypos_box.addWidget(self.clamp2_heavypos_value)
        clamp2_heavypos_box.addWidget(self.clamp2_absheavypos_value)
        clamp2_heavypos_box.addWidget(clamp2_heavypos_setbutton)
        clamp2_heavypos_box.addWidget(clamp2_heavypos_goto_button)
        
        clamp2_savepos_box = QHBoxLayout()
        clamp2_savepos_button = QPushButton("Save Positions")
        clamp2_savepos_button.clicked.connect(lambda: self.dnx.save_clamp2pos())
        clamp2_savepos_box.addWidget(clamp2_savepos_button)
        
        clamp2_homepos_box = QHBoxLayout()
        clamp2_homepos_button = QPushButton("Perform Homing Routine")
        clamp2_homepos_button.clicked.connect(lambda: self.dnx.home_clamp2())
        clamp2_gohome_button = QPushButton("Go Home")
        clamp2_gohome_button.clicked.connect(lambda: self.dnx.set_clamp2("home"))
        clamp2_homepos_box.addWidget(clamp2_homepos_button)
        clamp2_homepos_box.addWidget(clamp2_gohome_button)
        
        clamp2_go_box = QHBoxLayout()
        clamp2_tighten45_button = QPushButton("Tighten 45°")
        clamp2_tighten45_button.clicked.connect(lambda: self.dnx.set_position(DXL6_ID, self.dnx.get_position(DXL6_ID) + 512))
        clamp2_loosen45_button = QPushButton("Loosen 45°")
        clamp2_loosen45_button.clicked.connect(lambda: self.dnx.set_position(DXL6_ID, self.dnx.get_position(DXL6_ID) - 512))
        clamp2_tightin23_button = QPushButton("Tighten 23°")
        clamp2_tightin23_button.clicked.connect(lambda: self.dnx.set_position(DXL6_ID, self.dnx.get_position(DXL6_ID) + 256))
        clamp2_loosen23_button = QPushButton("Loosen 23°")
        clamp2_loosen23_button.clicked.connect(lambda: self.dnx.set_position(DXL6_ID, self.dnx.get_position(DXL6_ID) - 256))
        clamp2_go_box.addWidget(clamp2_tighten45_button)
        clamp2_go_box.addWidget(clamp2_loosen45_button)
        clamp2_go_box.addWidget(clamp2_tightin23_button)
        clamp2_go_box.addWidget(clamp2_loosen23_button)
        
        clamp2_box.addWidget(clamp2_label)
        clamp2_box.addLayout(clamp2_restpos_box)
        clamp2_box.addLayout(clamp2_lightpos_box)
        clamp2_box.addLayout(clamp2_mediumpos_box)
        clamp2_box.addLayout(clamp2_heavypos_box)
        clamp2_box.addLayout(clamp2_savepos_box)
        clamp2_box.addLayout(clamp2_homepos_box)
        clamp2_box.addLayout(clamp2_go_box)
        
        clamp_box.addLayout(clamp1_box)
        clamp_box.addLayout(clamp2_box)
        
        ## Clamping Configurations ##
        
        big_clampconfig_box = QVBoxLayout()
        big_clampconfig_box.setContentsMargins(0, 15, 0, 0)
        clamp_config_label = QLabel("Clamp Configurations")
        clamp_config_label.setStyleSheet("font-size: 10pt")
        
        clampconfig_box = QHBoxLayout()
        moveLR_button = QPushButton("Move Left/Right")
        moveLR_button.clicked.connect(lambda: self.dnx.set_movingLR())
        moveTB_button = QPushButton("Move Top/Bottom")
        moveTB_button.clicked.connect(lambda: self.dnx.set_movingTB())
        movehalf_button = QPushButton("Move Halves/All")
        movehalf_button.clicked.connect(lambda: self.dnx.set_movingHalf())
        clampconfig_box.addWidget(moveLR_button)
        clampconfig_box.addWidget(moveTB_button)
        clampconfig_box.addWidget(movehalf_button)
        
        big_clampconfig_box.addWidget(clamp_config_label)
        big_clampconfig_box.addLayout(clampconfig_box)
        
        box.addLayout(speed_box)
        box.addLayout(clamp_box)
        box.addLayout(big_clampconfig_box)
        self.setLayout(box)

        self.timer = QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_values)
        self.timer.start()

        QApplication.setStyle(QStyleFactory.create('Fusion'))
        self.setWindowTitle("4-DoF+Clamping Control GUI")
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
        elif motor_id == DXL4_ID:
            self.motor4_pos_value = pos_value
        elif motor_id == DXL5_ID:
            self.motor5_pos_value = pos_value
        else:
            self.motor6_pos_value = pos_value

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
        elif motor_id == DXL4_ID:
            self.motor4_voltage_value = voltage_value
        elif motor_id == DXL5_ID:
            self.motor5_voltage_value = voltage_value
        else:
            self.motor6_voltage_value = voltage_value

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
        elif motor_id == DXL4_ID:
            self.motor4_current_value = current_value
        elif motor_id == DXL5_ID:
            self.motor5_current_value = current_value
        else:
            self.motor6_current_value = current_value

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
        elif motor_id == DXL4_ID:
            self.motor4_temp_value = temp_value
        elif motor_id == DXL5_ID:
            self.motor5_temp_value = temp_value
        else:
            self.motor6_temp_value = temp_value

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
        
        if self.clamp1_keymove:
            switch = self.motor_switches[4]
            if switch.isChecked() != getattr(self, 'motor5_switch_last', None):
                self.motor5_switch_last = switch.isChecked()
                if switch.isChecked():
                    self.dnx.enable_torque(DXL5_ID)
                else:
                    self.dnx.disable_torque(DXL5_ID)
            self.dnx.set_velocity(DXL5_ID, int(self.motor_vel_values[4].text()))
            
        if self.clamp2_keymove:
            switch = self.motor_switches[5]
            if switch.isChecked() != getattr(self, 'motor6_switch_last', None):
                self.motor6_switch_last = switch.isChecked()
                if switch.isChecked():
                    self.dnx.enable_torque(DXL6_ID)
                else:
                    self.dnx.disable_torque(DXL6_ID)
            self.dnx.set_velocity(DXL6_ID, int(self.motor_vel_values[5].text()))

        for i, motor_id in enumerate([DXL1_ID, DXL2_ID, DXL3_ID, DXL4_ID, DXL5_ID, DXL6_ID]):
            pos_value = getattr(self, f'motor{i+1}_pos_value')
            voltage_value = getattr(self, f'motor{i+1}_voltage_value')
            current_value = getattr(self, f'motor{i+1}_current_value')
            temp_value = getattr(self, f'motor{i+1}_temp_value')

            pos_value.setText(str(self.dnx.get_position(motor_id)))
            voltage_value.setText(str(self.dnx.get_voltage(motor_id)))
            current_value.setText(str(self.dnx.get_current(motor_id)))
            temp_value.setText(str(self.dnx.get_temperature(motor_id)))
        
        self.clamp1_restpos_value.setText(str(self.dnx.clamp1_pos["rest"]))
        self.clamp1_absrestpos_value.setText(str(self.dnx.clamp1_pos["rest"] + self.dnx.clamp1_pos0))
        self.clamp1_lightpos_value.setText(str(self.dnx.clamp1_pos["light"]))
        self.clamp1_abslightpos_value.setText(str(self.dnx.clamp1_pos["light"] + self.dnx.clamp1_pos0))
        self.clamp1_mediumpos_value.setText(str(self.dnx.clamp1_pos["medium"]))
        self.clamp1_absmediumpos_value.setText(str(self.dnx.clamp1_pos["medium"] + self.dnx.clamp1_pos0))
        self.clamp1_heavypos_value.setText(str(self.dnx.clamp1_pos["heavy"]))
        self.clamp1_absheavypos_value.setText(str(self.dnx.clamp1_pos["heavy"] + self.dnx.clamp1_pos0))

        self.clamp2_restpos_value.setText(str(self.dnx.clamp2_pos["rest"]))
        self.clamp2_absrestpos_value.setText(str(self.dnx.clamp2_pos["rest"] + self.dnx.clamp2_pos0))
        self.clamp2_lightpos_value.setText(str(self.dnx.clamp2_pos["light"]))
        self.clamp2_abslightpos_value.setText(str(self.dnx.clamp2_pos["light"] + self.dnx.clamp2_pos0))
        self.clamp2_mediumpos_value.setText(str(self.dnx.clamp2_pos["medium"]))
        self.clamp2_absmediumpos_value.setText(str(self.dnx.clamp2_pos["medium"] + self.dnx.clamp2_pos0))
        self.clamp2_heavypos_value.setText(str(self.dnx.clamp2_pos["heavy"]))
        self.clamp2_absheavypos_value.setText(str(self.dnx.clamp2_pos["heavy"] + self.dnx.clamp2_pos0))

    def keyPressEvent(self, event):
        try:
            speed_value = int(self.speed_input.text())
        except ValueError:
            speed_value = DEFAULT_KEY_SPEED

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
        elif event.key() == Qt.Key_N:
            self.motor_vel_values[0].setText(str(-adjusted_speed))
            self.motor_vel_values[1].setText(str(-adjusted_speed))
            self.motor_vel_values[2].setText(str(-adjusted_speed))
            self.motor_vel_values[3].setText(str(-adjusted_speed))
        elif event.key() == Qt.Key_M:
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
            
        elif event.key() == Qt.Key_BracketLeft:
            self.clamp1_keymove = True
            self.motor_vel_values[4].setText(str(-CLAMP_KEY_SPEED))
        elif event.key() == Qt.Key_BracketRight:
            self.clamp1_keymove = True
            self.motor_vel_values[4].setText(str(CLAMP_KEY_SPEED))
        elif event.key() == Qt.Key_Semicolon:
            self.clamp2_keymove = True
            self.motor_vel_values[5].setText(str(-CLAMP_KEY_SPEED))
        elif event.key() == Qt.Key_Apostrophe:
            self.clamp2_keymove = True
            self.motor_vel_values[5].setText(str(CLAMP_KEY_SPEED))
            
        elif event.key() == Qt.Key_0:
            self.dnx.set_clamp1("home")
            self.dnx.set_clamp2("home")
        elif event.key() == Qt.Key_1:
            self.dnx.set_movingLR()
        elif event.key() == Qt.Key_2:
            self.dnx.set_movingTB()
        elif event.key() == Qt.Key_3:
            self.dnx.set_movingHalf()
        elif event.key() == Qt.Key_4:
            self.dnx.set_clamp1("rest")
            self.dnx.set_clamp2("rest")
            
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
        elif event.key() in [Qt.Key_BracketLeft, Qt.Key_BracketRight]:
            self.motor_vel_values[4].setText('0')
            self.dnx.set_velocity(DXL5_ID, 0)
            self.clamp1_keymove = False
        elif event.key() in [Qt.Key_Semicolon, Qt.Key_Apostrophe]:
            self.motor_vel_values[5].setText('0')
            self.dnx.set_velocity(DXL6_ID, 0)
            self.clamp2_keymove = False

    def check_homed(self):
        motor5_homed = True
        if abs(self.dnx.get_position(DXL5_ID)- self.dnx.clamp1_pos0) > 2:
            print("Motor 5 not homed")
            motor5_homed = False
        motor6_homed = True
        if abs(self.dnx.get_position(DXL6_ID)- self.dnx.clamp2_pos0) > 2:
            print("Motor 6 not homed")
            motor6_homed = False
        return motor5_homed and motor6_homed

    def closeEvent(self, event):
        if not self.check_homed():
            print("Clamps not homed. Please home clamps before closing the GUI.")
            QMessageBox.warning(self, 'Warning', 'Clamps not homed.\nPlease home clamps before closing the GUI.')
            event.ignore()
            return
        if self.have_gamepad():
            self.gamepad_thread.terminate()
        self.dnx.disable_torque(DXL1_ID)
        self.dnx.disable_torque(DXL2_ID)
        self.dnx.disable_torque(DXL3_ID)
        self.dnx.disable_torque(DXL4_ID)
        self.dnx.disable_torque(DXL5_ID)
        self.dnx.disable_torque(DXL6_ID)
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
