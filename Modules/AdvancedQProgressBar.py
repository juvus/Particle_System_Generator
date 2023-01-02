# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QProgressBar

class AdvancedQProgressBar(QProgressBar):
    """Class for advanced progress bar! The difference from the original one is that 
       it shanges a little the apearence"""
    def __init__(self, parent=None):
        super(AdvancedQProgressBar, self).__init__(parent=parent)
        self.state = None  # Flag of read-only
        
        # Apply the custom style
        self.setStyleSheet("QProgressBar {"
                           "border: 1px solid grey;"
                           "border-radius: 2px;"
                           "text-align: center;}"
                            
                           "QProgressBar::chunk {"
                           "background-color: #82CAFF;"
                           "width: 10px;"
                           "margin: 1px;}")