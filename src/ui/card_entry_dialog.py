"""
Card Entry Dialog
Dialog for adding and editing card entries.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QMessageBox, QComboBox, QFormLayout, QTextEdit, QCheckBox, QScrollArea, QWidget, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from ..models import CardEntry
from .file_attachment_widget import FileAttachmentWidget
from ..utils import apply_custom_title_bar


class CardEntryDialog(QDialog):
    """Dialog for adding and editing card entries."""
    
    def __init__(self, card_entry: CardEntry = None, parent=None):
        super().__init__(parent)
        self.card_entry = card_entry
        self.setup_ui()
        if card_entry:
            self.load_card_data()
        # Apply custom title bar after setup
        QTimer.singleShot(100, self.customize_title_bar)
    
    def setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle("Add Card" if not self.card_entry else "Edit Card")
        self.setModal(True)
        self.resize(500, 700)  # Increased height to accommodate file attachments
        
        # Create scroll area for the form
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setFrameShape(QScrollArea.NoFrame)

        # Create widget to hold the form
        form_widget = QWidget()
        layout = QVBoxLayout(form_widget)
        layout.setSpacing(8)  # Reduce vertical spacing between widgets
        layout.setContentsMargins(0, 0, 0, 0)  # Remove extra margins
        
        # Card Information Section Header
        card_info_label = QLabel("Card Information")
        card_info_label.setFont(QFont("Arial", 12, QFont.Bold))
        card_info_label.setStyleSheet("color: #0078D7; margin-top: 10px;")
        layout.addWidget(card_info_label)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Title
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("e.g., My Visa Card, Work Credit Card")
        form_layout.addRow("Title:", self.title_edit)
        
        # Card Type
        self.card_type_combo = QComboBox()
        self.card_type_combo.addItems(["Visa", "Mastercard", "American Express", "Discover", "Other"])
        self.card_type_combo.setEditable(True)
        form_layout.addRow("Card Type:", self.card_type_combo)
        
        # Card Number
        self.card_number_edit = QLineEdit()
        self.card_number_edit.setPlaceholderText("1234 5678 9012 3456")
        self.card_number_edit.setMaxLength(19)  # 16 digits + 3 spaces
        form_layout.addRow("Card Number:", self.card_number_edit)
        
        # Cardholder Name
        self.cardholder_name_edit = QLineEdit()
        self.cardholder_name_edit.setPlaceholderText("JOHN DOE")
        form_layout.addRow("Cardholder Name:", self.cardholder_name_edit)
        
        # Expiry Month
        self.expiry_month_combo = QComboBox()
        months = [f"{i:02d}" for i in range(1, 13)]
        self.expiry_month_combo.addItems(months)
        form_layout.addRow("Expiry Month:", self.expiry_month_combo)
        
        # Expiry Year
        self.expiry_year_combo = QComboBox()
        current_year = 2024
        years = [str(i) for i in range(current_year, current_year + 21)]
        self.expiry_year_combo.addItems(years)
        form_layout.addRow("Expiry Year:", self.expiry_year_combo)
        
        # CVV
        self.cvv_edit = QLineEdit()
        self.cvv_edit.setPlaceholderText("123")
        self.cvv_edit.setMaxLength(4)
        self.cvv_edit.setEchoMode(QLineEdit.Password)
        form_layout.addRow("CVV:", self.cvv_edit)
        
        # Category
        self.category_edit = QLineEdit()
        self.category_edit.setPlaceholderText("Cards")
        self.category_edit.setText("Cards")
        form_layout.addRow("Category:", self.category_edit)
        
        # Notes
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(80)  # Reduced height to make room for file attachments
        self.notes_edit.setPlaceholderText("Additional notes about this card...")
        form_layout.addRow("Notes:", self.notes_edit)
        
        layout.addLayout(form_layout)
        
        # File Attachments Section Header
        file_label = QLabel("File Attachments")
        file_label.setFont(QFont("Arial", 12, QFont.Bold))
        file_label.setStyleSheet("color: #0078D7; margin-top: 10px;")
        layout.addWidget(file_label)
        
        # File Attachments
        self.file_attachment_widget = FileAttachmentWidget()
        self.file_attachment_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        layout.addWidget(self.file_attachment_widget)
        
        # Favorite Checkbox (below file attachments)
        self.favorite_checkbox = QCheckBox("Favorite")
        layout.addWidget(self.favorite_checkbox)
        
        # Set the form widget as the scroll area's widget
        scroll_area.setWidget(form_widget)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll_area)

        # Buttons
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.handle_save)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078D7; color: white; border: none;
                padding: 10px 20px; border-radius: 4px; font-weight: bold;
            }
            QPushButton:hover { background-color: #005B9C; }
        """)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #6C757D; color: white; border: none;
                padding: 10px 20px; border-radius: 4px; font-weight: bold;
            }
            QPushButton:hover { background-color: #545B62; }
        """)
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
    
    def load_card_data(self):
        """Load existing card data into the form."""
        if self.card_entry:
            self.title_edit.setText(self.card_entry.title)
            
            # Set card type
            index = self.card_type_combo.findText(self.card_entry.card_type)
            if index >= 0:
                self.card_type_combo.setCurrentIndex(index)
            else:
                self.card_type_combo.setCurrentText(self.card_entry.card_type)
            
            self.card_number_edit.setText(self.card_entry.card_number)
            self.cardholder_name_edit.setText(self.card_entry.cardholder_name)
            
            # Set expiry month
            month_index = self.expiry_month_combo.findText(self.card_entry.expiry_month)
            if month_index >= 0:
                self.expiry_month_combo.setCurrentIndex(month_index)
            
            # Set expiry year
            year_index = self.expiry_year_combo.findText(self.card_entry.expiry_year)
            if year_index >= 0:
                self.expiry_year_combo.setCurrentIndex(year_index)
            
            self.cvv_edit.setText(self.card_entry.cvv)
            self.category_edit.setText(self.card_entry.category)
            self.notes_edit.setPlainText(self.card_entry.notes)
            self.favorite_checkbox.setChecked(self.card_entry.is_favorite)
            
            # Load attached files
            if hasattr(self.card_entry, 'attached_files'):
                self.file_attachment_widget.set_attached_files(self.card_entry.attached_files)
    
    def handle_save(self):
        """Handle saving the card entry."""
        title = self.title_edit.text().strip()
        card_type = self.card_type_combo.currentText().strip()
        card_number = self.card_number_edit.text().strip()
        cardholder_name = self.cardholder_name_edit.text().strip()
        expiry_month = self.expiry_month_combo.currentText()
        expiry_year = self.expiry_year_combo.currentText()
        cvv = self.cvv_edit.text().strip()
        category = self.category_edit.text().strip()
        notes = self.notes_edit.toPlainText().strip()
        is_favorite = self.favorite_checkbox.isChecked()
        
        # Validation
        if not title:
            QMessageBox.warning(self, "Missing Information", "Please enter a title for the card.")
            return
        
        if not card_type:
            QMessageBox.warning(self, "Missing Information", "Please select a card type.")
            return
        
        if not card_number:
            QMessageBox.warning(self, "Missing Information", "Please enter the card number.")
            return
        
        if not cardholder_name:
            QMessageBox.warning(self, "Missing Information", "Please enter the cardholder name.")
            return
        
        if not cvv:
            QMessageBox.warning(self, "Missing Information", "Please enter the CVV.")
            return
        
        # Create or update card entry
        if self.card_entry:
            # Update existing entry
            self.card_entry.title = title
            self.card_entry.card_type = card_type
            self.card_entry.card_number = card_number
            self.card_entry.cardholder_name = cardholder_name
            self.card_entry.expiry_month = expiry_month
            self.card_entry.expiry_year = expiry_year
            self.card_entry.cvv = cvv
            self.card_entry.category = category
            self.card_entry.notes = notes
            self.card_entry.is_favorite = is_favorite
            self.card_entry.attached_files = self.file_attachment_widget.get_files()
        else:
            # Create new entry
            self.card_entry = CardEntry(
                title=title,
                card_type=card_type,
                card_number=card_number,
                cardholder_name=cardholder_name,
                expiry_month=expiry_month,
                expiry_year=expiry_year,
                cvv=cvv,
                category=category,
                notes=notes,
                is_favorite=is_favorite,
                attached_files=self.file_attachment_widget.get_files()
            )
        
        self.accept() 

    def customize_title_bar(self):
        """Apply custom title bar styling using Windows API."""
        apply_custom_title_bar(self)

    def showEvent(self, event):
        super().showEvent(event)
        from PySide6.QtCore import QTimer
        QTimer.singleShot(100, self.customize_title_bar) 