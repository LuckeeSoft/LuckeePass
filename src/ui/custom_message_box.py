from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from ..utils import apply_custom_title_bar

class CustomMessageBox(QDialog):
    def __init__(self, title, message, icon=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(400)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Icon and message
        msg_layout = QHBoxLayout()
        if icon:
            icon_label = QLabel()
            icon_label.setPixmap(QIcon(icon).pixmap(48, 48))
            msg_layout.addWidget(icon_label, alignment=Qt.AlignTop)
        msg_label = QLabel(message)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet("font-size: 15px; color: #dce6f2;")
        msg_layout.addWidget(msg_label)
        layout.addLayout(msg_layout)

        # OK button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        ok_btn = QPushButton("OK")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)
        # Apply custom title bar
        QApplication.processEvents()
        apply_custom_title_bar(self) 