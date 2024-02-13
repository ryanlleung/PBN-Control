import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QCheckBox

class SwitchButton(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Create a checkbox
        switch = QCheckBox('Switch')

        # Set checkbox style to resemble a switch
        switch.setCheckable(True)
        switch.setStyleSheet("""
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
        """)

        # Add the checkbox to the layout
        layout.addWidget(switch)

        self.setLayout(layout)
        self.setWindowTitle('Switch Button')

def main():
    app = QApplication(sys.argv)
    window = SwitchButton()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
