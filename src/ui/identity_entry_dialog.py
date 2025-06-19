"""
Identity Entry Dialog
Dialog for adding and editing identity entries.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QMessageBox, QFormLayout, QTextEdit, QScrollArea, QWidget, QCheckBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

from ..models import IdentityEntry
from .file_attachment_widget import FileAttachmentWidget
from ..utils import apply_custom_title_bar


class IdentityEntryDialog(QDialog):
    """Dialog for adding and editing identity entries."""
    
    def __init__(self, identity_entry: IdentityEntry = None, parent=None):
        super().__init__(parent)
        self.identity_entry = identity_entry
        self.setup_ui()
        if identity_entry:
            self.load_identity_data()
        # Apply custom title bar after setup
        QTimer.singleShot(100, self.customize_title_bar)
    
    def setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle("Add Identity" if not self.identity_entry else "Edit Identity")
        self.setModal(True)
        self.resize(600, 800)  # Increased height to accommodate file attachments
        
        # Create scroll area for the form
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        
        # Create widget to hold the form
        form_widget = QWidget()
        layout = QVBoxLayout(form_widget)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Title
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("e.g., Personal Identity, Work Identity")
        form_layout.addRow("Title:", self.title_edit)
        
        # Personal Information Section
        personal_label = QLabel("Personal Information")
        personal_label.setFont(QFont("Arial", 12, QFont.Bold))
        personal_label.setStyleSheet("color: #0078D7; margin-top: 10px;")
        form_layout.addRow(personal_label)
        
        # First Name
        self.first_name_edit = QLineEdit()
        self.first_name_edit.setPlaceholderText("John")
        form_layout.addRow("First Name:", self.first_name_edit)
        
        # Last Name
        self.last_name_edit = QLineEdit()
        self.last_name_edit.setPlaceholderText("Doe")
        form_layout.addRow("Last Name:", self.last_name_edit)
        
        # Email
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("john.doe@example.com")
        form_layout.addRow("Email:", self.email_edit)
        
        # Phone
        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText("+1 (555) 123-4567")
        form_layout.addRow("Phone:", self.phone_edit)
        
        # Date of Birth
        self.dob_edit = QLineEdit()
        self.dob_edit.setPlaceholderText("MM/DD/YYYY")
        form_layout.addRow("Date of Birth:", self.dob_edit)
        
        # Address Section
        address_label = QLabel("Address Information")
        address_label.setFont(QFont("Arial", 12, QFont.Bold))
        address_label.setStyleSheet("color: #0078D7; margin-top: 10px;")
        form_layout.addRow(address_label)
        
        # Address
        self.address_edit = QLineEdit()
        self.address_edit.setPlaceholderText("123 Main Street")
        form_layout.addRow("Address:", self.address_edit)
        
        # City
        self.city_edit = QLineEdit()
        self.city_edit.setPlaceholderText("New York")
        form_layout.addRow("City:", self.city_edit)
        
        # State
        self.state_edit = QLineEdit()
        self.state_edit.setPlaceholderText("NY")
        form_layout.addRow("State:", self.state_edit)
        
        # Zip Code
        self.zip_code_edit = QLineEdit()
        self.zip_code_edit.setPlaceholderText("10001")
        form_layout.addRow("Zip Code:", self.zip_code_edit)
        
        # Country
        self.country_edit = QLineEdit()
        self.country_edit.setPlaceholderText("United States")
        self.country_edit.setText("United States")
        form_layout.addRow("Country:", self.country_edit)
        
        # Government IDs Section
        gov_label = QLabel("Government IDs")
        gov_label.setFont(QFont("Arial", 12, QFont.Bold))
        gov_label.setStyleSheet("color: #0078D7; margin-top: 10px;")
        form_layout.addRow(gov_label)
        
        # Social Security Number
        self.ssn_edit = QLineEdit()
        self.ssn_edit.setPlaceholderText("123-45-6789")
        self.ssn_edit.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Social Security Number:", self.ssn_edit)
        
        # Driver License
        self.driver_license_edit = QLineEdit()
        self.driver_license_edit.setPlaceholderText("DL123456789")
        form_layout.addRow("Driver License:", self.driver_license_edit)
        
        # Passport Number
        self.passport_edit = QLineEdit()
        self.passport_edit.setPlaceholderText("P123456789")
        form_layout.addRow("Passport Number:", self.passport_edit)
        
        # Category
        self.category_edit = QLineEdit()
        self.category_edit.setPlaceholderText("Identity")
        self.category_edit.setText("Identity")
        form_layout.addRow("Category:", self.category_edit)
        
        # Notes
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(100)
        self.notes_edit.setPlaceholderText("Additional notes about this identity...")
        form_layout.addRow("Notes:", self.notes_edit)
        
        layout.addLayout(form_layout)
        
        # File Attachments Section
        file_label = QLabel("File Attachments")
        file_label.setFont(QFont("Arial", 12, QFont.Bold))
        file_label.setStyleSheet("color: #0078D7; margin-top: 10px;")
        layout.addWidget(file_label)
        
        # File attachment widget
        self.file_attachment_widget = FileAttachmentWidget()
        layout.addWidget(self.file_attachment_widget)
        
        # Favorite Checkbox (moved below file attachments)
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
    
    def load_identity_data(self):
        """Load existing identity data into the form."""
        if self.identity_entry:
            self.title_edit.setText(self.identity_entry.title)
            self.first_name_edit.setText(self.identity_entry.first_name)
            self.last_name_edit.setText(self.identity_entry.last_name)
            self.email_edit.setText(self.identity_entry.email)
            self.phone_edit.setText(self.identity_entry.phone)
            self.dob_edit.setText(self.identity_entry.date_of_birth)
            self.address_edit.setText(self.identity_entry.address)
            self.city_edit.setText(self.identity_entry.city)
            self.state_edit.setText(self.identity_entry.state)
            self.zip_code_edit.setText(self.identity_entry.zip_code)
            self.country_edit.setText(self.identity_entry.country)
            self.ssn_edit.setText(self.identity_entry.social_security_number)
            self.driver_license_edit.setText(self.identity_entry.driver_license)
            self.passport_edit.setText(self.identity_entry.passport_number)
            self.category_edit.setText(self.identity_entry.category)
            self.notes_edit.setPlainText(self.identity_entry.notes)
            self.favorite_checkbox.setChecked(self.identity_entry.is_favorite)
            
            # Load file attachments
            if hasattr(self.identity_entry, 'attached_files'):
                self.file_attachment_widget.load_files(self.identity_entry.attached_files)
    
    def handle_save(self):
        """Handle saving the identity entry."""
        title = self.title_edit.text().strip()
        first_name = self.first_name_edit.text().strip()
        last_name = self.last_name_edit.text().strip()
        email = self.email_edit.text().strip()
        phone = self.phone_edit.text().strip()
        dob = self.dob_edit.text().strip()
        address = self.address_edit.text().strip()
        city = self.city_edit.text().strip()
        state = self.state_edit.text().strip()
        zip_code = self.zip_code_edit.text().strip()
        country = self.country_edit.text().strip()
        ssn = self.ssn_edit.text().strip()
        driver_license = self.driver_license_edit.text().strip()
        passport = self.passport_edit.text().strip()
        category = self.category_edit.text().strip()
        notes = self.notes_edit.toPlainText().strip()
        is_favorite = self.favorite_checkbox.isChecked()
        
        # Get file attachments
        attached_files = self.file_attachment_widget.get_files()
        
        # Validation
        if not title:
            QMessageBox.warning(self, "Missing Information", "Please enter a title for the identity.")
            return
        
        if not first_name:
            QMessageBox.warning(self, "Missing Information", "Please enter the first name.")
            return
        
        if not last_name:
            QMessageBox.warning(self, "Missing Information", "Please enter the last name.")
            return
        
        # Create or update identity entry
        if self.identity_entry:
            # Update existing entry
            self.identity_entry.title = title
            self.identity_entry.first_name = first_name
            self.identity_entry.last_name = last_name
            self.identity_entry.email = email
            self.identity_entry.phone = phone
            self.identity_entry.date_of_birth = dob
            self.identity_entry.address = address
            self.identity_entry.city = city
            self.identity_entry.state = state
            self.identity_entry.zip_code = zip_code
            self.identity_entry.country = country
            self.identity_entry.social_security_number = ssn
            self.identity_entry.driver_license = driver_license
            self.identity_entry.passport_number = passport
            self.identity_entry.category = category
            self.identity_entry.notes = notes
            self.identity_entry.is_favorite = is_favorite
            self.identity_entry.attached_files = attached_files
        else:
            # Create new entry
            self.identity_entry = IdentityEntry(
                title=title,
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone=phone,
                address=address,
                city=city,
                state=state,
                zip_code=zip_code,
                country=country,
                date_of_birth=dob,
                social_security_number=ssn,
                driver_license=driver_license,
                passport_number=passport,
                category=category,
                notes=notes,
                is_favorite=is_favorite,
                attached_files=attached_files
            )
        
        self.accept() 

    def customize_title_bar(self):
        """Apply custom title bar styling using Windows API."""
        apply_custom_title_bar(self)

    def showEvent(self, event):
        super().showEvent(event)
        from PySide6.QtCore import QTimer
        QTimer.singleShot(100, self.customize_title_bar) 