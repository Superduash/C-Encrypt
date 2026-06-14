<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:0d1117,50:1a1a2e,100:16213e&height=180&section=header&text=C-Encrypt&fontSize=70&fontColor=00d4ff&animation=fadeIn&fontAlignY=38&desc=Secure%20File%20Encryption%20Platform&descAlignY=58&descSize=18&descColor=8892b0"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Encryption-AES%20128%20Fernet-00d4ff?style=for-the-badge&logo=lock&logoColor=white"/>
  <img src="https://img.shields.io/badge/Auth-PBKDF2--HMAC--SHA256-success?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white"/>
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge"/>
</p>

<p align="center">
  <b>A terminal-based multi-user encrypted file vault with AES encryption, key sharing, and an admin control panel.</b>
</p>

---

## What is C-Encrypt?

C-Encrypt is a command-line file encryption platform where users can securely upload, encrypt, and share files — all from the terminal. It supports multiple accounts with role-based access (User / Admin), stores files encrypted with Fernet AES-128-CBC, and manages encryption keys separately so your data is never readable without the right key.

Built in Python. Runs entirely offline. No cloud dependency.

---

## Features

```
User Features                        Admin Features
─────────────────────────────        ──────────────────────────────
✦ Encrypt & upload any file          ✦ View and manage all users
✦ Decrypt & download with key        ✦ Force password resets
✦ Share encryption keys with users   ✦ View full system activity logs
✦ File integrity verification        ✦ Export and clear logs
✦ Backup all your keys               ✦ Orphaned file cleanup
✦ View recent activity log           ✦ System statistics overview
✦ Change password anytime            ✦ Toggle maintenance mode
✦ Delete account & all data          ✦ Delete any user account
```

---

## Security

| Layer | Method |
|---|---|
| Password hashing | PBKDF2-HMAC-SHA256 · 100,000 iterations |
| File encryption | Fernet (AES-128-CBC + HMAC-SHA256) |
| Legacy migration | SHA256 passwords auto-upgraded on login |
| File integrity | SHA256 checksums verified on every download |
| Key isolation | Encryption keys stored separately from files |
| Audit trail | Timestamped log of every user action |

No passwords stored in plaintext. Ever.

---

## Installation

**Requirements:** Python 3.8+ · Windows

```bash
# 1. Clone the repository
git clone https://github.com/Superduash/C-Encrypt.git
cd C-Encrypt

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch
python main.py
```

**Or on Windows — just double-click `start.bat`**
It auto-checks Python, installs dependencies silently, and launches the app.

---

## Getting Started

**Default admin credentials (change immediately after first login)**
```
Username: Admin
Password: admin
```

**Password requirements for new accounts**
- Minimum 8 characters
- At least one uppercase letter
- At least one number

---

## How It Works

```
Upload Flow                          Download Flow
────────────────────────             ────────────────────────
User provides file path              User selects encrypted file
        ↓                                    ↓
Fernet generates unique key          User selects matching key
        ↓                                    ↓
File encrypted → .enc stored         Fernet decrypts the file
        ↓                                    ↓
Key saved to /keys/                  SHA256 integrity verified
        ↓                                    ↓
SHA256 hash logged in metadata       File saved to /decrypted/
```

---

## Directory Structure

```
C-Encrypt/
├── main.py               ← Core application
├── start.bat             ← One-click Windows launcher
├── requirements.txt
└── cstorage/
    ├── encrypted/        ← Encrypted .enc files
    ├── keys/             ← Per-file .key files
    ├── decrypted/        ← Output after decryption
    ├── backups/          ← Key and log backups
    ├── users.txt         ← Hashed user credentials
    ├── logs.txt          ← Full activity audit trail
    └── metadata.json     ← File metadata and checksums
```

---

## Tech Stack

<p>
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" width="40" height="40" alt="Python"/>
  &nbsp;
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/windows8/windows8-original.svg" width="40" height="40" alt="Windows"/>
</p>

| Package | Purpose |
|---|---|
| `cryptography` | Fernet AES-128-CBC encryption and key generation |
| `colorama` | Cross-platform colored terminal output |
| `hashlib` | PBKDF2-HMAC-SHA256 password hashing + SHA256 integrity |

---

## Limitations

- Max file size: **50 MB** (prevents RAM exhaustion during Fernet encryption)
- Local storage only — files are stored on the same machine
- Terminal-only interface (no GUI)
- Windows-native launcher (`.bat`); runs on Linux/Mac via `python main.py`

---

## License

MIT — free to use, modify, and distribute.

---

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:16213e,50:1a1a2e,100:0d1117&height=100&section=footer"/>
</p>
