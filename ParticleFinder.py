#==========================================================================================
# Project:        Particle Finder module
# Description:    Tool for find the shape of the particle by parameters (reverse problem)
# Author:         Dmitry Safonov (Dmitry.Safonov@lut.fi)
# Organization:   Lappeenranta University of Technology (LUT)
#                 Solid/Liquid Separation Research Group            
# Last edited:    25.12.2020
#==========================================================================================

import sys
import os
from PyQt5.QtWidgets import (QMainWindow, QApplication, QDesktopWidget, QAction, 
                             QLabel, QPushButton, QMessageBox, QFileDialog, 
                             QCheckBox, QPlainTextEdit)
from PyQt5.QtGui import QIcon, QFont, QPixmap, QTextCursor
from PyQt5.QtCore import Qt, QThreadPool
from functools import partial
import json
import math as m
from time import gmtime, strftime, time
import matplotlib.pyplot as plt

# Program modules:
from Modules.Particle import Particle
from Modules.About import About
from Modules.PSOSettingsWindow import PSOSettingsWindow
from Modules.AdvancedQSpinBox import AdvancedQSpinBox
from Modules.AdvancedQLineEdit import AdvancedQLineEdit
from Modules.ImageLabel import ImageLabel
from Modules.PSOAlg_py import PSOAlg_py  # For demonstration use
from Modules.PSOAlg_dll import PSOAlg_dll  # For production use

#from Modules.PSOAlg.PSOAlg_cy import run_search_cy
from Modules.Worker import Worker


