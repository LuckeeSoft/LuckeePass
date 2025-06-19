"""
Title Bar Utilities
Custom title bar styling for Windows applications.
"""

import ctypes
from ctypes import wintypes


def apply_custom_title_bar(window):
    """Apply custom title bar styling to a window using Windows API."""
    try:
        # Get window handle
        hwnd = int(window.winId())
        
        # Windows API constants
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        DWMWA_CAPTION_COLOR = 35
        DWMWA_BORDER_COLOR = 34
        
        # Enable dark mode title bar (Windows 10 build 18985+)
        value = ctypes.c_int(1)  # 1 for dark, 0 for light
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, 
            DWMWA_USE_IMMERSIVE_DARK_MODE,
            ctypes.byref(value),
            ctypes.sizeof(value)
        )
        
        # Set custom title bar color (Windows 11 22000+)
        # Color format: 0x00BBGGRR (BGR) - Using exact app background color
        # App background: RGB(20, 30, 48) = BGR(48, 30, 20) = 0x00301E14
        color = ctypes.c_int(0x00301E14)  # Exact match to app background #141E30
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWA_CAPTION_COLOR,
            ctypes.byref(color),
            ctypes.sizeof(color)
        )
        
        # Set border color
        border_color = ctypes.c_int(0x00301E14)  # Same color as title bar
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWA_BORDER_COLOR,
            ctypes.byref(border_color),
            ctypes.sizeof(border_color)
        )
        
    except Exception as e:
        print(f"Could not customize title bar: {e}") 