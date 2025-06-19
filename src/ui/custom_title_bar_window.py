"""
Custom Title Bar Window
Base class for windows with custom title bar styling.
"""

from PySide6.QtWidgets import QMainWindow, QApplication
from PySide6.QtCore import Qt

from ..utils import apply_custom_title_bar


class CustomTitleBarWindow(QMainWindow):
    """Base class for windows with custom title bar styling."""
    
    def __init__(self):
        super().__init__()
        
        # Apply custom title bar after window is shown
        QApplication.processEvents()
        self.customize_title_bar()
    
    def showEvent(self, event):
        super().showEvent(event)
        # Delay title bar customization
        QApplication.processEvents()
        self.customize_title_bar()
    
    def customize_title_bar(self):
        """Apply custom title bar styling using Windows API."""
        apply_custom_title_bar(self) 