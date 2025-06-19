#!/usr/bin/env python3
"""
Password Generator & Manager
A completely offline password management application with encryption,
password generation, secure notes, and backup/restore functionality.
"""

import sys
import os

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor

from src.ui import MainWindow


def main():
    """Main application entry point."""
    # Set High DPI scaling for PySide6
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')

    # Custom dark blue palette
    dark_blue = QColor(20, 30, 48)
    mid_blue = QColor(36, 52, 71)
    accent_blue = QColor(44, 62, 80)
    text_color = QColor(220, 230, 242)
    highlight = QColor(0, 120, 215)
    disabled = QColor(120, 130, 150)

    palette = QPalette()
    palette.setColor(QPalette.Window, dark_blue)
    palette.setColor(QPalette.WindowText, text_color)
    palette.setColor(QPalette.Base, mid_blue)
    palette.setColor(QPalette.AlternateBase, dark_blue)
    palette.setColor(QPalette.ToolTipBase, text_color)
    palette.setColor(QPalette.ToolTipText, text_color)
    palette.setColor(QPalette.Text, text_color)
    palette.setColor(QPalette.Button, accent_blue)
    palette.setColor(QPalette.ButtonText, text_color)
    palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.Link, highlight)
    palette.setColor(QPalette.Highlight, highlight)
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    palette.setColor(QPalette.Disabled, QPalette.Text, disabled)
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, disabled)
    app.setPalette(palette)

    # Optional: dark blue stylesheet for extra polish
    app.setStyleSheet('''
        QWidget { background-color: #141E30; color: #dce6f2; }
        QMainWindow { background-color: #141E30; }
        QMainWindow::title { background-color: #141E30; color: #dce6f2; }
        QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QComboBox {
            background-color: #243447; color: #dce6f2; border: 1px solid #2c3e50;
        }
        QPushButton {
            background-color: #2c3e50; color: #dce6f2; border: 1px solid #1a2636;
            padding: 4px 12px; border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #1a2636;
        }
        QTabWidget::pane { border: 1px solid #2c3e50; }
        QTabBar::tab {
            background: #243447; color: #dce6f2; padding: 6px 16px;
        }
        QTabBar::tab:selected {
            background: #2c3e50; color: #ffffff;
        }
        QHeaderView::section {
            background-color: #243447;
            color: #dce6f2;
            border-top: 1px solid #2c3e50;
            border-bottom: 2px solid #60A3D9;
            border-right: 1.5px solid #60A3D9;
            border-left: none;
        }
        QHeaderView::section:last-of-type {
            border-right: none;
        }
        QTableWidget {
            background-color: #243447; alternate-background-color: #141E30;
            color: #dce6f2;
            border: none;
            border-radius: 12px;
            padding-top: 16px;
            padding-left: 6px;
            padding-right: 6px;
            gridline-color: #2c3e50;
        }
        QTableWidget::item {
            border-bottom: none;
            border-left: none;
            border-top: none;
        }
        QTableWidget::item:last-column {
            border-right: none;
        }
        QGroupBox {
            border: 1px solid #2c3e50; margin-top: 8px;
        }
        QGroupBox:title {
            subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px;
        }
        QScrollBar:vertical, QScrollBar:horizontal {
            background: #243447; width: 12px; margin: 0px;
        }
        QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
            background: #2c3e50; border-radius: 6px;
        }
        QStatusBar {
            background-color: #243447; color: #dce6f2; border-top: 1px solid #2c3e50;
        }
        QMenuBar {
            background-color: #243447; color: #dce6f2; border-bottom: 1px solid #2c3e50;
        }
        QMenuBar::item {
            background-color: transparent; padding: 4px 8px;
        }
        QMenuBar::item:selected {
            background-color: #2c3e50;
        }
        QDialog {
            background-color: #141E30; color: #dce6f2;
        }
        QMessageBox {
            background-color: #141E30; color: #dce6f2;
        }
        QMessageBox QPushButton {
            min-width: 80px; min-height: 24px;
        }
        QInputDialog {
            background-color: #141E30; color: #dce6f2;
        }
        QFileDialog {
            background-color: #141E30; color: #dce6f2;
        }
    ''')

    # Create and show main window
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main() 