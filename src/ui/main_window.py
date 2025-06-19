"""
Main Window
Main application window.
"""

import sys
import os
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTabWidget, QTableWidget, QTableWidgetItem,
    QMessageBox, QFileDialog, QGroupBox, QApplication, QDialog,
    QListWidget, QListWidgetItem, QStackedWidget, QMenu, QInputDialog,
    QCheckBox, QSizePolicy, QHeaderView, QMainWindow
)
from PySide6.QtGui import QIcon, QFont, QPixmap, QImage
from PySide6.QtCore import Qt, QTimer, QSettings

from ..core import UserManager, PasswordManager
from ..models import PasswordEntry, SecureNote, CardEntry, IdentityEntry
from .login_dialog import LoginDialog
from .password_entry_dialog import PasswordEntryDialog
from .secure_note_dialog import SecureNoteDialog
from .card_entry_dialog import CardEntryDialog
from .identity_entry_dialog import IdentityEntryDialog
from .welcome_dialog import WelcomeDialog
from .startup_choice_dialog import StartupChoiceDialog
from .welcome_back_dialog import WelcomeBackDialog
from .custom_message_box import CustomMessageBox
from src.utils.resource_path import resource_path, get_appdata_path
from src.utils.formatting import format_card_number, format_phone_number


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.user_manager = UserManager()
        self.password_manager = None

        # Initialize table attributes to None to ensure they exist before use
        self.password_table = None
        self.notes_table = None
        self.cards_table = None
        self.identities_table = None
        self.favorites_table = None

        # Initialize settings for saving column widths
        self.settings = QSettings("LuckeePass", "ColumnSizes")

        self.setup_ui()
        # Center the main window on the screen
        qr = self.frameGeometry()
        cp = QApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        self.show_login_dialog()
    
    def save_data_with_status(self):
        """Save data and update status bar."""
        try:
            self.password_manager.save_data()
            self.statusBar().showMessage("Data saved successfully", 3000)  # Show for 3 seconds
        except Exception as e:
            self.statusBar().showMessage(f"Save error: {str(e)}", 5000)
            QMessageBox.warning(
                self, "Save Error",
                f"Failed to save data:\n{str(e)}"
            )
    
    def setup_ui(self):
        """Setup the main user interface."""
        self.setWindowTitle("LuckeePass")
        self.setGeometry(100, 100, 900, 500)  # Revert to original geometry for resizable window
        self.setMinimumSize(600, 400)  # Keep minimum size
        
        # Set application icon
        icon = QIcon(resource_path("images/luckeepasslogo.png"))
        self.setWindowIcon(icon)
        
        # Use default window decorations, allow resizing from edges
        self.setWindowFlags(Qt.Window)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main horizontal layout for sidebar and content
        main_h_layout = QHBoxLayout(central_widget)
        main_h_layout.setContentsMargins(0, 0, 0, 0)
        main_h_layout.setSpacing(0)
        
        # Left Sidebar for navigation and search
        sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_widget)
        sidebar_layout.setContentsMargins(0, 10, 0, 0)  # Add 10px top margin for padding under title bar
        sidebar_layout.setSpacing(5)
        sidebar_widget.setFixedWidth(150) # Set fixed width for the sidebar widget
        
        # Global Search Bar in sidebar
        self.global_search_edit = QLineEdit()
        self.global_search_edit.setPlaceholderText("Search Vault")
        self.global_search_edit.textChanged.connect(self.global_search)
        self.global_search_edit.setStyleSheet("padding: 5px; border-radius: 3px; border: 1px solid #3A4C60; background-color: #1E2B38; color: white;") # Added stylesheet for padding and styling
        sidebar_layout.addWidget(self.global_search_edit)
        
        # Navigation list in sidebar
        self.sidebar_list = QListWidget()
        self.sidebar_list.setFixedWidth(150) # Set fixed width for the sidebar list
        self.sidebar_list.setStyleSheet("""
            QListWidget {
                background-color: #2D3E50;
                border: 1px solid #1E2B38;
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px 5px;
                border-bottom: 1px solid #3A4C60;
                color: #ECF0F1;
            }
            QListWidget::item:selected {
                background-color: #0078D7;
                color: white;
                border-radius: 3px;
            }
            QListWidget::item:hover:!selected {
                background-color: #4A637C;
            }
        """)
        sidebar_layout.addWidget(self.sidebar_list)
        
        main_h_layout.addWidget(sidebar_widget)
        
        # Right content area (stacked widget)
        self.content_stack = QStackedWidget()
        self.content_stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_h_layout.addWidget(self.content_stack)
        
        # Setup tabs (now content widgets) and add to sidebar and stack with icons
        # Reorder: Favorites first, then Logins (renamed from Passwords)
        self.content_stack.addWidget(self.setup_favorites_tab())
        favorites_item = QListWidgetItem(QIcon(resource_path("images/favorite.svg")), "Favorites")
        self.sidebar_list.addItem(favorites_item)
        
        self.content_stack.addWidget(self.setup_passwords_tab())
        passwords_item = QListWidgetItem(QIcon(resource_path("images/key.svg")), "Logins")
        self.sidebar_list.addItem(passwords_item)
        
        self.content_stack.addWidget(self.setup_cards_tab())
        cards_item = QListWidgetItem(QIcon(resource_path("images/card.svg")), "Cards")
        self.sidebar_list.addItem(cards_item)
        
        self.content_stack.addWidget(self.setup_identities_tab())
        identities_item = QListWidgetItem(QIcon(resource_path("images/id.svg")), "Identities")
        self.sidebar_list.addItem(identities_item)
        
        self.content_stack.addWidget(self.setup_notes_tab())
        notes_item = QListWidgetItem(QIcon(resource_path("images/note.svg")), "Secure Notes")
        self.sidebar_list.addItem(notes_item)
        
        self.content_stack.addWidget(self.setup_settings_tab())
        settings_item = QListWidgetItem(QIcon(resource_path("images/setting.svg")), "Settings")
        self.sidebar_list.addItem(settings_item)
        
        self.content_stack.addWidget(self.setup_about_tab())
        about_item = QListWidgetItem(QIcon(resource_path("images/about.svg")), "About")
        self.sidebar_list.addItem(about_item)
        
        # Connect sidebar navigation to stacked widget
        self.sidebar_list.currentRowChanged.connect(self.content_stack.setCurrentIndex)
        
        # Set initial selection to Favorites (now first)
        self.sidebar_list.setCurrentRow(0)
        
        # Connect global search to the centralized button state update
        self.global_search_edit.textChanged.connect(self.update_new_button_state)
        # Set initial button states
        self.update_new_button_state()
        
        # Status bar
        self.statusBar().showMessage("Ready")
        # Disable the size grip in the status bar to remove the bottom-right handle
        self.statusBar().setSizeGripEnabled(False)

        # Defer column persistence setup to ensure all tables are initialized
        QTimer.singleShot(0, self.setup_table_column_persistence)

    def setup_table_column_persistence(self):
        """Sets up persistence for column widths of all tables."""
        table_keys = [
            "password_table",
            "notes_table",
            "cards_table",
            "identities_table",
            "favorites_table",
        ]

        for key_str in table_keys:
            table = getattr(self, key_str)
            if table is not None:
                self.load_column_widths(table, key_str)
                table.horizontalHeader().sectionResized.connect(
                    lambda logicalIndex, oldSize, newSize, table_obj=table, table_key=key_str:
                        self.save_column_widths(table_obj, table_key)
                )

    def save_column_widths(self, table: QTableWidget, settings_key: str):
        """Save the current column widths of a QTableWidget."""
        header = table.horizontalHeader()
        column_widths = [header.sectionSize(i) for i in range(header.count())]
        self.settings.setValue(settings_key, column_widths)

    def load_column_widths(self, table: QTableWidget, settings_key: str):
        """Load and apply saved column widths to a QTableWidget."""
        column_widths = self.settings.value(settings_key)
        if column_widths and isinstance(column_widths, list):
            header = table.horizontalHeader()
            for i, width in enumerate(column_widths):
                if i < header.count():
                    header.resizeSection(i, int(width))

    def closeEvent(self, event):
        """Override close event to save column widths."""
        table_keys = [
            "password_table",
            "notes_table",
            "cards_table",
            "identities_table",
            "favorites_table",
        ]
        for key_str in table_keys:
            table = getattr(self, key_str)
            if table is not None:
                self.save_column_widths(table, key_str)
        super().closeEvent(event)

    def create_new_button(self, action_function):
        """Create a + New button with the specified action."""
        new_button = QPushButton("+ New")
        new_button.setFixedSize(70, 30)
        new_button.setStyleSheet("""
            QPushButton {
                background-color: #0078D7;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #005B9C;
            }
            QPushButton:pressed {
                background-color: #004578;
            }
        """)
        new_button.clicked.connect(action_function)
        return new_button
    
    def update_new_button_state(self):
        """Update the + New button state based on current tab and search status."""
        current_tab_index = self.content_stack.currentIndex()
        is_search_active = bool(self.global_search_edit.text().strip())
        
        # This method is now a placeholder since buttons are individual
        # The state will be managed by each individual button
        pass

    def show_login_dialog(self):
        """Show login dialog to authenticate user."""
        # Check if this is a new user (no master password set)
        if not self.user_manager.is_master_password_set():
            # Show startup choice dialog for new users
            choice_dialog = StartupChoiceDialog(self)
            
            if choice_dialog.exec() == QDialog.Accepted:
                if choice_dialog.choice == 'new':
                    # User wants to create a new vault
                    self.handle_new_vault_creation()
                elif choice_dialog.choice == 'restore':
                    # User wants to restore from existing file
                    self.handle_vault_restoration()
                else:
                    sys.exit()
            else:
                sys.exit()
        else:
            # Show login dialog for existing users
            dialog = LoginDialog(self.user_manager, self)
            
            if dialog.exec() == QDialog.Accepted:
                self.password_manager = PasswordManager(dialog.master_password, self.user_manager)
                self.password_manager.data_file = get_appdata_path("luckeepass_data.lp")
                self.setWindowTitle("LuckeePass")
                
                # Check if there are old JSON files that need to be converted
                self.convert_old_json_data()
                
                # Load existing data
                try:
                    self.password_manager.load_data()
                    self.refresh_data()
                    if len(self.password_manager.passwords) == 0 and len(self.password_manager.notes) == 0 and len(self.password_manager.cards) == 0 and len(self.password_manager.identities) == 0:
                        self.statusBar().showMessage("Ready to add logins, notes, cards, and identities")
                    else:
                        self.statusBar().showMessage(f"Loaded {len(self.password_manager.passwords)} logins, {len(self.password_manager.notes)} notes, {len(self.password_manager.cards)} cards, and {len(self.password_manager.identities)} identities")
                except Exception as e:
                    print(f"Error loading data: {str(e)}")
                    self.handle_data_loading_issue()
            else:
                sys.exit()

    def handle_new_vault_creation(self):
        """Handle creation of a new vault."""
        # Show welcome dialog for new users
        dialog = WelcomeDialog(self.user_manager, self)
        
        if dialog.exec() == QDialog.Accepted:
            self.password_manager = PasswordManager(dialog.master_password, self.user_manager)
            self.password_manager.data_file = get_appdata_path("luckeepass_data.lp")
            self.setWindowTitle("LuckeePass")
            
            # Load existing data (should be empty for new users)
            try:
                self.password_manager.load_data()
                self.refresh_data()
                self.statusBar().showMessage("Welcome! Ready to add your first logins, notes, cards, and identities")
            except Exception as e:
                print(f"Error loading data: {str(e)}")
                self.handle_data_loading_issue()
        else:
            sys.exit()

    def handle_vault_restoration(self):
        """Handle restoration of vault from existing file."""
        # Show welcome back dialog for restoration
        dialog = WelcomeBackDialog(self.user_manager, self)
        
        if dialog.exec() == QDialog.Accepted:
            self.password_manager = dialog.password_manager
            self.setWindowTitle("LuckeePass")
            
            # Refresh the data display
            self.refresh_data()
            
            # Show success message
            total_items = (len(self.password_manager.passwords) + 
                          len(self.password_manager.notes) + 
                          len(self.password_manager.cards) + 
                          len(self.password_manager.identities))
            
            if total_items > 0:
                self.statusBar().showMessage(f"Successfully restored {total_items} items to your vault")
            else:
                self.statusBar().showMessage("Vault restored successfully. Ready to add new items.")
        else:
            sys.exit()

    def convert_old_json_data(self):
        """Convert old JSON data files to the new LP format if they exist."""
        import json
        import os
        
        # Check for old JSON data files
        json_files = ["luckeepass_data.json", "luckeepass_data.json.backup"]
        converted_data = False
        
        for json_file in json_files:
            if os.path.exists(json_file):
                try:
                    with open(json_file, 'r') as f:
                        data = json.load(f)
                    
                    # Check if this is a valid LuckeePass data file
                    if data.get('app_name') == 'LuckeePass':
                        print(f"Found old JSON data file: {json_file}")
                        
                        # Convert the data to the new format
                        if 'passwords' in data and data['passwords']:
                            for entry_data in data['passwords']:
                                # Create PasswordEntry objects from the JSON data
                                from ..models import PasswordEntry
                                entry = PasswordEntry(
                                    title=entry_data.get('title', ''),
                                    username=entry_data.get('username', ''),
                                    password=entry_data.get('password', ''),
                                    url=entry_data.get('url', ''),
                                    notes=entry_data.get('notes', ''),
                                    category=entry_data.get('category', 'General'),
                                    is_favorite=entry_data.get('is_favorite', False)
                                )
                                # Set timestamps if they exist
                                if 'created' in entry_data:
                                    entry.created = entry_data['created']
                                if 'modified' in entry_data:
                                    entry.modified = entry_data['modified']
                                
                                self.password_manager.passwords.append(entry)
                                self.password_manager.categories.add(entry.category)
                        
                        if 'notes' in data and data['notes']:
                            for note_data in data['notes']:
                                # Create SecureNote objects from the JSON data
                                from ..models import SecureNote
                                note = SecureNote(
                                    title=note_data.get('title', ''),
                                    content=note_data.get('content', ''),
                                    category=note_data.get('category', 'General'),
                                    is_favorite=note_data.get('is_favorite', False)
                                )
                                # Set timestamps if they exist
                                if 'created' in note_data:
                                    note.created = note_data['created']
                                if 'modified' in note_data:
                                    note.modified = note_data['modified']
                                
                                self.password_manager.notes.append(note)
                                self.password_manager.categories.add(note.category)
                        
                        if 'cards' in data and data['cards']:
                            for card_data in data['cards']:
                                # Create CardEntry objects from the JSON data
                                from ..models import CardEntry
                                card = CardEntry(
                                    title=card_data.get('title', ''),
                                    card_type=card_data.get('card_type', ''),
                                    card_number=card_data.get('card_number', ''),
                                    cardholder_name=card_data.get('cardholder_name', ''),
                                    expiry_month=card_data.get('expiry_month', ''),
                                    expiry_year=card_data.get('expiry_year', ''),
                                    cvv=card_data.get('cvv', ''),
                                    notes=card_data.get('notes', ''),
                                    category=card_data.get('category', 'Cards'),
                                    is_favorite=card_data.get('is_favorite', False)
                                )
                                # Set timestamps if they exist
                                if 'created' in card_data:
                                    card.created = card_data['created']
                                if 'modified' in card_data:
                                    card.modified = card_data['modified']
                                
                                self.password_manager.cards.append(card)
                                self.password_manager.categories.add(card.category)
                        
                        if 'identities' in data and data['identities']:
                            for identity_data in data['identities']:
                                # Create IdentityEntry objects from the JSON data
                                from ..models import IdentityEntry
                                identity = IdentityEntry(
                                    title=identity_data.get('title', ''),
                                    first_name=identity_data.get('first_name', ''),
                                    last_name=identity_data.get('last_name', ''),
                                    email=identity_data.get('email', ''),
                                    phone=identity_data.get('phone', ''),
                                    address=identity_data.get('address', ''),
                                    city=identity_data.get('city', ''),
                                    state=identity_data.get('state', ''),
                                    zip_code=identity_data.get('zip_code', ''),
                                    country=identity_data.get('country', ''),
                                    date_of_birth=identity_data.get('date_of_birth', ''),
                                    social_security_number=identity_data.get('social_security_number', ''),
                                    driver_license=identity_data.get('driver_license', ''),
                                    passport_number=identity_data.get('passport_number', ''),
                                    notes=identity_data.get('notes', ''),
                                    category=identity_data.get('category', 'Identity'),
                                    is_favorite=identity_data.get('is_favorite', False)
                                )
                                # Set timestamps if they exist
                                if 'created' in identity_data:
                                    identity.created = identity_data['created']
                                if 'modified' in identity_data:
                                    identity.modified = identity_data['modified']
                                
                                self.password_manager.identities.append(identity)
                                self.password_manager.categories.add(identity.category)
                        
                        if 'files' in data and data['files']:
                            for file_data in data['files']:
                                # Create FileEntry objects from the JSON data
                                from ..models import FileEntry
                                import base64
                                
                                # Decode base64 file data
                                file_bytes = base64.b64decode(file_data.get('file_data', ''))
                                
                                file_entry = FileEntry(
                                    title=file_data.get('title', ''),
                                    file_data=file_bytes,
                                    file_name=file_data.get('file_name', ''),
                                    file_type=file_data.get('file_type', ''),
                                    file_size=file_data.get('file_size', 0),
                                    category=file_data.get('category', 'Files'),
                                    notes=file_data.get('notes', ''),
                                    is_favorite=file_data.get('is_favorite', False)
                                )
                                # Set timestamps if they exist
                                if 'created' in file_data:
                                    file_entry.created = file_data['created']
                                if 'modified' in file_data:
                                    file_entry.modified = file_data['modified']
                                
                                self.password_manager.files.append(file_entry)
                                self.password_manager.categories.add(file_entry.category)
                        
                        converted_data = True
                        print(f"Successfully converted data from {json_file}")
                        
                        # Save the converted data in the new LP format
                        try:
                            self.password_manager.save_data()
                            print("Converted data saved in new LP format")
                            
                            # Optionally, rename the old JSON file to avoid confusion
                            backup_name = f"{json_file}.converted"
                            if not os.path.exists(backup_name):
                                os.rename(json_file, backup_name)
                                print(f"Renamed {json_file} to {backup_name}")
                            
                        except Exception as e:
                            print(f"Error saving converted data: {str(e)}")
                        
                        # Only convert from the first valid file found
                        break
                        
                except Exception as e:
                    print(f"Error converting {json_file}: {str(e)}")
                    continue
        
        if converted_data:
            self.statusBar().showMessage("Successfully converted old data format to new format", 5000)

    def handle_data_loading_issue(self):
        """Handle data loading issues gracefully."""
        reply = QMessageBox.question(
            self, "Data Loading Issue",
            "There was an issue loading your existing data. This might be due to:\n"
            "• Different master password\n"
            "• Corrupted data file\n"
            "• Incompatible data format\n\n"
            "Would you like to start with fresh data?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Clear any partially loaded data and start fresh
            self.password_manager.passwords = []
            self.password_manager.notes = []
            self.password_manager.cards = []
            self.password_manager.identities = []
            self.password_manager.files = []
            self.password_manager.categories = set()
            self.refresh_data()
            self.statusBar().showMessage("Started with fresh data")
        else:
            # User chose not to start fresh, exit the application
            sys.exit()

    def refresh_data(self):
        """Refresh all data displays."""
        self.refresh_passwords()
        self.refresh_notes()
        self.refresh_cards()
        self.refresh_identities()
        self.refresh_favorites()
    
    def refresh_passwords(self):
        """Refresh password table."""
        self.password_table.setRowCount(len(self.password_manager.passwords))
        col_count = self.password_table.columnCount()
        for i, entry in enumerate(self.password_manager.passwords):
            self.password_table.setItem(i, 0, QTableWidgetItem(entry.title))
            self.password_table.setItem(i, 1, QTableWidgetItem(entry.username))
            self.password_table.setItem(i, 2, QTableWidgetItem("*" * len(entry.password)))
            self.password_table.setItem(i, 3, QTableWidgetItem(entry.url))
            self.password_table.setItem(i, 4, QTableWidgetItem(entry.category))
            self.password_table.setItem(i, 5, QTableWidgetItem(entry.modified[:10]))
        # No per-item styling
    
    def refresh_notes(self):
        """Refresh notes table."""
        self.notes_table.setRowCount(len(self.password_manager.notes))
        col_count = self.notes_table.columnCount()
        for i, note in enumerate(self.password_manager.notes):
            self.notes_table.setItem(i, 0, QTableWidgetItem(note.title))
            self.notes_table.setItem(i, 1, QTableWidgetItem(note.category))
            self.notes_table.setItem(i, 2, QTableWidgetItem(note.modified[:10]))
        # No per-item styling
    
    def refresh_cards(self):
        """Refresh cards table."""
        self.cards_table.setRowCount(len(self.password_manager.cards))
        col_count = self.cards_table.columnCount()
        for i, card in enumerate(self.password_manager.cards):
            self.cards_table.setItem(i, 0, QTableWidgetItem(card.title))
            self.cards_table.setItem(i, 1, QTableWidgetItem(card.card_type))
            # Mask card number except last 4 digits, but format the visible part
            if card.card_number and len(card.card_number) >= 4:
                digits = ''.join(filter(str.isdigit, card.card_number))
                if len(digits) > 4:
                    masked = '**** ' * ((len(digits) - 1) // 4)
                    last4 = digits[-4:]
                    display_number = f"{masked}{last4}".strip()
                else:
                    display_number = digits
                display_number = format_card_number(display_number)
            else:
                display_number = card.card_number
            self.cards_table.setItem(i, 2, QTableWidgetItem(display_number))
            self.cards_table.setItem(i, 3, QTableWidgetItem(card.cardholder_name))
            self.cards_table.setItem(i, 4, QTableWidgetItem(f"{card.expiry_month}/{card.expiry_year}"))
            self.cards_table.setItem(i, 5, QTableWidgetItem(card.category))
            self.cards_table.setItem(i, 6, QTableWidgetItem(card.modified[:10]))
        # No per-item styling
    
    def refresh_identities(self):
        """Refresh identities table."""
        self.identities_table.setRowCount(len(self.password_manager.identities))
        col_count = self.identities_table.columnCount()
        for i, identity in enumerate(self.password_manager.identities):
            self.identities_table.setItem(i, 0, QTableWidgetItem(identity.title))
            full_name = f"{identity.first_name} {identity.last_name}".strip()
            self.identities_table.setItem(i, 1, QTableWidgetItem(full_name))
            self.identities_table.setItem(i, 2, QTableWidgetItem(identity.email))
            # Mask phone number except last 4 digits, but format the visible part
            if identity.phone and len(identity.phone) >= 4:
                digits = ''.join(filter(str.isdigit, identity.phone))
                if len(digits) > 4:
                    masked = '*' * (len(digits) - 4) + digits[-4:]
                    # Format as ***-***-1234 if possible
                    if len(masked) == 10:
                        display_phone = f"***-***-{masked[-4:]}"
                    else:
                        display_phone = masked
                else:
                    display_phone = digits
                display_phone = format_phone_number(display_phone)
            else:
                display_phone = identity.phone
            self.identities_table.setItem(i, 3, QTableWidgetItem(display_phone))
            self.identities_table.setItem(i, 4, QTableWidgetItem(identity.category))
            self.identities_table.setItem(i, 5, QTableWidgetItem(identity.modified[:10]))
        # No per-item styling
    
    def refresh_favorites(self):
        """Refresh favorites table."""
        self.favorites_table.setRowCount(len(self.password_manager.favorites))
        col_count = self.favorites_table.columnCount()
        for i, fav in enumerate(self.password_manager.favorites):
            self.favorites_table.setItem(i, 0, QTableWidgetItem(fav.title))
            self.favorites_table.setItem(i, 1, QTableWidgetItem(fav.type))
            self.favorites_table.setItem(i, 2, QTableWidgetItem(fav.category))
            self.favorites_table.setItem(i, 3, QTableWidgetItem(fav.modified[:10]))
        # No per-item styling
    
    def filter_passwords(self):
        """Filter passwords based on search text."""
        search_text = self.global_search_edit.text().lower()
        
        for i in range(self.password_table.rowCount()):
            title = self.password_table.item(i, 0).text().lower()
            username = self.password_table.item(i, 1).text().lower()
            url = self.password_table.item(i, 3).text().lower()
            category = self.password_table.item(i, 4).text().lower()
            
            if (search_text in title or search_text in username or 
                search_text in url or search_text in category):
                self.password_table.setRowHidden(i, False)
            else:
                self.password_table.setRowHidden(i, True)
    
    def filter_notes(self):
        """Filter notes based on search text."""
        search_text = self.global_search_edit.text().lower()
        
        for i in range(self.notes_table.rowCount()):
            title = self.notes_table.item(i, 0).text().lower()
            category = self.notes_table.item(i, 1).text().lower()
            
            if search_text in title or search_text in category:
                self.notes_table.setRowHidden(i, False)
            else:
                self.notes_table.setRowHidden(i, True)
    
    def filter_cards(self):
        """Filter cards based on search text."""
        search_text = self.global_search_edit.text().lower()
        
        for i in range(self.cards_table.rowCount()):
            title = self.cards_table.item(i, 0).text().lower()
            card_type = self.cards_table.item(i, 1).text().lower()
            cardholder = self.cards_table.item(i, 3).text().lower()
            category = self.cards_table.item(i, 5).text().lower()
            
            if (search_text in title or search_text in card_type or 
                search_text in cardholder or search_text in category):
                self.cards_table.setRowHidden(i, False)
            else:
                self.cards_table.setRowHidden(i, True)
    
    def filter_identities(self):
        """Filter identities based on search text."""
        search_text = self.global_search_edit.text().lower()
        
        for i in range(self.identities_table.rowCount()):
            title = self.identities_table.item(i, 0).text().lower()
            name = self.identities_table.item(i, 1).text().lower()
            email = self.identities_table.item(i, 2).text().lower()
            phone = self.identities_table.item(i, 3).text().lower()
            category = self.identities_table.item(i, 4).text().lower()
            
            if (search_text in title or search_text in name or 
                search_text in email or search_text in phone or 
                search_text in category):
                self.identities_table.setRowHidden(i, False)
            else:
                self.identities_table.setRowHidden(i, True)
    
    def add_password(self):
        """Add a new password entry."""
        dialog = PasswordEntryDialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.password_manager.add_password(dialog.get_entry())
            self.refresh_passwords()
            self.refresh_favorites() # Refresh favorites in case new item is favorited
            self.save_data_with_status()
    
    def edit_password(self):
        """Edit the selected password entry."""
        current_row = self.password_table.currentRow()
        if current_row >= 0:
            password = self.password_manager.passwords[current_row]
            dialog = PasswordEntryDialog(password, parent=self)
            if dialog.exec() == QDialog.Accepted:
                self.password_manager.update_password(current_row, dialog.get_entry())
                self.refresh_passwords()
                self.refresh_favorites() # Refresh favorites in case favorite status changed
                self.save_data_with_status()
        else:
            QMessageBox.warning(self, "No Selection", "Please select a login to edit.")
    
    def delete_password(self):
        """Delete the selected password entry."""
        current_row = self.password_table.currentRow()
        if current_row >= 0:
            reply = QMessageBox.question(
                self, "Delete Login",
                "Are you sure you want to delete this login?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.password_manager.delete_password(current_row)
                self.refresh_passwords()
                self.refresh_favorites()
                self.save_data_with_status()
        else:
            QMessageBox.warning(self, "No Selection", "Please select a login to delete.")
    
    def copy_password(self):
        """Copy the selected password to clipboard."""
        current_row = self.password_table.currentRow()
        if current_row >= 0:
            password = self.password_manager.passwords[current_row]
            clipboard = QApplication.clipboard()
            clipboard.setText(password.password) # Copy actual password
            self.statusBar().showMessage("Password copied to clipboard", 2000)
        else:
            QMessageBox.warning(self, "No Selection", "Please select a login to copy.")
    
    def add_note(self):
        """Add a new secure note entry."""
        dialog = SecureNoteDialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.password_manager.add_note(dialog.get_note())
            self.refresh_notes()
            self.refresh_favorites() # Refresh favorites in case new item is favorited
            self.save_data_with_status()
    
    def edit_note(self):
        """Edit the selected secure note entry."""
        current_row = self.notes_table.currentRow()
        if current_row >= 0:
            note = self.password_manager.notes[current_row]
            dialog = SecureNoteDialog(note, parent=self)
            if dialog.exec() == QDialog.Accepted:
                self.password_manager.update_note(current_row, dialog.get_note())
                self.refresh_notes()
                self.refresh_favorites() # Refresh favorites in case favorite status changed
                self.save_data_with_status()
        else:
            QMessageBox.warning(self, "No Selection", "Please select a secure note to edit.")
    
    def delete_note(self):
        """Delete the selected secure note entry."""
        current_row = self.notes_table.currentRow()
        if current_row >= 0:
            reply = QMessageBox.question(
                self, "Delete Secure Note",
                "Are you sure you want to delete this secure note?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.password_manager.delete_note(current_row)
                self.refresh_notes()
                self.refresh_favorites()
                self.save_data_with_status()
        else:
            QMessageBox.warning(self, "No Selection", "Please select a secure note to delete.")
    
    def copy_note(self):
        """Copy the selected note content to clipboard."""
        current_row = self.notes_table.currentRow()
        if current_row >= 0:
            note = self.password_manager.notes[current_row]
            clipboard = QApplication.clipboard()
            clipboard.setText(note.content)
            self.statusBar().showMessage("Note content copied to clipboard", 2000)
        else:
            QMessageBox.warning(self, "No Selection", "Please select a secure note to copy.")
    
    def clear_corrupted_data(self):
        """Simulates clearing corrupted data, used for testing recovery paths."""
        reply = QMessageBox.question(
            self, "Clear Corrupted Data",
            "This will simulate clearing corrupted data. This action is irreversible. Proceed?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                # Delete the main data file
                if os.path.exists(self.password_manager.data_file):
                    os.remove(self.password_manager.data_file)
                    # Optionally delete salt file if it's separate and needs to be reset
                    salt_file = get_appdata_path("luckeepass_vault_salt.dat")
                    if os.path.exists(salt_file):
                        os.remove(salt_file)

                    # Reset password manager internal state
                    self.password_manager.passwords = []
                    self.password_manager.notes = []
                    self.password_manager.cards = []
                    self.password_manager.identities = []
                    self.password_manager.files = []
                    self.password_manager.categories = set()

                    self.refresh_data()
                    self.statusBar().showMessage("Corrupted data simulated and cleared.", 3000)
                    QMessageBox.information(self, "Success", "Corrupted data cleared successfully. Application will now restart to ensure a clean state.")
                    QApplication.instance().quit() # Restart application
                else:
                    QMessageBox.information(self, "Info", "No data file found to clear.")

            except Exception as e:
                self.statusBar().showMessage(f"Failed to clear corrupted data: {str(e)}", 5000)
                QMessageBox.critical(self, "Error", f"Failed to clear corrupted data: {str(e)}")
        else:
            QMessageBox.information(self, "Cancelled", "Clearing corrupted data cancelled.")
    
    def delete_account(self):
        """Deletes the user's account and all associated data."""
        reply = QMessageBox.question(
            self, "Delete Account",
            "Are you absolutely sure you want to delete your LuckeePass account and all its data? This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No # Default to No to prevent accidental deletion
        )

        if reply == QMessageBox.Yes:
            # Require password confirmation
            password, ok = QInputDialog.getText(
                self, "Confirm Password", 
                "Please enter your master password to confirm account deletion:",
                QLineEdit.Password
            )
            
            if not ok:
                QMessageBox.information(self, "Cancelled", "Account deletion cancelled.")
                return
            
            if not password:
                QMessageBox.warning(self, "Invalid Password", "Password cannot be empty.")
                return
            
            # Verify the password
            try:
                if not self.user_manager.verify_master_password(password):
                    QMessageBox.critical(self, "Invalid Password", "Incorrect master password. Account deletion cancelled.")
                    return
            except Exception as e:
                QMessageBox.critical(self, "Password Verification Error", f"Error verifying password: {str(e)}")
                return
            
            # Final confirmation after password verification
            final_reply = QMessageBox.question(
                self, "Final Confirmation",
                "Password verified. This is your final warning: deleting your account will permanently remove ALL your data including:\n\n"
                "• All passwords and logins\n"
                "• All secure notes\n"
                "• All credit card information\n"
                "• All identity information\n"
                "• All favorites and categories\n\n"
                "This action CANNOT be undone. Are you absolutely certain?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if final_reply == QMessageBox.Yes:
                try:
                    self.user_manager.delete_user_data()
                    self.statusBar().showMessage("Account deleted successfully", 3000)
                    QMessageBox.information(self, "Success", "Your LuckeePass account and all associated data have been permanently deleted. The application will now close.")
                    
                    # Close the application
                    sys.exit()
                    
                except Exception as e:
                    QMessageBox.critical(
                        self, "Deletion Failed",
                        f"Failed to delete account data: {str(e)}"
                    )
            else:
                QMessageBox.information(self, "Cancelled", "Account deletion cancelled.")
        else:
            QMessageBox.information(self, "Cancelled", "Account deletion cancelled.")

    def configure_table_resizing(self, table: QTableWidget):
        """Configure table column resizing behavior."""
        # Set the table to resize columns to content by default
        table.horizontalHeader().setStretchLastSection(True)
        # Allow horizontal header to be resized
        table.horizontalHeader().setSectionsMovable(True)
        # Set resize mode to interactive for better user control
        table.horizontalHeader().setSectionResizeMode(table.horizontalHeader().count() - 1, QHeaderView.Stretch)
        
        # For other columns, use ResizeToContents initially, then allow user to resize
        for i in range(table.horizontalHeader().count() - 1):
            table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Interactive)

    def setup_passwords_tab(self):
        """Setup the passwords tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Top toolbar with centered title and + New button on the right
        toolbar_layout = QHBoxLayout()
        
        # Title with icon and label
        icon_label = QLabel()
        icon_label.setPixmap(QIcon(resource_path("images/key.svg")).pixmap(24, 24))
        icon_label.setStyleSheet("background: transparent;")
        text_label = QLabel("Logins")
        text_label.setFont(QFont("Jua", 20, QFont.Bold))
        text_label.setStyleSheet("color: #60A3D9; background: transparent; margin-bottom: 2px;")
        
        title_layout = QHBoxLayout()
        title_layout.setSpacing(8)
        title_layout.addWidget(icon_label)
        title_layout.addWidget(text_label)
        title_widget = QWidget()
        title_widget.setLayout(title_layout)
        
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(title_widget)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.create_new_button(self.add_password))
        layout.addLayout(toolbar_layout)
        
        # Password table
        self.password_table = QTableWidget()
        self.password_table.setShowGrid(True)
        self.password_table.setColumnCount(6)
        self.password_table.setHorizontalHeaderLabels([
            "Title", "Username", "Password", "URL", "Category", "Last Modified"
        ])
        self.password_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.password_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.password_table.itemDoubleClicked.connect(self.edit_password)
        self.password_table.verticalHeader().setVisible(False)
        
        # Configure table resizing behavior
        self.configure_table_resizing(self.password_table)
        
        # Set size policy to make table expand with window
        self.password_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Enable context menu for passwords table
        self.password_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.password_table.customContextMenuRequested.connect(self.show_password_context_menu)
        
        layout.addWidget(self.password_table)
        
        return tab

    def setup_notes_tab(self):
        """Setup the secure notes tab."""
        tab = QWidget()
        notes_tab_layout = QVBoxLayout(tab)
        
        notes_tab_layout.setSpacing(4)
        
        # Top toolbar with centered title and + New button on the right
        toolbar_layout = QHBoxLayout()
        
        icon_label = QLabel()
        icon_label.setPixmap(QIcon(resource_path("images/note.svg")).pixmap(24, 24))
        icon_label.setStyleSheet("background: transparent;")
        text_label = QLabel("Secure Notes")
        text_label.setFont(QFont("Jua", 20, QFont.Bold))
        text_label.setStyleSheet("color: #60A3D9; background: transparent; margin-bottom: 2px;")
        
        title_layout = QHBoxLayout()
        title_layout.setSpacing(8)
        title_layout.addWidget(icon_label)
        title_layout.addWidget(text_label)
        title_widget = QWidget()
        title_widget.setLayout(title_layout)
        
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(title_widget)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.create_new_button(self.add_note))
        notes_tab_layout.addLayout(toolbar_layout)
        
        self.notes_table = QTableWidget()
        self.notes_table.setShowGrid(True)
        self.notes_table.setColumnCount(3)
        self.notes_table.setHorizontalHeaderLabels(["Title", "Category", "Last Modified"])
        self.notes_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.notes_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.notes_table.verticalHeader().setVisible(False)
        
        # Configure table resizing behavior
        self.configure_table_resizing(self.notes_table)
        
        # Set size policy to make table expand with window
        self.notes_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        notes_tab_layout.addWidget(self.notes_table)

        self.notes_table.itemDoubleClicked.connect(self.edit_note)
        self.notes_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.notes_table.customContextMenuRequested.connect(self.show_note_context_menu)
        
        return tab

    def setup_cards_tab(self):
        """Setup the cards tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Top toolbar with centered title and + New button on the right
        toolbar_layout = QHBoxLayout()
        
        icon_label = QLabel()
        icon_label.setPixmap(QIcon(resource_path("images/card.svg")).pixmap(24, 24))
        icon_label.setStyleSheet("background: transparent;")
        text_label = QLabel("Cards")
        text_label.setFont(QFont("Jua", 20, QFont.Bold))
        text_label.setStyleSheet("color: #60A3D9; background: transparent; margin-bottom: 2px;")
        
        title_layout = QHBoxLayout()
        title_layout.setSpacing(8)
        title_layout.addWidget(icon_label)
        title_layout.addWidget(text_label)
        title_widget = QWidget()
        title_widget.setLayout(title_layout)
        
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(title_widget)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.create_new_button(self.add_card))
        layout.addLayout(toolbar_layout)
        
        # Cards table
        self.cards_table = QTableWidget()
        self.cards_table.setShowGrid(True)
        self.cards_table.setColumnCount(7)
        self.cards_table.setHorizontalHeaderLabels([
            "Title", "Card Type", "Card Number", "Cardholder", "Expiry", "Category", "Last Modified"
        ])
        self.cards_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.cards_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.cards_table.itemDoubleClicked.connect(self.edit_card)
        self.cards_table.verticalHeader().setVisible(False)
        
        # Configure table resizing behavior
        self.configure_table_resizing(self.cards_table)
        
        # Set size policy to make table expand with window
        self.cards_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Enable context menu for cards table
        self.cards_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.cards_table.customContextMenuRequested.connect(self.show_card_context_menu)
        
        layout.addWidget(self.cards_table)
        
        return tab

    def setup_identities_tab(self):
        """Setup the identities tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Top toolbar with centered title and + New button on the right
        toolbar_layout = QHBoxLayout()
        
        icon_label = QLabel()
        icon_label.setPixmap(QIcon(resource_path("images/id.svg")).pixmap(24, 24))
        icon_label.setStyleSheet("background: transparent;")
        text_label = QLabel("Identities")
        text_label.setFont(QFont("Jua", 20, QFont.Bold))
        text_label.setStyleSheet("color: #60A3D9; background: transparent; margin-bottom: 2px;")
        
        title_layout = QHBoxLayout()
        title_layout.setSpacing(8)
        title_layout.addWidget(icon_label)
        title_layout.addWidget(text_label)
        title_widget = QWidget()
        title_widget.setLayout(title_layout)
        
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(title_widget)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(self.create_new_button(self.add_identity))
        layout.addLayout(toolbar_layout)
        
        # Identities table
        self.identities_table = QTableWidget()
        self.identities_table.setShowGrid(True)
        self.identities_table.setColumnCount(6)
        self.identities_table.setHorizontalHeaderLabels([
            "Title", "Name", "Email", "Phone", "Category", "Last Modified"
        ])
        self.identities_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.identities_table.itemDoubleClicked.connect(self.edit_identity)
        self.identities_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.identities_table.verticalHeader().setVisible(False)
        
        # Configure table resizing behavior
        self.configure_table_resizing(self.identities_table)
        
        # Set size policy to make table expand with window
        self.identities_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Enable context menu for identities table
        self.identities_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.identities_table.customContextMenuRequested.connect(self.show_identity_context_menu)
        
        layout.addWidget(self.identities_table)
        
        return tab

    def setup_favorites_tab(self):
        """Setup the favorites tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        layout.setSpacing(4)
        
        # Top toolbar with centered title (no button)
        toolbar_layout = QHBoxLayout()
        
        icon_label = QLabel()
        icon_label.setPixmap(QIcon(resource_path("images/favorite.svg")).pixmap(24, 24))
        icon_label.setStyleSheet("background: transparent;")
        text_label = QLabel("Favorites")
        text_label.setFont(QFont("Jua", 20, QFont.Bold))
        text_label.setStyleSheet("color: #60A3D9; background: transparent; margin-bottom: 2px;")
        
        title_layout = QHBoxLayout()
        title_layout.setSpacing(8)
        title_layout.addWidget(icon_label)
        title_layout.addWidget(text_label)
        title_widget = QWidget()
        title_widget.setLayout(title_layout)
        
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(title_widget)
        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)
        
        # Favorites table
        self.favorites_table = QTableWidget()
        self.favorites_table.setShowGrid(True)
        self.favorites_table.setColumnCount(4)
        self.favorites_table.setHorizontalHeaderLabels([
            "Title", "Type", "Category", "Last Modified"
        ])
        self.favorites_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.favorites_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.favorites_table.itemDoubleClicked.connect(self.edit_favorite)
        self.favorites_table.verticalHeader().setVisible(False)
        
        # Configure table resizing behavior
        self.configure_table_resizing(self.favorites_table)
        
        # Set size policy to make table expand with window
        self.favorites_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Enable context menu for favorites table
        self.favorites_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.favorites_table.customContextMenuRequested.connect(self.show_favorite_context_menu)
        
        layout.addWidget(self.favorites_table)
        
        return tab

    def setup_settings_tab(self):
        """Setup the settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Settings Title (centered)
        settings_title_layout = QHBoxLayout()
        settings_title_layout.setSpacing(8)
        settings_icon = QLabel()
        settings_icon.setPixmap(QIcon(resource_path("images/setting.svg")).pixmap(24, 24))
        settings_icon.setStyleSheet("background: transparent;")
        settings_icon.setAlignment(Qt.AlignVCenter)
        settings_label = QLabel("Settings")
        settings_label.setFont(QFont("Jua", 20, QFont.Bold))
        settings_label.setStyleSheet("color: #60A3D9; background: transparent; margin-bottom: 2px;")
        settings_label.setAlignment(Qt.AlignVCenter)
        title_layout = QHBoxLayout()
        title_layout.setSpacing(8)
        title_layout.addWidget(settings_icon)
        title_layout.addWidget(settings_label)
        title_widget = QWidget()
        title_widget.setLayout(title_layout)
        settings_title_layout.addStretch()
        settings_title_layout.addWidget(title_widget)
        settings_title_layout.addStretch()
        layout.addLayout(settings_title_layout)

        # General Settings Section
        general_group = QGroupBox("General Settings")
        general_layout = QVBoxLayout(general_group)

        # Auto-save setting
        auto_save_checkbox = QCheckBox("Auto-save changes")
        auto_save_checkbox.setChecked(True)  # Default to enabled
        auto_save_checkbox.setStyleSheet("color: #ECF0F1;")
        general_layout.addWidget(auto_save_checkbox)

        # Clear clipboard setting
        clear_clipboard_checkbox = QCheckBox("Clear clipboard after 30 seconds")
        clear_clipboard_checkbox.setChecked(True)  # Default to enabled
        clear_clipboard_checkbox.setStyleSheet("color: #ECF0F1;")
        general_layout.addWidget(clear_clipboard_checkbox)

        layout.addWidget(general_group)

        # Data Management Section (already a QGroupBox)
        data_group = QGroupBox("Data Management")
        data_layout = QVBoxLayout()
        # Add sub-description
        data_desc = QLabel("Export your encrypted vault for backup, or import a LuckeePass .lp file to restore your data. Only LuckeePass .lp files are supported.")
        data_desc.setStyleSheet("color: #BDC3C7; font-size: 11px; margin-bottom: 8px;")
        data_desc.setWordWrap(True)
        data_layout.addWidget(data_desc)
        # Buttons side by side
        btn_layout = QHBoxLayout()
        self.export_btn = QPushButton("Export Data")
        self.export_btn.clicked.connect(self.export_data)
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #28A745; color: white; border: none;
                padding: 12px 0; border-radius: 4px; font-weight: bold;
            }
            QPushButton:hover { background-color: #218838; }
        """)
        self.export_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn_layout.addWidget(self.export_btn)
        self.import_btn = QPushButton("Import Data")
        self.import_btn.clicked.connect(self.import_data)
        self.import_btn.setStyleSheet("""
            QPushButton {
                background-color: #17A2B8; color: white; border: none;
                padding: 12px 0; border-radius: 4px; font-weight: bold;
            }
            QPushButton:hover { background-color: #138496; }
        """)
        self.import_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        btn_layout.addWidget(self.import_btn)
        btn_layout.setSpacing(12)
        data_layout.addLayout(btn_layout)
        data_group.setLayout(data_layout)
        layout.addWidget(data_group)

        # Delete Account Section
        delete_group = QGroupBox("Delete Account")
        delete_layout = QVBoxLayout(delete_group)
        delete_title = QLabel("Delete Account")
        delete_title.setFont(QFont("Arial", 13, QFont.Bold))
        delete_title.setStyleSheet("color: #60A3D9;")
        delete_layout.addWidget(delete_title, alignment=Qt.AlignCenter)

        delete_info = QLabel(
            "Permanently delete your LuckeePass account and all associated data. "
            "This action cannot be undone."
        )

        delete_info.setWordWrap(True)
        delete_info.setStyleSheet("color: #E74C3C;") # Red text for warning
        delete_layout.addWidget(delete_info)

        self.delete_account_btn = QPushButton("Delete My Account")
        self.delete_account_btn.clicked.connect(self.delete_account)
        self.delete_account_btn.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C; color: white; border: none;
                padding: 10px 20px; border-radius: 4px; font-weight: bold;
            }
            QPushButton:hover { background-color: #C0392B; }
        """)
        delete_layout.addWidget(self.delete_account_btn)

        layout.addWidget(delete_group)

        layout.addStretch(1) # Push content to the top

        tab.setLayout(layout)
        return tab

    def setup_about_tab(self):
        """Setup the about tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Logo
        self.logo_label_about = QLabel()
        pixmap = QPixmap(resource_path("images/luckeepasslogo.png"))
        if not pixmap.isNull():
            self.logo_label_about.setPixmap(pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.logo_label_about.setAlignment(Qt.AlignCenter)
            layout.addWidget(self.logo_label_about, alignment=Qt.AlignCenter)
        else:
            print("Failed to load luckeepasslogo.png for about tab")

        # About LuckeePass label
        about_label = QLabel("LuckeePass by LuckeeSoft")
        about_label.setFont(QFont("Jua", 24, QFont.Bold))
        about_label.setStyleSheet("color: #60A3D9; margin-bottom: 10px;")
        layout.addWidget(about_label, alignment=Qt.AlignCenter)

        # Version label
        version_label = QLabel("Version 1.0.0")
        version_label.setFont(QFont("Arial", 12))
        version_label.setStyleSheet("color: #ECF0F1; margin-bottom: 20px;")
        layout.addWidget(version_label, alignment=Qt.AlignCenter)

        # Description
        description_label = QLabel(
            "LuckeePass by LuckeeSoft is a robust and intuitive password manager designed to secure your digital life. "
            "It allows you to safely store and manage a wide range of sensitive information, "
            "including logins, secure notes, credit card details, and personal identities. "
            "With industry-standard strong encryption, your data remains private and protected, "
            "giving you peace of mind and simplifying your online experience."
        )
        description_label.setWordWrap(True)
        description_label.setFont(QFont("Arial", 10))
        description_label.setStyleSheet("color: #BDC3C7;")
        layout.addWidget(description_label)

        # Key Features Section
        features_label = QLabel("Key Features:")
        features_label.setFont(QFont("Arial", 11, QFont.Bold))
        features_label.setStyleSheet("color: #ECF0F1; margin-top: 20px; margin-bottom: 5px;")
        layout.addWidget(features_label, alignment=Qt.AlignCenter)

        features_text = QLabel(
            "• Strong Encryption: Your data is protected with advanced encryption standards.<br/>"
            "• Cross-Platform Compatibility: Access your vaults seamlessly across multiple operating systems.<br/>"
            "• User-Friendly Interface: Simple and intuitive design for effortless management.<br/>"
            "• Data Organization: Categorize and search your entries for quick access."
        )
        features_text.setWordWrap(True)
        features_text.setFont(QFont("Arial", 9))
        features_text.setStyleSheet("color: #BDC3C7;")
        layout.addWidget(features_text)

        # Ko-fi message
        kofi_label = QLabel(
            "A little support goes a long way! If you'd like to help me keep creating, you can do so at <a href=\"https://ko-fi.com/luckeesoft\" style=\"color: #60A3D9; text-decoration: none;\">ko-fi.com/luckeesoft</a>"
        )
        kofi_label.setOpenExternalLinks(True)
        kofi_label.setWordWrap(True)
        kofi_label.setFont(QFont("Arial", 10))
        kofi_label.setStyleSheet("color: #BDC3C7; margin-top: 20px;")
        layout.addWidget(kofi_label)

        layout.addStretch(1)
        
        return tab

    # Settings functionality methods
    def export_data(self):
        """Export data to a file."""
        if not self.password_manager:
            QMessageBox.warning(self, "No Data", "No data available to export.")
            return
        
        # Check if there's any data to export
        total_items = (len(self.password_manager.passwords) + 
                      len(self.password_manager.notes) + 
                      len(self.password_manager.cards) + 
                      len(self.password_manager.identities) + 
                      len(self.password_manager.files))
        
        if total_items == 0:
            QMessageBox.information(self, "No Data", "No data available to export.")
            return
        
        # Ask user where to save the backup file
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Export LuckeePass Data",
            f"luckeepass_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.lp",
            "LuckeePass Backup Files (*.lp);;All Files (*.*)"
        )
        
        if file_path:
            try:
                # Ensure the file has .lp extension
                if not file_path.lower().endswith('.lp'):
                    file_path += '.lp'
                
                # Export the data using PasswordManager's export method
                lp_data = self.password_manager.export_data()
                
                # Write to the selected file
                with open(file_path, 'wb') as f:
                    f.write(lp_data)
                
                self.statusBar().showMessage(f"Data exported successfully to: {file_path}", 5000)
                CustomMessageBox(
                    "Export Successful",
                    f"Your LuckeePass data has been successfully exported to:\n\n{file_path}\n\n"
                    f"Exported {len(self.password_manager.passwords)} logins, "
                    f"{len(self.password_manager.notes)} notes, "
                    f"{len(self.password_manager.cards)} cards, and "
                    f"{len(self.password_manager.identities)} identities.\n\n"
                    "Keep this backup file safe and secure!",
                    parent=self
                ).exec()
                
            except Exception as e:
                self.statusBar().showMessage(f"Export failed: {str(e)}", 5000)
                QMessageBox.critical(
                    self, 
                    "Export Failed",
                    f"Failed to export data:\n{str(e)}"
                )
    
    def import_data(self):
        """Import data from a file."""
        if not self.password_manager:
            QMessageBox.warning(self, "No Session", "Please log in first before importing data.")
            return
        
        # Ask user to select the backup file
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Import LuckeePass Data",
            "",
            "LuckeePass Backup Files (*.lp);;All Files (*.*)"
        )
        
        if file_path:
            try:
                # Check if it's a valid LuckeePass backup file
                if not self.password_manager.is_valid_lp_file(file_path):
                    QMessageBox.warning(
                        self, 
                        "Invalid File",
                        "The selected file is not a valid LuckeePass backup file.\n\n"
                        "Please select a .lp file that was created by LuckeePass."
                    )
                    return
                
                # Read the backup file
                with open(file_path, 'rb') as f:
                    lp_data = f.read()
                
                # Check if there's existing data and ask user what to do
                existing_items = (len(self.password_manager.passwords) + 
                                len(self.password_manager.notes) + 
                                len(self.password_manager.cards) + 
                                len(self.password_manager.identities) + 
                                len(self.password_manager.files))
                
                if existing_items > 0:
                    reply = QMessageBox(
                        self
                    )
                    reply.setWindowTitle("Existing Data Found")
                    reply.setText(f"You currently have {existing_items} items in your vault.\n\n"
                                  "How would you like to handle the import?")
                    reply.setInformativeText("• Replace: Delete all existing data and import from backup\n"
                                           "• Merge: Add imported data to existing data (duplicates may occur)\n"
                                           "• Cancel: Keep existing data unchanged")
                    reply.setIcon(QMessageBox.Question)

                    # Change the default button texts
                    replace_button = reply.addButton("Replace", QMessageBox.ButtonRole.AcceptRole)
                    merge_button = reply.addButton("Merge", QMessageBox.ButtonRole.ActionRole)
                    cancel_button = reply.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)

                    reply.exec() # Execute the dialog again with custom buttons

                    if reply.clickedButton() == cancel_button:
                        return
                    elif reply.clickedButton() == replace_button:
                        # Replace existing data
                        self.password_manager.passwords = []
                        self.password_manager.notes = []
                        self.password_manager.cards = []
                        self.password_manager.identities = []
                        self.password_manager.files = []
                        self.password_manager.categories = set()
                
                # Import the data
                self.password_manager.import_data(lp_data)
                
                # Refresh the UI
                self.refresh_data()
                
                # Save the imported data
                self.save_data_with_status()
                
                imported_items = (len(self.password_manager.passwords) + 
                                len(self.password_manager.notes) + 
                                len(self.password_manager.cards) + 
                                len(self.password_manager.identities) + 
                                len(self.password_manager.files))
                
                self.statusBar().showMessage(f"Data imported successfully: {imported_items} total items", 5000)
                QMessageBox.information(
                    self, 
                    "Import Successful",
                    f"LuckeePass data has been successfully imported!\n\n"
                    f"Imported {len(self.password_manager.passwords)} logins, "
                    f"{len(self.password_manager.notes)} notes, "
                    f"{len(self.password_manager.cards)} cards, and "
                    f"{len(self.password_manager.identities)} identities.\n\n"
                    f"Total items in vault: {imported_items}"
                )
                
            except Exception as e:
                self.statusBar().showMessage(f"Import failed: {str(e)}", 5000)
                QMessageBox.critical(
                    self, 
                    "Import Failed",
                    f"Failed to import data:\n{str(e)}\n\n"
                    "This might be due to:\n"
                    "• Different master password\n"
                    "• Corrupted backup file\n"
                    "• Incompatible file format"
                )

    def closeEvent(self, event):
        """Handle application close event."""
        if self.password_manager:
            try:
                self.password_manager.save_data()
                self.statusBar().showMessage("Data saved successfully")
            except Exception as e:
                QMessageBox.warning(
                    self, "Save Warning",
                    f"Could not save data before closing:\n{str(e)}"
                )
        event.accept()

    def add_card(self):
        """Add a new card entry."""
        dialog = CardEntryDialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.password_manager.add_card(dialog.card_entry)
            self.refresh_cards()
            self.refresh_favorites()  # Refresh favorites in case new item is favorited
            self.save_data_with_status()
    
    def edit_card(self):
        """Edit the selected card entry."""
        current_row = self.cards_table.currentRow()
        if current_row >= 0:
            card = self.password_manager.cards[current_row]
            dialog = CardEntryDialog(card, parent=self)
            if dialog.exec() == QDialog.Accepted:
                self.password_manager.update_card(current_row, dialog.card_entry)
                self.refresh_cards()
                self.refresh_favorites()  # Refresh favorites in case favorite status changed
                self.save_data_with_status()
        else:
            QMessageBox.warning(self, "No Selection", "Please select a card to edit.")
    
    def delete_card(self):
        """Delete the selected card entry."""
        current_row = self.cards_table.currentRow()
        if current_row >= 0:
            reply = QMessageBox.question(
                self, "Delete Card",
                "Are you sure you want to delete this card?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.password_manager.delete_card(current_row)
                self.refresh_cards()
                self.save_data_with_status()
        else:
            QMessageBox.warning(self, "No Selection", "Please select a card to delete.")
    
    def copy_card_number(self):
        """Copy the selected card number to clipboard."""
        current_row = self.cards_table.currentRow()
        if current_row >= 0:
            card = self.password_manager.cards[current_row]
            clipboard = QApplication.clipboard()
            clipboard.setText(card.card_number)
            self.statusBar().showMessage("Card number copied to clipboard", 2000)
        else:
            QMessageBox.warning(self, "No Selection", "Please select a card to copy.")
    
    def add_identity(self):
        """Add a new identity entry."""
        dialog = IdentityEntryDialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.password_manager.add_identity(dialog.identity_entry)
            self.refresh_identities()
            self.refresh_favorites()  # Refresh favorites in case new item is favorited
            self.save_data_with_status()
    
    def edit_identity(self):
        """Edit the selected identity entry."""
        current_row = self.identities_table.currentRow()
        if current_row >= 0:
            identity = self.password_manager.identities[current_row]
            dialog = IdentityEntryDialog(identity, parent=self)
            if dialog.exec() == QDialog.Accepted:
                self.password_manager.update_identity(current_row, dialog.identity_entry)
                self.refresh_identities()
                self.refresh_favorites()  # Refresh favorites in case favorite status changed
                self.save_data_with_status()
        else:
            QMessageBox.warning(self, "No Selection", "Please select an identity to edit.")
    
    def delete_identity(self):
        """Delete the selected identity entry."""
        current_row = self.identities_table.currentRow()
        if current_row >= 0:
            reply = QMessageBox.question(
                self, "Delete Identity",
                "Are you sure you want to delete this identity?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.password_manager.delete_identity(current_row)
                self.refresh_identities()
                self.save_data_with_status()
        else:
            QMessageBox.warning(self, "No Selection", "Please select an identity to delete.")
    
    def copy_identity_name(self):
        """Copy the selected identity name to clipboard."""
        current_row = self.identities_table.currentRow()
        if current_row >= 0:
            identity = self.password_manager.identities[current_row]
            full_name = f"{identity.first_name} {identity.last_name}".strip()
            clipboard = QApplication.clipboard()
            clipboard.setText(full_name)
            self.statusBar().showMessage("Name copied to clipboard", 2000)
        else:
            QMessageBox.warning(self, "No Selection", "Please select an identity to copy.")

    def add_file(self):
        """Add a new file entry."""
        dialog = FileEntryDialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            self.password_manager.add_file(dialog.file_entry)
            self.refresh_files()
            self.refresh_favorites()  # Refresh favorites in case new item is favorited
            self.save_data_with_status()
    
    def edit_file(self):
        """Edit the selected file entry."""
        current_row = self.files_table.currentRow()
        if current_row >= 0:
            file_entry = self.password_manager.files[current_row]
            dialog = FileEntryDialog(file_entry, parent=self)
            if dialog.exec() == QDialog.Accepted:
                self.password_manager.update_file(current_row, dialog.file_entry)
                self.refresh_files()
                self.refresh_favorites()  # Refresh favorites in case favorite status changed
                self.save_data_with_status()
        else:
            QMessageBox.warning(self, "No Selection", "Please select a file to edit.")
    
    def delete_file(self):
        """Delete the selected file entry."""
        current_row = self.files_table.currentRow()
        if current_row >= 0:
            reply = QMessageBox.question(
                self, "Delete File",
                "Are you sure you want to delete this file?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.password_manager.delete_file(current_row)
                self.refresh_files()
                self.refresh_favorites()
                self.save_data_with_status()
        else:
            QMessageBox.warning(self, "No Selection", "Please select a file to delete.")
    
    def copy_file(self):
        """Copy the selected file to a new location."""
        current_row = self.files_table.currentRow()
        if current_row >= 0:
            file_entry = self.password_manager.files[current_row]
            
            # Ask user where to save the file
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save File As", file_entry.file_name,
                f"All Files (*.*);;{file_entry.file_type} Files (*{file_entry.file_type})"
            )
            
            if file_path:
                try:
                    with open(file_path, 'wb') as f:
                        f.write(file_entry.file_data)
                    self.statusBar().showMessage(f"File saved to: {file_path}", 3000)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")
        else:
            QMessageBox.warning(self, "No Selection", "Please select a file to copy.")

    # Favorite methods
    def add_favorite(self):
        """Placeholder for adding a favorite. Favoriting is done via individual entry dialogs."""
        QMessageBox.information(self, "Add Favorite", "To favorite an item, please open its specific entry (Password, Note, Card, or Identity) and check the 'Favorite' checkbox.")

    def edit_favorite(self):
        """Edit the selected favorite item."""
        current_row = self.favorites_table.currentRow()
        if current_row >= 0:
            item_title = self.favorites_table.item(current_row, 0).text()
            item_type = self.favorites_table.item(current_row, 1).text()
            
            item_found = False
            if item_type == "Password":
                for i, item in enumerate(self.password_manager.passwords):
                    if item.title == item_title:
                        dialog = PasswordEntryDialog(item, parent=self)
                        if dialog.exec() == QDialog.Accepted:
                            updated_item = dialog.get_entry()
                            self.password_manager.update_password(i, updated_item)
                            self.save_data_with_status()
                            self.refresh_data()
                        item_found = True
                        break
            elif item_type == "Secure Note":
                for i, item in enumerate(self.password_manager.notes):
                    if item.title == item_title:
                        dialog = SecureNoteDialog(item, parent=self)
                        if dialog.exec() == QDialog.Accepted:
                            updated_item = dialog.get_note()
                            self.password_manager.update_note(i, updated_item)
                            self.save_data_with_status()
                            self.refresh_data()
                        item_found = True
                        break
            elif item_type == "Card":
                for i, item in enumerate(self.password_manager.cards):
                    if item.title == item_title:
                        dialog = CardEntryDialog(item, parent=self)
                        if dialog.exec() == QDialog.Accepted:
                            updated_item = dialog.card_entry
                            self.password_manager.update_card(i, updated_item)
                            self.save_data_with_status()
                            self.refresh_data()
                        item_found = True
                        break
            elif item_type == "Identity":
                for i, item in enumerate(self.password_manager.identities):
                    if item.title == item_title:
                        dialog = IdentityEntryDialog(item, parent=self)
                        if dialog.exec() == QDialog.Accepted:
                            updated_item = dialog.identity_entry
                            self.password_manager.update_identity(i, updated_item)
                            self.save_data_with_status()
                            self.refresh_data()
                        item_found = True
                        break
            
            if not item_found:
                QMessageBox.warning(self, "Item Not Found", "Selected favorite item could not be found for editing.")
        else:
            QMessageBox.warning(self, "No Selection", "Please select an item to edit.")
    
    def delete_favorite(self):
        """Delete the selected favorite item (unfavorite it)."""
        current_row = self.favorites_table.currentRow()
        if current_row >= 0:
            item_title = self.favorites_table.item(current_row, 0).text()
            item_type = self.favorites_table.item(current_row, 1).text()

            reply = QMessageBox.question(
                self, "Unfavorite Item",
                f"Are you sure you want to unfavorite this {item_type.lower()}?\n\nThis will remove it from your favorites list but not delete the original entry.",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                item_unfavorited = False
                if item_type == "Password":
                    for item in self.password_manager.passwords:
                        if item.title == item_title:
                            item.is_favorite = False
                            item_unfavorited = True
                            break
                elif item_type == "Secure Note":
                    for item in self.password_manager.notes:
                        if item.title == item_title:
                            item.is_favorite = False
                            item_unfavorited = True
                            break
                elif item_type == "Card":
                    for item in self.password_manager.cards:
                        if item.title == item_title:
                            item.is_favorite = False
                            item_unfavorited = True
                            break
                elif item_type == "Identity":
                    for item in self.password_manager.identities:
                        if item.title == item_title:
                            item.is_favorite = False
                            item_unfavorited = True
                            break

                if item_unfavorited:
                    self.save_data_with_status()
                    self.refresh_data()
                    QMessageBox.information(self, "Removed", "Item successfully removed from favorites.")
                else:
                    QMessageBox.warning(self, "Error", "Could not find item to unfavorite. Please refresh and try again.")
        else:
            QMessageBox.warning(self, "No Selection", "Please select a favorite item to remove.")

    def copy_favorite(self):
        """Copy content of the selected favorite item to clipboard based on its type."""
        current_row = self.favorites_table.currentRow()
        if current_row >= 0:
            item_title = self.favorites_table.item(current_row, 0).text()
            item_type = self.favorites_table.item(current_row, 1).text()

            clipboard = QApplication.clipboard()
            copied_content = ""
            
            if item_type == "Password":
                for item in self.password_manager.passwords:
                    if item.title == item_title:
                        copied_content = item.password
                        break
            elif item_type == "Secure Note":
                for item in self.password_manager.notes:
                    if item.title == item_title:
                        copied_content = item.content
                        break
            elif item_type == "Card":
                for item in self.password_manager.cards:
                    if item.title == item_title:
                        copied_content = item.card_number
                        break
            elif item_type == "Identity":
                for item in self.password_manager.identities:
                    if item.title == item_title:
                        # For identity, copy a common field, e.g., email or full name
                        copied_content = f"{item.first_name} {item.last_name}".strip()
                        break
            
            if copied_content:
                clipboard.setText(copied_content)
                self.statusBar().showMessage(f"{item_type} content copied to clipboard", 2000)
            elif not copied_content:
                QMessageBox.warning(self, "Copy Error", "No content available to copy for the selected favorite item.")
        else:
            QMessageBox.warning(self, "No Selection", "Please select a favorite item to copy.")

    def global_search(self):
        """Perform global search across all tables based on the currently active tab.
        This method is connected to the textChanged signal of self.global_search_edit.
        """
        current_tab_index = self.content_stack.currentIndex()
        if current_tab_index == 0: # Favorites tab
            self.filter_favorites()
        elif current_tab_index == 1: # Passwords tab
            self.filter_passwords()
        elif current_tab_index == 2: # Cards tab
            self.filter_cards()
        elif current_tab_index == 3: # Identities tab
            self.filter_identities()
        elif current_tab_index == 4: # Secure Notes tab
            self.filter_notes()
        # No search for About tab

        self.update_new_button_state() # Update button states after search filter applied

    def filter_favorites(self):
        """Filter favorites based on search text."""
        search_text = self.global_search_edit.text().lower()
        
        for i in range(self.favorites_table.rowCount()):
            title = self.favorites_table.item(i, 0).text().lower()
            item_type = self.favorites_table.item(i, 1).text().lower()
            category = self.favorites_table.item(i, 2).text().lower()
            
            if search_text in title or search_text in item_type or search_text in category:
                self.favorites_table.setRowHidden(i, False)
            else:
                self.favorites_table.setRowHidden(i, True)
    
    def update_all_toolbar_buttons_states(self):
        """Updates the enabled/disabled state of all toolbar buttons based on selection and search status."""
        # Logic for buttons (Add, Edit, Delete, Copy)
        # Add buttons are always enabled
        for btn in self.add_buttons:
            btn.setEnabled(True)
        
        # Edit/Delete/Copy buttons depend on selection in the active table and no search
        current_tab_index = self.content_stack.currentIndex()
        is_search_active = bool(self.global_search_edit.text().strip())

        # Define current table based on active tab
        current_table = None
        if current_tab_index == 0: # Favorites tab
            current_table = self.favorites_table
        elif current_tab_index == 1: # Passwords tab
            current_table = self.password_table
        elif current_tab_index == 2: # Cards tab
            current_table = self.cards_table
        elif current_tab_index == 3: # Identities tab
            current_table = self.identities_table
        elif current_tab_index == 4: # Secure Notes tab
            current_table = self.notes_table

        has_selection = current_table and current_table.currentRow() >= 0

        # Disable edit/delete/copy buttons if search is active or no selection
        for btn in self.edit_buttons + self.delete_buttons + self.copy_buttons:
            btn.setEnabled(has_selection and not is_search_active)

    def show_password_context_menu(self, position):
        """Show context menu for password table."""
        index = self.password_table.indexAt(position)
        if index.isValid():
            menu = QMenu()
            edit_action = menu.addAction("Edit Login")
            delete_action = menu.addAction("Delete Login")
            copy_username_action = menu.addAction("Copy Username")
            copy_password_action = menu.addAction("Copy Password")
            copy_url_action = menu.addAction("Copy URL")
            toggle_favorite_action = menu.addAction("Favorite")
            
            action = menu.exec(self.password_table.viewport().mapToGlobal(position))
            
            if action == edit_action:
                self.edit_password()
            elif action == delete_action:
                self.delete_password()
            elif action == copy_username_action:
                clipboard = QApplication.clipboard()
                clipboard.setText(self.password_manager.passwords[index.row()].username)
                self.statusBar().showMessage("Username copied to clipboard", 2000)
            elif action == copy_password_action:
                self.copy_password()
            elif action == copy_url_action:
                clipboard = QApplication.clipboard()
                clipboard.setText(self.password_manager.passwords[index.row()].url)
                self.statusBar().showMessage("URL copied to clipboard", 2000)
            elif action == toggle_favorite_action:
                self.toggle_password_favorite(index.row())

    def show_note_context_menu(self, position):
        """Show context menu for notes table."""
        index = self.notes_table.indexAt(position)
        if index.isValid():
            menu = QMenu()
            edit_action = menu.addAction("Edit Secure Note")
            delete_action = menu.addAction("Delete Secure Note")
            copy_content_action = menu.addAction("Copy Content")
            toggle_favorite_action = menu.addAction("Favorite")
            
            action = menu.exec(self.notes_table.viewport().mapToGlobal(position))
            
            if action == edit_action:
                self.edit_note()
            elif action == delete_action:
                self.delete_note()
            elif action == copy_content_action:
                self.copy_note()
            elif action == toggle_favorite_action:
                self.toggle_note_favorite(index.row())

    def show_card_context_menu(self, position):
        """Show context menu for cards table."""
        index = self.cards_table.indexAt(position)
        if index.isValid():
            menu = QMenu()
            edit_action = menu.addAction("Edit Card")
            delete_action = menu.addAction("Delete Card")
            copy_card_number_action = menu.addAction("Copy Card Number")
            toggle_favorite_action = menu.addAction("Favorite")
            
            action = menu.exec(self.cards_table.viewport().mapToGlobal(position))
            
            if action == edit_action:
                self.edit_card()
            elif action == delete_action:
                self.delete_card()
            elif action == copy_card_number_action:
                self.copy_card_number()
            elif action == toggle_favorite_action:
                self.toggle_card_favorite(index.row())

    def show_identity_context_menu(self, position):
        """Show context menu for identities table."""
        index = self.identities_table.indexAt(position)
        if index.isValid():
            menu = QMenu()
            edit_action = menu.addAction("Edit Identity")
            delete_action = menu.addAction("Delete Identity")
            copy_name_action = menu.addAction("Copy Full Name")
            copy_email_action = menu.addAction("Copy Email")
            copy_phone_action = menu.addAction("Copy Phone")
            toggle_favorite_action = menu.addAction("Favorite")
            
            action = menu.exec(self.identities_table.viewport().mapToGlobal(position))
            
            if action == edit_action:
                self.edit_identity()
            elif action == delete_action:
                self.delete_identity()
            elif action == copy_name_action:
                clipboard = QApplication.clipboard()
                identity = self.password_manager.identities[index.row()]
                clipboard.setText(f"{identity.first_name} {identity.last_name}".strip())
                self.statusBar().showMessage("Full Name copied to clipboard", 2000)
            elif action == copy_email_action:
                clipboard = QApplication.clipboard()
                clipboard.setText(self.password_manager.identities[index.row()].email)
                self.statusBar().showMessage("Email copied to clipboard", 2000)
            elif action == copy_phone_action:
                clipboard = QApplication.clipboard()
                clipboard.setText(self.password_manager.identities[index.row()].phone)
                self.statusBar().showMessage("Phone copied to clipboard", 2000)
            elif action == toggle_favorite_action:
                self.toggle_identity_favorite(index.row())

    def show_file_context_menu(self, position):
        """Show context menu for files table."""
        index = self.files_table.indexAt(position)
        if index.isValid():
            menu = QMenu()
            edit_action = menu.addAction("Edit File")
            delete_action = menu.addAction("Delete File")
            copy_file_action = menu.addAction("Copy File")
            toggle_favorite_action = menu.addAction("Favorite")
            
            action = menu.exec(self.files_table.viewport().mapToGlobal(position))
            
            if action == edit_action:
                self.edit_file()
            elif action == delete_action:
                self.delete_file()
            elif action == copy_file_action:
                self.copy_file()
            elif action == toggle_favorite_action:
                self.toggle_file_favorite(index.row())

    def show_favorite_context_menu(self, position):
        """Show context menu for favorites table."""
        index = self.favorites_table.indexAt(position)
        if index.isValid():
            menu = QMenu()
            edit_action = menu.addAction("Edit Original Entry")
            unfavorite_action = menu.addAction("Unfavorite")
            copy_content_action = menu.addAction("Copy Content")

            action = menu.exec(self.favorites_table.viewport().mapToGlobal(position))

            if action == edit_action:
                self.edit_favorite()
            elif action == unfavorite_action:
                self.delete_favorite()
            elif action == copy_content_action:
                self.copy_favorite()

    def toggle_password_favorite(self, row):
        """Toggle the favorite status of a password entry."""
        if 0 <= row < len(self.password_manager.passwords):
            password_entry = self.password_manager.passwords[row]
            password_entry.is_favorite = not password_entry.is_favorite
            self.save_data_with_status()
            self.refresh_passwords()
            self.refresh_favorites()
            self.statusBar().showMessage(f"Login '{password_entry.title}' favorite status toggled", 2000)

    def toggle_note_favorite(self, row):
        """Toggle the favorite status of a secure note entry."""
        if 0 <= row < len(self.password_manager.notes):
            note_entry = self.password_manager.notes[row]
            note_entry.is_favorite = not note_entry.is_favorite
            self.save_data_with_status()
            self.refresh_notes()
            self.refresh_favorites()
            self.statusBar().showMessage(f"Secure Note '{note_entry.title}' favorite status toggled", 2000)

    def toggle_card_favorite(self, row):
        """Toggle the favorite status of a card entry."""
        if 0 <= row < len(self.password_manager.cards):
            card_entry = self.password_manager.cards[row]
            card_entry.is_favorite = not card_entry.is_favorite
            self.save_data_with_status()
            self.refresh_cards()
            self.refresh_favorites()
            self.statusBar().showMessage(f"Card '{card_entry.title}' favorite status toggled", 2000)

    def toggle_identity_favorite(self, row):
        """Toggle the favorite status of an identity entry."""
        if 0 <= row < len(self.password_manager.identities):
            identity_entry = self.password_manager.identities[row]
            identity_entry.is_favorite = not identity_entry.is_favorite
            self.save_data_with_status()
            self.refresh_identities()
            self.refresh_favorites()
            self.statusBar().showMessage(f"Identity '{identity_entry.title}' favorite status toggled", 2000)

    def toggle_file_favorite(self, row):
        """Toggle the favorite status of a file entry."""
        if 0 <= row < len(self.password_manager.files):
            file_entry = self.password_manager.files[row]
            file_entry.is_favorite = not file_entry.is_favorite
            self.save_data_with_status()
            self.refresh_files()
            self.refresh_favorites()
            self.statusBar().showMessage(f"File '{file_entry.title}' favorite status toggled", 2000)