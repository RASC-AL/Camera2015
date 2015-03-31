import sys
import os
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from conf import COMM_FILE

class CamConfig(QDialog):
	config = ['Camera 0', 'Camera 1', 'Camera 2', 'Camera 3', '', 'Camera 0 & 1']

	def __init__(self, parent=None):
		super(CamConfig, self).__init__(parent)
		
		self.cam = 0

		self.configComboBox = QComboBox()
		self.configComboBox.addItems(self.config)
		self.sendButton = QPushButton("Send")

		topLayout = QHBoxLayout()
		topLayout.addWidget(self.configComboBox)
		topLayout.addWidget(self.sendButton)
		self.setLayout(topLayout)

		self.connect(self.sendButton, SIGNAL("clicked()"), 
				self.send)

		self.setWindowTitle("CamConfig")

	def send(self):
		self.cam = self.configComboBox.currentIndex()
		with open(COMM_FILE, 'w') as f:
			f.write(str(self.cam))
		print self.cam

if __name__ == '__main__':

	app = QApplication(sys.argv)
	form = CamConfig()
	form.show()
	app.exec_()