# Main window class     
class ParticleFinder(QMainWindow):  
    """Class of a main window of the particle finder tool"""
    def __init__(self):
        """Constructor of the class"""
        super().__init__()
        
        self.particle = Particle()  # Construct particle for determination of its parameters
        
        self.init_CEDiameter = None  # Initial CE diameter of the particle, [um]
        self.init_circularity = None  # Initial particle circularity, [-]
        self.init_convexity = None  # Initial particle convexity, [-]
        self.init_elongation = None  # Initial particle elongation, [-]
        self.nDim = None  # Number of particle dimensions
        self.iterLimit = None  # Limit of algorithm iteration
        self.precisionLimit = None  # Limit of the algorithm precision
        self.useIterLimit = None  # Use iterLimit as stop search parameter
        self.usePrecisionLimit = None  # Use PrecisionLimit as stop search parameter
        self.useVisualIter = None  # Flag to show shape at every search iteration
        self.useLoglIter = None  # Flag to log data about search every iteration
        self.showErrorPlot = None  # Flag to show or not the error plot after the search
        self.algStartTime = None  # Starting time of the searching
        self.algTime = None  # Time of searching, [s]
        self.partPictXPos = 310  # X position of the particle picture
        self.partPictYPos = 60  # Y position of the particle picture
        self.lamp = False  # Flag showing the work of the green lamp       
        self.settingsWindow = None  # Oblect of window with algorithm settings
        
        # PSO optimization algorithm hyperparameters:
        self.psoAlg_py = None  # Instance of the PSO algorithm class (Python code)
        self.psoAlg_dll = PSOAlg_dll()  # Instance of the PSO algorithm class (C code from dll)
        self.PSO_nVar = None  # Number of unknown (decision) variables (equal to nDim)
        self.PSO_varMin = None  # Lower bound of decision variables
        self.PSO_varMax = None  # Upper bound of decision variables
        self.PSO_nPop = None  # Population size (swarm size)
        self.PSO_w = None  # Inertia coefficient
        self.PSO_wDamp = None  # Damping ratio of inertia coefficient
        self.PSO_c1 = None  # Personal acceleration coefficient
        self.PSO_c2 = None  # Social acceleration coefficient
        self.PSO_a = None  # Additional randomization of a-th particle in swarm
        self.PSO_b = None  # Additional randomization of all particles every b-th iteration
        
        self.particleAlg = None  # Instance of the particle used in algorithm
        self.particleCalc = None  # Instance of the particle used in calculations
        self.costFunction = None  # Instanse of the Cost Function class
        
        # Results of the search:
        self.result_iteration = None
        self.result_dims = None
        self.result_globalBestCost = None
        self.result_arrayBestCosts = None
        self.result_params = None
        self.result_doSearch = None
        
        self.init_ui()  # Initialize the user interface elements
    
    def init_ui(self):
        """Method for the initialization of the UI"""
        self.setFixedSize(1020, 627)  # Window size
        self.center_window() #  Center the window on desktop
        self.setWindowIcon(QIcon('Resources/icon.png'))
        self.setWindowTitle('Particle finder tool')  # Window title
        
        # Menu and submenu creation 
        mainMenu = self.menuBar() 
        particleMenu = mainMenu.addMenu('Particle') 
        infoMenu = mainMenu.addMenu('Info')  
        # Menu action - save shape
        self.saveShapeAct = QAction(QIcon('Resources/save.png'), 'Save data...', self)
        self.saveShapeAct.setShortcut('Ctrl+S')
        self.saveShapeAct.setFont(QFont('Arial', 11))
        self.saveShapeAct.triggered.connect(self.save_particle_data)
        self.saveShapeAct.setDisabled(True)
        # Menu action - load shape...
        loadShapeAct = QAction(QIcon('Resources/load.png'), 'Load data...', self)
        loadShapeAct.setShortcut('Ctrl+L')
        loadShapeAct.setFont(QFont('Arial', 11))
        loadShapeAct.triggered.connect(self.load_particle_data)
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
        
        # Add actions to menu: Particle -> ...
        particleMenu.addAction(self.saveShapeAct)
        particleMenu.addAction(loadShapeAct)
        
        # Add actions to menu: Info -> ...
        infoMenu.addAction(helpAct)
        infoMenu.addAction(aboutAct)
        
        # Labels (initial properties)
        self.lbl_titleInitParams = QLabel('Initial parameters:', self)
        self.lbl_titleInitParams.setGeometry(20, 30, 220, 20)
        self.lbl_titleInitParams.setFont(QFont('Arial', 11, weight=QFont.Bold))
        
        # Labels (dimensions and scale)
        self.lbl_titleDims = QLabel('Particle shape and dimensions:', self)
        self.lbl_titleDims.setGeometry(310, 30, 220, 20)
        self.lbl_titleDims.setFont(QFont('Arial', 11, weight=QFont.Bold))
        
        # Labels (Particle properties)
        self.lbl_titleParams = QLabel('Particle parameters:', self)
        self.lbl_titleParams.setGeometry(720, 30, 220, 20)
        self.lbl_titleParams.setFont(QFont('Arial', 11, weight=QFont.Bold))
        
        # Labels (Search algorithms)
        self.lbl_searchAlg = QLabel('Search algorithm:', self)
        self.lbl_searchAlg.setGeometry(20, 193, 220, 20)
        self.lbl_searchAlg.setFont(QFont('Arial', 11, weight=QFont.Bold))
        
        # Create the "initial properties" labels, edits and units:
        dct = {
            'init_CEDiameter':   {'label': 'CE Diameter:',
                                  'unit' : '[\u03BCm]'},
            'init_circularity':  {'label': 'Circularity:', 
                                  'unit' : '[-]'},
            'init_convexity':    {'label': 'Convexity:',
                                  'unit' : '[-]'},
            'init_elongation':   {'label': 'Elongation:',
                                  'unit' : '[-]'}}
            
        self.initParamsLabels = {} # Dictionary with initial parameters labels
        self.initParamsEdits = {}  # Dictionary with initial parameters edits
        self.initParamsUnits = {}  # Dictionary with initial parameters units
        y = 60
        for item in dct:
            self.initParamsLabels[item] = QLabel(dct[item]['label'], self)
            self.initParamsLabels[item].setAlignment(Qt.AlignLeft)
            self.initParamsLabels[item].setGeometry(20, y, 103, 21)
            self.initParamsLabels[item].setFont(QFont('Arial', 11))
            
            self.initParamsEdits[item] = AdvancedQLineEdit(self)
            self.initParamsEdits[item].setAlignment(Qt.AlignRight)
            self.initParamsEdits[item].setGeometry(123, y, 90, 21)
            self.initParamsEdits[item].setFont(QFont('Arial', 11))
            
            self.initParamsUnits[item] = QLabel(dct[item]['unit'], self)
            self.initParamsUnits[item].setAlignment(Qt.AlignLeft)
            self.initParamsUnits[item].setGeometry(230, y, 130, 21)
            self.initParamsUnits[item].setFont(QFont('Arial', 11))   
            y += 23
        
        # Check for entering only numbers to the edits
        self.initParamsEdits['init_CEDiameter'].editingFinished.connect(
                partial(self.update_initParams,  'init_CEDiameter'))
        self.initParamsEdits['init_circularity'].editingFinished.connect(
                partial(self.update_initParams, 'init_circularity'))
        self.initParamsEdits['init_convexity'].editingFinished.connect(
                partial(self.update_initParams, 'init_convexity'))
        self.initParamsEdits['init_elongation'].editingFinished.connect(
                partial(self.update_initParams, 'init_elongation'))
        
        # Block with axes number changer
        self.lbl_axesNum = QLabel('Axes number:', self)
        self.lbl_axesNum.setAlignment(Qt.AlignLeft)
        self.lbl_axesNum.setGeometry(20, 152, 95, 21)
        self.lbl_axesNum.setFont(QFont('Arial', 11))
        
        self.spb_axesNum = AdvancedQSpinBox(self)
        self.spb_axesNum.setAlignment(Qt.AlignRight)
        self.spb_axesNum.setGeometry(123, 152, 55, 21)
        self.spb_axesNum.setFont(QFont('Arial', 11))
        self.spb_axesNum.setRange(3, 32)
        self.spb_axesNum.valueChanged.connect(self.val_changed_spb_axesNum)
        
        self.btn_resetAxesNum = QPushButton(self)
        self.btn_resetAxesNum.setGeometry(193, 152, 21, 21)
        self.btn_resetAxesNum.setIcon(QIcon(QPixmap('./Resources/arrow.png')))
        self.btn_resetAxesNum.clicked.connect(self.reset_axesNum)
        
        # Label of search algorithm
        self.lbl_algorithmName = QLabel('Particle swarm optimization', self)
        self.lbl_algorithmName.setAlignment(Qt.AlignLeft)
        self.lbl_algorithmName.setGeometry(20, 216, 200, 21)
        self.lbl_algorithmName.setFont(QFont('Arial', 11))
        
        # Buttons to open the searching algorithm settings
        self.btn_PSOAlg_set = QPushButton(self)
        self.btn_PSOAlg_set.setGeometry(230, 216, 21, 21)
        self.btn_PSOAlg_set.setIcon(QIcon(QPixmap('./Resources/settings.png')))
        self.btn_PSOAlg_set.clicked.connect(self.open_PSOAlg_settings)             
      
        # Algorithms iteration and precision limits
        self.chb_iterLimit = QCheckBox('Use iterations limit:', self)
        self.chb_iterLimit.setGeometry(20, 262, 200, 21)
        self.chb_iterLimit.setFont(QFont('Arial', 11))
        self.chb_iterLimit.clicked.connect(self.chb_iterLimit_clicked)
        
        self.spb_iterLimit = AdvancedQSpinBox(self)
        self.spb_iterLimit.setAlignment(Qt.AlignRight)
        self.spb_iterLimit.setGeometry(175, 262, 75, 21)
        self.spb_iterLimit.setFont(QFont('Arial', 11))
        self.spb_iterLimit.setRange(1, 10000)
        self.spb_iterLimit.valueChanged.connect(self.val_changed_spb_iterLimit)
              
        self.chb_precisionLimit = QCheckBox('Use precision limit:', self)
        self.chb_precisionLimit.setGeometry(20, 285, 200, 21)
        self.chb_precisionLimit.setFont(QFont('Arial', 11))
        self.chb_precisionLimit.clicked.connect(self.chb_precisionLimit_clicked)
        
        self.edt_precisionLimit = AdvancedQLineEdit(self)
        self.edt_precisionLimit.setAlignment(Qt.AlignRight)
        self.edt_precisionLimit.setGeometry(175, 285, 75, 21)
        self.edt_precisionLimit.setFont(QFont('Arial', 11))
        self.edt_precisionLimit.editingFinished.connect(self.update_precisionLimit)
          
        # Elements for rendering and logging section
        self.chb_visualIter = QCheckBox('Visualize each iteration', self)
        self.chb_visualIter.setGeometry(20, 331, 200, 21)
        self.chb_visualIter.setFont(QFont('Arial', 11))
        self.chb_visualIter.clicked.connect(self.chb_visualIter_clicked)
        
        self.chb_loglIter = QCheckBox('Write log each iteration', self)
        self.chb_loglIter.setGeometry(20, 354, 200, 21)
        self.chb_loglIter.setFont(QFont('Arial', 11))
        self.chb_loglIter.clicked.connect(self.chb_loglIter_clicked)
        
        self.chb_errorPlot = QCheckBox('Show plot with error evolution', self)
        self.chb_errorPlot.setGeometry(20, 377, 220, 21)
        self.chb_errorPlot.setFont(QFont('Arial', 11))
        self.chb_errorPlot.clicked.connect(self.chb_errorPlot_clicked)
        
        # Real dimension of the particle 
        self.lbl_realWidth = QLabel('Dimension:', self)
        self.lbl_realWidth.setAlignment(Qt.AlignRight)
        self.lbl_realWidth.setGeometry(340, 446, 130, 21)
        self.lbl_realWidth.setFont(QFont('Arial', 11))
        
        self.edt_realWidth = AdvancedQLineEdit(self)
        self.edt_realWidth.setAlignment(Qt.AlignRight)
        self.edt_realWidth.setGeometry(480, 446, 70, 21)
        self.edt_realWidth.setFont(QFont('Arial', 11))
        self.edt_realWidth.set_readOnly(True)
        
        self.lbl_realWidthUnit = QLabel('[\u03BCm]', self)
        self.lbl_realWidthUnit.setAlignment(Qt.AlignLeft)
        self.lbl_realWidthUnit.setGeometry(562, 446, 100, 21)
        self.lbl_realWidthUnit.setFont(QFont('Arial', 11))
        
        # Create the " particle parameters" labels, edits and units:
        dct = {
            'areaPixels':    {'label': 'Particle Area:',
                              'unit' : '[pix]'},
            'areaUm2':       {'label': 'Particle Area:',
                              'unit' : '[\u03BCm\u00B2]'},
            'aspectRatio':   {'label': 'Aspect Ratio:',
                              'unit' : '[-]'},
            'CEDiameter':   {'label': 'CE Diameter:',
                              'unit' : '[\u03BCm]'},
            'centreXPos':    {'label': 'Centre X Position:',
                              'unit' : '[pix]'},
            'centreYPos':    {'label': 'Centre Y Position:',
                              'unit' : '[pix]'},
            'circularity':   {'label': 'Circularity:',
                              'unit' : '[-]'},
            'convexity':     {'label': 'Convexity:',
                              'unit' : '[-]'},
            'elongation':    {'label': 'Elongation:',
                              'unit' : '[-]'},
            'HSCircularity': {'label': 'HS Circularity:',
                              'unit' : '[-]'},
            'length':        {'label': 'Length:',
                              'unit' : '[\u03BCm]'},
            'majorAxisDeg':     {'label': 'Major Axis:',
                              'unit' : '[\u00B0]'},
            'maxDistance':   {'label': 'Max. Distance:',
                              'unit' : '[\u03BCm]'},
            'perimeter':     {'label': 'Perimeter:',
                              'unit' : '[\u03BCm]'},
            'SEVolume':      {'label': 'SE Volume:',
                              'unit' : '[\u03BCm\u00B3]'},
            'solidity':      {'label': 'Solidity:',
                              'unit' : '[-]'},
            'width':         {'label': 'Width:',
                              'unit' : '[\u03BCm]'}}

        self.paramsLabels = {}  # Dictionary with parameters labels
        self.paramsEdits = {}  # Dictionary with parameters edits
        self.paramsUnits = {}  # Dictionary with parameters units
        y = 60
        for item in dct:
            self.paramsLabels[item] = QLabel(dct[item]['label'], self)
            self.paramsLabels[item].setAlignment(Qt.AlignLeft)
            self.paramsLabels[item].setGeometry(720, y, 130, 21)
            self.paramsLabels[item].setFont(QFont('Arial', 11))
            
            self.paramsEdits[item] = AdvancedQLineEdit(self)
            self.paramsEdits[item].setAlignment(Qt.AlignRight)
            self.paramsEdits[item].setGeometry(850, y, 90, 21)
            self.paramsEdits[item].setFont(QFont('Arial', 11))
            self.paramsEdits[item].set_readOnly(True)
            
            self.paramsUnits[item] = QLabel(dct[item]['unit'], self)
            self.paramsUnits[item].setAlignment(Qt.AlignLeft)
            self.paramsUnits[item].setGeometry(955, y, 130, 21)
            self.paramsUnits[item].setFont(QFont('Arial', 11))   
            y += 23
        
        # The most important parameters filled with red gray color
        self.paramsEdits['CEDiameter'].set_red_bkg()
        self.paramsEdits['circularity'].set_red_bkg()
        self.paramsEdits['convexity'].set_red_bkg()
        self.paramsEdits['elongation'].set_red_bkg()
        
        # Label with dimension arrow <----->
        self.lbl_arrow = QLabel(self)
        self.lbl_arrow.setGeometry(310, 424, 360, 20)
        self.lbl_arrow.setPixmap(QPixmap('Resources/dimension_arrow.png'))
        
        # Buttons for start and stop searching the shape
        self.btn_searchShape = QPushButton('Search', self)
        self.btn_searchShape.setGeometry(20, 410, 70, 27)
        self.btn_searchShape.clicked.connect(self.find_shape_do_before_search)
        
        self.btn_stopSearch = QPushButton('Stop', self)
        self.btn_stopSearch.setGeometry(100, 410, 70, 27)
        self.btn_stopSearch.clicked.connect(self.stop_search)

        # Lamps indicator
        self.lbl_lamp = QLabel(self)
        self.lbl_lamp.setGeometry(180, 410, 25, 25)
        self.lbl_lamp.setPixmap(QPixmap('Resources/lamp_off.png'))
        
        # Terminal text edit
        self.terminal = QPlainTextEdit(self)
        self.terminal.setGeometry(20, 479, 980, 128)
        self.terminal.setFont(QFont('Arial', 9)) 
        self.terminal.setReadOnly(True)
        
        self.put_default_parameters()
        
        # Label with particle image
        self.lbl_particlePicture = ImageLabel(self, self.nDim, 5, False)
        self.lbl_particlePicture.bkgTransp = 255  # Make background white color 
        self.lbl_particlePicture.setGeometry(self.partPictXPos, self.partPictYPos, 360, 360)
        
        self.show()
        self.threadpool = QThreadPool()
    
    def put_default_parameters(self):
        self.init_CEDiameter = 193.44
        self.initParamsEdits['init_CEDiameter'].setText('{0:.2f}'.format(self.init_CEDiameter))
        self.init_circularity = 0.635
        self.initParamsEdits['init_circularity'].setText('{0:.3f}'.format(self.init_circularity))
        self.init_convexity = 0.852
        self.initParamsEdits['init_convexity'].setText('{0:.3f}'.format(self.init_convexity))
        self.init_elongation = 0.099
        self.initParamsEdits['init_elongation'].setText('{0:.3f}'.format(self.init_elongation))
        self.nDim = 12
        self.spb_axesNum.set_value(self.nDim)
        self.iterLimit = 1000
        self.useIterLimit = True
        self.chb_iterLimit.setChecked(True)
        self.spb_iterLimit.set_value(self.iterLimit)
        self.precisionLimit = 0.01
        self.usePrecisionLimit = True
        self.chb_precisionLimit.setChecked(True)
        self.edt_precisionLimit.setText('{0:.6f}'.format(self.precisionLimit))
        self.useVisualIter = True
        self.chb_visualIter.setChecked(True)
        self.useLoglIter = True
        self.chb_loglIter.setChecked(True)
        self.showErrorPlot = True
        self.chb_errorPlot.setChecked(True)
        self.edt_realWidth.setText('?')
        for item in self.paramsEdits:
            self.paramsEdits[item].setText('?')
        self.PSO_nVar = self.nDim
        self.PSO_varMin = 0.0
        self.PSO_varMax = 1.0
        self.PSO_nPop = 5
        self.PSO_w = 1.0  #1
        self.PSO_wDamp = 0.99  #0.99
        self.PSO_c1 = 2.0
        self.PSO_c2 = 2.0
        self.PSO_a = 5
        self.PSO_b = 200
        
    def update_initParams(self, fieldName):
        """Method for update the values in the edit fields with initial parameters"""   
        # Save old value
        if fieldName == 'init_CEDiameter':
            oldValue = self.init_CEDiameter
            message = 'CE diameter'
        elif fieldName == 'init_circularity':
            oldValue = self.init_circularity
            message = 'Circularity'
        elif fieldName == 'init_convexity':
            oldValue = self.init_convexity
            message = 'Convexity'
        elif fieldName == 'init_elongation':
            oldValue = self.init_elongation
            message = 'Elongation'      
        
        # Treat the new value
        newValueStr = self.initParamsEdits[fieldName].text()  # Get the raw string
        newValueStr = newValueStr.replace(',','.')  # Symbol ',' is also available
        error = False
        try:
            newValue = float(newValueStr)
        except:
            error = True   
        
        self.initParamsEdits[fieldName].setText('{0}'.format(oldValue))
        
        # Treat the possible error
        if error:
            text = '{0} should be a number!'.format(message)
            self.show_error_window(text)
        else:
            self.initParamsEdits[fieldName].setText('{0}'.format(newValue))
            if fieldName == 'init_CEDiameter': self.init_CEDiameter = newValue
            if fieldName == 'init_circularity': self.init_circularity = newValue
            if fieldName == 'init_convexity': self.init_convexity = newValue
            if fieldName == 'init_elongation': self.init_elongation = newValue
               
    def chb_iterLimit_clicked(self):
        """Method to define weather use iterLimit or not"""
        if self.chb_iterLimit.isChecked():
            self.useIterLimit = True
        else:
            self.useIterLimit = False 
    
    def val_changed_spb_iterLimit(self):
        """Method for update the value in the spin box with iterLimit"""
        self.iterLimit = self.spb_iterLimit.value()
    
    def chb_precisionLimit_clicked(self):
        """Method to define weather use precisionLimit or not"""
        if self.chb_precisionLimit.isChecked():
            self.usePrecisionLimit = True
        else:
            self.usePrecisionLimit = False    

    def update_precisionLimit(self):
        """Method for update the value in the edit field with precisionLimit"""
        # Save old value
        oldValue = self.precisionLimit
        message = 'Precision limit'
        
        # Treat the new value
        newValueStr = self.edt_precisionLimit.text()  # Get the raw string
        newValueStr = newValueStr.replace(',','.')  # Symbol ',' is also available
        error = False
        try:
            newValue = float(newValueStr)
        except:
            error = True
        self.edt_precisionLimit.setText('{0:.6f}'.format(oldValue))
        # Treat the possible error
        if error:
            text = '{0} should be a number!'.format(message)
            self.show_error_window(text)
        else:
            self.edt_precisionLimit.setText('{0:.6f}'.format(newValue))
            self.precisionLimit = newValue   
    
    def chb_visualIter_clicked(self):
        """Method to define weather show particle shape every iteration or not"""
        if self.chb_visualIter.isChecked():
            self.useVisualIter = True
        else:
            self.useVisualIter = False
    
    def chb_loglIter_clicked(self):
        """Method to define weather show log of every iteration or not"""
        if self.chb_loglIter.isChecked():
            self.useLoglIter = True
        else:
            self.useLoglIter = False
        
    def chb_errorPlot_clicked(self):
        """Method to define weather show the error plot or not"""
        if self.chb_errorPlot.isChecked():
            self.showErrorPlot = True
        else:
            self.showErrorPlot = False
    
    def show_error_window(self, text):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(text)
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_() 
    
    def val_changed_spb_axesNum(self):
        self.nDim = self.spb_axesNum.value()
        self.PSO_nVar = self.nDim
        self.lbl_particlePicture.set_N(self.nDim)
        # Put some default values to the edit boxes
        self.edt_realWidth.setText('?')
        for item in self.paramsEdits:
            self.paramsEdits[item].setText('?')    
        self.update()        

    def reset_axesNum(self):
        self.nDim = 12
        self.spb_axesNum.setValue(self.nDim) 
        
    def write_to_terminal(self, text):
        dateTime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        self.terminal.moveCursor(QTextCursor.Start, 0);
        self.terminal.insertPlainText('{0}:   {1}\n'.format(dateTime, text))
      
    def open_PSOAlg_settings(self):
        """Method to open window with PSO algorithm settings"""
        self.settingsWindow = PSOSettingsWindow(self)
    
    def set_PSO_settings_data(self, settingsData):
        """Method for save setings data comming from settings window"""
        # Update the PSO algorithm parameters
        self.PSO_nPop = settingsData['PSO_nPop']
        self.PSO_w = settingsData['PSO_w']
        self.PSO_wDamp = settingsData['PSO_wDamp']
        self.PSO_c1 = settingsData['PSO_c1']
        self.PSO_c2 = settingsData['PSO_c2']
        self.PSO_a = settingsData['PSO_a']
        self.PSO_b = settingsData['PSO_b']
    
    def find_shape_do_before_search(self):
        """Preparation method for start searching the shape"""
        # Change the state of the green lamp
        if self.lamp:
            self.lbl_lamp.setPixmap(QPixmap('Resources/lamp_off.png'))
            self.lamp = False
        else:
            self.lbl_lamp.setPixmap(QPixmap('Resources/lamp_on.png'))
            self.lamp = True
            
        # Remove values from the parameters edits
        self.edt_realWidth.setText('?')
        for item in self.paramsEdits:
            self.paramsEdits[item].setText('?')
        
        # Disable some elements on the window during the search
        self.enable_elemets(False)
        
        # Enable menu action to save the data
        self.saveShapeAct.setEnabled(True)
        
        # Find shape with workers (using python or cython)
        if self.useVisualIter or self.useLoglIter:
            # Find the shape with python (slower, but with loging the progress)
            worker = Worker(self.find_shape_main)
            worker.signals.progress.connect(self.update_shape_and_parameters)
            worker.signals.finished.connect(self.find_shape_do_after_search)
            self.threadpool.start(worker)
        else:
            # Find the shape with dll (faster, but without loging the progress)
            worker = Worker(self.find_shape_main_dll)
            worker.signals.progress.connect(self.update_shape_and_parameters)
            worker.signals.finished.connect(self.find_shape_do_after_search)
            self.threadpool.start(worker)  
    
    def find_shape_main(self, progress_callback):
        """Main method to find the shape of the particle with python code"""     
        self.algStartTime = time()  # Start time
        # Define new instance of PSO searching algorithm
        self.psoAlg_py = PSOAlg_py(
            progress_callback,
            init_circularity = self.init_circularity,
            init_convexity = self.init_convexity,
            init_elongation = self.init_elongation,
            nVar = self.PSO_nVar,
            varMin = self.PSO_varMin,
            varMax = self.PSO_varMax,
            useIterLimit = self.useIterLimit,
            iterLimit = self.iterLimit,
            usePrecisionLimit = self.usePrecisionLimit,
            precisionLimit = self.precisionLimit,
            showErrorPlot = self.showErrorPlot,
            nPop = self.PSO_nPop,
            w = self.PSO_w,
            wDamp = self.PSO_wDamp,
            c1 = self.PSO_c1,
            c2 = self.PSO_c2,
            a = self.PSO_a,
            b = self.PSO_b)    
        
        # Run search and recieve the results
        self.psoAlg_py.run_search()        
    
    def find_shape_main_dll(self, progress_callback):
        """Main method to find the shape of the particle with cython code"""
        self.algStartTime = time()  # Start time
        
        # Execute the function for the search   
        results = self.psoAlg_dll.run_search(
            init_circularity = self.init_circularity,
            init_convexity = self.init_convexity,
            init_elongation = self.init_elongation,
            nVar = self.PSO_nVar,
            varMin = self.PSO_varMin,
            varMax = self.PSO_varMax,
            useIterLimit = self.useIterLimit,
            iterLimit = self.iterLimit,
            usePrecisionLimit = self.usePrecisionLimit,
            precisionLimit = self.precisionLimit,
            showErrorPlot = self.showErrorPlot,
            nPop = self.PSO_nPop,
            w = self.PSO_w,
            wDamp = self.PSO_wDamp,
            c1 = self.PSO_c1,
            c2 = self.PSO_c2,
            a = self.PSO_a,
            b = self.PSO_b)
        
        results['doSearch'] = False
        self.update_shape_and_parameters(results)               
        
    def update_shape_and_parameters(self, data):
        """Method to update the shape and particle parameters
           Data is a dictionary with parameters, shape etc."""
        
        self.result_iteration = data['iteration']
        self.result_dims = data['globalBestPosition']
        self.result_globalBestCost = data['globalBestCost']
        self.result_arrayBestCosts = data['arrayBestCosts']
        self.result_doSearch = data['doSearch']
        
        # Determine the image scale
        self.result_params = self.particle.get_particle_parameters(1.0, self.result_dims, self.nDim)
        areaPixels = self.result_params['areaPixels']
        imgScale = self.init_CEDiameter * m.sqrt(m.pi / (areaPixels * 4))
        self.result_params = self.particle.get_particle_parameters(imgScale, self.result_dims, self.nDim)

        if self.useVisualIter or (not self.result_doSearch):
            # Draw the particle
            self.lbl_particlePicture.set_dimsValues(self.result_dims)
            self.lbl_particlePicture.drawParticle = True
            
            # Data to create the blue circle with CE Doameter
            dataCirc = (self.result_params['centreXPos'],
                        self.result_params['centreYPos'],
                        self.result_params['CEDiameter']/self.result_params['imgScale']) # To scale on the image
            majorAxisPoints = self.result_params['majorAxisPoints']
            minorAxisPoints = self.result_params['minorAxisPoints']

            # Draw the blue circle 
            self.lbl_particlePicture.dataCirc = dataCirc
            self.lbl_particlePicture.majorAxisPoints = majorAxisPoints
            self.lbl_particlePicture.minorAxisPoints = minorAxisPoints
            self.lbl_particlePicture.drawBlueCircle = True
            self.update()  
            
            # Update the fields with parameters
            self.paramsEdits['areaPixels'].setText('{0:d}'.format(int(self.result_params['areaPixels'])))
            self.paramsEdits['areaUm2'].setText('{0:.2f}'.format(self.result_params['areaUm2']))
            self.paramsEdits['CEDiameter'].setText('{0:.2f}'.format(self.result_params['CEDiameter']))
            self.paramsEdits['centreXPos'].setText('{0:d}'.format(int(self.result_params['centreXPos'])))
            self.paramsEdits['centreYPos'].setText('{0:d}'.format(int(self.result_params['centreYPos'])))
            self.paramsEdits['perimeter'].setText('{0:.2f}'.format(self.result_params['perimeter']))
            self.paramsEdits['circularity'].setText('{0:.3f}'.format(self.result_params['circularity']))
            self.paramsEdits['convexity'].setText('{0:.3f}'.format(self.result_params['convexity']))
            self.paramsEdits['solidity'].setText('{0:.3f}'.format(self.result_params['solidity']))
            self.paramsEdits['HSCircularity'].setText('{0:.3f}'.format(self.result_params['HSCircularity']))
            self.paramsEdits['SEVolume'].setText('{0:.2f}'.format(self.result_params['SEVolume']))
            self.paramsEdits['majorAxisDeg'].setText('{0:.2f}'.format(self.result_params['majorAxisDeg']))
            self.paramsEdits['length'].setText('{0:.2f}'.format(self.result_params['length']))
            self.paramsEdits['width'].setText('{0:.2f}'.format(self.result_params['width']))
            self.paramsEdits['aspectRatio'].setText('{0:.3f}'.format(self.result_params['aspectRatio']))
            self.paramsEdits['elongation'].setText('{0:.3f}'.format(self.result_params['elongation']))
            self.paramsEdits['maxDistance'].setText('{0:.2f}'.format(self.result_params['maxDistance']))  
            self.edt_realWidth.setText('{0:.2f}'.format(self.result_params['realWidth']))
        
        if self.useLoglIter or (not self.result_doSearch):
            text = 'Iteration: {0:d};   RMSE: {1:.6f}'.format(self.result_iteration, self.result_globalBestCost)
            self.write_to_terminal(text)
        
    def find_shape_do_after_search(self):
        # Change the state of the green lamp
        if self.lamp:
            self.lbl_lamp.setPixmap(QPixmap('Resources/lamp_off.png'))
            self.lamp = False
        else:
            self.lbl_lamp.setPixmap(QPixmap('Resources/lamp_on.png'))
            self.lamp = True
        
        # Calculate the total searching time
        self.algTime = time() - self.algStartTime
        
        # Write to the terminal the important information
        self.write_to_terminal("Searching is finished! Total searching time: {0:.2f} [s]".format(
                self.algTime))
        
        # Enable elements
        self.enable_elemets(True)
        
        # Show plot
        if self.showErrorPlot:
            self.make_plot()       
    
    def make_plot(self):
        """Method to create the error development plot"""
        plt.figure(1)
        
        # If solution was found faster than iterLimit count zeros in the array should
        # not be printed
        data = []
        for i in self.result_arrayBestCosts:
            if (i == 0):
                break
            else:
                data.append(i)
        
        plt.semilogy(data)
        plt.xlabel('Iterations')
        plt.ylabel('Best cost')
        plt.grid(True)
        plt.show()
 
    def enable_elemets(self, flag):
        self.initParamsEdits['init_CEDiameter'].setEnabled(flag)
        self.initParamsEdits['init_circularity'].setEnabled(flag)
        self.initParamsEdits['init_convexity'].setEnabled(flag)
        self.initParamsEdits['init_elongation'].setEnabled(flag)
        self.spb_axesNum.setEnabled(flag)
        self.btn_resetAxesNum.setEnabled(flag)
        self.btn_PSOAlg_set.setEnabled(flag)
        self.chb_iterLimit.setEnabled(flag)
        self.spb_iterLimit.setEnabled(flag)
        self.chb_precisionLimit.setEnabled(flag)
        self.edt_precisionLimit.setEnabled(flag)
        self.chb_visualIter.setEnabled(flag)
        self.chb_loglIter.setEnabled(flag)
        self.chb_errorPlot.setEnabled(flag)
        self.btn_searchShape.setEnabled(flag)
    
    def stop_search(self):
        self.psoAlg.doSearch = False
        
    def save_particle_data(self):
        """Method for saving the particle shape in json format in txt file"""
        data = {}
        data['nDim'] = self.nDim
        data['imgScale'] = self.particleCalc.imgScale
        data['imgWidth'] = self.particleCalc.imgWidth
        data['realWidth'] = self.particleCalc.realWidth
        data['dimsValues'] = self.particleCalc.dimsValues        
        # Important particle parameters
        data['CEDiameter'] = self.result_params['CEDiameter']
        data['circularity'] = self.result_params['circularity']
        data['convexity'] = self.result_params['convexity']
        data['elongation'] = self.result_params['elongation'] 
        
        name = QFileDialog.getSaveFileName(self, 'Save data', 'Saves/untitled.txt', 'Text files (*.txt)')[0]
        
        if name != '': 
            with open(name, 'w') as outfile:  
                json.dump(data, outfile)
                
        self.write_to_terminal('File succesfully saved!')
    
    def load_particle_data(self):
        name = QFileDialog.getOpenFileName(self, 'Load data', 'Saves/', 'Text files (*.txt)')[0]
        if name != '':
            with open(name) as json_file:
                data = json.load(json_file)
                
                # Load the data to the initial values          
                self.init_CEDiameter = data['CEDiameter']
                self.initParamsEdits['init_CEDiameter'].setText('{0:.2f}'.format(data['CEDiameter']))
                self.init_circularity = data['circularity']
                self.initParamsEdits['init_circularity'].setText('{0:.3f}'.format(data['circularity']))
                self.init_convexity = data['convexity']
                self.initParamsEdits['init_convexity'].setText('{0:.3f}'.format(data['convexity']))
                self.init_elongation = data['elongation']
                self.initParamsEdits['init_elongation'].setText('{0:.3f}'.format(data['elongation']))
                self.nDim = data['nDim']
                self.spb_axesNum.set_value(self.nDim)
                        
                # Remove values from the parameters edits
                self.edt_realWidth.setText('?')
                for item in self.paramsEdits:
                    self.paramsEdits[item].setText('?')
                    
                # Remove the shape of the particle
                self.lbl_particlePicture.drawParticle = False
                self.lbl_particlePicture.drawBlueCircle = False
                self.update() 
                
    def show_help(self):
        path = os.getcwd() + '\Help\Help_ParticleFinder.pdf'
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
        mainWindow = ParticleFinder()
        app.exec_()
    run_app()
    #sys.exit(app.exec_())