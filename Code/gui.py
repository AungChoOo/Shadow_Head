import sys
import time
import pyfirmata
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication,QWidget,QSlider,QLabel,QGridLayout

board = pyfirmata.Arduino('/dev/ttyACM0')
iter8 = pyfirmata.util.Iterator(board)
iter8.start()

pin9 = board.get_pin('d:9:s')
pin10 = board.get_pin('d:10:s')
pin11 = board.get_pin('d:11:s')

pin9.write(90)
pin10.write(90)
pin11.write(30)

class shadow_head(QWidget):
    def __init__(self):
        super(shadow_head,self).__init__()
        self.initUI()

    def initUI(self):
        self.widget = QWidget()
        self.widget.setWindowTitle("Shadow Head")

        self.label1 = QLabel('X : ')
        self.label2 = QLabel('Y : ')
        self.label3 = QLabel('Z : ')

        self.x = QSlider(Qt.Horizontal)
        self.x.setMinimum(-90)
        self.x.setMaximum(90)
        self.x.setValue(0)
        self.x.setTickPosition(QSlider.TicksBelow)
        self.x.setTickInterval(5)
        self.x.valueChanged.connect(self.move_servo)

        self.y = QSlider(Qt.Horizontal)
        self.y.setMinimum(-90)
        self.y.setMaximum(90)
        self.y.setValue(0)
        self.y.setTickPosition(QSlider.TicksBelow)
        self.y.setTickInterval(5)
        self.y.valueChanged.connect(self.move_servo)

        self.z = QSlider(Qt.Horizontal)
        self.z.setMinimum(0)
        self.z.setMaximum(150)
        self.z.setValue(30)
        self.z.setTickPosition(QSlider.TicksBelow)
        self.z.setTickInterval(5)
        self.z.valueChanged.connect(self.move_servo)

        layout = QGridLayout()
        layout.addWidget(self.x,0,0)
        layout.addWidget(self.y,1,0)
        layout.addWidget(self.z,2,0)
        layout.addWidget(self.label1,0,1)
        layout.addWidget(self.label2,1,1)
        layout.addWidget(self.label3,2,1)
        self.widget.setLayout(layout)
        self.widget.show()

    def move_servo(self):
        analogdata1 = int(self.x.value())
        analogdata2 = int(self.y.value())
        analogdata3 = int(self.z.value())
        self.label1.setText('X : '+str(analogdata1))
        self.label2.setText('Y : '+str(analogdata2))
        self.label3.setText('Z : '+str(analogdata3))
        servo1 = analogdata1-analogdata2+90
        servo2 = analogdata1+analogdata2+90

        servo1 = max(min(170, servo1), 0)
        servo2 = max(min(170, servo2), 0)

        pin9.write(servo1)
        pin10.write(servo2)
        pin11.write(analogdata3)

def main():
	app = QApplication(sys.argv)
	sh = shadow_head()
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()