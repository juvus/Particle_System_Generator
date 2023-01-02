#==========================================================================================
# Project:        Particle Tester module
# Description:    Program for testing the different particle shapes
# Author:         Dmitry Safonov (Dmitry.Safonov@lut.fi)
# Organization:   Lappeenranta University of Technology (LUT)
#                 Solid/Liquid Separation Research Group            
# Last edited:    24.12.2020
#==========================================================================================

import sys
import os
from PyQt5.QtWidgets import (QMainWindow, QApplication, QDesktopWidget, QAction, QMenu, 
                             QLabel, QPushButton, QMessageBox, QFileDialog)
from PyQt5.QtGui import QIcon, QFont, QPainter, QPixmap, QColor
from PyQt5.QtCore import Qt
from PIL.ImageQt import ImageQt
import json
import random as rnd
rnd.seed()

# Program modules:
from Modules.Particle import Particle
from Modules.SlidersField import SlidersField
from Modules.SinglePicture import SinglePicture
from Modules.About import About
from Modules.RealImageLoader import RealImageLoader
from Modules.PTesterSettingsWindow import PTesterSettingsWindow
from Modules.AdvancedQSpinBox import AdvancedQSpinBox
from Modules.AdvancedQLineEdit import AdvancedQLineEdit

# Main window class     
class ParticleTester(QMainWindow):  
    """Class of a main window of the tool"""
    def __init__(self):
        """Constructor of the class"""
        super().__init__()     
        self.nDim = 12  # Number of particle dimensions
        self.dimsValues = [0.5] * self.nDim  # dimension values
        self.dimsCoord = []  # verticies coordinates
        self.imgScale = 1.0  # Image scale [um/pix]
        self.imgWidth = 360  # Image width [pix]
        self.realWidth = 360  # Particle real width [um] 
        
        self.slidersFieldXPos = 20  # X pos of sliders field top left corner
        self.slidersFieldYPos = 60  # Y pos of sliders field top left corner
        
        self.imageLoader = None  # Window for loading the real image
        self.init_ui()  # Initialize the user interface elements
        self.realImageData = {}  # Real particle image data dictionary
        self.picWidthHeight = 1200  # Width and Height of the particle single picture
        self.picParticleColor = [0, 0, 0]  # Color of the particle on the single picture
        self.picBkgColor = [197, 197, 197]  # Color of the background on the single picture
        self.picShowScale = True  # Scale visibility on the single picture 
        self.particleData = {}  # Dict with calculated particle parameters
        self.particle = Particle()  # Construct particle for determination of its parameters
        
        self.new_particle_data()  # Make new particle and slider field
        self.put_default_data()  # put the default data to all elements     
    
    def init_ui(self):
        """Method for the initialization of the UI"""
        self.setFixedSize(730, 535)  # Window size
        self.center_window() #  Center the window on desktop
        self.setWindowIcon(QIcon('Resources/icon.png'))
        self.setWindowTitle('Particle tester tool')  # Window title
        # Menu and submenu creation 
        mainMenu = self.menuBar() 
        particleMenu = mainMenu.addMenu('Particle') 
        infoMenu = mainMenu.addMenu('Info')
        # Menu action - new default particle
        newAct = QAction(QIcon('Resources/new_particle.png'), 'New', self)
        newAct.setShortcut('Ctrl+N')
        newAct.setFont(QFont('Arial', 11))
        newAct.triggered.connect(self.new_particle_data)
        # Menu action - randomize particle
        randAct = QAction(QIcon('Resources/rnd_particle.png'), 'Randomize', self)
        randAct.setShortcut('Ctrl+R')
        randAct.setFont(QFont('Arial', 11))
        randAct.triggered.connect(self.randomize_particle)
        # Menu action - save shape
        saveShapeAct = QAction(QIcon('Resources/save.png'), 'Save data...', self)
        saveShapeAct.setShortcut('Ctrl+S')
        saveShapeAct.setFont(QFont('Arial', 11))
        saveShapeAct.triggered.connect(self.save_particle_data)
        # Menu action - load shape...
        loadShapeAct = QAction(QIcon('Resources/load.png'), 'Load data...', self)
        loadShapeAct.setShortcut('Ctrl+L')
        loadShapeAct.setFont(QFont('Arial', 11))
        loadShapeAct.triggered.connect(self.load_particle_data)
        # Submenu - Particle -> Picture
        pictureSubMenu = QMenu('Picture', self)
        pictureSubMenu.setFont(QFont('Arial', 11))
        pictureSubMenu.setIcon(QIcon('Resources/particle_picture.png'))
        # Submenu - Particle -> Real image
        realImageSubMenu = QMenu('Real Image', self)
        realImageSubMenu.setFont(QFont('Arial', 11))
        realImageSubMenu.setIcon(QIcon('Resources/real_image.png'))
        # Menu action - Particle -> Picture -> Show
        pictureShowAct = QAction(QIcon('Resources/show.png'), 'Show', self)
        pictureShowAct.setFont(QFont('Arial', 11))
        pictureShowAct.triggered.connect(self.show_picture)
        # Menu action - Particle -> Picture -> Save...
        pictureSaveAct = QAction(QIcon('Resources/save.png'), 'Save...', self)
        pictureSaveAct.setFont(QFont('Arial', 11))
        pictureSaveAct.triggered.connect(self.save_picture)
        # Menu action - Particle -> Real image -> Load...
        imageLoadRealAct = QAction(QIcon('Resources/load.png'), 'Load...', self)
        imageLoadRealAct.setFont(QFont('Arial', 11))
        imageLoadRealAct.triggered.connect(self.load_real_image)
        # Menu action - Particle -> Real image -> Clear
        self.imageClearRealAct = QAction(QIcon('Resources/clear.png'), 'Clear', self)
        self.imageClearRealAct.setFont(QFont('Arial', 11))
        self.imageClearRealAct.triggered.connect(self.clear_real_image)
        self.imageClearRealAct.setDisabled(True)
        # Menu action - Particle -> Settings...
        settingsAct = QAction(QIcon('Resources/settings.png'), 'Settings...', self)
        settingsAct.setFont(QFont('Arial', 11))
        settingsAct.triggered.connect(self.open_settings_window)
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
        particleMenu.addAction(newAct)
        particleMenu.addAction(randAct)
        particleMenu.addSeparator()
        particleMenu.addAction(saveShapeAct)
        particleMenu.addAction(loadShapeAct)
        particleMenu.addSeparator()
        particleMenu.addMenu(pictureSubMenu)
        pictureSubMenu.addAction(pictureShowAct)
        pictureSubMenu.addAction(pictureSaveAct)
        particleMenu.addMenu(realImageSubMenu)
        particleMenu.addSeparator()
        particleMenu.addAction(settingsAct)
        
        # Add actions to menu: Particle -> Real Image -> ...
        realImageSubMenu.addAction(imageLoadRealAct)
        realImageSubMenu.addAction(self.imageClearRealAct)
        
        # Add actions to menu: Info -> ...
        infoMenu.addAction(helpAct)
        infoMenu.addAction(aboutAct)
        
        # Labels (dimensions and scale)
        self.lbl_titleDims = QLabel('Particle shape and dimensions:', self)
        self.lbl_titleDims.setGeometry(20, 30, 220, 20)
        self.lbl_titleDims.setFont(QFont('Arial', 11, weight=QFont.Bold))
        
        # Labels (Particle properties)
        self.lbl_titleParams = QLabel('Particle parameters:', self)
        self.lbl_titleParams.setGeometry(430, 30, 220, 20)
        self.lbl_titleParams.setFont(QFont('Arial', 11, weight=QFont.Bold))
        
        # Create the "dimensions" labels, edits and units:
        dct = {
            'imgScale':  {'label': 'Image scale:',
                          'unit' : '[\u03BCm/pix]'},
            'imgWidth':  {'label': 'Dimension (image):', 
                          'unit' : '[pix]'},
            'realWidth': {'label': 'Dimension (real):',
                          'unit' : '[\u03BCm]'}}
        
        self.dimsLabels = {}  # Dictionary with dimensions labels
        self.dimsEdits = {}  # Dictionary with dinensions edits
        self.dimsUnits = {}  # Dictionary with dimensions units
        y = 455
        for item in dct:
            self.dimsLabels[item] = QLabel(dct[item]['label'], self)
            self.dimsLabels[item].setAlignment(Qt.AlignRight)
            self.dimsLabels[item].setGeometry(65, y, 130, 21)
            self.dimsLabels[item].setFont(QFont('Arial', 11))
            
            self.dimsEdits[item] = AdvancedQLineEdit(self)
            self.dimsEdits[item].setAlignment(Qt.AlignRight)
            self.dimsEdits[item].setGeometry(205, y, 70, 21)
            self.dimsEdits[item].setFont(QFont('Arial', 11))
            
            self.dimsUnits[item] = QLabel(dct[item]['unit'], self)
            self.dimsUnits[item].setAlignment(Qt.AlignLeft)
            self.dimsUnits[item].setGeometry(287, y, 100, 21)
            self.dimsUnits[item].setFont(QFont('Arial', 11))   
            y += 23
        
        self.dimsEdits['imgScale'].editingFinished.connect(self.update_real_width)
        self.dimsEdits['realWidth'].editingFinished.connect(self.update_image_scale)
        self.dimsEdits['imgWidth'].set_readOnly(True)
        
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
            'majorAxis':     {'label': 'Major Axis:',
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
            self.paramsLabels[item].setGeometry(430, y, 130, 21)
            self.paramsLabels[item].setFont(QFont('Arial', 11))
            
            self.paramsEdits[item] = AdvancedQLineEdit(self)
            self.paramsEdits[item].setAlignment(Qt.AlignRight)
            self.paramsEdits[item].setGeometry(560, y, 90, 21)
            self.paramsEdits[item].setFont(QFont('Arial', 11))
            self.paramsEdits[item].set_readOnly(True)
            
            self.paramsUnits[item] = QLabel(dct[item]['unit'], self)
            self.paramsUnits[item].setAlignment(Qt.AlignLeft)
            self.paramsUnits[item].setGeometry(665, y, 130, 21)
            self.paramsUnits[item].setFont(QFont('Arial', 11))   
            y += 23
    
        # Label, spinbox and button  for axes number change
        self.lbl_axes_num = QLabel('Axes number:', self)
        self.lbl_axes_num.setAlignment(Qt.AlignLeft)
        self.lbl_axes_num.setGeometry(430, 474, 95, 21)
        self.lbl_axes_num.setFont(QFont('Arial', 11))   
        
        self.spb_axesNum = AdvancedQSpinBox(self)
        self.spb_axesNum.setAlignment(Qt.AlignRight)
        self.spb_axesNum.setGeometry(535, 474, 55, 21)
        self.spb_axesNum.setFont(QFont('Arial', 11))
        self.spb_axesNum.setRange(3, 32)
        self.spb_axesNum.set_value(self.nDim)
        self.spb_axesNum.valueChanged.connect(self.val_changed_spb_axesNum)
        
        self.btn_resetAxesNum = QPushButton(self)
        self.btn_resetAxesNum.setGeometry(600, 474, 21, 21)
        self.btn_resetAxesNum.setIcon(QIcon(QPixmap('./Resources/arrow.png')))
        self.btn_resetAxesNum.clicked.connect(self.reset_axesNum)
        
        # Label with dimension arrow <----->
        self.lbl_arrow = QLabel(self)
        self.lbl_arrow.setGeometry(20, 427, 360, 20)
        self.lbl_arrow.setPixmap(QPixmap('Resources/dimension_arrow.png'))
        
        # Label with real image and sliders
        self.lbl_imageSliders = QLabel(self)
        self.lbl_imageSliders.setGeometry(self.slidersFieldXPos, self.slidersFieldYPos, 360, 360)
    
        self.show()

    def center_window(self):
        """Method for center the main window on the desktop"""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
    def new_particle_data(self):
        """Method for creating new default particle and slider field"""
        self.dimsValues = [0.5] * self.nDim  # default particle dimensions
        self.imgScale = 1.0  # default image scale
        self.realWidth = 360  # default real width    
        self.slidersField = SlidersField(self.imgWidth, self.nDim, self.dimsValues)
        self.update()
        self.update_parameters()  
    
    def save_particle_data(self):
        """Method for saving the particle shape in json format in txt file"""
        data = {}
        data['nDim'] = self.nDim
        data['imgScale'] = self.imgScale
        data['imgWidth'] = self.imgWidth
        data['realWidth'] = self.realWidth
        data['dimsValues'] = self.dimsValues
        # Important particle parameters
        data['CEDiameter'] = self.particleData['CEDiameter'] 
        data['circularity'] = self.particleData['circularity'] 
        data['convexity'] = self.particleData['convexity'] 
        data['elongation'] = self.particleData['elongation']
        
        name = QFileDialog.getSaveFileName(self, 'Save data', 'Saves/untitled.txt', 'Text files (*.txt)')[0]
        
        if name != '': 
            with open(name, 'w') as outfile:  
                json.dump(data, outfile)
    
    def load_particle_data(self):
        name = QFileDialog.getOpenFileName(self, 'Load data', 'Saves/', 'Text files (*.txt)')[0]
        if name != '':
            with open(name) as json_file:
                data = json.load(json_file)
                self.nDim = data['nDim']
                self.imgScale = data['imgScale']
                self.dimsValues = data['dimsValues']
                self.slidersField = SlidersField(self.imgWidth, self.nDim, self.dimsValues)
                # update dimensions fields
                self.dimsEdits['imgScale'].setText('{0:.3f}'.format(self.imgScale))
                self.dimsEdits['imgWidth'].setText('{0:d}'.format(self.imgWidth))
                self.dimsEdits['realWidth'].setText('{0:.3f}'.format(self.realWidth))
                self.update_parameters()  # update particle parameters 
    
    def put_default_data(self):
        self.imgScale = 1.0
        self.dimsEdits['imgScale'].setText('{0:.3f}'.format(self.imgScale))
        self.update_real_width()
        self.dimsEdits['imgWidth'].setText('{0:d}'.format(self.imgWidth))
        self.dimsValues = [0.5] * self.nDim
        self.update_parameters()  # update particle parameters
    
    def update_parameters(self):
        """Method for recalculate and update the particle parameters"""
        
        # Calculation the parameters and coordinates:
        self.particleData = self.particle.get_particle_parameters(self.imgScale, self.dimsValues, self.nDim)
        self.dimsCoord = self.particleData['dimsCoord']
        
        # Save calculated parameters and update the edits:
        self.imgScale = self.particleData['imgScale']
        self.realWidth = self.particleData['realWidth']        
        
        areaPixels = self.particleData['areaPixels']
        self.paramsEdits['areaPixels'].setText('{0:d}'.format(int(areaPixels)))
        
        areaUm2 = self.particleData['areaUm2']
        self.paramsEdits['areaUm2'].setText('{0:.2f}'.format(areaUm2))       
        
        CEDiameter = self.particleData['CEDiameter']
        self.paramsEdits['CEDiameter'].setText('{0:.2f}'.format(CEDiameter))
        
        centreXPos = self.particleData['centreXPos']
        centreYPos = self.particleData['centreYPos']
        self.paramsEdits['centreXPos'].setText('{0:d}'.format(int(centreXPos)))
        self.paramsEdits['centreYPos'].setText('{0:d}'.format(int(centreYPos)))        
        
        perimeter = self.particleData['perimeter']
        self.paramsEdits['perimeter'].setText('{0:.2f}'.format(perimeter))
        
        circularity = self.particleData['circularity']
        self.paramsEdits['circularity'].setText('{0:.3f}'.format(circularity))
        
        convexity = self.particleData['convexity']
        self.paramsEdits['convexity'].setText('{0:.3f}'.format(convexity))
        
        solidity = self.particleData['solidity']
        self.paramsEdits['solidity'].setText('{0:.3f}'.format(solidity))
        
        HSCircularity = self.particleData['HSCircularity']
        self.paramsEdits['HSCircularity'].setText('{0:.3f}'.format(HSCircularity))
        
        SEVolume = self.particleData['SEVolume']
        self.paramsEdits['SEVolume'].setText('{0:.2f}'.format(SEVolume))
        
        majorAxisDeg = self.particleData['majorAxisDeg']
        self.paramsEdits['majorAxis'].setText('{0:.2f}'.format(majorAxisDeg))
        
        length = self.particleData['length']
        self.paramsEdits['length'].setText('{0:.2f}'.format(length))
        
        width = self.particleData['width']
        self.paramsEdits['width'].setText('{0:.2f}'.format(width))
        
        aspectRatio = self.particleData['aspectRatio']
        self.paramsEdits['aspectRatio'].setText('{0:.3f}'.format(aspectRatio))
        
        elongation = self.particleData['elongation']
        self.paramsEdits['elongation'].setText('{0:.3f}'.format(elongation))
        
        maxDistance = self.particleData['maxDistance']
        self.paramsEdits['maxDistance'].setText('{0:.2f}'.format(maxDistance))
        
    def val_changed_spb_axesNum(self):
        """Method for handle the value change of the axesNum spin box"""
        oldValue = self.imgScale  # save old value of the image scale
        
        # Update number of slides and real image data
        self.nDim = self.spb_axesNum.value()
        if self.imageLoader != None:
            # set value to spb
            self.imageLoader.spb_axesNum.set_value(self.nDim)
            self.imageLoader.val_changed_spb_axesNum()
            self.imageLoader.image_load()
            
        self.new_particle_data()  # Create new particle data
        self.dimsEdits['imgScale'].setText('{0:.3f}'.format(oldValue))
        self.update_real_width()
    
    def reset_axesNum(self):        
        self.nDim = 12      
        # set new value to the spb and automatically call onChange signal
        self.spb_axesNum.setValue(self.nDim)
    
    def paintEvent(self, event):  
        # Create new pixmap and fill it with transparent color
        imageLoaded = False
        if self.realImageData == {}:
            self.pixmap = QPixmap(360, 360)
            self.pixmap.fill(QColor(255, 255, 255, 0))
        else:
            self.pixmap = self.convert_to_QPixmap(self.realImageData['imageMod'])
            imageLoaded = True
        
        # Define qpaiter on created pixmap
        qp = QPainter(self.pixmap)  # Draw in label, not on the form!!!
        qp.setRenderHint(QPainter.Antialiasing, True)  # Smooth lines
        
        # Data to create the blue circle with CE Doameter
        dataCirc = (self.particleData['centreXPos'],
                    self.particleData['centreYPos'],
                    self.particleData['CEDiameter'] / self.particleData['imgScale']) # To scale on the image
        majorAxisPoints = self.particleData['majorAxisPoints']
        minorAxisPoints = self.particleData['minorAxisPoints']
        
        # Draw all necessary graphics on the pixmap
        self.slidersField.render(qp, dataCirc, majorAxisPoints, minorAxisPoints, imageLoaded)  # Render the sliders field: 
        
        # Update the label with image and sliders
        self.lbl_imageSliders.setPixmap(self.pixmap)
        
    def mousePressEvent(self, event):
        """Method for handle the single left click of the mouse"""
        x = event.x() - 20
        y = event.y() - 60
        self.slidersField.ready_to_slide(x, y)
        self.slidersField.slide(x, y)
        self.dimsValues = self.slidersField.get_values()
        self.update_parameters()  # Update particle parameters       
        self.update()  # Update the whole form
        
    def mouseMoveEvent(self, event):
        """Method for hangle the mouse move with pressed left click"""
        x = event.x() - 20
        y = event.y() - 60
        self.slidersField.slide(x, y)
        self.dimsValues = self.slidersField.get_values()
        self.update_parameters()  # Update particle parameters       
        self.update()  # Update the whole form
        
    def update_real_width(self):
        oldValue = self.imgScale
        string = self.dimsEdits['imgScale'].text()  # Get the raw string
        string = string.replace(',','.')  # Symbol ',' is also available 
        error = False
        # Trying to convert text to the value:
        try:
            self.imgScale = float(string)
        except:
            error = True 
        # Possible error handling
        if error:
            string = '{0:.3f}'.format(oldValue)
            self.dimsEdits['imgScale'].setText(string)
            text = 'Image scale should be a number!'
            self.show_error_window(text) 
        else:  # Update the real width field
            self.realWidth = self.imgScale * 360
            string = '{0:.2f}'.format(self.realWidth)
            self.dimsEdits['realWidth'].setText(string)
            self.update_parameters()  # update particle parameters 
        
    def update_image_scale(self):
        oldValue = self.realWidth
        string = self.dimsEdits['realWidth'].text()  # Get the raw string
        string = string.replace(',', '.')  # Symbol ',' is also available
        error = False
        # Trying to convert text to the value:
        try:
            self.realWidth = float(string)
        except:
            error = True
        # Possible error handling
        if error:
            string = '{0:.2f}'.format(oldValue)
            self.dimsEdits['realWidth'].setText(string)
            text = 'Image width (real) should be a number!'
            self.show_error_window(text) 
        else:  # Update the real width field
            self.imgScale = self.realWidth / 360
            string = '{0:.3f}'.format(self.imgScale)
            self.dimsEdits['imgScale'].setText(string)
            self.update_parameters() # update particle parameters
  
    def show_error_window(self, text):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(text)
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
        
    def randomize_particle(self):
        """Method for generating the random particle and recreating the sliders field"""
        for i in range(self.nDim):
            self.dimsValues[i] = rnd.random()
        
        self.slidersField = SlidersField(self.imgWidth, self.nDim, self.dimsValues)
        self.update()
        self.update_parameters()  # update particle parameters

    def save_picture(self):
        '''Method for saving the picture (*.png) of the particle''' 
        path = QFileDialog.getSaveFileName(self, 'Save picture', 'Images/untitled.png', 'Image files (*.png)')[0]
        if path != '':
            self.singlePicture = SinglePicture()
            self.singlePicture.get_single_picture(
                realWidth = self.realWidth,
                margins = True,
                coordinates = self.dimsCoord,
                picWidthHeight = self.picWidthHeight,
                picParticleColor = self.picParticleColor,
                picBkgColor = self.picBkgColor,
                picShowScale = self.picShowScale)
            self.singlePicture.save_picture(path)
        
    def show_picture(self):
        '''Method to show the particle picture in the default image editor'''
        self.singlePicture = SinglePicture()
        self.singlePicture.get_single_picture(
            realWidth = self.realWidth,
            margins = True,
            coordinates = self.dimsCoord,
            picWidthHeight = self.picWidthHeight,
            picParticleColor = self.picParticleColor,
            picBkgColor = self.picBkgColor,
            picShowScale = self.picShowScale)
        self.singlePicture.show_picture()
        
    def load_real_image(self):
        """Method for open the new window to load the real particle image
           and manipulation of the image! 
        """
        if self.imageLoader == None:  # Hasn't been opened before 
            self.imageLoader = RealImageLoader(self)
        else:  # Has been opened before
            self.imageLoader.show()  
    
    def set_real_image_data(self, realImageData):
        """Method for save real particle data after loading and possible
        adjusting the real image of the particle"""        
        self.realImageData = realImageData
        self.imageClearRealAct.setEnabled(True)       
        # Update number of slides
        self.nDim = self.realImageData['axesNum']       
        # Create new particle data
        self.new_particle_data()        
        # Update scale and realWidth
        string = '{0:.3f}'.format(self.realImageData['curScale'])
        self.dimsEdits['imgScale'].setText(string)        
        self.update_real_width()
        # Set axesNum spinbox
        self.spb_axesNum.set_value(self.nDim)
        
    def convert_to_QPixmap(self, image):
        qim = ImageQt(image)
        pix = QPixmap.fromImage(qim)
        return pix
    
    def open_settings_window(self):
        """Method for open setings window of the current tool"""
        self.settingsWindow = PTesterSettingsWindow(self)
        
    def set_settings_data(self, settingsData):
        """Method for save setings data comming from settings window"""
        # Update the picture parameters
        self.picWidthHeight = settingsData['picWidthHeight']
        self.picParticleColor = settingsData['picParticleColor']
        self.picBkgColor = settingsData['picBkgColor']
        self.picShowScale = settingsData['picShowScale']    
    
    def clear_real_image(self):
        self.realImageData = {}       
        
    def show_help(self):
        path = os.getcwd() + '\Help\Help_ParticleTester.pdf'
        os.startfile(path)
        
    def show_about(self):
        self.about = About()

if __name__ == '__main__':
    def run_app():
        app = QApplication(sys.argv)
        app.setFont(QFont('Arial', 11)) 
        mainWindow = ParticleTester()
        app.exec_()
    run_app()