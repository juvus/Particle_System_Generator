# -*- coding: utf-8 -*-

from PyQt5.QtGui import QColor, QPen, QBrush
from PyQt5.QtCore import Qt, QPoint
import math as m
import time

class RoundSlider:
    """Class for creating the unique slider"""
    def __init__(self, x0, y0, r, value):
        """Constructor of the class
        Args:
            x0 (int): X coordinate of the circle centre;
            y0 (int): Y coordinate of the circle centre;
            r (int): raduis of the clider circle
            value (float): Current position of the slider (0.0 - 360.0) 
        """
        self.x0 = x0
        self.y0 = y0
        self.r = r
        self.value = value
        self.slideFlag = False  # Flag to show it the slider ready to move
        self.rad = 5  # Radius of the slider moving part (circle)
        
        self.centre = QPoint(x0, y0)       
        self.set_position(self.value)
    
    def set_position(self, value):
        """Method for update the X and Y coordinates of the slider
        Args:
            value [float]: New position of the slider (0.0 - 360.0)
        """
        self.value = value
        angle = m.pi * self.value / 180  # angle in radians
        self.posX = int(round(m.cos(angle) * self.r)) + self.x0
        self.posY = int(round(m.sin(angle) * self.r)) + self.y0       
        self.pos = QPoint(self.posX, self.posY)
         

    def render(self, qp):
        """Method for drawing the slider on the form
        Args:
            qp (obj): QPainter object from the parent form.
        """
        qp.setPen(QPen(QColor(0, 0, 0, 255), 1, Qt.DashLine))  # Outline
        qp.setBrush(QBrush(QColor(255, 255, 255, 0), Qt.SolidPattern))  # Fill
        qp.drawEllipse(self.centre, self.r, self.r)  # slider curve (circle)
        
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
        
        # distance to the centre
        distance = m.sqrt(m.pow(x - self.x0, 2) + m.pow(y - self.y0, 2))
        if (distance >= (self.r - self.rad)) and distance <= (self.r + self.rad):
            self.slideFlag = True
        
    def slide(self, x, y):
        """Method to move the slider according to mouse move 
        Args:
            x (int): X coordinate of the cursor
            y (int): Y coordinate of the cursor
        """
        if self.slideFlag:
            R = m.sqrt(m.pow(self.x0 - x, 2) + m.pow(self.y0 - y, 2))
            angle = m.asin(abs(self.y0 - y)/R)  # with respect to horizontal line
            
            if (x > self.x0):  # I or IV quarter CW
                if (y >= self.y0):  # I quarter CW
                    angle = angle + 0
                elif (y < self.y0):  # IV quarter CW
                    angle = 2 * m.pi - angle
            elif (x <= self.x0):  # II or III quarter CW
                if (y >= self.y0):  # II quarter CW
                    angle = m.pi - angle
                elif (y < self.y0):  # III quarter CW
                    angle = angle + m.pi
            self.value = angle * 180 / m.pi
            self.set_position(self.value)