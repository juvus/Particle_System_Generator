# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QLineEdit

class AdvancedQLineEdit(QLineEdit):
    """Class for advanced line edit! The difference from the original one is that 
       it shanges a little the apearence of the ReadOnly state"""
    def __init__(self, parent=None):
        super(AdvancedQLineEdit, self).__init__(parent=parent)
        self.state = None  # Flag of read-only
        
    def set_readOnly(self, state):
        self.state = state
        self.setReadOnly(state)  # Normal change the state
        self.set_gray_bkg()

    def set_gray_bkg(self):
        """Method to set backgrount to the gray color"""
        if self.state:
            self.setStyleSheet("QLineEdit[readOnly=\"true\"] {"
                               "color: #303030;"
                               "background-color: #F0F0F0;"
                               "border: 1px solid #B0B0B0;"
                               "border-radius: 2px;}")

    def set_red_bkg(self):
        """Method to set backgrount to the gray red color"""
        if self.state:
            self.setStyleSheet("QLineEdit[readOnly=\"true\"] {"
                               "color: #303030;"
                               "background-color: #E8C5C5;"
                               "border: 1px solid #B0B0B0;"
                               "border-radius: 2px;}")