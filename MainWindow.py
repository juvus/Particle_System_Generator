# -*- coding: utf-8 -*-
"""
Project:        Particle systems generator program 
Description:    Main window of the particle systems generator program
Author:         Dmitry Safonov (Dmitry.Safonov@lut.fi)
Organization:   Lappeenranta University of Technology (LUT)
                Solid/Liquid Separation Research Group            
Last edited:    05.04.2019
"""
import sys
import os

from PyQt5.QtWidgets import (QMainWindow, QApplication, QDesktopWidget, QAction, 
                             QLabel, QPushButton, QMessageBox, QFileDialog, QCheckBox)
from PyQt5.QtGui import QIcon, QFont, QPixmap, QPainter, QPen, QColor, QBrush
from PyQt5.QtCore import Qt, QThreadPool, QTimer

# Program modules:
from Modules.About import About

# Tools classes:
from ParticleTester import ParticleTester
from ParticleFinder import ParticleFinder
from ParticlesGenerator import ParticlesGenerator
from PicturesRender import PicturesRender

# Main window class     
class MainWindow(QMainWindow):
    """Class of a main window of the pictures render tool"""
    def __init__(self):
        """Constructor of the class"""
        super().__init__()
        self.particleTester = None
        self.particleFinder = None
        self.particlesGenerator = None
        self.picturesRender = None
        
        self.init_ui()  # Initialize the user interface elements

    def init_ui(self):
        """Method for the initialization of the UI"""
        self.setFixedSize(400, 240)  # Window size
        self.center_window()  # Center the window on desktop
        self.setWindowIcon(QIcon('Resources/icon.png'))
        self.setWindowTitle('Particles system generator')  # Window title
        # Menu and submenu creation 
        mainMenu = self.menuBar() 
        infoMenu = mainMenu.addMenu('Info')
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
        # Add actions to menu: Info -> ...
        infoMenu.addAction(helpAct)
        infoMenu.addAction(aboutAct)
        
        # Label (Particle system properties)
        self.lbl_title = QLabel('*** Particle systems generator ***', self)
        self.lbl_title.setGeometry(20, 30, 360, 20)
        self.lbl_title.setAlignment(Qt.AlignCenter)
        self.lbl_title.setFont(QFont('Arial', 11, weight=QFont.Bold))           

        # Block for particle tester tool
        self.lbl_particleTester = QLabel('1. Particle tester tool', self)
        self.lbl_particleTester.setGeometry(30, 69, 360, 20)
        self.lbl_particleTester.setAlignment(Qt.AlignLeft)
        self.lbl_particleTester.setFont(QFont('Arial', 11))
        
        self.btn_particleTester = QPushButton('Run', self)
        self.btn_particleTester.setGeometry(317, 64, 60, 28)
        self.btn_particleTester.clicked.connect(self.run_particle_tester_tool)
        
        # Block for particle finder tool
        self.lbl_particleFinder = QLabel('2. Particle finder tool', self)
        self.lbl_particleFinder.setGeometry(30, 111, 360, 20)
        self.lbl_particleFinder.setAlignment(Qt.AlignLeft)
        self.lbl_particleFinder.setFont(QFont('Arial', 11))
        
        self.btn_particleFinder = QPushButton('Run', self)
        self.btn_particleFinder.setGeometry(317, 106, 60, 28)
        self.btn_particleFinder.clicked.connect(self.run_particle_finder_tool)
        
        # Block for particles generator tool
        self.lbl_particlesGenerator = QLabel('3. Particles generator tool', self)
        self.lbl_particlesGenerator.setGeometry(30, 153, 360, 20)
        self.lbl_particlesGenerator.setAlignment(Qt.AlignLeft)
        self.lbl_particlesGenerator.setFont(QFont('Arial', 11))
        
        self.btn_particlesGenerator = QPushButton('Run', self)
        self.btn_particlesGenerator.setGeometry(317, 148, 60, 28)
        self.btn_particlesGenerator.clicked.connect(self.run_particles_generator_tool)
        
        # Block for pictures render tool
        self.lbl_picturesRender = QLabel('4. Pictures render tool', self)
        self.lbl_picturesRender.setGeometry(30, 195, 360, 20)
        self.lbl_picturesRender.setAlignment(Qt.AlignLeft)
        self.lbl_picturesRender.setFont(QFont('Arial', 11))
        
        self.btn_picturesRender = QPushButton('Run', self)
        self.btn_picturesRender.setGeometry(317, 190, 60, 28)
        self.btn_picturesRender.clicked.connect(self.run_pictures_render_tool)
        
        self.show()
    
    def run_particle_tester_tool(self):
        self.particleTester = ParticleTester()
    
    def run_particle_finder_tool(self):
        self.particleFinder = ParticleFinder()
    
    def run_particles_generator_tool(self):
        self.particlesGenerator = ParticlesGenerator()
    
    def run_pictures_render_tool(self):
        self.picturesRender = PicturesRender()

    def paintEvent(self, event):
        """paintEvent to update the thumbnail picture """
        qp = QPainter(self)
        qp.setRenderHint(QPainter.Antialiasing, True)
        
        qp.setPen(QPen(QColor(170, 170, 170, 255), 2.0, Qt.SolidLine))  # Outline
        qp.setBrush(QBrush(QColor(255, 255, 255, 255), Qt.SolidPattern))  # Fill
        
        # Draw the rectangle for particle tester tool
        qp.drawRect(18, 60, 364, 36)
        # Draw the rectangle for particle finder tool
        qp.drawRect(18, 102, 364, 36)
        # Draw the rectangle for particles generator tool
        qp.drawRect(18, 144, 364, 36)
        # Draw the rectangle for pictures render tool
        qp.drawRect(18, 186, 364, 36)
        
    def show_help(self):
        path = os.getcwd() + '\Help\Help_MainProgram.pdf'
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
        mainWindow = MainWindow()
        app.exec_()
    run_app()
    #sys.exit(app.exec_())