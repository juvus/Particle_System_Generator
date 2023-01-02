# -*- coding: utf-8 -*-

import sys
import os
from PyQt5.QtWidgets import (QMainWindow, QApplication, QDesktopWidget, QLabel,
                             QAction, QMenu, QGraphicsView, QFileDialog, QLineEdit,
                             QPushButton, QMessageBox)
from PyQt5.QtCore import Qt, QPoint, QCoreApplication
from PyQt5.QtGui import (QIcon, QFont, QPixmap, QPainter, QColor, QPen, QBrush, 
                         QPolygon, QCursor)
import math as m
import time

# Program modules:
from .About import About
from .RoundSlider import RoundSlider
from .RealImage import RealImage
from .ImageLabel import ImageLabel
from .AdvancedQSpinBox import AdvancedQSpinBox
from .Slider import Slider

class RealImageLoader(QMainWindow):
    """Class for creating a new helper window, load and manipulate 
       the image of the real particle and then send it to the main program window 
    """
    def __init__(self, particleTester):
        super().__init__()
        self.particleTester = particleTester  # Link to particleTester
        self.N = 12  # Number of particle dimensions
        self.fieldX = 30  # x of top left corner of the field
        self.fieldY = 70  # y of top left corner of the field
        self.fieldWidth = 360  # Width=Height of the field (px)
        self.xC = self.fieldX + 180  #  X coordinate of the center of the field
        self.yC = self.fieldY + 180  #  Y coordinate of the center of the field
        self.r = 180  # big radius of the field
        self.roundSlider = RoundSlider(x0 = self.fieldX + self.fieldWidth/2,
                                       y0 = self.fieldY + self.fieldWidth/2,
                                       r = 190, 
                                       value = 0.0) 
        self.image = RealImage(self.N)  # Create an instance of the real image
        
        self.curX = 0  # Current X coord of cursor when left mouse button clicked 
        self.curY = 0  # Current Y coord of cursor when left mouse button clicked 
        self.offsetX = 0  # Offcet along the X axis
        self.offsetY = 0  # Offcet along the Y axis 
        self.flagCursor = ''  # Flag showing whether cursor have been set or not
        self.flagShift = False  # Flag showing whether we should move the image or not
        self.path = ''  # Path to the last opened image in editor
        self.origScale = 1.0  # Orignal scale of the image (um/pix)
        self.curScale = 1.0  # Curent scale of the image (um/pix)
        
        self.init_ui()  # Initialize the user interface elements
        
    def init_ui(self):
        """Method for the initialization of the UI"""
        self.setFixedSize(855, 460)  # Window size
        self.center_window() #  Center the window on desktop
        self.setWindowIcon(QIcon('Resources/icon.png'))
        self.setWindowTitle('Real particle image loader')  # Window title
        self.center_window() #  Center the window on desktop
        
        # Menu and submenu creation 
        mainMenu = self.menuBar() 
        imageMenu = mainMenu.addMenu('Image')
        infoMenu = mainMenu.addMenu('Info')
        # Menu action - Image -> Open...
        openAct = QAction(QIcon('Resources/load.png'), 'Open...', self)
        openAct.setShortcut('Ctrl+O')
        openAct.setFont(QFont('Arial', 11))
        openAct.triggered.connect(self.open_image)
        # Menu action - Image -> Save...
        saveAct = QAction(QIcon('Resources/save.png'), 'Save...', self)
        saveAct.setShortcut('Ctrl+S')
        saveAct.setFont(QFont('Arial', 11))
        saveAct.triggered.connect(self.save_image)
        # Menu action - Image -> Reset
        resetAct = QAction(QIcon('Resources/reset.png'), 'Reset all', self)
        resetAct.setShortcut('Ctrl+R')
        resetAct.setFont(QFont('Arial', 11))
        resetAct.triggered.connect(self.reset_image)
        # Menu action - Image -> Clear
        clearAct = QAction(QIcon('Resources/clear.png'), 'Clear', self)
        clearAct.setShortcut('Ctrl+C')
        clearAct.setFont(QFont('Arial', 11))
        clearAct.triggered.connect(self.clear_image)
        # Menu action: Info -> Help 
        helpAct = QAction(QIcon('Resources/help.png'), 'Help', self)
        helpAct.setFont(QFont('Arial', 11))
        helpAct.setShortcut('Ctrl+H')
        helpAct.triggered.connect(self.show_help)
        # Menu action Info -> About
        aboutAct = QAction(QIcon('Resources/about.png'), 'About', self)
        aboutAct.setFont(QFont('Arial', 11))
        aboutAct.setShortcut('Ctrl+A')
        aboutAct.triggered.connect(self.show_about)
        
         # Add actions to menu particleMenu
        imageMenu.addAction(openAct)
        imageMenu.addAction(saveAct)
        imageMenu.addAction(resetAct)
        imageMenu.addAction(clearAct)
        # Add actions to menu infoMenu
        infoMenu.addAction(helpAct)
        infoMenu.addAction(aboutAct)
        
        # Labels
        self.lbl_title = QLabel('Real particle image:', self)
        self.lbl_title.setAlignment(Qt.AlignCenter)
        self.lbl_title.setGeometry(30, 30, 360, 21)
        self.lbl_title.setFont(QFont('Arial', 11, weight=QFont.Bold))
        
        self.lbl_adj_prop = QLabel('Image adjustment and properties:', self)
        self.lbl_adj_prop.setAlignment(Qt.AlignCenter)
        self.lbl_adj_prop.setGeometry(430, 30, 404, 21)
        self.lbl_adj_prop.setFont(QFont('Arial', 11, weight=QFont.Bold))
        
        # Create the control labels, sliders and units:
        self.lbl_offsetX = QLabel('Offset X:', self)
        self.lbl_offsetX.setAlignment(Qt.AlignLeft)
        self.lbl_offsetX.setGeometry(430, 60, 80, 21)
        self.lbl_offsetX.setFont(QFont('Arial', 11)) 
        
        self.lbl_offsetY = QLabel('Offset Y:', self)
        self.lbl_offsetY.setAlignment(Qt.AlignLeft)
        self.lbl_offsetY.setGeometry(430, 83, 80, 21)
        self.lbl_offsetY.setFont(QFont('Arial', 11)) 
        
        self.lbl_rotation = QLabel('Rotation:', self)
        self.lbl_rotation.setAlignment(Qt.AlignLeft)
        self.lbl_rotation.setGeometry(430, 106, 80, 21)
        self.lbl_rotation.setFont(QFont('Arial', 11))
        
        self.lbl_scale = QLabel('Scale:', self)
        self.lbl_scale.setAlignment(Qt.AlignLeft)
        self.lbl_scale.setGeometry(430, 129, 80, 21)
        self.lbl_scale.setFont(QFont('Arial', 11)) 
        
        self.lbl_origScale = QLabel('Original scale:', self)
        self.lbl_origScale.setAlignment(Qt.AlignLeft)
        self.lbl_origScale.setGeometry(430, 152, 95, 21)
        self.lbl_origScale.setFont(QFont('Arial', 11)) 
        
        self.lbl_origScaleUnit = QLabel('[\u03BCm/pix]', self)
        self.lbl_origScaleUnit.setAlignment(Qt.AlignLeft)
        self.lbl_origScaleUnit.setGeometry(618, 152, 95, 21)
        self.lbl_origScaleUnit.setFont(QFont('Arial', 11))
        
        self.lbl_curScale = QLabel('Current scale:', self)
        self.lbl_curScale.setAlignment(Qt.AlignLeft)
        self.lbl_curScale.setGeometry(430, 175, 95, 21)
        self.lbl_curScale.setFont(QFont('Arial', 11)) 
        
        self.lbl_curScaleUnit = QLabel('[\u03BCm/pix]', self)
        self.lbl_curScaleUnit.setAlignment(Qt.AlignLeft)
        self.lbl_curScaleUnit.setGeometry(618, 175, 95, 21)
        self.lbl_curScaleUnit.setFont(QFont('Arial', 11))
        
        self.lbl_color = QLabel('Color:', self)
        self.lbl_color.setAlignment(Qt.AlignLeft)
        self.lbl_color.setGeometry(430, 198, 95, 21)
        self.lbl_color.setFont(QFont('Arial', 11)) 
        
        self.lbl_brightness = QLabel('Brightness:', self)
        self.lbl_brightness.setAlignment(Qt.AlignLeft)
        self.lbl_brightness.setGeometry(430, 221, 95, 21)
        self.lbl_brightness.setFont(QFont('Arial', 11))
        
        self.lbl_contrast = QLabel('Contrast:', self)
        self.lbl_contrast.setAlignment(Qt.AlignLeft)
        self.lbl_contrast.setGeometry(430, 244, 95, 21)
        self.lbl_contrast.setFont(QFont('Arial', 11))
        
        self.lbl_sharpness = QLabel('Sharpness:', self)
        self.lbl_sharpness.setAlignment(Qt.AlignLeft)
        self.lbl_sharpness.setGeometry(430, 267, 95, 21)
        self.lbl_sharpness.setFont(QFont('Arial', 11))

        self.lbl_transp = QLabel('Transparency:', self)
        self.lbl_transp.setAlignment(Qt.AlignLeft)
        self.lbl_transp.setGeometry(430, 290, 95, 21)
        self.lbl_transp.setFont(QFont('Arial', 11))

        self.lbl_axes_num = QLabel('Axes number:', self)
        self.lbl_axes_num.setAlignment(Qt.AlignLeft)
        self.lbl_axes_num.setGeometry(430, 336, 95, 21)
        self.lbl_axes_num.setFont(QFont('Arial', 11))

        # Create sliders
        self.sld_offsetX = Slider(535, 70, 735, 70, 0.5)
        self.sld_offsetY = Slider(535, 93, 735, 93, 0.5)
        self.sld_rotation = Slider(535, 116, 735, 116, 0.0)
        self.sld_scale = Slider(535, 139, 735, 139, 0.5)
        self.sld_color = Slider(535, 208, 735, 208, 1.0)
        self.sld_brightness = Slider(535, 231, 735, 231, 0.5)
        self.sld_contrast = Slider(535, 254, 735, 254, 0.5)
        self.sld_sharpness = Slider(535, 277, 735, 277, 0.5)
        self.sld_transp = Slider(535, 300, 735, 300, 1.0)
        
        # Create edits
        self.edt_origScale = QLineEdit('', self)
        self.edt_origScale.setAlignment(Qt.AlignRight)
        self.edt_origScale.setGeometry(535, 152, 70, 21)
        self.edt_origScale.setFont(QFont('Arial', 11))
        self.edt_origScale.setText('{0:.2f}'.format(self.origScale))
        self.edt_origScale.editingFinished.connect(self.update_curScale)
        
        self.edt_curScale = QLineEdit('', self)
        self.edt_curScale.setAlignment(Qt.AlignRight)
        self.edt_curScale.setGeometry(535, 175, 70, 21)
        self.edt_curScale.setFont(QFont('Arial', 11))
        self.edt_curScale.setText('{0:.2f}'.format(self.curScale))

        # Create spin boxes
        self.spb_offsetX = AdvancedQSpinBox(self)
        self.spb_offsetX.setAlignment(Qt.AlignRight)
        self.spb_offsetX.setGeometry(748, 60, 55, 21)
        self.spb_offsetX.setFont(QFont('Arial', 11))
        self.spb_offsetX.setRange(-100, 100)
        self.spb_offsetX.valueChanged.connect(self.val_changed_spb_offsetX)
        
        self.spb_offsetY = AdvancedQSpinBox(self)
        self.spb_offsetY.setAlignment(Qt.AlignRight)
        self.spb_offsetY.setGeometry(748, 83, 55, 21)
        self.spb_offsetY.setFont(QFont('Arial', 11))
        self.spb_offsetY.setRange(-100, 100)
        self.spb_offsetY.valueChanged.connect(self.val_changed_spb_offsetY)
        
        self.spb_rotation = AdvancedQSpinBox(self)
        self.spb_rotation.setAlignment(Qt.AlignRight)
        self.spb_rotation.setGeometry(748, 106, 55, 21)
        self.spb_rotation.setFont(QFont('Arial', 11))
        self.spb_rotation.setRange(0, 360)
        self.spb_rotation.valueChanged.connect(self.val_changed_spb_rotation)        
        
        self.spb_scale = AdvancedQSpinBox(self)
        self.spb_scale.setAlignment(Qt.AlignRight)
        self.spb_scale.setGeometry(748, 129, 55, 21)
        self.spb_scale.setFont(QFont('Arial', 11))
        self.spb_scale.setRange(-100, 100)
        self.spb_scale.valueChanged.connect(self.val_changed_spb_scale)
      
        self.spb_color = AdvancedQSpinBox(self)
        self.spb_color.setAlignment(Qt.AlignRight)
        self.spb_color.setGeometry(748, 198, 55, 21)
        self.spb_color.setFont(QFont('Arial', 11))
        self.spb_color.setRange(0, 100)
        self.spb_color.set_value(100)
        self.spb_color.valueChanged.connect(self.val_changed_spb_color)
        
        self.spb_brightness = AdvancedQSpinBox(self)
        self.spb_brightness.setAlignment(Qt.AlignRight)
        self.spb_brightness.setGeometry(748, 221, 55, 21)
        self.spb_brightness.setFont(QFont('Arial', 11))
        self.spb_brightness.setRange(-100, 100)
        self.spb_brightness.set_value(0)
        self.spb_brightness.valueChanged.connect(self.val_changed_spb_brightness)
        
        self.spb_contrast = AdvancedQSpinBox(self)
        self.spb_contrast.setAlignment(Qt.AlignRight)
        self.spb_contrast.setGeometry(748, 244, 55, 21)
        self.spb_contrast.setFont(QFont('Arial', 11))
        self.spb_contrast.setRange(-100, 100)
        self.spb_contrast.setValue(0)
        self.spb_contrast.valueChanged.connect(self.val_changed_spb_contrast)
        
        self.spb_sharpness = AdvancedQSpinBox(self)
        self.spb_sharpness.setAlignment(Qt.AlignRight)
        self.spb_sharpness.setGeometry(748, 267, 55, 21)
        self.spb_sharpness.setFont(QFont('Arial', 11))
        self.spb_sharpness.setRange(-100, 100)
        self.spb_sharpness.valueChanged.connect(self.val_changed_spb_sharpness)
        
        self.spb_transp = AdvancedQSpinBox(self)
        self.spb_transp.setAlignment(Qt.AlignRight)
        self.spb_transp.setGeometry(748, 290, 55, 21)
        self.spb_transp.setFont(QFont('Arial', 11))
        self.spb_transp.setRange(0, 100)
        self.spb_transp.set_value(100)
        self.spb_transp.valueChanged.connect(self.val_changed_spb_transp)    
        
        self.spb_axesNum = AdvancedQSpinBox(self)
        self.spb_axesNum.setAlignment(Qt.AlignRight)
        self.spb_axesNum.setGeometry(535, 336, 55, 21)
        self.spb_axesNum.setFont(QFont('Arial', 11))
        self.spb_axesNum.setRange(3, 32)
        self.spb_axesNum.set_value(self.N)
        self.spb_axesNum.valueChanged.connect(self.val_changed_spb_axesNum)       
        
        # Create reset to default buttons
        self.btn_resetOffsetX = QPushButton(self)
        self.btn_resetOffsetX.setGeometry(813, 60, 21, 21)
        self.btn_resetOffsetX.setIcon(QIcon(QPixmap('./Resources/arrow.png')))
        self.btn_resetOffsetX.clicked.connect(self.reset_offsetX)
        
        self.btn_resetOffsetY = QPushButton(self)
        self.btn_resetOffsetY.setGeometry(813, 83, 21, 21)
        self.btn_resetOffsetY.setIcon(QIcon(QPixmap('./Resources/arrow.png')))
        self.btn_resetOffsetY.clicked.connect(self.reset_offsetY)
        
        self.btn_resetRotation = QPushButton(self)
        self.btn_resetRotation.setGeometry(813, 106, 21, 21)
        self.btn_resetRotation.setIcon(QIcon(QPixmap('./Resources/arrow.png')))
        self.btn_resetRotation.clicked.connect(self.reset_rotation)     
        
        self.btn_resetScale = QPushButton(self)
        self.btn_resetScale.setGeometry(813, 129, 21, 21)
        self.btn_resetScale.setIcon(QIcon(QPixmap('./Resources/arrow.png')))
        self.btn_resetScale.clicked.connect(self.reset_scale)
        
        self.btn_resetColor = QPushButton(self)
        self.btn_resetColor.setGeometry(813, 198, 21, 21)
        self.btn_resetColor.setIcon(QIcon(QPixmap('./Resources/arrow.png')))
        self.btn_resetColor.clicked.connect(self.reset_color)
        
        self.btn_resetBrightness = QPushButton(self)
        self.btn_resetBrightness.setGeometry(813, 221, 21, 21)
        self.btn_resetBrightness.setIcon(QIcon(QPixmap('./Resources/arrow.png')))
        self.btn_resetBrightness.clicked.connect(self.reset_brightness)
        
        self.btn_resetContrast = QPushButton(self)
        self.btn_resetContrast.setGeometry(813, 244, 21, 21)
        self.btn_resetContrast.setIcon(QIcon(QPixmap('./Resources/arrow.png')))
        self.btn_resetContrast.clicked.connect(self.reset_contrast)
        
        self.btn_resetSharpness = QPushButton(self)
        self.btn_resetSharpness.setGeometry(813, 267, 21, 21)
        self.btn_resetSharpness.setIcon(QIcon(QPixmap('./Resources/arrow.png')))
        self.btn_resetSharpness.clicked.connect(self.reset_sharpness)

        self.btn_resetTransp = QPushButton(self)
        self.btn_resetTransp.setGeometry(813, 290, 21, 21)
        self.btn_resetTransp.setIcon(QIcon(QPixmap('./Resources/arrow.png')))
        self.btn_resetTransp.clicked.connect(self.reset_transp)
        
        self.btn_resetAxesNum = QPushButton(self)
        self.btn_resetAxesNum.setGeometry(600, 336, 21, 21)
        self.btn_resetAxesNum.setIcon(QIcon(QPixmap('./Resources/arrow.png')))
        self.btn_resetAxesNum.clicked.connect(self.reset_axesNum)
        
        # Create load and cancel buttons
        self.btn_load = QPushButton('Load', self)
        self.btn_load.setGeometry(685, 417, 70, 27)
        self.btn_load.clicked.connect(self.image_load)
        
        self.btn_cancel = QPushButton('Cancel', self)
        self.btn_cancel.setGeometry(765, 417, 70, 27)
        self.btn_cancel.clicked.connect(self.load_cancel)
        
        # Label with image
        self.lbl_image = ImageLabel(self, self.N, 5, False)
        self.lbl_image.setGeometry(self.fieldX, self.fieldY, self.fieldWidth, self.fieldWidth)
        self.image_update()
        
        self.setMouseTracking(True)  # to follow the mouse move without left button clicked
        self.show()           
    
    def test(self):
        print('test')
    
    def center_window(self):
        """Method for center the main window on the desktop"""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft()) 
    
    def open_image(self):
        """Method for open a new image for further processing"""
        self.path = ''
        self.path = QFileDialog.getOpenFileName(self, 'Open image', './Images/', 'Images (*.png *.jpg)')[0]
        if self.path != '':
            self.image.open_image(self.path)
            # Reset all image modifications
            self.reset_image()
    
    def save_image(self):
        """Method for save the processed image in (*.png)"""
        path = QFileDialog.getSaveFileName(self, 'Save picture', 'Images/untitled.png', 'Image files (*.png)')[0]
        if path != '':
            self.image.save_image(path)
    
    def reset_image(self):
        """Method for reset all settings of the opened image"""
        self.reset_offsetX()
        self.reset_offsetY()
        self.reset_rotation()
        self.reset_scale()
        self.reset_color()
        self.reset_brightness()
        self.reset_contrast()
        self.reset_sharpness()
        self.reset_transp()
        self.reset_axesNum()
        self.update_curScale()
        self.image_update()
    
    def clear_image(self):
        """Method for clear the image and reset all the settings"""
        self.image = RealImage(self.N)
        self.reset_image()
    
    def show_help(self):
        """Method for show help of Image Loader"""
        path = os.getcwd() + '\Resources\help.pdf'
        os.startfile(path)
        
    def show_about(self):
        """Method for show the window with info about the software"""
        self.about = About()
    
    def paintEvent(self, event):
        """Method for render the window"""    
        qp = QPainter(self) 
        qp.setRenderHint(QPainter.Antialiasing, True)  # Smooth lines
        
        # Draw the round slider
        self.roundSlider.render(qp)
        
        # Draw the endings of the sliders (small vertical lines)
        qp.setPen(QPen(QColor(0, 0, 0, 255), 1.2, Qt.SolidLine))
        y = 70
        for i in range(11):
            if (i!=4) and (i!=5):
                qp.drawLine(QPoint(535, y + 23 * i - 4), QPoint(535, y + 23 * i + 4))
                qp.drawLine(QPoint(735, y + 23 * i - 4), QPoint(735, y + 23 * i + 4))    
        
        # Draw the control sliders
        self.sld_offsetX.render(qp)  # Offset along X axis
        self.sld_offsetY.render(qp)  # Offset along Y axis
        self.sld_rotation.render(qp)  # Image rotation
        self.sld_scale.render(qp)  # Image scale
        self.sld_color.render(qp)  # Image color saturation
        self.sld_brightness.render(qp)  # Image brightness
        self.sld_contrast.render(qp)  # Image contrast
        self.sld_sharpness.render(qp)  # Image edges sharpness
        self.sld_transp.render(qp)  # Image transparency to white
        
    def enhance_image(self):
        """Method that combines all image enhances after some changes """
        # Allpy image enhace
        self.image.set_enhance(color=self.sld_color.value,
                               brightness=self.sld_brightness.value,
                               contrast=self.sld_contrast.value,
                               sharpness=self.sld_sharpness.value,
                               transp=self.sld_transp.value)
        # Make image transformation and updates
        self.image_update()

    def image_update(self):
        """Method for calculate the image transformation and update on the form"""
        self.image.transform(angle = self.roundSlider.value, offset = (self.offsetX, self.offsetY))
        self.lbl_image.setPixmap(self.image.convert_to_QPixmap())  # Draw the image
        self.update()  # Update the whole form
       
    def wheelEvent(self, event):
        """Method for handle the mouse wheel rotation"""
        delta = int(-event.angleDelta().y() / 120)
        self.image.ratio += delta * self.image.ratio * 0.1  # positive - scale up, negative - scale down
        # Restrictions to the ratio values
        if self.image.ratio < self.image.ratioMin:
            self.image.ratio = self.image.ratioMin
        if self.image.ratio > self.image.ratioMax:
            self.image.ratio = self.image.ratioMax
        
        # After new scaling we need to recalculate the limits
        self.image.calc_shift_limits()
        
        # Update the offset slider positions and spin boxes as well
        a = self.image.offsetLeftLimit
        b = self.image.offsetRightLimit
        c = self.image.offsetUpLimit
        d = self.image.offsetDownLimit
        self.sld_offsetX.set_position((self.offsetX - a)/(b - a))
        self.spb_offsetX.set_value(int(round(-100 + self.sld_offsetX.value * 200)))
        self.sld_offsetY.set_position((self.offsetY - c)/(d - c))
        self.spb_offsetY.set_value(int(round(-100 + self.sld_offsetY.value * 200)))
        
        # Update the scale slider and spin box as well
        ratioMin = self.image.ratioMin
        ratioMax = self.image.ratioMax
        self.sld_scale.set_position(1 - ((self.image.ratio - ratioMin)/(ratioMax - ratioMin)))
        self.spb_scale.set_value(int(round(-100 + self.sld_scale.value * 200)))
        self.update_curScale()
    
        # Make image transformation and updates
        self.image_update() 

    def mousePressEvent(self, event):
        """Method for handle the single left click of the mouse"""    
        x = event.x()
        y = event.y()  
        
        # Distance from the (x0, y0) point
        distance = m.sqrt(m.pow(x - self.xC, 2) + m.pow(y - self.yC, 2))
        self.flagShift = False
        if distance <= self.r:
            self.flagShift = True
        
        # Sliders move by single click
        self.roundSlider.ready_to_slide(x, y)
        if self.roundSlider.slideFlag:
            self.roundSlider.slide(x, y)
            # update rotation slider and spin box as well
            self.sld_rotation.set_position(self.roundSlider.value / 360.0)
            self.spb_rotation.set_value(int(round(self.sld_rotation.value * 360)))
        
        # Image offset limits for later use
        a = self.image.offsetLeftLimit
        b = self.image.offsetRightLimit
        c = self.image.offsetUpLimit
        d = self.image.offsetDownLimit
        
        # Click on offsetX slider 
        self.sld_offsetX.ready_to_slide(x, y)
        if self.sld_offsetX.slideFlag:
            self.sld_offsetX.slide(x, y)
            self.spb_offsetX.set_value(int(round(-100 + self.sld_offsetX.value * 200))) 
            self.offsetX = int(round(a + (b - a) * self.sld_offsetX.value))
        
        # Click on offsetY slider
        self.sld_offsetY.ready_to_slide(x, y)
        if self.sld_offsetY.slideFlag:
            self.sld_offsetY.slide(x, y)
            self.spb_offsetY.set_value(int(round(-100 + self.sld_offsetY.value * 200)))
            self.offsetY = int(round(c + (d - c) * self.sld_offsetY.value))
        
        # Click on rotation slider
        self.sld_rotation.ready_to_slide(x, y)
        if self.sld_rotation.slideFlag:
            self.sld_rotation.slide(x, y)
            self.spb_rotation.set_value(int(round(self.sld_rotation.value * 360)))
            self.roundSlider.set_position(self.sld_rotation.value * 360)
        
        # Click on scale slider
        self.sld_scale.ready_to_slide(x, y)
        if self.sld_scale.slideFlag:
            ratioMin = self.image.ratioMin
            ratioMax = self.image.ratioMax              
            self.sld_scale.slide(x, y)
            self.spb_scale.set_value(int(round(-100 + self.sld_scale.value * 200)))      
            self.image.ratio = ratioMin + (ratioMax - ratioMin) * (1 - self.sld_scale.value)
            self.update_curScale()
        
        # Click on color slider
        self.sld_color.ready_to_slide(x, y)
        if self.sld_color.slideFlag:
            self.sld_color.slide(x, y)
            self.spb_color.set_value(int(round(self.sld_color.value * 100)))
            self.enhance_image()

        # Click on brightness slider
        self.sld_brightness.ready_to_slide(x, y)
        if self.sld_brightness.slideFlag:
            self.sld_brightness.slide(x, y)
            self.spb_brightness.set_value(int(round(-100 + self.sld_brightness.value * 200)))
            self.enhance_image()
            
        # Click on contrast slider
        self.sld_contrast.ready_to_slide(x, y)
        if self.sld_contrast.slideFlag:
            self.sld_contrast.slide(x, y)
            self.spb_contrast.set_value(int(round(-100 + self.sld_contrast.value * 200)))
            self.enhance_image()    
            
        # Click on sharpness slider
        self.sld_sharpness.ready_to_slide(x, y)
        if self.sld_sharpness.slideFlag:
            self.sld_sharpness.slide(x, y)
            self.spb_sharpness.set_value(int(round(-100 + self.sld_contrast.value * 200)))
            self.enhance_image()
            
       # Click on transparency slider
        self.sld_transp.ready_to_slide(x, y)
        if self.sld_transp.slideFlag:
            self.sld_transp.slide(x, y)
            self.spb_transp.set_value(int(round(self.sld_transp.value * 100)))
            self.enhance_image()     
        
        # Store the current x and y coordinates to calculate the shift from
        self.curX = x
        self.curY = y

        # Make image transformation and updates
        self.image_update()  
        
    def mouseMoveEvent(self, event):
        """Method for handle the mouse move with pressed left click"""
        x = event.x()
        y = event.y()
        
        # Distance from the (x0, y0) point
        distance = m.sqrt(m.pow(x - self.xC, 2) + m.pow(y - self.yC, 2))
    
        # Mouse move without buttons
        if event.buttons() == Qt.NoButton:  
            self.mouse_pointer_change(distance)
 
        # Mouse move while left pressed
        elif event.buttons() == Qt.LeftButton:  
            
            # Image offset limits for later use
            a = self.image.offsetLeftLimit
            b = self.image.offsetRightLimit
            c = self.image.offsetUpLimit
            d = self.image.offsetDownLimit
            
            # If clicked on the round slider and then moise move
            if self.roundSlider.slideFlag:
                self.roundSlider.slide(x, y)
                # update rotation slider and spin box as well
                self.sld_rotation.set_position(self.roundSlider.value / 360.0)
                self.spb_rotation.set_value(int(round(self.sld_rotation.value * 360)))
            
            # If clicked on the polygon area and then mouse move
            if self.flagShift:  
            
                alfa = self.image.angle * m.pi / 180  # Transformation degrees -> radians
                # Determine the image offset along X coordinate
                shift = ((x - self.curX) * m.cos(alfa) + (y - self.curY) * m.sin(alfa)) * self.image.ratio
                self.offsetX = self.offsetX + shift      
                
                # I. Limit to the right shifting (along X coordinate):
                if self.offsetX > self.image.offsetRightLimit:
                    self.offsetX = self.image.offsetRightLimit
                
                # Limit to the left shifting (along Y coordinate):
                if self.offsetX < self.image.offsetLeftLimit:
                    self.offsetX = self.image.offsetLeftLimit
                
                # Update offsetX slider and spin box
                self.sld_offsetX.set_position((self.offsetX - a)/(b - a))
                self.spb_offsetX.set_value(int(round(-100 + self.sld_offsetX.value * 200)))        
            
                # II. Determine the image offset along Y coordinate
                shift = ((y - self.curY) * m.cos(alfa) - (x - self.curX) * m.sin(alfa)) * self.image.ratio
                self.offsetY = self.offsetY + shift
            
                # Limit to the bottom shifting (along X coordinate):
                if self.offsetY > self.image.offsetDownLimit:
                    self.offsetY = self.image.offsetDownLimit
                
                # Limit to the up shifting (along X coordinate):
                if self.offsetY < self.image.offsetUpLimit:
                    self.offsetY = self.image.offsetUpLimit
                    
                # Update offsetX slider and spin box
                self.sld_offsetY.set_position((self.offsetY - c)/(d - c))
                self.spb_offsetY.set_value(int(round(-100 + self.sld_offsetY.value * 200)))
                
                # Update the current position of the cursor, to add a shift pisex by pixel  
                self.curY = y
                self.curX = x
                
            # If clicked on the offsetX slider and then mouse move
            if self.sld_offsetX.slideFlag:
                self.sld_offsetX.slide(x, y)
                self.spb_offsetX.set_value(int(round(-100 + self.sld_offsetX.value * 200))) 
                self.offsetX = int(round(a + (b - a) * self.sld_offsetX.value))
                
            # If clicked on the offsetY slider and then mouse move
            if self.sld_offsetY.slideFlag:
                self.sld_offsetY.slide(x, y)
                self.spb_offsetY.set_value(int(round(-100 + self.sld_offsetY.value * 200))) 
                self.offsetY = int(round(c + (d - c) * self.sld_offsetY.value))
                
            # If clicked on the rotation slider and then mouse move
            if self.sld_rotation.slideFlag:
                self.sld_rotation.slide(x, y)
                self.spb_rotation.set_value(int(round(self.sld_rotation.value * 360)))
                self.roundSlider.set_position(self.sld_rotation.value * 360)
                
            # If clicked on the scale slider and then mouse move
            if self.sld_scale.slideFlag:
                ratioMin = self.image.ratioMin
                ratioMax = self.image.ratioMax
                self.sld_scale.slide(x, y)
                self.spb_scale.set_value(int(round(-100 + self.sld_scale.value * 200)))
                self.image.ratio = ratioMin + (ratioMax - ratioMin) * (1 - self.sld_scale.value)
                self.update_curScale()
             
            # If clicked on the color slider and then mouse move
            if self.sld_color.slideFlag:
                self.sld_color.slide(x, y)
                self.spb_color.set_value(int(round(self.sld_color.value * 100)))
                self.enhance_image()

            # If clicked on the brightness slider and then mouse move
            if self.sld_brightness.slideFlag:
                self.sld_brightness.slide(x, y)
                self.spb_brightness.set_value(int(round(-100 + self.sld_brightness.value * 200)))
                self.enhance_image()

            # If clicked on the contrast slider slider and then mouse move
            if self.sld_contrast.slideFlag:
                self.sld_contrast.slide(x, y)
                self.spb_contrast.set_value(int(round(-100 + self.sld_contrast.value * 200)))
                self.enhance_image()  
                
            # If clicked on the sharpness slider slider and then mouse move
            if self.sld_sharpness.slideFlag:
                self.sld_sharpness.slide(x, y)
                self.spb_sharpness.set_value(int(round(-100 + self.sld_sharpness.value * 200)))
                self.enhance_image()
            
            # If clicked on the transparency slider and then mouse move
            if self.sld_transp.slideFlag:
                self.sld_transp.slide(x, y)
                self.spb_transp.set_value(int(round(self.sld_transp.value * 100)))
                self.enhance_image() 
            
            # Make image transformation and updates
            self.image_update()    
    
    def mouse_pointer_change(self, distance):
        """Method for change the mouse pointer depending on its position"""
        # Change the cursor according to the distance
        if (distance <= self.r) and (self.flagCursor != 'SizeAllCursor'):
            self.setCursor(QCursor(Qt.SizeAllCursor))
            self.flagCursor = 'SizeAllCursor'
        elif (distance > self.r) and (self.flagCursor != 'ArrowCursor'):
            self.setCursor(QCursor(Qt.ArrowCursor))
            self.flagCursor = 'ArrowCursor'
            
    def update_curScale(self):
        """Method for updating current scale value"""
        string = self.edt_origScale.text()  # Get the raw string
        string = string.replace(',', '.')  # Symbol ',' is also available
        error = False
        try:
            value = float(string)
            self.origScale = value
        except:
            error = True
        # Update the text field itself
        string = '{0}'.format(self.origScale)
        self.edt_origScale.setText(string)
        
        if error:
            text = 'Original scale should be a number!'
            self.show_error_window(text) 
        else:  # Update the current scale
            self.curScale = value * self.image.ratio
            string = '{0:.3f}'.format(self.curScale)
            self.edt_curScale.setText(string)
    
    def show_error_window(self, text):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(text)
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    # ========== SPIN BOXES METHODS HANDLE ==========
    
    def val_changed_spb_offsetX(self):
        """Method for handle the value change of the offsetX spin box"""
        value = self.spb_offsetX.value()
        
        # Image offset limits for later use
        a = self.image.offsetLeftLimit
        b = self.image.offsetRightLimit
        
        # Update slider position and image offset
        self.sld_offsetX.set_position((value + 100)/200)
        self.offsetX = int(round(a + (b - a) * self.sld_offsetX.value))   
        
        # Make image transformation and updates
        self.image_update() 
        
    def val_changed_spb_offsetY(self):
        """Method for handle the value change of the offsetY spin box"""
        value = self.spb_offsetY.value()
        
        # Image offset limits for later use
        c = self.image.offsetUpLimit
        d = self.image.offsetDownLimit    
        
        # Update slider position and image offset
        self.sld_offsetY.set_position((value + 100)/200)
        self.offsetY = int(round(c + (d - c) * self.sld_offsetY.value)) 
        
        # Make image transformation and updates
        self.image_update() 
    
    def val_changed_spb_rotation(self):
        """Method for handle the value change of the rotation spin box"""
        value = self.spb_rotation.value()
        
        # Update the slider position and round slider position
        self.sld_rotation.set_position(value / 360)
        self.roundSlider.set_position(self.sld_rotation.value * 360)
        
        # Make image transformation and updates
        self.image_update() 
    
    
    def val_changed_spb_scale(self):
        """Method for handle the value change of the scale spin box"""
        value = self.spb_scale.value()
        
        # image min and max ratio for later use
        ratioMin = self.image.ratioMin
        ratioMax = self.image.ratioMax
        
        # Update the slider and image scale
        self.sld_scale.set_position((value + 100)/200)
        self.image.ratio = ratioMin + (ratioMax - ratioMin) * (1 - self.sld_scale.value)
        self.update_curScale()
        
        # Make image transformation and updates
        self.image_update() 

    def val_changed_spb_color(self):
        """Method for handle the value change of the color spin box"""
        value = self.spb_color.value()
        # Update the slider and image scale
        self.sld_color.set_position(value / 100)
        self.enhance_image()

    def val_changed_spb_brightness(self):
        """Method for handle the value change of the brightness spin box"""
        value = self.spb_brightness.value()
        # Update the slider and image brightness
        self.sld_brightness.set_position((value + 100)/ 200)
        self.enhance_image()

    def val_changed_spb_contrast(self):
        """Method for handle the value change of the contrast of the spin box"""
        value = self.spb_contrast.value()
        # Update the slider and image contrast
        self.sld_contrast.set_position((value + 100) / 200)
        self.enhance_image()
        
    def val_changed_spb_sharpness(self):
        """Method for handle the value change of the sharpness of the spin box"""
        value = self.spb_sharpness.value()
        # Update the slider and image contrast
        self.sld_sharpness.set_position((value + 100) / 200)
        self.enhance_image()
        
    def val_changed_spb_transp(self):
        """Method for handle the value change of the transparency spin box"""
        value = self.spb_transp.value()
        # Update the slider and image scale
        self.sld_transp.set_position(value / 100)
        self.enhance_image()
        
    def val_changed_spb_axesNum(self):
        """Method for handle the value change of the axesNum spin box"""
        self.N = self.spb_axesNum.value()
        self.lbl_image.set_N(self.N)
        self.image.set_N(self.N)
        self.image_update()
    
    # ========== RESET BUTTONS ==========
    
    def reset_offsetX(self):
        """Method to reset the offsetX value (set it to 0 value)"""
        # Image offset limits for later use
        a = self.image.offsetLeftLimit
        b = self.image.offsetRightLimit
        
        # Update slider position, image offset and spin box value
        self.sld_offsetX.set_position(0.5)
        self.spb_offsetX.set_value(0)
        self.offsetX = int(round(a + (b - a) * self.sld_offsetX.value))       
        
        # Make image transformation and updates
        self.image_update()        
        
    def reset_offsetY(self):
        """Method to reset the offsetY value (set it to 0 value)"""
        # Image offset limits for later use
        c = self.image.offsetUpLimit
        d = self.image.offsetDownLimit
        
        # Update slider position, image offset and spin box value
        self.sld_offsetY.set_position(0.5)
        self.spb_offsetY.set_value(0)
        self.offsetY = int(round(c + (d - c) * self.sld_offsetY.value)) 
        
        # Make image transformation and updates
        self.image_update() 
         
    def reset_rotation(self):
        """Method to reset the rotation value (set it to 0 value)"""
        # Update the slider position and round slider position
        self.sld_rotation.set_position(0)
        self.roundSlider.set_position(0)
        self.spb_rotation.set_value(0)
        
        # Make image transformation and updates
        self.image_update()   
    
    def reset_scale(self):
        """Method to reset the scale value (set it to 0 value)"""       
        # Update the slider, image scale and spin box value
        self.sld_scale.set_position(0.5)
        self.spb_scale.set_value(0)
        self.image.ratio = self.image.ratioInit
        self.update_curScale()
        
        # Make image transformation and updates
        self.image_update() 
    
    def reset_color(self):
        """Method to reset the color value (set it to 1.0 value)"""
        # Update the slider and image color
        self.sld_color.set_position(1)
        self.spb_color.set_value(100)
        self.enhance_image()
    
    def reset_brightness(self):
        """Method to reset the brightness value (set it to 0.5 value)"""
        # Update the slider and image brightness
        self.sld_brightness.set_position(0.5)
        self.spb_brightness.set_value(0)
        self.enhance_image()
    
    def reset_contrast(self):
        """Method to reset the contrast value (set it to 0.5 value)"""
        # Update the slider and image contrast
        self.sld_contrast.set_position(0.5)
        self.spb_contrast.set_value(0)
        self.enhance_image()
    
    def reset_sharpness(self):
        """Method to reset the sharpness value (set it to 0.5 value)"""
        # Update the slider and image sharpness
        self.sld_sharpness.set_position(0.5)
        self.spb_sharpness.set_value(0)
        self.enhance_image()
    
    def reset_transp(self):
        """Method to reset the transparency value (set it to 1.0 value)"""
        # Update the slider and image color
        self.sld_transp.set_position(1)
        self.spb_transp.set_value(100)
        self.enhance_image()
        
    def reset_axesNum(self):
        self.spb_axesNum.setValue(12)
        self.image_update()
    
    # ========== BOTTOM BUTTONS ==========
    
    def image_load(self):
        """Method for load the particle image to ParticleTester"""
        # Create a dictionary with image and data to send back
        data = {'path':       self.image.path,
                'imageMod':   self.image.imageMod,
                'angle':      self.image.angle,
                'ratio':      self.image.ratio,
                'origScale':  self.origScale,
                'curScale':   self.curScale,
                'offsetX':    self.image.offsetX,
                'offsetY':    self.image.offsetY,
                'color':      self.image.color,
                'brightness': self.image.brightness,
                'contrast':   self.image.contrast,
                'sharpness':  self.image.sharpness,
                'transp':     self.image.transp,
                'axesNum':    self.N}
        # Send data to ParticleTester
        self.particleTester.set_real_image_data(data)
        self.close()
    
    def load_cancel(self):
        """Method for closing the current window without any changes"""
        self.close()

