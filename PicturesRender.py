# -*- coding: utf-8 -*-
"""
Project:        Pictures render tool 
Description:    Program for rendering the pictures with prevously generated
                particles with particles generator tool.
Author:         Dmitry Safonov (Dmitry.Safonov@lut.fi)
Organization:   Lappeenranta University of Technology (LUT)
                Solid/Liquid Separation Research Group            
Last edited:    30.03.2019
"""
import sys
import os
import numpy as np
from PyQt5.QtWidgets import (QMainWindow, QApplication, QDesktopWidget, QAction, 
                             QLabel, QPushButton, QMessageBox, QFileDialog, QCheckBox)
from PyQt5.QtGui import QIcon, QFont, QPixmap
from PyQt5.QtCore import Qt, QThreadPool, QTimer
from time import localtime, strftime, time
import random as rnd
import math as m
from operator import itemgetter
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from PIL.ImageQt import ImageQt

# Program modules:
from Modules.About import About
from Modules.AdvancedQSpinBox import AdvancedQSpinBox
from Modules.AdvancedQLineEdit import AdvancedQLineEdit
from Modules.AdvancedQProgressBar import AdvancedQProgressBar
from Modules.Worker import Worker
from Modules.EditValidateFcn import edit_str_to_value
from Modules.PRenderSettingsWindow import ColorSettingsWindow

