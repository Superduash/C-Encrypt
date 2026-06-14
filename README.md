<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&height=260&color=0:0f172a,50:0ea5e9,100:06b6d4&text=C-Encrypt&fontSize=70&fontColor=ffffff&animation=fadeIn&fontAlignY=38&desc=Secure%20Multi-User%20File%20Encryption%20Platform&descAlignY=58&descSize=18"/>
</p>

<div align="center">

### 🔒 Encrypt • Store • Verify • Share

A secure terminal-based file vault built with Python that enables encrypted file storage, key management, user authentication, integrity verification, and administrative controls.

<br>

<img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/Encryption-Fernet_AES-00d4ff?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Security-PBKDF2_HMAC_SHA256-success?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows"/>
<img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge"/>

</div>

---

# 📸 Preview

<p align="center">
  <img src="assets/demo.gif" width="900">
</p>

> Replace with a GIF showing Login → Encrypt → Decrypt → Admin Panel

---

# 🚀 Why C-Encrypt?

Most file encryption projects stop at simply encrypting and decrypting files.

C-Encrypt simulates a complete secure file management system with:

- Multi-user authentication
- Role-based access control
- File encryption
- Encryption key management
- Integrity verification
- Audit logging
- Administrative controls

All running completely offline.

---

# ✨ Features

## 👤 User Features

- Encrypt files securely
- Decrypt files with matching keys
- Share encryption keys
- Backup encryption keys
- Verify file integrity
- Manage account credentials
- View activity history

## 🛡️ Admin Features

- Manage users
- Force password resets
- View complete audit logs
- Export system logs
- Toggle maintenance mode
- Remove inactive accounts
- Monitor system activity

---

# 🔐 Security Highlights

| Security Layer | Implementation |
|---------------|---------------|
| Authentication | PBKDF2-HMAC-SHA256 |
| Encryption | Fernet AES |
| Integrity Verification | SHA256 Checksums |
| Key Management | Isolated Key Storage |
| Logging | Full Audit Trail |
| Password Migration | Automatic Legacy Upgrade |

### Security Principles

```text
✓ No plaintext passwords
✓ Unique encryption key per file
✓ SHA256 integrity validation
✓ Key isolation architecture
✓ Complete activity logging
✓ Offline operation
```

---

# ⚡ Quick Start

### Clone Repository

```bash
git clone https://github.com/Superduash/C-Encrypt.git
cd C-Encrypt
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run

```bash
python main.py
```

### Windows Launcher

```text
start.bat
```

Automatically:

- Checks Python
- Installs dependencies
- Launches application

---

# 🏗️ Tech Stack

<div align="center">

<img src="https://skillicons.dev/icons?i=python" height="55"/>
<img src="https://skillicons.dev/icons?i=windows" height="55"/>

</div>

<br>

| Library | Purpose |
|----------|----------|
| cryptography | File encryption & key generation |
| hashlib | Password hashing & integrity checks |
| colorama | Enhanced terminal UI |

---

# 📊 Project Overview

| Category | Details |
|----------|----------|
| Language | Python |
| Interface | CLI / Terminal |
| Authentication | Multi-User |
| Authorization | Role-Based |
| Encryption | Fernet AES |
| Storage | Local |
| Platform | Windows |

---

# 📁 Screenshots

<p align="center">

<img src="assets/login.png" width="700">

<br><br>

<img src="assets/encryption.png" width="700">

<br><br>

<img src="assets/admin.png" width="700">

</p>

---

# 🛣️ Future Improvements

- [ ] GUI Version
- [ ] Linux Installer
- [ ] Docker Deployment
- [ ] Multi-Factor Authentication
- [ ] SQLite Database Migration
- [ ] Secure Cloud Backup
- [ ] REST API Support

---

# 📄 License

MIT License

Free to use, modify, and distribute.

---

<div align="center">

### ⭐ If you found this project interesting, consider starring the repository

Built by **Ashwin** using Python and modern security principles.

</div>

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&height=180&section=footer&color=0:06b6d4,50:0ea5e9,100:0f172a"/>
</p>
