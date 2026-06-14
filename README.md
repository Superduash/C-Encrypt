<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:0d1117,50:1a1a2e,100:16213e&height=220&section=header&text=C-Encrypt&fontSize=72&fontColor=00d4ff&animation=fadeIn&fontAlignY=38&desc=Multi-User%20File%20Encryption%20Platform&descAlignY=58&descSize=18&descColor=8892b0"/>
</p>

<div align="center">

### Secure • Offline • Multi-User • Auditable

A secure terminal-based file vault built in Python that enables encrypted file storage, key management, user authentication, and administrative monitoring.

<br>

<img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/Encryption-Fernet_AES_128-00d4ff?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Auth-PBKDF2_HMAC_SHA256-success?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows"/>
<img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge"/>

</div>

---

## Preview

<p align="center">
  <img src="logo.png" width="180"/>
</p>

> Replace the image above with a terminal screenshot or GIF demonstration.
>
> A 15-second demo GIF will increase engagement more than any README section.

---

# Why C-Encrypt?

Most beginner encryption projects stop at:

- Encrypt File
- Decrypt File

C-Encrypt goes beyond that.

It simulates a complete secure file management system with authentication, key isolation, integrity verification, audit logging, role-based permissions, and administrative controls.

Designed as a Python mini-project while following real-world security principles.

---

# Core Features

<table>
<tr>
<td width="50%">

### User Features

- Encrypt any file
- Decrypt using matching key
- Secure key sharing
- Key backup system
- File integrity verification
- Password management
- Personal activity logs
- Account deletion

</td>
<td width="50%">

### Admin Features

- User management
- Force password resets
- View audit logs
- Export logs
- Maintenance mode
- Remove inactive users
- System statistics
- Delete user accounts

</td>
</tr>
</table>

---

# Security Architecture

<table>
<tr>
<th>Layer</th>
<th>Implementation</th>
</tr>

<tr>
<td>Password Protection</td>
<td>PBKDF2-HMAC-SHA256 (100,000 iterations)</td>
</tr>

<tr>
<td>File Encryption</td>
<td>Fernet AES-128 Encryption</td>
</tr>

<tr>
<td>Integrity Verification</td>
<td>SHA256 Checksums</td>
</tr>

<tr>
<td>Key Storage</td>
<td>Separated From Encrypted Files</td>
</tr>

<tr>
<td>Audit Trail</td>
<td>Timestamped Activity Logging</td>
</tr>

<tr>
<td>Password Migration</td>
<td>Automatic Legacy SHA256 Upgrade</td>
</tr>

</table>

### Security Highlights

```text
✓ No plaintext passwords
✓ Unique encryption key per file
✓ Integrity validation on download
✓ Separated key storage
✓ Full activity tracking
✓ Offline operation
```

---

# System Workflow

```text
                USER
                  │
                  ▼

        Authentication Layer
                  │
                  ▼

         Encryption Engine
                  │
      ┌───────────┼───────────┐
      │           │           │
      ▼           ▼           ▼

 Encrypted     Metadata      Keys
   Files       Storage      Storage

      │
      ▼

 Activity Logger
```

---

# Encryption Process

```text
UPLOAD

File
 │
 ▼

Generate Key
 │
 ▼

Encrypt File
 │
 ▼

Store .enc File
 │
 ▼

Store Key
 │
 ▼

Generate SHA256
 │
 ▼

Log Activity
```

```text
DOWNLOAD

Encrypted File
 │
 ▼

Select Key
 │
 ▼

Decrypt
 │
 ▼

Verify SHA256
 │
 ▼

Restore File
 │
 ▼

Log Activity
```

---

# Project Statistics

| Metric | Value |
|----------|----------|
| Language | Python |
| Interface | Terminal / CLI |
| Authentication | Multi-User |
| Authorization | Role-Based |
| Encryption | Fernet AES |
| Integrity | SHA256 |
| Storage | Local |
| Logging | Audit Trail |
| Platform | Windows |

---

# Installation

### Requirements

```text
Python 3.8+
Windows
```

### Clone Repository

```bash
git clone https://github.com/Superduash/C-Encrypt.git
cd C-Encrypt
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Application

```bash
python main.py
```

### Windows Users

Simply launch:

```text
start.bat
```

The launcher automatically:

- Checks Python installation
- Installs dependencies
- Starts the application

---

# Quick Start

### Default Administrator Account

```text
Username : Admin
Password : admin
```

Change the password immediately after first login.

### Password Rules

```text
Minimum 8 characters
At least 1 uppercase letter
At least 1 number
```

---

# Project Structure

```text
C-Encrypt
│
├── main.py
├── start.bat
├── requirements.txt
│
└── cstorage
    │
    ├── encrypted
    ├── keys
    ├── decrypted
    ├── backups
    ├── users.txt
    ├── logs.txt
    └── metadata.json
```

---

# Technology Stack

<div align="center">

<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" width="60"/>
&nbsp;&nbsp;&nbsp;
<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/windows8/windows8-original.svg" width="60"/>

</div>

| Library | Purpose |
|----------|----------|
| cryptography | File encryption and key generation |
| hashlib | Password hashing and integrity verification |
| colorama | Colored terminal interface |

---

# Future Improvements

- [ ] GUI Version
- [ ] Linux Installer
- [ ] Docker Deployment
- [ ] Multi-Factor Authentication
- [ ] Secure Database Storage
- [ ] Encrypted Cloud Backup
- [ ] File Versioning
- [ ] REST API Support

---

# Educational Objectives

This project demonstrates:

- Applied Cryptography
- Authentication Systems
- Role-Based Access Control
- Secure File Management
- Audit Logging
- Python Application Architecture

---

# License

Distributed under the MIT License.

Feel free to use, modify, and distribute.

---

<div align="center">

### Built with Python and Security Principles

If you found this project useful, consider giving it a ⭐

</div>

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:16213e,50:1a1a2e,100:0d1117&height=120&section=footer"/>
</p>
