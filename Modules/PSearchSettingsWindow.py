# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QMainWindow, QDesktopWidget, QLabel, QPushButton)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import (QIcon, QFont, QPixmap)

from .AdvancedQSpinBox import AdvancedQSpinBox

class PSearchSettingsWindow(QMainWindow):
    """Class for creating a settings window for parallel search""" 
    def __init__(self, parentTool):
        super().__init__()
        self.parentTool = parentTool  # Link to parent class    
        # Current settings of the parallel search
        self.numThreads = self.parentTool.numThreads  
        self.init_ui()  # Initialize the user interface elements

    def init_ui(self):
        """Method for the initialization of the UI"""
        self.setFixedSize(302, 80)  # Window size
        self.center_window() #  Center the window on desktop
        self.setWindowIcon(QIcon('Resources/icon.png'))
        self.setWindowTitle('Parallel search settings')  # Window title
        self.center_window() #  Center the window on desktop
        
        # Section with number of threads setting
        self.lbl_numThreads = QLabel('Number of threads:', self)
        self.lbl_numThreads.setAlignment(Qt.AlignLeft)
        self.lbl_numThreads.setGeometry(10, 10, 150, 21)
        self.lbl_numThreads.setFont(QFont('Arial', 11))
        
        self.spb_numThreads = AdvancedQSpinBox(self)
        self.spb_numThreads.setAlignment(Qt.AlignRight)
        self.spb_numThreads.setGeometry(167, 10, 90, 21)
        self.spb_numThreads.setFont(QFont('Arial', 11))
        self.spb_numThreads.setRange(1, 20)
        self.spb_numThreads.valueChanged.connect(self.val_changed_spb_numThreads)
        
        self.btn_resetNumThreads = QPushButton(self)
        self.btn_resetNumThreads.setGeometry(270, 10, 21, 21)
        self.btn_resetNumThreads.setIcon(QIcon(QPixmap('./Resources/arrow.png')))
        self.btn_resetNumThreads.clicked.connect(self.reset_numThreads)
            
        # Buttons
        self.btn_OK = QPushButton('OK', self)
        self.btn_OK.setGeometry(141, 43, 70, 27)
        self.btn_OK.clicked.connect(self.set_settings)
        
        self.btn_cancel = QPushButton('Cancel', self)
        self.btn_cancel.setGeometry(221, 43, 70, 27)
        self.btn_cancel.clicked.connect(self.cancel_settings)   
        
        # Set current values of the parameters
        self.set_current_params()
        self.show()

    def set_current_params(self):
        """Method for settings current values of the parallel search"""
        self.spb_numThreads.setValue(self.numThreads)
        
    def val_changed_spb_numThreads(self):
        """Method for updating the numThreads value after changind the spin box"""
        value = self.spb_numThreads.value()
        self.numThreads = value
                
    def center_window(self):
        """Method for center the main window on the desktop"""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())  
    
    def reset_numThreads(self, item):
        """Method to return the numThreads to it's default values"""
        self.spb_numThreads.setValue(10)
    
    def set_settings(self):
        """Method for save the chosen parallel search settings"""
        # Create the dictionary with the settings data 
        settingsData = {'numThreads' : self.numThreads}
        
        # Send settings data to ParticleTester
        self.parentTool.set_PSearch_settings_data(settingsData)
        self.close()
        
    def cancel_settings(self):
        """Method for closing the current window without any changes"""
        self.close()