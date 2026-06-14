<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&height=220&color=0:0d1117,50:0f3460,100:00d4ff&text=C-Encrypt&fontSize=56&fontColor=ffffff&animation=fadeIn&fontAlignY=40&desc=Secure%20File%20Encryption%20Platform&descAlignY=60&descColor=c9d1d9&descSize=18"/>
</p>

<div align="center">

### 🔒 Secure File Encryption • 👥 Multi-User Access • 🛡️ Integrity Verification

A terminal-based file encryption platform built in Python that allows users to securely encrypt, decrypt, manage, and share files while maintaining strong security practices.

<br>

<img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/Fernet-AES_Encryption-00d4ff?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Auth-PBKDF2--HMAC--SHA256-success?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows"/>
<img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge"/>

</div>

---

## 📸 Preview

<p align="center">
  <img src="assets/cencrypt.gif" width="900"/>
</p>

### Admin Panel

<p align="center">
  <img src="assets/adminpanel.png" width="900"/>
</p>
---

## ✨ Features

### User Features

* Encrypt and decrypt files securely
* Share encryption keys with other users
* Verify file integrity using SHA256
* Backup encryption keys
* View personal activity logs
* Change account password
* Delete account and data

### Admin Features

* Manage all registered users
* Force password resets
* View complete audit logs
* Export system logs
* System statistics overview
* Maintenance mode controls
* Remove inactive users

---

## 🔐 Security

| Layer                  | Implementation               |
| ---------------------- | ---------------------------- |
| Password Security      | PBKDF2-HMAC-SHA256           |
| File Encryption        | Fernet (AES Encryption)      |
| Integrity Verification | SHA256 Checksums             |
| Audit Logging          | Timestamped Activity Logs    |
| Key Management         | Separate Key Storage         |
| Legacy Support         | Automatic Password Migration |

### Security Highlights

* No plaintext passwords
* Unique encryption key per file
* Integrity verification on download
* Complete activity tracking
* Fully offline operation

---

## 🛠 Tech Stack

<p align="left">
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" width="45"/>
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/windows8/windows8-original.svg" width="45"/>
</p>

| Library      | Purpose                                   |
| ------------ | ----------------------------------------- |
| cryptography | Encryption & key generation               |
| hashlib      | Password hashing & integrity verification |
| colorama     | Terminal UI styling                       |

---

## 🚀 Installation

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

Automatically installs dependencies and launches the application.

---

## 📂 Project Structure

```text
C-Encrypt
├── main.py
├── start.bat
├── requirements.txt
└── cstorage/
```

---

## 🎯 Future Improvements

* [ ] GUI Version
* [ ] Linux Installer
* [ ] Docker Support
* [ ] Multi-Factor Authentication
* [ ] Cloud Backup Support
* [ ] REST API Integration

---

## 📜 License

MIT License

Free to use, modify, and distribute.

---

<div align="center">

⭐ If you found this project interesting, consider starring the repository.

Built with Python and security principles.

</div>

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&height=120&section=footer&color=0:00d4ff,50:0f3460,100:0d1117"/>
</p>
