# LuckeePass by LuckeeSoft

A secure, modern, and completely offline password manager and generator built with PySide6. LuckeePass helps you safely store passwords, notes, cards, identities, and files—all protected by strong encryption and your master password.

---

## 🚀 Features

- **AES-256 Encryption**: All sensitive data is encrypted using industry-standard encryption
- **Master Password Protection**: One password to secure your entire vault
- **Offline-Only**: No cloud, no tracking, no internet required
- **Password Generator**: Create strong, customizable passwords
- **Secure Notes**: Store sensitive text securely
- **File Attachments**: Attach and encrypt files with any entry
- **Backup & Restore**: Encrypted backups for peace of mind
- **User-Friendly Interface**: Clean, intuitive, and modern design
- **Cross-Platform**: Works on Windows (and can be ported to other OSes)

---

## 🖥️ Installation

### Prerequisites
- Python 3.8+
- pip

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run LuckeePass
```bash
python main.py
```

---

## 📝 Usage

### First Launch
1. Start the app: `python main.py`
2. Choose to create a new vault or restore an existing one
3. Set your master password (cannot be recovered if lost!)
4. Start adding passwords, notes, cards, identities, and files

### Adding Entries
- Use the sidebar to navigate between Logins, Notes, Cards, Identities, and Files
- Click "Add" to create a new entry
- Attach files, add notes, and organize with categories

### Password Generator
- Go to the "Password Generator" tab
- Set your preferences (length, character sets, etc.)
- Click "Generate" and copy to clipboard

### Backup & Restore
- Go to the "Settings" tab
- **Export**: Save an encrypted backup (`.lp` file)
- **Import**: Restore from a previous backup

### Demo Database
- A sample database (`luckeepass_demo.lp`) is included for exploration

---

## 🔒 Security

- **Encryption**: AES-256 (Fernet), PBKDF2 with SHA-256, 100,000 iterations, random salt
- **No Data Leaks**: All sensitive data is encrypted; master password is never stored
- **Offline**: No network communication
- **Best Practices**: Use a strong master password and keep backups safe

---

## 📁 File Structure

```
bs toolkit/
├── main.py                # App entry point
├── requirements.txt       # Dependencies
├── src/                   # Source code
│   ├── core/              # Core logic (encryption, password mgmt)
│   ├── models/            # Data models
│   ├── ui/                # User interface
│   └── utils/             # Utilities
├── images/                # App icons and images
├── luckeepass_demo.lp     # Demo database
└── README.md              # This file
```

---

## 🧩 Dependencies
- PySide6
- cryptography
- bcrypt
- Pillow
- qrcode (for future features)

Install all with:
```bash
pip install -r requirements.txt
```

---

## 🤝 Contributing
Pull requests and suggestions are welcome! Please open an issue to discuss changes or features.

---

## 📜 License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## ⚠️ Disclaimer
LuckeePass by LuckeeSoft is provided as-is for personal and educational use. While it uses strong encryption, you are responsible for keeping your master password secure, making regular backups, and understanding the security implications. The developers are not liable for any data loss or security breaches.

---

**Made with ❤️ by LuckeeSoft** 