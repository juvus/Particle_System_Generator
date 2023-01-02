# -*- coding: utf-8 -*-

import math as m
from PyQt5.QtGui import QColor, QPen, QBrush, QPolygon
from PyQt5.QtCore import Qt, QPoint
from Modules.Slider import Slider

class SlidersField:
    """Class for the field of sliders"""
    def __init__(self, width, N, values):
        """Constructor of the class
        Args:
            x (int): X coordinate of the top left corner of the sliders field.
            y (int): Y coordinate of the top left corner of the sliders field.
            width (int): Width of the sliders field widget.
            N (int): Number of sliders arranged in a circle
            values (float[]): Array of sliders values (0.0 - 1.0) 
        """
        self.width = width  # Width=Height of the slider field (px)    
        self.N = N  # Number of sliders arranged in a circle
        self.values = values 
        self.dSm = 5  # small radius = centreRadius
        self.sliders = []  # Array of sliders
        self.generate_sliders()     

    def generate_sliders(self):
        """Method for the sliders generation"""
        self.xC = int(round(self.width/2))  # X of the center
        self.yC = int(round(self.width/2))  # Y of the center
        self.dBg = int(round(self.width/2))  # big radius
        # Set of sliders
        for i in range(self.N):
            angle = i * 2 * m.pi/self.N
            x0 = int(round(self.xC + self.dSm * m.cos(angle)))
            x1 = int(round(self.xC + self.dBg * m.cos(angle)))
            y0 = int(round(self.yC + self.dSm * m.sin(angle)))
            y1 = int(round(self.yC + self.dBg * m.sin(angle)))
            # Create slider
            self.sliders.append(Slider(x0, y0, x1, y1, self.values[i]))

    def get_values(self):
        self.values = []
        for i in range(self.N):
            self.values.append(self.sliders[i].value)
        return self.values  
    
    def render(self, qp, dataCirc, majorAxisPoints, minorAxisPoints, imageLoaded):
        """Method for render the sliders field (with bottom arrow)
        Args:
            qp (obj): QPainter object from the parent form.
        """
        if imageLoaded:
            transp = 0  # Transparent fill
        else:
            transp = 255
        
        # Draw a large circle (white):
        qp.setPen(QPen(QColor(0, 0, 0, 255), 1.2, Qt.SolidLine))  # Outline
        qp.setBrush(QBrush(QColor(255, 255, 255, transp), Qt.SolidPattern))  # Fill
        polygon = QPolygon()
        for i in range(self.N):
            point = QPoint(self.sliders[i].x1, self.sliders[i].y1)
            polygon.append(point)
        qp.drawPolygon(polygon)       
        
        # Draw a small circle (white):
        qp.setPen(QPen(QColor(0, 0, 0, 255), 1.2, Qt.SolidLine))  # Outline
        qp.setBrush(QBrush(QColor(255, 255, 255, transp), Qt.SolidPattern))  # Fill
        polygon = QPolygon()
        for i in range(self.N):
            point = QPoint(self.sliders[i].x0, self.sliders[i].y0)
            polygon.append(point)
        qp.drawPolygon(polygon)
        
        # Draw a particle (red color)
        qp.setPen(QPen(QColor(255, 0, 0, 255), 1.2, Qt.SolidLine))  # Outline
        qp.setBrush(QBrush(QColor(255, 0, 0, 20), Qt.SolidPattern))  # Fill
        polygon = QPolygon()
        for i in range(self.N):
            polygon.append(self.sliders[i].pos)
        qp.drawPolygon(polygon)       
        
        # Draw a major axis
        qp.setPen(QPen(QColor(0, 0, 255, 200), 1.2, Qt.DashLine))
        x0 = majorAxisPoints[0][0] + self.width/2
        y0 = majorAxisPoints[0][1] + self.width/2
        x1 = majorAxisPoints[1][0] + self.width/2
        y1 = majorAxisPoints[1][1] + self.width/2
        qp.drawLine(QPoint(x0, y0), QPoint(x1, y1))
        
        # Draw a minor axis
        qp.setPen(QPen(QColor(0, 0, 255, 200), 1.0, Qt.DashLine))
        x0 = minorAxisPoints[0][0] + self.width/2
        y0 = minorAxisPoints[0][1] + self.width/2
        x1 = minorAxisPoints[1][0] + self.width/2
        y1 = minorAxisPoints[1][1] + self.width/2
        qp.drawLine(QPoint(x0, y0), QPoint(x1, y1))
        
        # Draw a circle with CE diameter and its centre (blue color)
        x = dataCirc[0] + self.width/2
        y = dataCirc[1] + self.width/2
        r = dataCirc[2]/2
        qp.setPen(QPen(QColor(0, 0, 255, 200), 1.0, Qt.SolidLine))  # Outline
        qp.setBrush(QBrush(QColor(0, 0, 255, 100), Qt.SolidPattern))  # Fill
        qp.drawEllipse(QPoint(x, y), 3, 3)  # Centre point
        qp.setPen(QPen(QColor(0, 0, 255, 200), 1.0, Qt.DashLine))
        qp.setBrush(QBrush(QColor(0, 0, 0, 0), Qt.SolidPattern))  # Fill
        qp.drawEllipse(QPoint(x, y), r, r)  # Circle with CE diameter
  
        # Draw all the sliders
        for i in range(self.N):
            self.sliders[i].render(qp) 

    def ready_to_slide(self, x, y):
        """Method for determining if any slider ready to slide after click
        Args:
            x (int): X coordinate of the cursor
            y (int): Y coordinate of the cursor
        """
        for i in range(self.N):
            self.sliders[i].ready_to_slide(x, y)

    def slide(self, x, y):
        """Method to move any the slider
        Args:
            x (int): X coordinate of the cursor
            y (int): Y coordinate of the cursor
        """
        for i in range(self.N):
            self.sliders[i].slide(x, y)
        