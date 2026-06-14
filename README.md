<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:0d1117,50:1a1a2e,100:16213e&height=220&section=header&text=C-Encrypt&fontSize=72&fontColor=00d4ff&animation=fadeIn&fontAlignY=38&desc=Secure%20Multi-User%20File%20Encryption%20Platform&descAlignY=58&descSize=18&descColor=8892b0"/>
</p>

<div align="center">

### 🔒 Secure • Offline • Multi-User • Auditable

A Python-powered encrypted file vault featuring user authentication, AES encryption, integrity verification, key management, and administrative controls.

<br>

<img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/Fernet-AES_Encryption-00d4ff?style=for-the-badge"/>
<img src="https://img.shields.io/badge/PBKDF2-HMAC_SHA256-success?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows"/>
<img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge"/>

</div>

---

## 🎬 Demo

<p align="center">
  <img src="assets/demo.gif" width="850"/>
</p>

> Login → Encrypt → Share Key → Decrypt → Verify Integrity → Admin Management

---

## ✨ Why C-Encrypt?

Most encryption projects stop at encrypting and decrypting files.

C-Encrypt simulates a complete secure file management system by combining:

- Multi-user authentication
- Role-based permissions
- Encryption key management
- File integrity verification
- Activity auditing
- Administrative controls

All while running completely offline.

---

## 🚀 Features

### 👤 User Features

- Encrypt any file securely
- Decrypt using matching key
- Share encryption keys
- Backup key files
- Verify file integrity
- Change password
- View activity history
- Delete account

### 🛡️ Admin Features

- Manage users
- Force password resets
- View audit logs
- Export system logs
- Maintenance mode
- System statistics
- Remove inactive accounts
- Delete users

---

## 🔐 Security

| Feature | Implementation |
|----------|----------|
| Password Hashing | PBKDF2-HMAC-SHA256 |
| Iterations | 100,000 |
| File Encryption | Fernet AES |
| Integrity Verification | SHA256 Checksums |
| Key Isolation | Separate Key Storage |
| Audit Trail | Full Activity Logging |
| Legacy Migration | Automatic Upgrade Support |

### Security Highlights

```text
✓ No plaintext passwords
✓ Unique encryption key per file
✓ Integrity verification on every download
✓ Separated key and file storage
✓ Complete audit trail
✓ Fully offline operation
```

---

## 📊 Project Overview

| Category | Value |
|----------|----------|
| Language | Python |
| Interface | Terminal (CLI) |
| Authentication | Multi-User |
| Authorization | Role-Based |
| Encryption | Fernet AES |
| Integrity | SHA256 |
| Storage | Local |
| Platform | Windows |

---

## 🛠 Tech Stack

<div align="center">

<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" width="60"/>
&nbsp;&nbsp;
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/windows8/windows8-original.svg" width="60"/>

</div>

<br>

| Library | Purpose |
|----------|----------|
| cryptography | Encryption & Key Management |
| hashlib | Password Hashing & Integrity Checks |
| colorama | Terminal UI Styling |

---

## ⚡ Quick Start

```bash
git clone https://github.com/Superduash/C-Encrypt.git

cd C-Encrypt

pip install -r requirements.txt

python main.py
```

### Windows Users

```text
start.bat
```

Automatically:

- Checks Python installation
- Installs dependencies
- Launches application

---

## 📁 Project Structure

```text
C-Encrypt/
│
├── main.py
├── start.bat
├── requirements.txt
│
└── cstorage/
    ├── encrypted/
    ├── keys/
    ├── decrypted/
    ├── backups/
    ├── users.txt
    ├── logs.txt
    └── metadata.json
```

---

## 🗺 Roadmap

- [x] Multi-user authentication
- [x] File encryption
- [x] File decryption
- [x] Key management
- [x] Audit logging
- [x] Admin control panel
- [ ] GUI version
- [ ] Linux support
- [ ] Docker deployment
- [ ] Cloud backup support
- [ ] Multi-factor authentication

---

## 📚 What I Learned

- Applied Cryptography
- Secure Authentication
- Role-Based Access Control
- Audit Logging Systems
- Python Application Architecture
- File Integrity Verification

---

## 📄 License

Released under the MIT License.

---

<div align="center">

### ⭐ If you found this project interesting, consider starring the repository.

Built by Ashwin as part of ITD2102 Python Mini Project.

</div>

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:16213e,50:1a1a2e,100:0d1117&height=120&section=footer"/>
</p>
