# -*- coding: utf-8 -*-

from PyQt5.QtGui import QColor, QPen, QBrush
from PyQt5.QtCore import Qt, QPoint
import math as m
import time

class Slider:
    """Class for creating the unique slider"""
    def __init__(self, x0, y0, x1, y1, value):
        """Constructor of the class
        Args:
            x0 (int): X coordinate of the top left corner of the slider.
            y0 (int): Y coordinate of the top left corner of the slider.
            x1 (int): X coordinate of the bottom right corner of the slider.
            y1 (int): Y coordinate of the bottom right corner of the slider.
            value (float): Current position of the slider (0.0 - 1.0) 
        """
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.posX = 0  # X coordinate of the slider centre
        self.posY = 0  # Y coordinate of the slider centre
        self.value = value
        self.slideFlag = False  # Flag to show it the slider ready to move
        self.rad = 5  # Radius of the slider moving part (circle)
        self.lineType = 'DashLine'
        
        self.begin = QPoint(x0, y0)
        self.end = QPoint(x1, y1)
        
        self.set_position(self.value)
    
    def set_position(self, value):
        """Method for update the X and Y coordinates of the slider
        Args:
            value [float]: New position of the slider (0.0 - 1.0)
        """
        self.value = value
        self.posX = int(round((self.x1 - self.x0) * self.value + self.x0))
        self.posY = int(round((self.y1 - self.y0) * self.value + self.y0))
        self.pos = QPoint(self.posX, self.posY) 

    def render(self, qp):
        """Method for drawing the slider on the form
        Args:
            qp (obj): QPainter object from the parent form.
        """
        # Determine the line type
        if self.lineType == 'SolidLine':
            lineType = Qt.SolidLine
        elif self.lineType == 'DashLine':
            lineType = Qt.DashLine            
        
        qp.setPen(QPen(QColor(0, 0, 0, 255), 1, lineType))  # Outline
        qp.drawLine(self.begin, self.end)  # Slider line
        qp.setPen(QPen(QColor(0, 0, 0, 255), 1, Qt.SolidLine))  # Outline
        qp.setBrush(QBrush(QColor(255, 255, 255, 255), Qt.SolidPattern))  # Fill     
        qp.drawEllipse(self.pos, self.rad, self.rad)  # Slider movable circle  

    def ready_to_slide(self, x, y):
        """Method for determining if the slider ready to slide after click on 
           round handle or slider line
        Args:
            x (int): X coordinate of the cursor
            y (int): Y coordinate of the cursor
        """      
        self.slideFlag = False
        needCalculation = False  # Flag to indicate do we need calc or not  
        
        if (abs(self.x0 - self.x1) >= abs(self.y0 - self.y1)):   # close to horizontal
            if (x >= self.x1 and x <= self.x0) or (x >= self.x0 and x <= self.x1):
                needCalculation = True
        else:  # close to vertical
            if (y >= self.y1 and y <= self.y0) or (y >= self.y0 and y <= self.y1):
                needCalculation = True          
            
        # Define the minimum distance from the point (x, y) to the line
        if needCalculation:
            a = self.y1 - self.y0
            b = self.x1 - self.x0
            if a == 0:  # horizontal line
                x2 = x
                y2 = self.y0
            elif b == 0:  # vertical line
                y2 = y
                x2 = self.x0
            else:
                c = -self.x0 * a / b + self.y0
                d = x * b / a + y
                x2 = ((d - c) * b * a)/(m.pow(a, 2) + m.pow(b, 2))
                y2 = x2 * a / b + c      
            distance = m.sqrt(m.pow(x - x2, 2) + m.pow(y - y2, 2))
            if distance <= self.rad:
                self.slideFlag = True
                
        # Also always slider is ready to slide if clicked on round slider
        distance = m.sqrt(m.pow(x - self.posX, 2) + m.pow(y - self.posY, 2))
        if distance <= self.rad:
            self.slideFlag = True

    def slide(self, x, y):
        """Method to move the slider according to mouse move 
        Args:
            x (int): X coordinate of the cursor
            y (int): Y coordinate of the cursor
        """
        if self.slideFlag:
            if abs(self.x1 - self.x0) >= abs(self.y1 - self.y0):
                self.posX = x
                # Movement restriction
                if self.posX < min(self.x0, self.x1):
                    self.posX = min(self.x0, self.x1)
                if self.posX > max(self.x0, self.x1):
                    self.posX = max(self.x0, self.x1)
                # Recalculation of value and y
                self.value = abs((self.posX - self.x0)/(self.x1 - self.x0))
                self.posY = int(round((self.y1 - self.y0) * self.value + self.y0))
            else:
                self.posY = y
                # Movement restriction
                if self.posY < min(self.y0, self.y1):
                    self.posY = min(self.y0, self.y1)
                if self.posY > max(self.y0, self.y1):
                    self.posY = max(self.y0, self.y1)
                # Recalculation of value and x
                self.value = abs((self.posY - self.y0)/(self.y1 - self.y0))
                self.posX = int(round((self.x1 - self.x0) * self.value + self.x0))
            self.pos = QPoint(self.posX, self.posY)