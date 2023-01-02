# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import (QPainter, QPolygon, QColor, QPen, QBrush, QPixmap)
from PyQt5.QtCore import Qt, QPoint
import math as m

class ImageLabelGenerator(QLabel):
    def __init__(self, parent = None, drawFlag = "None"):
        super(ImageLabelGenerator, self).__init__(parent=parent)
        #super().__init__(self)
        self.N = 0  # Number of radius vectors
        self.drawFlag = drawFlag  # Flag for drawing
        self.pSearchImg = QPixmap('Resources/pSearchImg.png')
        self.transpImage = QPixmap('Resources/transpImage.png')
        self.dimsValues = []  # Particle dimension values for drawing
        self.partPolCorners = []  # Coordinates of the particle corners
        self.width = 243  # Width of the picture with particle image
        self.bigRadius = 110  # Maximum value of radius-vector (in px)
    
    def set_dimsValues(self, data):
        """Method for setting the particle dimension values"""
        self.dimsValues = data
        self.N = len(self.dimsValues)
        self.calc_particle_corner_coordinates()
            
    def calc_particle_corner_coordinates(self):
        """Method for determination the particle polygon corners coordinates"""
        # Empty the array
        self.partPolCorners = []
        # Calculate the coordinates
        for i in range(self.N):
            angle = i * 2 * m.pi/self.N
            radius = self.dimsValues[i] * self.bigRadius
            x = int(round(120 + radius * m.cos(angle)))
            y = int(round(120 + radius * m.sin(angle)))
            self.partPolCorners.append((x, y))     
        
    def paintEvent(self, event):
        """Method override of the painting on th elabel""" 
        # Serve the main paint event
        super().paintEvent(event)  
        qp = QPainter(self) 
        qp.setRenderHint(QPainter.Antialiasing, True)
        
        # Graphics on the label:      
        if self.drawFlag == "PSImg":
            self.setPixmap(self.pSearchImg)
        else:
            self.setPixmap(self.transpImage)
            self.render(qp)
        
    def render(self, qp):
        """Method for render the additional graphics on the label"""
        # Fill the picture with white color
        qp.setPen(QPen(QColor(170, 170, 170, 255), 1.2, Qt.SolidLine))  # Outline
        qp.setBrush(QBrush(QColor(255, 255, 255, 255), Qt.SolidPattern))  # Fill
        polygon = QPolygon()
        polygon.append(QPoint(0, 0))
        polygon.append(QPoint(self.width, 0))
        polygon.append(QPoint(self.width, self.width))
        polygon.append(QPoint(0, self.width))
        qp.drawPolygon(polygon)
            
        # Draw a particle shape
        if self.drawFlag == "Part":
            qp.setPen(QPen(QColor(50, 50, 50, 255), 1.2, Qt.SolidLine))  # Outline
            qp.setBrush(QBrush(QColor(50, 50, 50, 255), Qt.SolidPattern))  # Fill
            polygon = QPolygon()
            for item in self.partPolCorners:
                point = QPoint(item[0], item[1])
                polygon.append(point)      
            qp.drawPolygon(polygon)
        
        # Draw a single circle when spherical particles are generated
        if self.drawFlag == "Circ":
            qp.setPen(QPen(QColor(50, 50, 50, 255), 1.2, Qt.SolidLine))  # Outline
            qp.setBrush(QBrush(QColor(50, 50, 50, 255), Qt.SolidPattern))  # Fill
            qp.drawEllipse(QPoint(self.width/2, self.width/2), 70, 70)
        
        
 