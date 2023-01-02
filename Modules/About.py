# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QWidget, QDesktopWidget, QLabel)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont, QPixmap

class About(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()  # Initialize the user interface elements
        
    def init_ui(self):
        self.setFixedSize(420, 350)  # Window size
        self.setWindowIcon(QIcon('Resources/icon.png'))
        self.setWindowTitle('About')  # Window title
        # Remove maximize and minimize buttons
        self.setWindowFlags(self.windowFlags() & Qt.CustomizeWindowHint)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMinMaxButtonsHint)  
        self.center_window() #  Center the window on desktop      
        self.generate_about()
        self.show()
        
    def center_window(self):
        """Method for center the main window on the desktop"""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
    def generate_about(self):
        self.vLine = QLabel(self) # Vertical orange line
        self.vLine.setGeometry(40, 30, 5, 285)
        self.vLine.setStyleSheet("QLabel { background-color : #fb5103;}")

        self.lbl_1 = QLabel('Particle systems generator', self)
        self.lbl_1.setGeometry(60, 30, 300, 25)
        self.lbl_1.setFont(QFont('Arial', 16))
        
        self.lbl_2 = QLabel('Version: beta-1.0', self)
        self.lbl_2.setGeometry(60, 60, 230, 20)
        self.lbl_2.setFont(QFont('Arial', 12))
        
        self.lbl_3 = QLabel('Lappeenranta-Lahti University of Technology', self)
        self.lbl_3.setGeometry(60, 90, 350, 20)
        self.lbl_3.setFont(QFont('Arial', 12))
        
        self.lbl_4 = QLabel('Solid-Liquid Separation Research Group', self)
        self.lbl_4.setGeometry(60, 120, 300, 20)
        self.lbl_4.setFont(QFont('Arial', 12))
       
        self.lutlogo = QLabel(self)
        self.lutlogo.setGeometry(50, 150, 100, 100)
        self.lutlogo.setPixmap(QPixmap('Resources/lut_logo.png'))
        
        self.lbl_5 = QLabel('Author: Dmitry Safonov', self)
        self.lbl_5.setGeometry(60, 260, 250, 20)
        self.lbl_5.setFont(QFont('Arial', 12))
        
        self.lbl_6 = QLabel('', self)
        self.lbl_6.setText('''E-mail: <a href='mailto:dmitry.safonov@lut.fi'>Dmitry.Safonov@lut.fi</a>''')
        self.lbl_6.setOpenExternalLinks(True)
        self.lbl_6.setGeometry(60, 290, 250, 20)
        self.lbl_6.setFont(QFont('Arial', 12))
    
    
