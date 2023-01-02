# -*- coding: utf-8 -*-
"""
Project:        Particles system generator program 
Description:    Starting point of the program
Author:         Dmitry Safonov (Dmitry.Safonov@lut.fi)
Organization:   Lappeenranta University of Technology (LUT)
                Solid/Liquid Separation Research Group            
Last edited:    05.04.2019
"""
import sys
import os

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont

# Tools classes:
from MainWindow import MainWindow

if __name__ == '__main__':
    def run_app():
        app = QApplication(sys.argv)
        app.setFont(QFont('Arial', 11)) 
        mainWindow = MainWindow()
        app.exec_()
    run_app()