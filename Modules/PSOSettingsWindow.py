# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (QMainWindow, QDesktopWidget, QLabel, QLineEdit,
                             QPushButton, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import (QIcon, QFont, QPixmap)

from functools import partial
from .AdvancedQSpinBox import AdvancedQSpinBox

class PSOSettingsWindow(QMainWindow):
    """Class for creating a new settings window for the Ptester tool""" 
    def __init__(self, parentTool):
        super().__init__()
        self.parentTool = parentTool  # Link to particleFinder
        # Current settings of the PSO algorithm
        self.PSO_nPop = self.parentTool.PSO_nPop
        self.PSO_w = self.parentTool.PSO_w
        self.PSO_wDamp = self.parentTool.PSO_wDamp
        self.PSO_c1 = self.parentTool.PSO_c1
        self.PSO_c2 = self.parentTool.PSO_c2
        self.PSO_a = self.parentTool.PSO_a
        self.PSO_b = self.parentTool.PSO_b
        self.iterLimit = self.parentTool.iterLimit
        
        self.init_ui()  # Initialize the user interface elements

    def init_ui(self):
        """Method for the initialization of the UI"""
        self.setFixedSize(302, 218)  # Window size
        self.center_window() #  Center the window on desktop
        self.setWindowIcon(QIcon('Resources/icon.png'))
        self.setWindowTitle('PSO algorithm settings')  # Window title
        self.center_window() #  Center the window on desktop

        dct = {'PSO_nPop' : 'Population size:',
               'PSO_w'    : 'Inertia coefficient:',
               'PSO_wDamp': 'Damping ratio:',
               'PSO_c1'   : 'Personal acceleration:',
               'PSO_c2'   : 'Social acceleration:',
               'PSO_a'    : 'Particle randomization:',
               'PSO_b'    : 'Swarm randomization:'}
        
        self.paramsLabels = {} # Dictionary with parameters labels
        self.paramsEdits = {}  # Dictionary with parameters edits
        self.paramResetBtn = {} # Dictionary with defaults buttons
        
        y = 10
        for item in dct:
            # Labels:
            self.paramsLabels[item] = QLabel(dct[item], self)
            self.paramsLabels[item].setAlignment(Qt.AlignLeft)
            self.paramsLabels[item].setGeometry(10, y, 150, 21)
            self.paramsLabels[item].setFont(QFont('Arial', 11))
            
            # Edits and spin boxes
            if item == 'PSO_nPop':  # Population size is a integer spin box
                self.paramsEdits[item] = AdvancedQSpinBox(self)
                self.paramsEdits[item].setAlignment(Qt.AlignRight)
                self.paramsEdits[item].setGeometry(167, y, 90, 21)
                self.paramsEdits[item].setFont(QFont('Arial', 11))
                self.paramsEdits[item].setRange(1, 500)
                self.paramsEdits[item].valueChanged.connect(self.val_changed_spb_nPop)
            elif item == 'PSO_a':  # Particle randomization is a spin box
                self.paramsEdits[item] = AdvancedQSpinBox(self)
                self.paramsEdits[item].setAlignment(Qt.AlignRight)
                self.paramsEdits[item].setGeometry(167, y, 90, 21)
                self.paramsEdits[item].setFont(QFont('Arial', 11))
                self.paramsEdits[item].setRange(1, self.PSO_nPop)
                self.paramsEdits[item].valueChanged.connect(self.val_changed_spb_a)
            elif item == 'PSO_b':  # Swarm randomization is a spin box
                self.paramsEdits[item] = AdvancedQSpinBox(self)
                self.paramsEdits[item].setAlignment(Qt.AlignRight)
                self.paramsEdits[item].setGeometry(167, y, 90, 21)
                self.paramsEdits[item].setFont(QFont('Arial', 11))
                self.paramsEdits[item].setRange(1, self.iterLimit)
                self.paramsEdits[item].valueChanged.connect(self.val_changed_spb_b)                                
            else:
                self.paramsEdits[item] = QLineEdit(self)
                self.paramsEdits[item].setAlignment(Qt.AlignRight)
                self.paramsEdits[item].setGeometry(167, y, 90, 21)
                self.paramsEdits[item].setFont(QFont('Arial', 11))
                self.paramsEdits[item].editingFinished.connect(partial(self.update_parameter_value, item))
            
            # Buttons
            self.paramResetBtn[item] = QPushButton(self)
            self.paramResetBtn[item].setGeometry(270, y, 21, 21)
            self.paramResetBtn[item].setIcon(QIcon(QPixmap('./Resources/arrow.png')))
            self.paramResetBtn[item].clicked.connect(partial(self.reset_parameter, item)) 
            y+=23
        
        # Buttons
        y += 10
        self.btn_OK = QPushButton('OK', self)
        self.btn_OK.setGeometry(141, y, 70, 27)
        self.btn_OK.clicked.connect(self.set_settings)
        
        self.btn_cancel = QPushButton('Cancel', self)
        self.btn_cancel.setGeometry(221, y, 70, 27)
        self.btn_cancel.clicked.connect(self.cancel_settings)   
        
        # Set current values of the parameters
        self.set_current_params()
        self.show()

    def set_current_params(self):
        """Method for settings current values of the algorithm parameters"""
        # set current algorithm parameters
        self.paramsEdits['PSO_nPop'].setValue(self.PSO_nPop)
        self.paramsEdits['PSO_w'].setText('{0:.2f}'.format(self.PSO_w))
        self.paramsEdits['PSO_wDamp'].setText('{0:.2f}'.format(self.PSO_wDamp))
        self.paramsEdits['PSO_c1'].setText('{0:.2f}'.format(self.PSO_c1))
        self.paramsEdits['PSO_c2'].setText('{0:.2f}'.format(self.PSO_c2))
        self.paramsEdits['PSO_a'].setValue(self.PSO_a)
        self.paramsEdits['PSO_b'].setValue(self.PSO_b)
        
    def val_changed_spb_nPop(self):
        """Method for updating the nPop value after changind the spin box"""
        value = self.paramsEdits['PSO_nPop'].value()
        self.PSO_nPop = value
        self.paramsEdits['PSO_a'].setRange(1, value)
    
    def val_changed_spb_a(self):
        value = self.paramsEdits['PSO_a'].value()
        self.PSO_a = value
    
    def val_changed_spb_b(self):
        value = self.paramsEdits['PSO_b'].value()
        self.PSO_b = value   
        
    def update_parameter_value(self, item):
        """Method for updating the parameter value after finish editing in edit box"""   
        # Save old value
        if item == 'PSO_w':
            oldValue = self.PSO_w
            message = 'Inertia coefficient'
        elif item == 'PSO_wDamp':
            oldValue = self.PSO_wDamp
            message = 'Damping ratio'
        elif item == 'PSO_c1':
            oldValue = self.PSO_c1
            message = 'Personal acceleration'
        elif item == 'PSO_c2':
            oldValue = self.PSO_c2
            message = 'Social acceleration'      
        
        # Treat the new value
        newValueStr = self.paramsEdits[item].text()  # Get the raw string
        newValueStr = newValueStr.replace(',','.')  # Symbol ',' is also available
        error = False
        try:
            newValue = float(newValueStr)
        except:
            error = True   
        
        self.paramsEdits[item].setText('{0:.2f}'.format(oldValue))
        
        # Treat the possible error
        if error:
            text = '{0} should be a number!'.format(message)
            self.show_error_window(text)
        else:
            self.paramsEdits[item].setText('{0:.2f}'.format(newValue))
            # Update the new value
            if item == 'PSO_w': self.PSO_w = newValue
            if item == 'PSO_wDamp': self.PSO_wDamp = newValue
            if item == 'PSO_c1': self.PSO_c1 = newValue
            if item == 'PSO_c2': self.PSO_c2 = newValue
      
    def show_error_window(self, text):
        """Method to show the window with error message"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(text)
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_() 
        
    def center_window(self):
        """Method for center the main window on the desktop"""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())  
    
    def reset_parameter(self, item):
        """Method to return the parameters to their default values"""
        if item == 'PSO_nPop':
            self.paramsEdits['PSO_nPop'].setValue(50)
        elif item == 'PSO_w':
            self.paramsEdits['PSO_w'].setText('1.00')
        elif item == 'PSO_wDamp':
            self.paramsEdits['PSO_wDamp'].setText('0.99')
        elif item == 'PSO_c1':
            self.paramsEdits['PSO_c1'].setText('2.00')
        elif item == 'PSO_c2':
            self.paramsEdits['PSO_c2'].setText('2.00')
        elif item == 'PSO_a':
            self.paramsEdits['PSO_a'].setValue(5)
        elif item == 'PSO_b':
            self.paramsEdits['PSO_b'].setValue(200)
    
    def set_settings(self):
        """Method for save the chosen PSO algorithm settings"""
        # Create the dictionary with the settings data 
        settingsData = {'PSO_nPop' : self.PSO_nPop,
                        'PSO_w'    : self.PSO_w,
                        'PSO_wDamp': self.PSO_wDamp,
                        'PSO_c1'   : self.PSO_c1,
                        'PSO_c2'   : self.PSO_c2,
                        'PSO_a'    : self.PSO_a,
                        'PSO_b'    : self.PSO_b}
        
        # Send settings data to ParticleTester
        self.parentTool.set_PSO_settings_data(settingsData)
        self.close()
        
    def cancel_settings(self):
        """Method for closing the current window without any changes"""
        self.close()