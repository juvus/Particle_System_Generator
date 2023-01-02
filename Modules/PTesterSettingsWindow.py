# -*- coding: utf-8 -*-

import sys
import os
from PyQt5.QtWidgets import (QMainWindow, QApplication, QDesktopWidget, QLabel,
                             QAction, QGraphicsView, QColorDialog, QLineEdit,
                             QPushButton, QGroupBox, QSpinBox, QCheckBox, QWidget)
from PyQt5.QtCore import Qt, QPoint, QCoreApplication, QObject, pyqtSignal
from PyQt5.QtGui import (QIcon, QFont, QPixmap, QPainter, QColor, QPen, QBrush, 
                         QPolygon, QCursor)

class AdvancedLabel(QLabel):
    """Custom class to override some methods of QLabel class"""
    clicked = pyqtSignal()  # Click sygnal definition
    
    def __init__(self, parent=None):
        super(AdvancedLabel, self).__init__(parent=parent)    
        
    def enterEvent(self, event):
        """Method for handle the event of mouse in to the widget"""
        self.setCursor(QCursor(Qt.PointingHandCursor))
        
    def leaveEvent(self, event):
        """Method for handle the event of mouse out of the widget"""
        self.setCursor(QCursor(Qt.ArrowCursor))
        
    def mousePressEvent(self, event):
        """Method for handle the mouse press event on a label"""
        self.clicked.emit()  
    

