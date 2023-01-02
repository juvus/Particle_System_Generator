# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import (QPainter, QPolygon, QColor, QPen, QBrush)
from PyQt5.QtCore import Qt, QPoint
import math as m

class ImageLabel(QLabel):
    def __init__(self, parent=None, N=12, smallRadius=20, drawParticle=False):
        super(ImageLabel, self).__init__(parent=parent)
        #super().__init__(self)
        self.N = N
        self.drawParticle = drawParticle  # Flag to draw a particle on image or not
        self.bkgTransp = 0  # Background transparency of the polygons
        self.dimsValues = []  # Particle dimension values for drawing
        self.partPolCorners = []  # Coordinates of the particle corners
        self.bigRadius = 180  # Radius of the big polygon
        self.smallRadius = smallRadius  # Radius of the small bolygon (20 default)
        self.bigPolCorners = []  # Coordinates of the big polygon corners
        self.smallPolCorners = []  # Coordinates of the small plygon corners
        self.calc_corners_coordinates()
        self.setMouseTracking(True)  # Enable mouse traching over the label
        # Blue circle of CEDiameter and Major and Minor axis
        self.drawBlueCircle = False
        self.dataCirc = None
        self.majorAxisPoints = None
        self.minorAxisPoints = None
        self.width = 360
        
        
        
    def set_N(self, N):
        self.N = N
        self.calc_corners_coordinates()
    
    def set_dimsValues(self, data):
        self.dimsValues = data
        self.calc_particle_corner_coordinates()
    
    def calc_corners_coordinates(self):
        """Method for determination the small and big polygon corners coordinates"""
        # Empty the arrays
        self.bigPolCorners = []
        self.smallPolCorners = []
        # Calculate the coordinates
        for i in range(self.N):
            angle = i * 2 * m.pi/self.N
            x = int(round(180 + self.smallRadius * m.cos(angle)))
            y = int(round(180 + self.smallRadius * m.sin(angle)))
            self.smallPolCorners.append((x, y))
            
            x = int(round(180 + self.bigRadius * m.cos(angle)))
            y = int(round(180 + self.bigRadius * m.sin(angle)))
            self.bigPolCorners.append((x, y))
            
    def calc_particle_corner_coordinates(self):
        """Method for determination the particle polygon corners coordinates"""
        # Empty the array
        self.partPolCorners = []
        # Calculate the coordinates
        for i in range(self.N):
            angle = i * 2 * m.pi/self.N
            radius = self.dimsValues[i] * (self.bigRadius - self.smallRadius)
            x = int(round(180 + (self.smallRadius + radius) * m.cos(angle)))
            y = int(round(180 + (self.smallRadius + radius) * m.sin(angle)))
            self.partPolCorners.append((x, y))     
        
    def paintEvent(self, event):
        """Method override of the painting on th elabel""" 
        # Serve the main paint event
        super().paintEvent(event)  
        qp = QPainter(self) 
        qp.setRenderHint(QPainter.Antialiasing, True)
        
        # Additional graphics on  the label:
        self.render(qp)     
        
    def render(self, qp):
        """Method for render the additional graphics on the label"""
         # Draw the big polygon
        qp.setPen(QPen(QColor(0, 0, 0, 255), 1.2, Qt.SolidLine))  # Outline
        qp.setBrush(QBrush(QColor(255, 255, 255, self.bkgTransp), Qt.SolidPattern))  # Fill
        polygon = QPolygon()
        for item in self.bigPolCorners:
            point = QPoint(item[0], item[1])
            polygon.append(point)      
        qp.drawPolygon(polygon)
        
        # draw the small polygon in the middle
        polygon = QPolygon()
        for item in self.smallPolCorners:
            point = QPoint(item[0], item[1])
            polygon.append(point)      
        qp.drawPolygon(polygon)
        
        # Draw a dashed lines between two polygons 
        qp.setPen(QPen(QColor(0, 0, 0, 255), 1, Qt.DashLine))  # Outline
        for i in range(self.N):
            begin = QPoint(self.smallPolCorners[i][0], self.smallPolCorners[i][1])
            end = QPoint(self.bigPolCorners[i][0], self.bigPolCorners[i][1])
            qp.drawLine(begin, end)    
            
        # Draw a particle shape
        if self.drawParticle:
            qp.setPen(QPen(QColor(255, 0, 0, 255), 1.2, Qt.SolidLine))  # Outline
            qp.setBrush(QBrush(QColor(255, 0, 0, 20), Qt.SolidPattern))  # Fill
            polygon = QPolygon()
            for item in self.partPolCorners:
                point = QPoint(item[0], item[1])
                polygon.append(point)      
            qp.drawPolygon(polygon)
                
        if self.drawBlueCircle:
            # Draw a major axis
            qp.setPen(QPen(QColor(0, 0, 255, 200), 1.2, Qt.DashLine))
            x0 = self.majorAxisPoints[0][0] + self.width/2
            y0 = self.majorAxisPoints[0][1] + self.width/2
            x1 = self.majorAxisPoints[1][0] + self.width/2
            y1 = self.majorAxisPoints[1][1] + self.width/2
            qp.drawLine(QPoint(x0, y0), QPoint(x1, y1))
            
            # Draw a minor axis
            qp.setPen(QPen(QColor(0, 0, 255, 200), 1.0, Qt.DashLine))
            x0 = self.minorAxisPoints[0][0] + self.width/2
            y0 = self.minorAxisPoints[0][1] + self.width/2
            x1 = self.minorAxisPoints[1][0] + self.width/2
            y1 = self.minorAxisPoints[1][1] + self.width/2
            qp.drawLine(QPoint(x0, y0), QPoint(x1, y1))
            
            # Draw a circle with CE diameter and its centre (blue color)
            x = self.dataCirc[0] + self.width/2
            y = self.dataCirc[1] + self.width/2
            r = self.dataCirc[2]/2
            qp.setPen(QPen(QColor(0, 0, 255, 200), 1.0, Qt.SolidLine))  # Outline
            qp.setBrush(QBrush(QColor(0, 0, 255, 100), Qt.SolidPattern))  # Fill
            qp.drawEllipse(QPoint(x, y), 3, 3)  # Centre point
            qp.setPen(QPen(QColor(0, 0, 255, 200), 1.0, Qt.DashLine))
            qp.setBrush(QBrush(QColor(0, 0, 0, 0), Qt.SolidPattern))  # Fill
            qp.drawEllipse(QPoint(x, y), r, r)  # Circle with CE diameter
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        