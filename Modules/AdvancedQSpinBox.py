# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QSpinBox

class AdvancedQSpinBox(QSpinBox):
    """Class for advanced spin box! The difference from the original one is that 
       it arrise ValueChanged signal only after manual change the spin box value """
    def __init__(self, parent=None):
        super(AdvancedQSpinBox, self).__init__(parent=parent)
        
    def set_value(self, value):
        self.blockSignals(True)  # Block valueChanched signal
        self.setValue(value)  # Call self method
        self.blockSignals(False)  # Enable valueChanched signal