class PTesterSettingsWindow(QMainWindow):
    """Class for creating a new settings window for the Ptester tool""" 
    def __init__(self, particleTester):
        super().__init__()
        self.particleTester = particleTester  # Link to particleTester
        # Initial information about single particle picture
        self.picWidthHeight = self.particleTester.picWidthHeight
        self.picParticleColor = self.particleTester.picParticleColor
        self.picBkgColor = self.particleTester.picBkgColor
        self.picShowScale = self.particleTester.picShowScale
        self.prtColPixmap = None  # Pixmap of particle color current picker
        self.bkgColPixmap = None  # Pixmap of background 
        self.prtThumbPixmap = None  # Large particle thumbnail
        self.init_ui()  # Initialize the user interface elements

    def init_ui(self):
        """Method for the initialization of the UI"""
        self.setFixedSize(375, 200)  # Window size
        self.center_window() #  Center the window on desktop
        self.setWindowIcon(QIcon('Resources/icon.png'))
        self.setWindowTitle('Settings')  # Window title
        self.center_window() #  Center the window on desktop
        
        # Group boxes
        self.gb_particleImage = QGroupBox('Particle picture', self)
        self.gb_particleImage.setGeometry(10, 10, 355, 125)

        # Particle image settings elements:
        self.lbl_picSize = QLabel('Width and height:', self.gb_particleImage)
        self.lbl_picSize.setAlignment(Qt.AlignLeft)
        self.lbl_picSize.setGeometry(10, 23, 121, 21)
        self.lbl_picSize.setFont(QFont('Arial', 11))    
        
        self.spb_picSize = QSpinBox(self.gb_particleImage)
        self.spb_picSize.setAlignment(Qt.AlignRight)
        self.spb_picSize.setGeometry(140, 23, 60, 21)
        self.spb_picSize.setFont(QFont('Arial', 11))
        self.spb_picSize.setRange(1, 3000)
        self.spb_picSize.setValue(self.picWidthHeight)
        self.spb_picSize.valueChanged.connect(self.val_changed_spb_picSize)

        self.lbl_picSizeUnit = QLabel('[px]', self.gb_particleImage)
        self.lbl_picSizeUnit.setAlignment(Qt.AlignLeft)
        self.lbl_picSizeUnit.setGeometry(215, 23, 31, 21)
        self.lbl_picSizeUnit.setFont(QFont('Arial', 11))
        
        # Particle color
        self.lbl_particleColor = QLabel('Particle color:', self.gb_particleImage)
        self.lbl_particleColor.setAlignment(Qt.AlignLeft)
        self.lbl_particleColor.setGeometry(10, 46, 121, 21)
        self.lbl_particleColor.setFont(QFont('Arial', 11))
        
        self.partColorPicker = AdvancedLabel(self.gb_particleImage)
        self.partColorPicker.setGeometry(140, 47, 20, 20)
        self.partColorPicker.clicked.connect(self.pick_particle_color)
        
        # Background color
        self.lbl_backgroundColor = QLabel('Background color:', self.gb_particleImage)
        self.lbl_backgroundColor.setAlignment(Qt.AlignLeft)
        self.lbl_backgroundColor.setGeometry(10, 69, 121, 21)
        self.lbl_backgroundColor.setFont(QFont('Arial', 11))
        
        self.bkgColorPicker = AdvancedLabel(self.gb_particleImage)
        self.bkgColorPicker.setGeometry(140, 70, 20, 20)
        self.bkgColorPicker.clicked.connect(self.pick_background_color)
        
        # Show scale
        self.lbl_showScale = QLabel('Show scale:', self.gb_particleImage)
        self.lbl_showScale.setAlignment(Qt.AlignLeft)
        self.lbl_showScale.setGeometry(10, 92, 121, 21)
        self.lbl_showScale.setFont(QFont('Arial', 11))
        
        self.chb_showScale = QCheckBox(self.gb_particleImage)
        self.chb_showScale.setGeometry(140, 92, 21, 21)
        self.chb_showScale.setFont(QFont('Arial', 11))
        self.chb_showScale.stateChanged.connect(self.change_show_scale)
        if self.picShowScale:
            self.chb_showScale.setChecked(True)
        
        # Particle large thumbnail
        self.partThumbnail = QLabel('', self.gb_particleImage)
        self.partThumbnail.setGeometry(253, 23, 87, 87) 
        
        # Buttons
        self.btn_OK = QPushButton('OK', self)
        self.btn_OK.setGeometry(215, 165, 70, 27)
        self.btn_OK.clicked.connect(self.set_settings)
        
        self.btn_cancel = QPushButton('Cancel', self)
        self.btn_cancel.setGeometry(295, 165, 70, 27)
        self.btn_cancel.clicked.connect(self.cancel_settings)   
        
        self.show()
    
    def center_window(self):
        """Method for center the main window on the desktop"""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())  
    
    def val_changed_spb_picSize(self):
        """Method for handle the value change of the picSize spin box"""
        value = self.spb_picSize.value()
        self.picWidthHeight = value
    
    def paintEvent(self, event):
        """Method for render the window"""
        # Create thumbnail image of particle color picker
        r = self.picParticleColor[0]
        g = self.picParticleColor[1]
        b = self.picParticleColor[2]        
        self.prtColPixmap = QPixmap(21, 21)
        qp = QPainter(self.prtColPixmap)
        qp.setRenderHint(QPainter.Antialiasing, True)  # Smooth lines
        qp.setPen(QPen(QColor(0, 0, 0), 2, Qt.SolidLine))  # Outline
        qp.setBrush(QBrush(QColor(255, 255, 255), Qt.SolidPattern))  # Fill
        qp.drawRect(0, 0, 20, 20)
        qp.setPen(QPen(QColor(r, g, b), 2, Qt.SolidLine))  # Outline
        qp.setBrush(QBrush(QColor(r, g, b), Qt.SolidPattern))  # Fill
        qp.drawRect(3, 3, 14, 14)      
        self.partColorPicker.setPixmap(self.prtColPixmap)
        
        # Create thumbnail image of background color picler
        r = self.picBkgColor[0]
        g = self.picBkgColor[1]
        b = self.picBkgColor[2]
        self.bkgColPixmap = QPixmap(21, 21)
        qp = QPainter(self.bkgColPixmap)
        qp.setRenderHint(QPainter.Antialiasing, True)  # Smooth lines
        qp.setPen(QPen(QColor(0, 0, 0), 2, Qt.SolidLine))  # Outline
        qp.setBrush(QBrush(QColor(255, 255, 255), Qt.SolidPattern))  # Fill
        qp.drawRect(0, 0, 20, 20)
        qp.setPen(QPen(QColor(r, g, b), 2, Qt.SolidLine))  # Outline
        qp.setBrush(QBrush(QColor(r, g, b), Qt.SolidPattern))  # Fill
        qp.drawRect(3, 3, 14, 14)      
        self.bkgColorPicker.setPixmap(self.bkgColPixmap)
        
        # Create large particle thumbnail
        # 1. Particle and background
        self.prtThumbPixmap = QPixmap(87, 87)
        qp = QPainter(self.prtThumbPixmap)
        qp.setRenderHint(QPainter.Antialiasing, True)  # Smooth lines
        r = self.picBkgColor[0]
        g = self.picBkgColor[1]
        b = self.picBkgColor[2]  
        qp.setPen(QPen(QColor(r, g, b), 2, Qt.SolidLine))  # Outline
        qp.setBrush(QBrush(QColor(r, g, b), Qt.SolidPattern))  # Fill
        qp.drawRect(0, 0, 87, 87)
        r = self.picParticleColor[0]
        g = self.picParticleColor[1]
        b = self.picParticleColor[2] 
        qp.setPen(QPen(QColor(r, g, b), 2, Qt.SolidLine))  # Outline
        qp.setBrush(QBrush(QColor(r, g, b), Qt.SolidPattern))  # Fill
        qp.drawEllipse(QPoint(44, 44), 25, 25)
        # 2. Scale
        if self.picShowScale:
            qp.setRenderHint(QPainter.Antialiasing, False)
            qp.setPen(QPen(QColor(0, 0, 0), 1, Qt.SolidLine))  # Outline
            qp.setBrush(QBrush(QColor(255, 255, 255), Qt.SolidPattern))  # Fill
            qp.drawRect(19, 75, 10, 3)
            qp.drawRect(39, 75, 10, 3)
            qp.drawRect(59, 75, 10, 3)
            qp.setBrush(QBrush(QColor(0, 0, 0), Qt.SolidPattern))  # Fill
            qp.drawRect(29, 75, 10, 3)
            qp.drawRect(49, 75, 10, 3)      
        
        self.partThumbnail.setPixmap(self.prtThumbPixmap)
    
    def pick_particle_color(self):
        # Open the color picker dialog with the initial color
        r = self.picParticleColor[0]
        g = self.picParticleColor[1]
        b = self.picParticleColor[2]
        color = QColorDialog.getColor(QColor(r, g, b))
        
        if color.isValid():
            self.picParticleColor[0] = color.red()
            self.picParticleColor[1] = color.green()
            self.picParticleColor[2] = color.blue()
        
    def pick_background_color(self):
        # Open the color picker dialog with the initial color
        r = self.picBkgColor[0]
        g = self.picBkgColor[1]
        b = self.picBkgColor[2]
        color = QColorDialog.getColor(QColor(r, g, b))
        
        if color.isValid():
            self.picBkgColor[0] = color.red()
            self.picBkgColor[1] = color.green()
            self.picBkgColor[2] = color.blue()
    
    def change_show_scale(self):
        if self.chb_showScale.isChecked():
            self.picShowScale = True
        else:
            self.picShowScale = False    
    
    def set_settings(self):
        """Method for save the chosen picture settings"""
        # Create the dictionary with the settings data 
        settingsData = {'picWidthHeight': self.picWidthHeight,
                        'picParticleColor': self.picParticleColor,
                        'picBkgColor': self.picBkgColor,
                        'picShowScale': self.picShowScale}
        
        # Send settings data to ParticleTester
        self.particleTester.set_settings_data(settingsData)
        self.close()
        
    def cancel_settings(self):
        """Method for closing the current window without any changes"""
        self.close()