# Main window class     
class PicturesRender(QMainWindow):
    """Class of a main window of the pictures render tool"""
    def __init__(self):
        """Constructor of the class"""
        super().__init__()
        rnd.seed()
        self.nDim = None  # Number of particle dimensions
        self.dimsValues = None  # Radius vectors of the particle shape   
        # Particles system properties
        self.onlySpherical = None  # Flag to render only spherical particles
        self.init_picturesNum = None  # Initial number of pictures with particles
        self.init_partPerPicture = None  # Initial number of particles per picture
        self.init_particlesNum = None  # Initial total number of particles
        self.particlesNum = None  # Current total number of particles
        self.partPerPicture = None  # Current number of particles per picture
        self.picturesNum = None  # Current umber of pictures with particles
        self.sumAreaUm2 = None  # Sum of all particles areas per picture (in um2)
        self.areaUm2PerPic = None 
        # Render parameters:
        self.stopRender = False  # Flag to stop the render
        self.stopReading = False  # Flag to stop reading the file
        self.lamp = False  # Flag showing the work of the green lamp
        self.renderStartTime = None  # Render start time
        self.elapsedTime = None  # Elapsed time of the render in seconds
        self.timeToFinish = None  # Seconds to finish the pictures render      
        self.renderedParts = None  # Total amount of rendered particles
        self.renderedPicts = None  # Total amount of rendered pictures
        self.percentComplete = None  # Percent to complete the render
        self.picParticleColor = None  # Color of the particle on the picture
        self.picBkgColor = None  # Color of the background on the picture
        self.picShowScale = None  # Scale visibility on the single picture
        # Additional fields
        self.pictureScale = None  # Scale (um/pix) of the picture
        self.pictureSize = None  # Size (pix) of the picture
        self.realSize = None  # Real size (um) of the picture
        self.picSolidity = None  # Picture solidity (%)
        self.blurPerc = None  # % of blurred particles on picture
        self.blurValue = None  # % of blur
        self.useOverlap = None  # Flag to use overlap or not
        self.thumbnailPic = None  # Thumbnail picture on Window
        self.thumbnailScale = None  # Scale of the thumbnail picture
        self.thumbnailSize = 243  # Size of the side of thembnail picture
        self.folderName = None  # Folder name
        self.fileName = None  # File Name of the input PSysGen file
        self.threadpool = QThreadPool()
        self.init_ui()  # Initialize the user interface elements

    def init_ui(self):
        """Method for the initialization of the UI"""
        self.setFixedSize(574, 535)  # Window size
        self.center_window()  # Center the window on desktop
        self.setWindowIcon(QIcon('Resources/icon.png'))
        self.setWindowTitle('Pictures render tool')  # Window title
        # Menu and submenu creation 
        mainMenu = self.menuBar() 
        PSystemMenu = mainMenu.addMenu('PSystem')
        infoMenu = mainMenu.addMenu('Info')
        # Menu action - PSystem -> Load file...
        self.loadPSysAct = QAction(QIcon('Resources/load.png'), 'Open file...', self)
        self.loadPSysAct.setShortcut('Ctrl+O')
        self.loadPSysAct.setFont(QFont('Arial', 11))
        self.loadPSysAct.triggered.connect(self.load_PSystem_data)
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
        # Add actions to menu: PSystem -> ...
        PSystemMenu.addAction(self.loadPSysAct)
        # Add actions to menu: Info -> ...
        infoMenu.addAction(helpAct)
        infoMenu.addAction(aboutAct)
        
        # Label (Particle system properties)
        self.lbl_PSProps = QLabel('Particles system properties:', self)
        self.lbl_PSProps.setGeometry(20, 30, 220, 20)
        self.lbl_PSProps.setFont(QFont('Arial', 11, weight=QFont.Bold))           
        # Label (Picture properties)
        self.lbl_pictProps = QLabel('Picture properties:', self)
        self.lbl_pictProps.setGeometry(20, 191, 220, 20)
        self.lbl_pictProps.setFont(QFont('Arial', 11, weight=QFont.Bold))
        # Label (Render effects)
        self.lbl_renderEffects = QLabel('Render effects:', self)
        self.lbl_renderEffects.setGeometry(20, 352, 220, 20)
        self.lbl_renderEffects.setFont(QFont('Arial', 11, weight=QFont.Bold))
        # Label (Rendering picture)
        self.lbl_renderingPict = QLabel('Rendering picture:', self)
        self.lbl_renderingPict.setGeometry(310, 30, 220, 20)
        self.lbl_renderingPict.setFont(QFont('Arial', 11, weight=QFont.Bold))
        # Label (Rendering information)
        self.lbl_renderingInfo = QLabel('Rendering information:', self)
        self.lbl_renderingInfo.setGeometry(310, 309, 220, 20)
        self.lbl_renderingInfo.setFont(QFont('Arial', 11, weight=QFont.Bold))

        """Particle system properties section"""
        # Block with particles type
        self.lbl_partType = QLabel('Particles type:', self)
        self.lbl_partType.setAlignment(Qt.AlignLeft)
        self.lbl_partType.setGeometry(20, 53, 150, 21)
        self.lbl_partType.setFont(QFont('Arial', 11))

        self.edt_partType = AdvancedQLineEdit(self)
        self.edt_partType.setAlignment(Qt.AlignRight)
        self.edt_partType.setGeometry(163, 53, 101, 21)
        self.edt_partType.setFont(QFont('Arial', 11))
        self.edt_partType.set_readOnly(True)

        # Block with axes number
        self.lbl_axesNum = QLabel('Axes number:', self)
        self.lbl_axesNum.setAlignment(Qt.AlignLeft)
        self.lbl_axesNum.setGeometry(20, 76, 95, 21)
        self.lbl_axesNum.setFont(QFont('Arial', 11))
        
        self.edt_axesNum = AdvancedQLineEdit(self)
        self.edt_axesNum.setAlignment(Qt.AlignRight)
        self.edt_axesNum.setGeometry(163, 76, 101, 21)
        self.edt_axesNum.setFont(QFont('Arial', 11))
        self.edt_axesNum.set_readOnly(True)

        # Block with particle total number
        self.lbl_particlesNum = QLabel('Particles number:', self)
        self.lbl_particlesNum.setAlignment(Qt.AlignLeft)
        self.lbl_particlesNum.setGeometry(20, 99, 150, 21)
        self.lbl_particlesNum.setFont(QFont('Arial', 11))

        self.edt_particlesNum = AdvancedQLineEdit(self)
        self.edt_particlesNum.setAlignment(Qt.AlignRight)
        self.edt_particlesNum.setGeometry(163, 99, 101, 21)
        self.edt_particlesNum.setFont(QFont('Arial', 11))
        self.edt_particlesNum.set_readOnly(True)

        # Block with number of pictures
        self.lbl_picturesNum = QLabel('Number of pictures:', self)
        self.lbl_picturesNum.setAlignment(Qt.AlignLeft)
        self.lbl_picturesNum.setGeometry(20, 122, 150, 21)
        self.lbl_picturesNum.setFont(QFont('Arial', 11))

        self.spb_picturesNum = AdvancedQSpinBox(self)
        self.spb_picturesNum.setAlignment(Qt.AlignRight)
        self.spb_picturesNum.setGeometry(163, 122, 65, 21)
        self.spb_picturesNum.setFont(QFont('Arial', 11))
        self.spb_picturesNum.setRange(1, 9000)
        self.spb_picturesNum.valueChanged.connect(self.val_changed_spb_picturesNum)

        self.btn_resetPicturesNum = QPushButton(self)
        self.btn_resetPicturesNum.setGeometry(244, 122, 21, 21)
        self.btn_resetPicturesNum.setIcon(QIcon(QPixmap('Resources/arrow.png')))
        self.btn_resetPicturesNum.clicked.connect(self.reset_picturesNum)
        
        # Block with particles per picture
        self.lbl_partPerPicture = QLabel('Particles in picture:', self)
        self.lbl_partPerPicture.setAlignment(Qt.AlignLeft)
        self.lbl_partPerPicture.setGeometry(20, 145, 150, 21)
        self.lbl_partPerPicture.setFont(QFont('Arial', 11))

        self.spb_partPerPicture = AdvancedQSpinBox(self)
        self.spb_partPerPicture.setAlignment(Qt.AlignRight)
        self.spb_partPerPicture.setGeometry(163, 145, 65, 21)
        self.spb_partPerPicture.setFont(QFont('Arial', 11))
        self.spb_partPerPicture.setRange(1, 9000)
        self.spb_partPerPicture.valueChanged.connect(self.val_changed_spb_partPerPicture)

        self.btn_resetPartPerPicture = QPushButton(self)
        self.btn_resetPartPerPicture.setGeometry(244, 145, 21, 21)
        self.btn_resetPartPerPicture.setIcon(QIcon(QPixmap('Resources/arrow.png')))
        self.btn_resetPartPerPicture.clicked.connect(self.reset_picturesNum)

        """Picture properties section"""
        # Block with picture scale (um/pix)
        self.lbl_pictureScale = QLabel('Scale, [\u03BCm/pix]:', self)
        self.lbl_pictureScale.setAlignment(Qt.AlignLeft)
        self.lbl_pictureScale.setGeometry(20, 214, 150, 21)
        self.lbl_pictureScale.setFont(QFont('Arial', 11))

        self.edt_pictureScale = AdvancedQLineEdit(self)
        self.edt_pictureScale.setAlignment(Qt.AlignRight)
        self.edt_pictureScale.setGeometry(163, 214, 65, 21)
        self.edt_pictureScale.setFont(QFont('Arial', 11))
        self.edt_pictureScale.editingFinished.connect(self.update_edt_pictureScale)

        self.btn_resetPictureScale = QPushButton(self)
        self.btn_resetPictureScale.setGeometry(244, 214, 21, 21)
        self.btn_resetPictureScale.setIcon(QIcon(QPixmap('Resources/arrow.png')))
        self.btn_resetPictureScale.clicked.connect(self.reset_pictureScale)

        # Block with picture size to render
        self.lbl_pictureSize = QLabel('Picture size, [pix]:', self)
        self.lbl_pictureSize.setAlignment(Qt.AlignLeft)
        self.lbl_pictureSize.setGeometry(20, 237, 150, 21)
        self.lbl_pictureSize.setFont(QFont('Arial', 11))
        
        self.spb_pictureSize = AdvancedQSpinBox(self)
        self.spb_pictureSize.setAlignment(Qt.AlignRight)
        self.spb_pictureSize.setGeometry(163, 237, 65, 21)
        self.spb_pictureSize.setFont(QFont('Arial', 11))
        self.spb_pictureSize.setRange(100, 9000)
        self.spb_pictureSize.valueChanged.connect(self.val_changed_spb_pictureSize)
        
        self.btn_resetPictureSize = QPushButton(self)
        self.btn_resetPictureSize.setGeometry(244, 237, 21, 21)
        self.btn_resetPictureSize.setIcon(QIcon(QPixmap('Resources/arrow.png')))
        self.btn_resetPictureSize.clicked.connect(self.reset_pictureSize)

        # Block with picture real size (um) for information
        self.lbl_realSize = QLabel('Real size, [\u03BCm]:', self)
        self.lbl_realSize.setAlignment(Qt.AlignLeft)
        self.lbl_realSize.setGeometry(20, 260, 150, 21)
        self.lbl_realSize.setFont(QFont('Arial', 11))

        self.edt_realSize = AdvancedQLineEdit(self)
        self.edt_realSize.setAlignment(Qt.AlignRight)
        self.edt_realSize.setGeometry(163, 260, 101, 21)
        self.edt_realSize.setFont(QFont('Arial', 11))
        self.edt_realSize.set_readOnly(True)

        # Block with calculated picture solidity
        self.lbl_picSolidity = QLabel('Picture solidity, [%]:', self)
        self.lbl_picSolidity.setAlignment(Qt.AlignLeft)
        self.lbl_picSolidity.setGeometry(20, 283, 150, 21)
        self.lbl_picSolidity.setFont(QFont('Arial', 11))

        self.edt_picSolidity = AdvancedQLineEdit(self)
        self.edt_picSolidity.setAlignment(Qt.AlignRight)
        self.edt_picSolidity.setGeometry(163, 283, 101, 21)
        self.edt_picSolidity.setFont(QFont('Arial', 11))
        self.edt_picSolidity.set_readOnly(True)

        # Block with colors settings of the final picture
        self.lbl_colorSettings = QLabel('Color settings:', self)
        self.lbl_colorSettings.setAlignment(Qt.AlignLeft)
        self.lbl_colorSettings.setGeometry(20, 306, 150, 21)
        self.lbl_colorSettings.setFont(QFont('Arial', 11))

        self.btn_openSettings = QPushButton(self)
        self.btn_openSettings.setGeometry(163, 306, 21, 21)
        self.btn_openSettings.setIcon(QIcon(QPixmap('Resources/settings.png')))
        self.btn_openSettings.clicked.connect(self.open_color_settings)

        """Render effects section"""
        # Block with percent of blurred particles
        self.lbl_blurPerc = QLabel('Blurred part-s, [%]:', self)
        self.lbl_blurPerc.setAlignment(Qt.AlignLeft)
        self.lbl_blurPerc.setGeometry(20, 375, 150, 21)
        self.lbl_blurPerc.setFont(QFont('Arial', 11))

        self.spb_blurPerc = AdvancedQSpinBox(self)
        self.spb_blurPerc.setAlignment(Qt.AlignRight)
        self.spb_blurPerc.setGeometry(163, 375, 65, 21)
        self.spb_blurPerc.setFont(QFont('Arial', 11))
        self.spb_blurPerc.setRange(0, 100)
        self.spb_blurPerc.valueChanged.connect(self.val_changed_spb_blurPerc)

        self.btn_resetBlurPerc = QPushButton(self)
        self.btn_resetBlurPerc.setGeometry(244, 375, 21, 21)
        self.btn_resetBlurPerc.setIcon(QIcon(QPixmap('Resources/arrow.png')))
        self.btn_resetBlurPerc.clicked.connect(self.reset_blurPerc)

        # Block with value of blur (0 - 1)
        self.lbl_blurValue = QLabel('Blur value, [%]:', self)
        self.lbl_blurValue.setAlignment(Qt.AlignLeft)
        self.lbl_blurValue.setGeometry(20, 398, 150, 21)
        self.lbl_blurValue.setFont(QFont('Arial', 11))

        self.spb_blurValue = AdvancedQSpinBox(self)
        self.spb_blurValue.setAlignment(Qt.AlignRight)
        self.spb_blurValue.setGeometry(163, 398, 65, 21)
        self.spb_blurValue.setFont(QFont('Arial', 11))
        self.spb_blurValue.setRange(0, 100)
        self.spb_blurValue.valueChanged.connect(self.val_changed_spb_blurValue)

        self.btn_resetBlurValue = QPushButton(self)
        self.btn_resetBlurValue.setGeometry(244, 398, 21, 21)
        self.btn_resetBlurValue.setIcon(QIcon(QPixmap('Resources/arrow.png')))
        self.btn_resetBlurValue.clicked.connect(self.reset_blurValue)

        # Checkbox to use particles overlapping or not
        self.chb_useOverlap = QCheckBox('Use particles overlapping', self)
        self.chb_useOverlap.setGeometry(20, 421, 200, 21)
        self.chb_useOverlap.setFont(QFont('Arial', 11))
        self.chb_useOverlap.clicked.connect(self.chb_useOverlap_clicked)

        """Rendered picture section"""
        # Label with particle image
        self.lbl_rendPicture = QLabel(self)
        self.lbl_rendPicture.setGeometry(310, 55, self.thumbnailSize, self.thumbnailSize)
        
        """Rendering information section"""
        # Block with rendering start time
        self.lbl_startDateTime = QLabel('Started date/time:', self)
        self.lbl_startDateTime.setAlignment(Qt.AlignLeft)
        self.lbl_startDateTime.setGeometry(310, 332, 150, 21)
        self.lbl_startDateTime.setFont(QFont('Arial', 11))

        self.edt_startDateTime = AdvancedQLineEdit(self)
        self.edt_startDateTime.setAlignment(Qt.AlignRight)
        self.edt_startDateTime.setGeometry(452, 332, 101, 21)
        self.edt_startDateTime.setFont(QFont('Arial', 11))
        self.edt_startDateTime.set_readOnly(True)

        # Block with elapsed time
        self.lbl_elapsedTime = QLabel('Elapsed time:', self)
        self.lbl_elapsedTime.setAlignment(Qt.AlignLeft)
        self.lbl_elapsedTime.setGeometry(310, 355, 150, 21)
        self.lbl_elapsedTime.setFont(QFont('Arial', 11))

        self.edt_elapsedTime = AdvancedQLineEdit(self)
        self.edt_elapsedTime.setAlignment(Qt.AlignRight)
        self.edt_elapsedTime.setGeometry(452, 355, 101, 21)
        self.edt_elapsedTime.setFont(QFont('Arial', 11))
        self.edt_elapsedTime.set_readOnly(True)

        # Block with time to finish
        self.lbl_timeToFinish = QLabel('Time to finish:', self)
        self.lbl_timeToFinish.setAlignment(Qt.AlignLeft)
        self.lbl_timeToFinish.setGeometry(310, 378, 150, 21)
        self.lbl_timeToFinish.setFont(QFont('Arial', 11))

        self.edt_timeToFinish = AdvancedQLineEdit(self)
        self.edt_timeToFinish.setAlignment(Qt.AlignRight)
        self.edt_timeToFinish.setGeometry(452, 378, 101, 21)
        self.edt_timeToFinish.setFont(QFont('Arial', 11))
        self.edt_timeToFinish.set_readOnly(True)

        # Block with pictures rendered
        self.lbl_renderedPicts = QLabel('Rendered pictures:', self)
        self.lbl_renderedPicts.setAlignment(Qt.AlignLeft)
        self.lbl_renderedPicts.setGeometry(310, 401, 150, 21)
        self.lbl_renderedPicts.setFont(QFont('Arial', 11))

        self.edt_renderedPicts = AdvancedQLineEdit(self)
        self.edt_renderedPicts.setAlignment(Qt.AlignRight)
        self.edt_renderedPicts.setGeometry(452, 401, 101, 21)
        self.edt_renderedPicts.setFont(QFont('Arial', 11))
        self.edt_renderedPicts.set_readOnly(True)

        # Block with particles rendered
        self.lbl_renderedParts = QLabel('Rendered particles:', self)
        self.lbl_renderedParts.setAlignment(Qt.AlignLeft)
        self.lbl_renderedParts.setGeometry(310, 424, 150, 21)
        self.lbl_renderedParts.setFont(QFont('Arial', 11))

        self.edt_renderedParts = AdvancedQLineEdit(self)
        self.edt_renderedParts.setAlignment(Qt.AlignRight)
        self.edt_renderedParts.setGeometry(452, 424, 101, 21)
        self.edt_renderedParts.setFont(QFont('Arial', 11))
        self.edt_renderedParts.set_readOnly(True)

        # Buttons for start and stop rendering the pictures
        self.btn_render = QPushButton('Render', self)
        self.btn_render.setGeometry(20, 459, 80, 27)
        self.btn_render.clicked.connect(self.make_render_do_before)
        
        self.btn_stopRendering = QPushButton('Stop', self)
        self.btn_stopRendering.setGeometry(112, 459, 70, 27)
        self.btn_stopRendering.clicked.connect(self.stop_render)
        
        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.timer_event)

        # Lamps indicator
        self.lbl_lamp = QLabel(self)
        self.lbl_lamp.setGeometry(194, 459, 25, 25)
        self.lbl_lamp.setPixmap(QPixmap('Resources/lamp_off.png'))
        
        # Progress bar
        self.progressBar = AdvancedQProgressBar(self)
        self.progressBar.setGeometry(20, 500, 534, 21)
        
        self.put_default_parameters()
        self.show()

    def put_default_parameters(self):
        """Method for putting the default values and parameters"""
        self.edt_partType.setText('Undefined')
        self.edt_axesNum.setText('Undefined')
        self.edt_particlesNum.setText('Undefined')
        self.spb_picturesNum.setEnabled(False)
        self.btn_resetPicturesNum.setEnabled(False)
        self.spb_partPerPicture.setEnabled(False)
        self.btn_resetPartPerPicture.setEnabled(False)
        self.sumAreaUm2 = 0
        self.pictureScale = 0.2
        self.edt_pictureScale.setText('{0:.3f}'.format(self.pictureScale))
        self.pictureSize = 3000
        self.spb_pictureSize.set_value(self.pictureSize)
        self.update_edt_realSize()
        self.update_edt_picSolidity()
        self.blurPerc = 0
        self.spb_blurPerc.set_value(self.blurPerc)
        self.blurValue = 0
        self.spb_blurValue.set_value(self.blurValue)
        self.useOverlap = False
        self.chb_useOverlap.setChecked(False)
        self.edt_startDateTime.setText('?')
        self.edt_elapsedTime.setText('00:00:00')
        self.timeToFinish = 0
        self.edt_timeToFinish.setText('?')
        self.renderedPicts = 0
        self.edt_renderedPicts.setText('0')
        self.renderedParts = 0
        self.edt_renderedParts.setText('0')
        self.percentComplete = 0
        self.progressBar.setValue(self.percentComplete)
        self.picShowScale = False
        self.lbl_rendPicture.drawPicture = True
        self.btn_render.setEnabled(False)
        self.btn_stopRendering.setEnabled(False)
        self.picBkgColor = [197, 197, 197]
        self.picParticleColor = [0, 0, 0]
        self.thumbnailPic = Image.new('RGB', (self.thumbnailSize, self.thumbnailSize), 
                                      tuple(self.picBkgColor))

    def load_PSystem_data(self):
        """Method for loading the txt file with particle system data"""
        # Determine the PSystem txt filename
        self.fileName = QFileDialog.getOpenFileName(self, 'Load PSystem data', 'GenPartSystems/', 'Text files (*.txt)')[0]
        error = False
        if self.fileName != '':
            with open(self.fileName, "r") as inputFile:
                try:
                    # Reak the onlyShperical flag
                    lineStr = inputFile.readline()  
                    if int(lineStr) == 0:
                        self.onlySpherical = False
                        self.edt_partType.setText('Non-spherical')
                    elif int(lineStr) == 1:
                        self.onlySpherical = True
                        self.edt_partType.setText('Spherical')
                    else:
                        error = True
                        
                    # Read the nDim
                    lineStr = inputFile.readline()
                    self.nDim = int(lineStr)
                    self.edt_axesNum.setText('{0:d}'.format(self.nDim))
                    
                    # Read the pictures number
                    lineStr = inputFile.readline()
                    self.init_picturesNum = int(lineStr)
                    self.picturesNum = self.init_picturesNum
                    
                    # Read the particlesPerPicture
                    lineStr = inputFile.readline()
                    self.init_partPerPicture = int(lineStr)
                    self.partPerPicture = self.init_partPerPicture
                    
                    # Calculate the total amount of particles
                    self.init_particlesNum = self.picturesNum * self.partPerPicture
                    self.particlesNum = self.init_particlesNum
                    self.edt_particlesNum.setText('{0:d}'.format(self.particlesNum))
                    
                    # Set the new range to spb
                    self.spb_picturesNum.setRange(1, self.particlesNum)
                    self.spb_partPerPicture.setRange(1, self.particlesNum)
                    
                    # Update the spb
                    self.spb_picturesNum.set_value(self.picturesNum)
                    self.spb_partPerPicture.set_value(self.partPerPicture)
                    
                    # Read the last line - sumAreaUm2
                    for lineStr in inputFile:
                        pass
                    self.sumAreaUm2 = float(lineStr)
                    
                    # Put the init value to the picturesNum
                    #self.spb_picturesNum.setValue(self.init_picturesNum)
                    
                    # Calculate the picture solidity in %
                    self.update_edt_picSolidity()   
                except:
                    error = True
            
            if error:
                text = 'Error reading the file!'
                self.show_error_window(text)
            else:
                # Enable some elements
                self.spb_picturesNum.setEnabled(True)
                self.spb_picturesNum.setRange(1, self.particlesNum)
                self.btn_resetPicturesNum.setEnabled(True)
                self.spb_partPerPicture.setEnabled(True)
                self.spb_partPerPicture.setRange(1, self.particlesNum)
                self.btn_resetPartPerPicture.setEnabled(True)
                self.btn_render.setEnabled(True)
                self.btn_stopRendering.setEnabled(True)
        
    def chb_useOverlap_clicked(self):
        """Method to define weather use particles overlap or not"""
        if self.chb_useOverlap.isChecked():
            self.useOverlap = True
        else:
            self.useOverlap = False

    def update_edt_pictureScale(self):
        """Method for update the pictureScale editbox"""
        oldValue = self.pictureScale  # Save old value
        editStr = self.edt_pictureScale.text()
        (newValue, errorCode, errorText) = edit_str_to_value('Picture scale', editStr)
        if errorCode == 0:  # No errors
            self.pictureScale = newValue
            self.edt_pictureScale.setText('{0:.3f}'.format(newValue))
            self.update_edt_realSize()
            self.update_edt_picSolidity()
        else:  # Error
            self.edt_pictureScale.setText('{0:.3f}'.format(oldValue))
            self.show_error_window(errorText)

    def update_edt_realSize(self):
        """Method for calculation and update the realSize"""
        self.realSize = self.pictureScale * self.pictureSize
        self.edt_realSize.setText('{0:.3f}'.format(self.realSize))

    def update_edt_picSolidity(self):
        """Method for calculation and update the picSolidity"""
        if self.sumAreaUm2 == 0:
            text = 'Undefined'
        else:
            self.areaUm2PerPic = self.sumAreaUm2 / self.picturesNum
            self.picSolidity = self.areaUm2PerPic * 100 / (m.pow(self.realSize, 2))
            text = '{0:.2f}'.format(self.picSolidity)
            # Indicate the high solidity value
            if self.picSolidity >= 80:
                self.edt_picSolidity.set_red_bkg()
            else:
                self.edt_picSolidity.set_gray_bkg()
        self.edt_picSolidity.setText(text)

    def val_changed_spb_picturesNum(self):
        """Method for change the spb_picturesNum"""
        self.picturesNum = self.spb_picturesNum.value()
        self.partPerPicture = self.init_particlesNum // self.picturesNum
        self.particlesNum = self.picturesNum * self.partPerPicture
        # Update the edits
        self.edt_particlesNum.setText('{0:d}'.format(self.particlesNum))
        self.spb_partPerPicture.set_value(self.partPerPicture)
        self.update_edt_picSolidity()

    def val_changed_spb_partPerPicture(self):
        """Method for change the spb_partPerPicture"""
        self.partPerPicture = self.spb_partPerPicture.value()
        self.picturesNum = self.init_particlesNum // self.partPerPicture
        self.particlesNum = self.picturesNum * self.partPerPicture
        # Update the edits
        self.edt_particlesNum.setText('{0:d}'.format(self.particlesNum))
        self.spb_picturesNum.set_value(self.picturesNum)
        self.update_edt_picSolidity()

    def val_changed_spb_pictureSize(self):
        """Method for change spb_pictureSize value"""
        self.pictureSize = self.spb_pictureSize.value()
        self.update_edt_realSize()
        self.update_edt_picSolidity()
    
    def val_changed_spb_blurPerc(self):
        """Method for change the blurPerc value"""
        self.blurPerc = self.spb_blurPerc.value()
    
    def val_changed_spb_blurValue(self):
        """Method for change the blurValue value"""
        self.blurValue = self.spb_blurValue.value()

    def reset_picturesNum(self):
        """Method for reset the spb_picturesNum value to initial value"""
        self.picturesNum = self.init_picturesNum
        self.spb_picturesNum.setValue(self.picturesNum)

    def reset_partPerPicture(self):
        """Method for reset the spb_partPerPicture value to initial value"""
        self.partPerPicture = self.init_partPerPicture
        self.spb_partPerPicture.setValue(self.partPerPicture)

    def reset_pictureScale(self):
        """Method for reset the edt_pictureScale value to default"""
        self.pictureScale = 0.2
        self.edt_pictureScale.setText('{0:.3f}'.format(self.pictureScale))
        self.update_edt_realSize()
        self.update_edt_picSolidity()

    def reset_pictureSize(self):
        """Method for reset the spb_pictureSize value to default"""
        self.pictureSize = 3000
        self.spb_pictureSize.set_value(self.pictureSize)
        self.update_edt_realSize()
        self.update_edt_picSolidity()
        
    def reset_blurPerc(self):
        """Method for reset the spb_blurPerc value to default"""
        self.blurPerc = 0
        self.spb_blurPerc.set_value(self.blurPerc)     

    def reset_blurValue(self):
        """Method for reset the spb_blurValue value to default"""
        self.blurValue = 0
        self.spb_blurValue.set_value(self.blurValue)

    def open_color_settings(self):
        """Method to open window with colors settings"""
        self.settingsWindow = ColorSettingsWindow(self)

    def set_settings_data(self, settingsData):
        """Method for save color setings data comming from settings window"""
        self.picParticleColor = settingsData['picParticleColor']
        self.picBkgColor = settingsData['picBkgColor']
        self.picShowScale = settingsData['picShowScale']
        # Make new empty thumbnail
        self.thumbnailPic = Image.new('RGB', (self.thumbnailSize, self.thumbnailSize), 
                                      tuple(self.picBkgColor))
        
    def make_render_do_before(self):
        """Preparation method for start rendering the pictures"""
        # Choose the output folder with rendered pictures
        self.folderName = QFileDialog.getExistingDirectory(self, 'Choose folder for pictures',
                                                           'RenderedPictures/', QFileDialog.ShowDirsOnly)
        
        if self.folderName != '':
            # Check if the folder is empty or not
            if os.listdir(self.folderName):
                text = 'Folder is not empty.\nEmpty the folder before render!'
                self.show_error_window(text)
                return None  # Exit the generation method
            self.change_lamp_state()
        else:
            text = 'Folder has not been chosen.\nChoose the folder!'
            self.show_error_window(text)
            return None  # Exit the generation method

        # If everything is OK with folder we can set the preparations:
        self.thumbnailScale = self.pictureSize * self.pictureScale / self.thumbnailSize
        self.percentComplete = 0  # Set the progress bar to 0%
        self.progressBar.setValue(self.percentComplete)
        self.enable_elements(False)  # Disable some window elements:
        self.timeToFinish = 0
        self.elapsedTime = 0  # Reset the elapsed time
        self.timer.start(1000)
        self.stopRender = False  # Do the generation

        # Load the font if necessary
        if self.picShowScale:
            height = int(round(self.pictureSize + 0.05 * self.pictureSize))
            h = int(round(height - self.pictureSize) * 0.1)
            fontWidth = h * 4
            self.font = ImageFont.truetype('Resources/arial.ttf', fontWidth, encoding="utf-8")

        # Save the generation started date-time
        dateTime = strftime("%Y-%m-%d %H:%M:%S", localtime())
        self.edt_startDateTime.setFont(QFont('Arial', 7))
        self.edt_startDateTime.setText(dateTime)

        # Add aditional text file with information to the folder
        fileName = '{0}/_info.txt'.format(self.folderName)
        with open(fileName, 'w') as f:
            textLines = ['Particle type: ' + ('Spherical\n' if self.onlySpherical == 1 else 'Non-spherical\n'),
                         'Axes number: {0:d}\n'.format(self.nDim),
                         'Particles number: {0:d}\n'.format(self.particlesNum),
                         'Number of pictures: {0:d}\n'.format(self.picturesNum),
                         'Particles in picture: {0:d}\n'.format(self.partPerPicture),
                         'Scale, [um/pix]: {0:.3f}\n'.format(self.pictureScale),
                         'Picture size, [pix]: {0:d}\n'.format(self.pictureSize),
                         'Real size, [um]: {0:.3f}\n'.format(self.realSize),
                         'Picture solidity, [%]: {0:.2f}\n'.format(self.picSolidity),
                         'Blured particles, [%]: {0:d}\n'.format(self.blurPerc),
                         'Blured value, [%]: {0:d}\n'.format(self.blurValue),
                         '===== Render information =====\n',
                         'Started date/time: ' + dateTime + '\n']
            f.writelines(textLines)

        # Make worker with multi threading
        worker = Worker(self.make_render_main_process)
        worker.signals.progress.connect(self.update_window_and_parameters)
        worker.signals.finished.connect(self.make_render_do_after)
        self.threadpool.start(worker)

    def make_render_main_process(self, progress_callback):
        """Main method for particles generation"""
        progressData = {'thumbnail': None,  # Current picture of the thumbnail
                        'percentComplete': None,  # Percentage to complete the rendering
                        'timeToFinish': None,  # Time to finish as formatted string
                        'rendParticles': None,  # Number of rendered particles
                        'rendPictures': None}  # Number of rendered pictures

        # Open the GenPartSystem txt file with particles shape data
        inputFile = open(self.fileName, "r")
        
        for i in range(4):
            lineStr = inputFile.readline()

        progressData['rendParticles'] = 0
        progressData['rendPictures'] = 0
        
        # Main pictures render loop:
        for i in range(self.picturesNum):
            # Check to stop the render
            if self.stopRender or self.stopReading:
                break
            
            # Make a new picture and thumbnail
            color = self.picBkgColor + [255]  # add alpha channel
            renderPicture = Image.new('RGBA', (self.pictureSize, self.pictureSize), tuple(color))
            thumbnailPic = Image.new('RGBA', (self.thumbnailSize, self.thumbnailSize), tuple(color))

            # Grab the particles data from the GenPartSystem txt file
            batch = []  # batch with partPerPic amount of particles
            
            for j in range(self.partPerPicture):
                lineStr = inputFile.readline()
                
                if lineStr == "":  # If the rows are lower then should be
                    self.stopReading = True
                    break

                listStr = lineStr.split(',') 
                listStr.pop(0)  # delete the first element with particle number
                listNum = [float(x) for x in listStr]
                # In case of not full particle data we meet EOF, last row is AreaUm2,
                # so, it will produce here the [] and couse an error
                if listNum != []:
                    batch.append(listNum)

            # Sort the batch from large to low with respect to imgScale
            batch = sorted(batch, key=itemgetter(0), reverse=True)
            
            # Looking over every part. in sorted batch for prod. partPic and partPicThumb
            for batchRow in batch:
                # Check to stop the render
                if self.stopRender:
                    break
                
                # Determining the size of partPicture with only 1 particle
                if self.onlySpherical:
                    partPicSize = int(round(batchRow[0] / self.pictureScale))
                    partPicSizeThumb = int(round(batchRow[0] / self.thumbnailScale))
                else:
                    partPicSize = int(round(batchRow[0] * 360 / self.pictureScale))
                    partPicSizeThumb = int(round(batchRow[0] * 360 / self.thumbnailScale))
                
                if not self.onlySpherical:
                    batchRow.pop(0)  # Remain only dims in batchRow   
                
                # Produce pictures with only 1 particle
                (partPic, partPicThumb) = self.produce_particle_picture(
                        partPicSize, partPicSizeThumb, batchRow)
                
                doPositionSearch = True
                searchCount = 0
                while doPositionSearch:
                    # Determine the random coordinates on big pictures
                    roll = rnd.random()
                    x = int(round(roll * (self.pictureSize - partPicSize)))
                    xThumb = int(round(roll * (self.thumbnailSize - partPicSizeThumb)))
                    roll = rnd.random()
                    y = int(round(roll * (self.pictureSize - partPicSize)))  
                    yThumb = int(round(roll * (self.thumbnailSize - partPicSizeThumb)))
                
                    if self.useOverlap:
                        doPositionSearch = False
                    else:  # Determine the overlapping
                        # Get the crop of the renderPicture to determine the overlaping   
                        crop = renderPicture.crop((x, y, x + partPicSize, y + partPicSize))
                        
                        # Convert images to the np arrays:
                        np_partPic = np.array(partPic)
                        np_crop = np.array(crop)
                        
                        # Map partPic: 0 - transparency, 1 - particle
                        map_partPic = np.where(np_partPic[:, :, 3] == 0, 0, 1)
                        # Map crop: 0 - background, 1 - other particle
                        map_crop = np.where(((np_crop[:, :, 0] == self.picBkgColor[0]) & \
                                             (np_crop[:, :, 1] == self.picBkgColor[1]) & \
                                             (np_crop[:, :, 2] == self.picBkgColor[2])), 0, 1)
                        # Analyze the intersection of the matixes
                        product = map_partPic * map_crop
                        overlap = np.any(product)  # If any 1, we have colision
                        
                        # If there is no any overlaping:
                        if not overlap:
                            doPositionSearch = False
                        else:
                            searchCount += 1
                            # If we created 100 tryes than change the orientation of the particle
                            if searchCount % 20 == 0:
                                (partPic, partPicThumb) = self.produce_particle_picture(
                                        partPicSize, partPicSizeThumb, batchRow)
                            if searchCount == 500:
                                doPositionSearch = False
                            
                # Now we have coordinates and ready to put the image to big one
                renderPicture.paste(partPic, (x, y), mask = partPic)              
                thumbnailPic.paste(partPicThumb, (xThumb, yThumb), mask = partPicThumb)
                
                # Calculate the time to finish
                curPartNum = progressData['rendParticles']
                #timeString = ''
                if curPartNum == 0:
                    self.renderStartTime = time()  # Start time
                    timeString = '00:00:00'
                elif curPartNum % self.partPerPicture == 0:
                    timeDelta = time() - self.renderStartTime
                    self.renderStartTime = time()
                    value = ((self.particlesNum - curPartNum - 1) // self.partPerPicture) * timeDelta
                    self.timeToFinish = int(round((8 * self.timeToFinish + 2 * value) / 10))  # Damping for smoothing
                    timeString = self.make_label_for_time(self.timeToFinish)
                progressData['timeToFinish'] = timeString
    
                # Update the percent complete for the progress bar:
                self.percentComplete = curPartNum * 100 / (self.particlesNum - 1)
                progressData['percentComplete'] = self.percentComplete           
                # Increase the rendered particles number
                progressData['rendParticles'] += 1            
                # Update the thumbnail picture
                progressData['thumbnail'] = thumbnailPic
                # Send the callback
                progress_callback.emit(progressData)  
            
            # Draw a scale bar if it is necessary:
            if self.picShowScale:
                # Make extended render picture with field at the bottom
                color = (255, 255, 255, 255)
                height = int(round(self.pictureSize + 0.05 * self.pictureSize))
                oldPicture = renderPicture.copy() 
                renderPicture = Image.new('RGB', (self.pictureSize, height), color)
                renderPicture.paste(oldPicture, (0, 0))
                
                # Draw the sclae bar
                x0 = 0  # Start point of the scale (X)
                y0 = self.pictureSize + (height - self.pictureSize) * 0.2  # Start point of the scale (Y)
                h = int(round(height - self.pictureSize) * 0.1)  # Width of the scale
                part = (self.pictureSize) / 10
                draw = ImageDraw.Draw(renderPicture)
                fill = 'red'
                for j in range(10):
                    draw.rectangle((x0 + part*j, y0, x0 + part*(j+1), y0 + h), fill=fill, outline='red')
                    fill = ('white' if fill == 'red' else 'red')
                
                # Draw informative text
                x = int(round(self.pictureSize / 5))  # X Position of the text
                y = int(round(y0 + h * 3))  # Y position of the text  
                textStr = ''
                textStr += '{0:.2f} [\u03BCm]; '.format(self.realSize)
                textStr += '{0:d} [pix]; '.format(self.pictureSize)
                textStr += 'Scale: {0:.3f} [\u03BCm/pix]; '.format(self.pictureScale)
                textStr += 'Solidity: {0:.2f}%'.format(self.picSolidity)
                draw.text((x, y), textStr, font=self.font, fill=(255, 0, 0, 255))
            
            # Save the picture
            fileName = '{0}/image_{1}.png'.format(self.folderName, progressData['rendPictures'])
            renderPicture.save(fileName, 'PNG')
            
            progressData['rendPictures'] += 1
            # Send the callback
            progress_callback.emit(progressData)


        # Close the input GenPartSystem txt file
        inputFile.close()
        
    def update_window_and_parameters(self, progressData):
        """Method to update particle shape and parameters during the generation"""     
        # Update the thumbnail picture
        self.thumbnailPic = progressData['thumbnail']
        
        # Update the average time to complete the render:
        self.edt_timeToFinish.setText(progressData['timeToFinish'])

        # Update the number of generated particles and pictures
        self.edt_renderedParts.setText('{0:d}'.format(progressData['rendParticles']))
        self.edt_renderedPicts.setText('{0:d}'.format(progressData['rendPictures']))

        # Update the progress bar
        self.progressBar.setValue(progressData['percentComplete'])
        self.update()

    def make_render_do_after(self):
        """Method for doing some things after the generation procedure"""         
        self.change_lamp_state()  # Change the state of the green lamp
        self.edt_timeToFinish.setText('00:00:00')
        self.timer.stop()  # Stop the timer
        
        # Append the information file with some information 
        fileName = '{0}/_info.txt'.format(self.folderName)
        with open(fileName, 'a') as f:
            f.write('Elapsed time: ' + self.edt_elapsedTime.text() + '\n')
        
        # Enable window elements
        self.enable_elements(True)
        
        if self.stopRender:
            text = 'Render has been stopped!'
        else:
            text = 'Render is finished!'
        self.show_information_window(text)

    def stop_render(self):
        """Method for interupting the generation"""
        self.stopRender = True
        
    def change_lamp_state(self):
        """Method for change the lamp state"""
        if self.lamp:
            self.lbl_lamp.setPixmap(QPixmap('Resources/lamp_off.png'))
            self.lamp = False
        else:
            self.lbl_lamp.setPixmap(QPixmap('Resources/lamp_on.png'))
            self.lamp = True
        
    def enable_elements(self, flag):
        """Method for enable or disable some elements while rendering"""
        self.loadPSysAct.setEnabled(flag)
        self.spb_picturesNum.setEnabled(flag)
        self.btn_resetPicturesNum.setEnabled(flag)
        self.spb_partPerPicture.setEnabled(flag)
        self.btn_resetPartPerPicture.setEnabled(flag)
        self.edt_pictureScale.setEnabled(flag)
        self.btn_resetPictureScale.setEnabled(flag)
        self.spb_pictureSize.setEnabled(flag)
        self.btn_resetPictureSize.setEnabled(flag)
        self.btn_openSettings.setEnabled(flag)
        self.spb_blurPerc.setEnabled(flag)
        self.btn_resetBlurPerc.setEnabled(flag)
        self.spb_blurValue.setEnabled(flag)
        self.btn_resetBlurValue.setEnabled(flag)
        self.chb_useOverlap.setEnabled(flag)
        self.btn_render.setEnabled(flag)
    
    def timer_event(self):
        self.elapsedTime += 1
        timeString = self.make_label_for_time(self.elapsedTime)
        self.edt_elapsedTime.setText(timeString)

    def paintEvent(self, event):
        """paintEvent to update the thumbnail picture """       
        qim = ImageQt(self.thumbnailPic)
        qpix = QPixmap.fromImage(qim)
        self.lbl_rendPicture.setPixmap(qpix)
    
    def produce_particle_picture(self, partPicSize, partPicSizeThumb, batchRow):  
        # Determine the coordinates of the points
        if not self.onlySpherical:
            # Block with angle randomization
            randAngle = rnd.uniform(0, m.pi * 2)
            #randAngle = 1.5         
            coord = self.get_coordinates_only(partPicSize, batchRow, randAngle)
            coordThumb = self.get_coordinates_only(partPicSizeThumb, batchRow, randAngle)
                      
        # Create the partPicture with transparent background
        color = tuple(self.picBkgColor + [0])  # Transparent color
        partPic = Image.new('RGBA', (partPicSize, partPicSize), tuple(color))
        partPicThumb = Image.new('RGBA', (partPicSizeThumb, partPicSizeThumb), tuple(color))             
                        
        # Draw the partPicture and partPicSizeThumb on particle pictures
        fill = tuple(self.picParticleColor + [255])
        outline = tuple(self.picParticleColor + [255])
        draw = ImageDraw.Draw(partPic)
        if self.onlySpherical:
            draw.ellipse((0, 0, partPicSize, partPicSize), fill=fill, outline=outline)
        else:
            draw.polygon(coord, fill=fill, outline=outline)
        partPic = partPic.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        draw = ImageDraw.Draw(partPicThumb)
        if self.onlySpherical:
            draw.ellipse((0, 0, partPicSizeThumb, partPicSizeThumb), fill=fill, outline=outline)
        else:
            draw.polygon(coordThumb, fill=fill, outline=outline)
        partPicThumb = partPicThumb.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        # Apply the bigger blur if it is necessary
        roll = rnd.random() * 100
        if roll <= self.blurPerc:  # Need to blur
            #roll = rnd.uniform(0.0, self.blurValue)
            blurRadius = self.blurValue * (partPicSize/10) / 100
            blurRadiusThumb = self.blurValue * (partPicSizeThumb/10) / 100
            partPic = partPic.filter(ImageFilter.GaussianBlur(radius=blurRadius))
            partPicThumb = partPicThumb.filter(ImageFilter.GaussianBlur(radius=blurRadiusThumb))
        
        return partPic, partPicThumb
    
    def get_coordinates_only(self, size, dims, randAngle):  
        """Function for the calculation of shape coordinates"""  
        dimsCoord = ()  # Coordinates ((x,y),...) of all dims points (0 in left top corner)        
        # Calculate the centre radius for new size
        centreRadius = 5 * size / 360    
        dN = 2*m.pi / self.nDim
        array = [0] * self.nDim
        
        for i in range(self.nDim):
            radius = dims[i] * (size / 2 - centreRadius) + centreRadius  # Slider starts not from the center!
            angle = i * dN + randAngle
            x = int(round(m.cos(angle) * radius + size / 2))
            y = int(round(m.sin(angle) * radius + size / 2))
            array[i] = (x, y)
        dimsCoord = tuple(array)
        return dimsCoord    
      
    def make_label_for_time(self, value):
        """Method for creating good-loking string with time"""
        hours = value // 3600
        value = value - hours * 3600
        minutes = value // 60
        value = value - minutes * 60
        seconds = value
        return "{0:d}:{1:02d}:{2:02d}".format(hours, minutes, seconds)
    
    def show_error_window(self, text):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(text)
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def show_information_window(self, text):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(text)
        msg.setWindowTitle("Information")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def show_help(self):
        path = os.getcwd() + '\Help\Help_PicturesRender.pdf'
        os.startfile(path)
        
    def show_about(self):
        self.about = About()
   
    def center_window(self):
        """Method for center the main window on the desktop"""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

if __name__ == '__main__':
    def run_app():
        app = QApplication(sys.argv)
        app.setFont(QFont('Arial', 11)) 
        mainWindow = PicturesRender()
        app.exec_()
    run_app()
    #sys.exit(app.exec_())