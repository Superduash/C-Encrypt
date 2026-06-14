import os
import sys
import hashlib
import json
import time
import shutil
import getpass
import warnings
import re
from datetime import datetime
from cryptography.fernet import Fernet, InvalidToken
from colorama import init, Fore, Style

# tkinter is built into Python — used for native file/folder dialogs
try:
    import tkinter as tk
    from tkinter import filedialog
    _TK_AVAILABLE = True
except ImportError:
    _TK_AVAILABLE = False

# Initialize colorama for cross-platform colored terminal output
init(autoreset=True)

class CEncryptLogic:
    def __init__(self):
        self.BASE_DIR = os.path.abspath(os.path.dirname(__file__))
        self.CSTORAGE_DIR = os.path.join(self.BASE_DIR, 'cstorage')
        self.ENCRYPTED_DIR = os.path.join(self.CSTORAGE_DIR, 'encrypted')
        self.KEYS_DIR = os.path.join(self.CSTORAGE_DIR, 'keys')
        self.DECRYPTED_DIR = os.path.join(self.CSTORAGE_DIR, 'decrypted')
        self.BACKUP_DIR = os.path.join(self.CSTORAGE_DIR, 'backups')
        self.USERS_FILE = os.path.join(self.CSTORAGE_DIR, 'users.txt')
        self.LOGS_FILE = os.path.join(self.CSTORAGE_DIR, 'logs.txt')
        self.METADATA_FILE = os.path.join(self.CSTORAGE_DIR, 'metadata.json')
        self.MAINTENANCE_FILE = os.path.join(self.CSTORAGE_DIR, 'maintenance.flag')
        
        self.ADMIN_USER = "Admin"
        self.ADMIN_PASS = "admin"
        self.MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB limit to prevent RAM exhaustion
        
        self.ensure_dirs()
        self.create_admin()

    def ensure_dirs(self):
        try:
            for directory in [self.CSTORAGE_DIR, self.ENCRYPTED_DIR, self.KEYS_DIR,
                              self.DECRYPTED_DIR, self.BACKUP_DIR]:
                os.makedirs(directory, exist_ok=True)
            for file_path in [self.USERS_FILE, self.LOGS_FILE]:
                if not os.path.exists(file_path):
                    open(file_path, 'a', encoding='utf-8').close()
            if not os.path.exists(self.METADATA_FILE):
                with open(self.METADATA_FILE, 'w', encoding='utf-8') as f:
                    json.dump({}, f, indent=2)
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Creating directories: {e}{Style.RESET_ALL}")
            sys.exit(1)

    def create_admin(self):
        if not self._check_user_exists(self.ADMIN_USER):
            hashed = self._hash_password_new(self.ADMIN_USER, self.ADMIN_PASS)
            with open(self.USERS_FILE, 'a', encoding='utf-8') as f:
                f.write(f"{self.ADMIN_USER}:{hashed}:ADMIN:false\n")

    # --- Security: Upgraded to PBKDF2 with seamless legacy SHA256 migration ---
    def _hash_password_new(self, username, password):
        return hashlib.pbkdf2_hmac('sha256', password.encode(), username.encode(), 100000).hex()

    def _hash_password_old(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def _upgrade_password_hash(self, username, new_hash, role, reset_flag):
        try:
            lines = []
            with open(self.USERS_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split(':')
                    if len(parts) >= 2 and parts[0] == username:
                        lines.append(f"{username}:{new_hash}:{role}:{reset_flag}\n")
                    else:
                        lines.append(line)
            with open(self.USERS_FILE, 'w', encoding='utf-8') as f:
                f.writelines(lines)
        except Exception:
            pass

    def _log_action(self, username, action, details):
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_entry = f"[{timestamp}] - USER: {username} - ACTION: {action} - DETAILS: {details}\n"
            with open(self.LOGS_FILE, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception:
            pass

    def check_password_strength(self, password):
        errors = []
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        if not re.search(r'[0-9]', password):
            errors.append("Password must contain at least one number")
        return (True, []) if not errors else (False, errors)

    def register_user(self, username, password):
        if not username:
            return "Username cannot be empty."
        if not password:
            return "Password cannot be empty."
        if len(username) < 3:
            return "Username must be at least 3 characters long."
        if len(username) > 32:
            return "Username must be 32 characters or less."
        if ' ' in username:
            return "Username cannot contain spaces."
        if ':' in username:
            return "Username cannot contain colons."
        if not re.match(r'^[a-zA-Z0-9_\-]+$', username):
            return "Username can only contain letters, numbers, underscores, and hyphens."

        # Case-insensitive duplicate check with helpful message
        if os.path.exists(self.USERS_FILE):
            with open(self.USERS_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    existing = line.strip().split(':')[0]
                    if existing.lower() == username.lower():
                        if existing == username:
                            return "Username already taken. Please choose a different one."
                        else:
                            return f"Username already taken (as '{existing}'). Please choose a different one."

        is_strong, issues = self.check_password_strength(password)
        if not is_strong:
            return "Password requirements not met:\n" + "\n".join(f"  * {issue}" for issue in issues)

        hashed_password = self._hash_password_new(username, password)
        with open(self.USERS_FILE, 'a', encoding='utf-8') as f:
            f.write(f"{username}:{hashed_password}:USER:false\n")
        self._log_action(username, "REGISTER", "New user created")
        return "Success"

    def login_user(self, username, password):
        if not username or not password:
            return False, None, "Username and password cannot be empty.", False
        if not os.path.exists(self.USERS_FILE):
            return False, None, "No users registered yet.", False

        # Collect all registered usernames for helpful suggestions
        all_usernames = []
        with open(self.USERS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split(':')
                if len(parts) >= 2 and parts[0]:
                    all_usernames.append(parts[0])

        # Check exact match
        if username not in all_usernames:
            # Check if it's a case mismatch
            lower_map = {u.lower(): u for u in all_usernames}
            if username.lower() in lower_map:
                correct = lower_map[username.lower()]
                self._log_action(username, "LOGIN_FAIL", "Username case mismatch")
                return False, None, f"Username not found. Did you mean '{correct}'?", False
            self._log_action(username, "LOGIN_FAIL", "User not found")
            return False, None, "Username not found. Check spelling or register a new account.", False

        # Exact username found — now verify password
        with open(self.USERS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split(':')
                if len(parts) >= 2 and parts[0] == username:
                    stored_hash = parts[1]
                    role = parts[2] if len(parts) > 2 else "USER"
                    reset_required = parts[3] == "true" if len(parts) > 3 else False

                    if stored_hash == self._hash_password_new(username, password):
                        self._log_action(username, "LOGIN", f"User logged in as {role}")
                        return True, role, None, reset_required
                    elif stored_hash == self._hash_password_old(password):
                        # Upgrade legacy hash silently
                        new_hash = self._hash_password_new(username, password)
                        self._upgrade_password_hash(username, new_hash, role, str(reset_required).lower())
                        self._log_action(username, "LOGIN", f"User logged in as {role} (Hash Upgraded)")
                        return True, role, None, reset_required
                    else:
                        self._log_action(username, "LOGIN_FAIL", "Incorrect password")
                        return False, None, "Incorrect password.", False

        return False, None, "Login failed.", False

    def get_all_users(self):
        try:
            users = []
            with open(self.USERS_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split(':')
                    if len(parts) >= 2:
                        username = parts[0]
                        role = parts[2] if len(parts) > 2 else "USER"
                        users.append(f"{username} ({role})")
            return users
        except Exception:
            return []

    def get_all_files(self):
        try:
            return os.listdir(self.ENCRYPTED_DIR)
        except Exception:
            return []

    def upload_file(self, username, file_path):
        if self.is_maintenance_mode():
            return "Error: System is in maintenance mode. Uploads disabled."
        if not file_path or not os.path.exists(file_path):
            return "Error: File not found."
        
        try:
            file_size = os.path.getsize(file_path)
            if file_size > self.MAX_FILE_SIZE:
                return f"Error: File exceeds maximum allowed size of {self._format_file_size(self.MAX_FILE_SIZE)}."
            
            key = Fernet.generate_key()
            cipher = Fernet(key)
            with open(file_path, 'rb') as file:
                file_data = file.read()
            encrypted_data = cipher.encrypt(file_data)
            file_hash = hashlib.sha256(encrypted_data).hexdigest()
            
            original_name = os.path.basename(file_path)
            final_name = self._get_unique_filename(username, original_name)
            encrypted_name = f"{username}_{final_name}.enc"
            key_name = f"{username}_{final_name}.key"
            
            with open(os.path.join(self.ENCRYPTED_DIR, encrypted_name), 'wb') as f:
                f.write(encrypted_data)
            with open(os.path.join(self.KEYS_DIR, key_name), 'wb') as f:
                f.write(key)
                
            self.save_file_metadata(username, final_name, file_size, file_hash)
            size_str = self._format_file_size(file_size)
            self._log_action(username, "UPLOAD", f"File: {final_name} ({size_str})")
            return f"Success! File uploaded as '{encrypted_name}'."
        except Exception as e:
            return f"Error: {e}"

    def _get_unique_filename(self, username, filename):
        if '.' in filename:
            name, ext = filename.rsplit('.', 1)
            ext = '.' + ext
        else:
            name = filename
            ext = ''
            
        base_encrypted = f"{username}_{filename}.enc"
        if not os.path.exists(os.path.join(self.ENCRYPTED_DIR, base_encrypted)):
            return filename
            
        counter = 1
        while True:
            new_name = f"{name} ({counter}){ext}"
            test_encrypted = f"{username}_{new_name}.enc"
            if not os.path.exists(os.path.join(self.ENCRYPTED_DIR, test_encrypted)):
                return new_name
            counter += 1

    def get_user_files(self, username):
        try:
            all_files = os.listdir(self.ENCRYPTED_DIR)
            user_files = [f for f in all_files if f.startswith(f"{username}_") and f.endswith(".enc")]
            shared_files = []
            user_keys = self.get_user_keys(username)
            
            for key_file in user_keys:
                if key_file.startswith(f"{username}_"):
                    continue  # Skip own keys
                
                base_filename = key_file.replace(".key", "")
                for enc_file in all_files:
                    if enc_file.endswith(".enc") and enc_file.replace(".enc", "") == base_filename:
                        if enc_file not in shared_files:
                            shared_files.append(enc_file)
                            
            return sorted(list(set(user_files + shared_files)))
        except Exception:
            return []

    def download_file(self, username, encrypted_name, key_path, save_dir=None):
        if self.is_maintenance_mode():
            return "Error: System is in maintenance mode. Downloads disabled."
        try:
            if not os.path.exists(key_path):
                return "Error: Key file not found."
            with open(key_path, 'rb') as f:
                key = f.read()
            cipher = Fernet(key)
            
            encrypted_path = os.path.join(self.ENCRYPTED_DIR, encrypted_name)
            if not os.path.exists(encrypted_path):
                return "Error: Encrypted file not found."
                
            with open(encrypted_path, 'rb') as f:
                encrypted_data = f.read()
                
            current_hash = hashlib.sha256(encrypted_data).hexdigest()
            original_name = encrypted_name.split('_', 1)[1].replace(".enc", "") if '_' in encrypted_name else encrypted_name.replace(".enc", "")
            owner = encrypted_name.split('_')[0] if '_' in encrypted_name else username
            
            metadata = self.get_file_metadata(owner, original_name)
            if metadata and 'hash' in metadata:
                if current_hash != metadata['hash']:
                    self._log_action(username, "INTEGRITY_FAIL", f"Hash mismatch for {encrypted_name}")
                    return "Error: File integrity check failed. File may be corrupted."
                    
            decrypted_data = cipher.decrypt(encrypted_data)
            # Use custom save_dir if provided, otherwise default to decrypted folder
            out_dir = save_dir if save_dir and os.path.isdir(save_dir) else self.DECRYPTED_DIR
            decrypted_path = os.path.join(out_dir, original_name)
            with open(decrypted_path, 'wb') as f:
                f.write(decrypted_data)
                
            self._log_action(username, "DOWNLOAD", f"File: {original_name}")
            return f"Success! File saved to '{decrypted_path}'."
        except InvalidToken:
            self._log_action(username, "DOWNLOAD_FAIL", f"Invalid key for {encrypted_name}")
            return "Error: Wrong key. Decryption failed."
        except Exception as e:
            return f"Error: {e}"

    def get_user_keys(self, username):
        try:
            all_keys = os.listdir(self.KEYS_DIR)
            # Get all encrypted files directly without calling get_user_files (avoid circular dependency)
            all_enc_files = os.listdir(self.ENCRYPTED_DIR)
            user_enc_files = [f.replace(".enc", "") for f in all_enc_files if f.startswith(f"{username}_") and f.endswith(".enc")]
            
            # Also include keys that match shared files
            user_keys = []
            for key_file in all_keys:
                if not key_file.endswith(".key"):
                    continue
                key_base = key_file.replace(".key", "")
                # Include if it's user's own key or if they have access via sharing
                if key_base in user_enc_files or key_file.startswith(f"{username}_"):
                    user_keys.append(key_file)
            
            return sorted(user_keys)
        except Exception:
            return []

    def _check_user_exists(self, username):
        if not os.path.exists(self.USERS_FILE):
            return False
        try:
            with open(self.USERS_FILE, 'r', encoding='utf-8') as f:
                return any(line.strip().split(':')[0] == username for line in f)
        except Exception:
            return False

    def share_key(self, username, key_name, target_user):
        if not target_user:
            return "Please enter a username."
        if target_user == username:
            return "Error: Cannot share with yourself."
        if not self._check_user_exists(target_user):
            return f"Error: User '{target_user}' does not exist."
        try:
            original_key = os.path.join(self.KEYS_DIR, key_name)
            if not os.path.exists(original_key):
                return "Error: Key file not found."
            file_part = key_name.replace(f"{username}_", "")
            new_key_path = os.path.join(self.KEYS_DIR, f"{target_user}_{file_part}")
            shutil.copy(original_key, new_key_path)
            self._log_action(username, "SHARE", f"Shared with {target_user}")
            return f"Success! Key shared with {target_user}."
        except Exception as e:
            return f"Error: {e}"

    def delete_file(self, username, encrypted_name):
        if not encrypted_name.startswith(f"{username}_"):
            return "Error: Not your file."
        try:
            key_name = encrypted_name.replace(".enc", ".key")
            encrypted_path = os.path.join(self.ENCRYPTED_DIR, encrypted_name)
            key_path = os.path.join(self.KEYS_DIR, key_name)
            
            for path in [encrypted_path, key_path]:
                if os.path.exists(path):
                    os.remove(path)
                    
            original_name = encrypted_name.replace(f"{username}_", "").replace(".enc", "")
            self.delete_file_metadata(username, original_name)
            self._log_action(username, "DELETE", f"Deleted {encrypted_name}")
            return "Success! File and key deleted."
        except Exception as e:
            return f"Error: {e}"

    def delete_key(self, username, key_name):
        if not key_name.startswith(f"{username}_"):
            return "Error: Not your key."
        try:
            key_path = os.path.join(self.KEYS_DIR, key_name)
            if os.path.exists(key_path):
                os.remove(key_path)
                self._log_action(username, "DELETE_KEY", f"Deleted key: {key_name}")
                return "Success! Key deleted."
            return "Error: Key file not found."
        except Exception as e:
            return f"Error: {e}"

    def get_recent_activity(self, username, limit=5):
        try:
            if not os.path.exists(self.LOGS_FILE):
                return []
            with open(self.LOGS_FILE, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in reversed(f.readlines()) if f"USER: {username}" in line]
            return lines[:limit]
        except Exception:
            return []

    def backup_user_keys(self, username):
        try:
            keys = self.get_user_keys(username)
            if not keys:
                return "Error: No keys to backup."
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(self.BACKUP_DIR, f"{username}_keys_backup_{timestamp}.txt")
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(f"C-Encrypt Key Backup for {username}\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n")
                for key_file in keys:
                    f.write(f"Key: {key_file}\n")
                    with open(os.path.join(self.KEYS_DIR, key_file), 'rb') as kf:
                        f.write(f"Data: {kf.read().decode('utf-8')}\n")
            self._log_action(username, "BACKUP_KEYS", f"Backed up {len(keys)} keys")
            return f"Success! Keys backed up to: {backup_path}"
        except Exception as e:
            return f"Error: {e}"

    def change_password(self, username, old_password, new_password):
        try:
            lines = []
            found = False
            old_hash = self._hash_password_new(username, old_password) if old_password else None
            new_hash = self._hash_password_new(username, new_password)
            
            with open(self.USERS_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split(':')
                    if len(parts) >= 2 and parts[0] == username:
                        # Allow change if old_password matches new hash OR if it matches legacy hash (for forced resets)
                        if old_hash is None or parts[1] == old_hash or parts[1] == self._hash_password_old(old_password):
                            role = parts[2] if len(parts) > 2 else "USER"
                            lines.append(f"{username}:{new_hash}:{role}:false\n")
                            found = True
                        else:
                            return "Error: Current password is incorrect."
                    else:
                        lines.append(line)
                        
            if not found:
                return "Error: User not found."
                
            with open(self.USERS_FILE, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            self._log_action(username, "PASSWORD_CHANGE", "Password changed")
            return "Success"
        except Exception as e:
            return f"Error: {e}"

    def get_all_users_detailed(self):
        try:
            users = []
            with open(self.USERS_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split(':')
                    if len(parts) >= 2:
                        username = parts[0]
                        role = parts[2] if len(parts) > 2 else "USER"
                        users.append({
                            "username": username,
                            "role": role,
                            "files": len(self.get_user_files(username)),
                            "keys": len(self.get_user_keys(username))
                        })
            return users
        except Exception:
            return []

    def delete_user_account(self, admin_user, target_user):
        if target_user == self.ADMIN_USER:
            return "Error: Cannot delete admin account."
        try:
            for f in self.get_user_files(target_user):
                if f.startswith(f"{target_user}_"):
                    self.delete_file(target_user, f)
            with open(self.USERS_FILE, 'r', encoding='utf-8') as f:
                lines = [line for line in f if not line.startswith(f"{target_user}:")]
            with open(self.USERS_FILE, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            self._log_action(admin_user, "DELETE_USER", f"Deleted user: {target_user}")
            return f"Success! User '{target_user}' deleted."
        except Exception as e:
            return f"Error: {e}"

    def reset_user_password(self, admin_user, target_user, new_password):
        is_strong, issues = self.check_password_strength(new_password)
        if not is_strong:
            return "Password requirements not met:\n" + "\n".join(f"  * {issue}" for issue in issues)
        try:
            new_hash = self._hash_password_new(target_user, new_password)
            lines = []
            found = False
            with open(self.USERS_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split(':')
                    if len(parts) >= 2 and parts[0] == target_user:
                        role = parts[2] if len(parts) > 2 else "USER"
                        lines.append(f"{target_user}:{new_hash}:{role}:false\n")
                        found = True
                    else:
                        lines.append(line)
            if not found:
                return "Error: User not found."
            with open(self.USERS_FILE, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            self._log_action(admin_user, "RESET_PASSWORD", f"Reset password for: {target_user}")
            return "Success"
        except Exception as e:
            return f"Error: {e}"

    def set_password_reset_required(self, admin_user, target_user, required=True):
        try:
            lines = []
            found = False
            with open(self.USERS_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split(':')
                    if len(parts) >= 2 and parts[0] == target_user:
                        role = parts[2] if len(parts) > 2 else "USER"
                        reset_flag = "true" if required else "false"
                        lines.append(f"{target_user}:{parts[1]}:{role}:{reset_flag}\n")
                        found = True
                    else:
                        lines.append(line)
            if not found:
                return "Error: User not found."
            with open(self.USERS_FILE, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            action = "enabled" if required else "disabled"
            self._log_action(admin_user, "SET_RESET_FLAG", f"Password reset {action} for: {target_user}")
            return f"Success! Password reset requirement {action} for '{target_user}'."
        except Exception as e:
            return f"Error: {e}"

    def get_user_activity_summary(self):
        try:
            if not os.path.exists(self.LOGS_FILE):
                return {}
            activity = {}
            with open(self.LOGS_FILE, 'r', encoding='utf-8') as f:
                for line in f:
                    if "USER:" in line:
                        parts = line.split("USER:")
                        if len(parts) > 1:
                            user_part = parts[1].split("-")[0].strip()
                            action_part = line.split("ACTION:")[1].split("-")[0].strip() if "ACTION:" in line else ""
                            if user_part not in activity:
                                activity[user_part] = {"uploads": 0, "downloads": 0, "deletes": 0, "logins": 0}
                            if "UPLOAD" in action_part:
                                activity[user_part]["uploads"] += 1
                            elif "DOWNLOAD" in action_part and "FAIL" not in action_part:
                                activity[user_part]["downloads"] += 1
                            elif "DELETE" in action_part:
                                activity[user_part]["deletes"] += 1
                            elif action_part == "LOGIN":
                                activity[user_part]["logins"] += 1
            return activity
        except Exception:
            return {}

    def export_metadata(self):
        try:
            if not os.path.exists(self.METADATA_FILE):
                return "Error: No metadata to export."
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            export_path = os.path.join(self.BACKUP_DIR, f"metadata_export_{timestamp}.json")
            shutil.copy(self.METADATA_FILE, export_path)
            return f"Success! Metadata exported to: {export_path}"
        except Exception as e:
            return f"Error: {e}"

    def find_orphaned_files(self):
        try:
            with open(self.METADATA_FILE, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            all_enc_files = set(os.listdir(self.ENCRYPTED_DIR))
            all_key_files = set(os.listdir(self.KEYS_DIR))
            tracked_files = set()
            tracked_keys = set()
            
            for key in metadata.keys():
                parts = key.split('_', 1)
                if len(parts) == 2:
                    username, filename = parts
                    tracked_files.add(f"{username}_{filename}.enc")
                    tracked_keys.add(f"{username}_{filename}.key")
                    
            orphaned_enc = list(all_enc_files - tracked_files)
            orphaned_keys = list(all_key_files - tracked_keys)
            return orphaned_enc, orphaned_keys
        except Exception:
            return [], []

    def cleanup_orphaned_files(self, admin_user, orphaned_enc, orphaned_keys):
        try:
            removed = []
            for enc_file in orphaned_enc:
                enc_path = os.path.join(self.ENCRYPTED_DIR, enc_file)
                if os.path.exists(enc_path):
                    os.remove(enc_path)
                    removed.append(enc_file)
            for key_file in orphaned_keys:
                key_path = os.path.join(self.KEYS_DIR, key_file)
                if os.path.exists(key_path):
                    os.remove(key_path)
                    removed.append(key_file)
            self._log_action(admin_user, "CLEANUP", f"Removed {len(removed)} orphaned files")
            return f"Success! Removed {len(removed)} orphaned files."
        except Exception as e:
            return f"Error: {e}"

    def save_file_metadata(self, username, filename, size, file_hash=None):
        try:
            with open(self.METADATA_FILE, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            key = f"{username}_{filename}"
            metadata[key] = {
                "upload_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "size": size,
                "encrypted": True,
                "hash": file_hash
            }
            with open(self.METADATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
        except Exception:
            pass

    def get_file_metadata(self, owner, filename):
        try:
            with open(self.METADATA_FILE, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            return metadata.get(f"{owner}_{filename}")
        except Exception:
            return None

    def delete_file_metadata(self, username, filename):
        try:
            with open(self.METADATA_FILE, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            key = f"{username}_{filename}"
            if key in metadata:
                del metadata[key]
            with open(self.METADATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
        except Exception:
            pass

    def get_logs(self):
        try:
            if not os.path.exists(self.LOGS_FILE):
                return "No logs found."
            with open(self.LOGS_FILE, 'r', encoding='utf-8') as f:
                logs = f.read()
            return logs if logs else "Log file is empty."
        except Exception as e:
            return f"Error: {e}"

    def clear_logs(self):
        try:
            open(self.LOGS_FILE, 'w', encoding='utf-8').close()
            return "Logs cleared successfully."
        except Exception as e:
            return f"Error: {e}"

    def export_logs(self):
        try:
            if not os.path.exists(self.LOGS_FILE):
                return "Error: No logs to export."
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            export_path = os.path.join(self.BACKUP_DIR, f"logs_export_{timestamp}.txt")
            shutil.copy(self.LOGS_FILE, export_path)
            return f"Success! Logs exported to: {export_path}"
        except Exception as e:
            return f"Error: {e}"

    def admin_delete_any_file(self, admin_user, encrypted_name):
        try:
            key_name = encrypted_name.replace(".enc", ".key")
            for path in [os.path.join(self.ENCRYPTED_DIR, encrypted_name), os.path.join(self.KEYS_DIR, key_name)]:
                if os.path.exists(path):
                    os.remove(path)
            self._log_action(admin_user, "ADMIN_DELETE", f"Deleted {encrypted_name}")
            return "Success! File deleted."
        except Exception as e:
            return f"Error: {e}"

    def is_maintenance_mode(self):
        return os.path.exists(self.MAINTENANCE_FILE)

    def set_maintenance_mode(self, enabled):
        try:
            if enabled:
                with open(self.MAINTENANCE_FILE, 'w', encoding='utf-8') as f:
                    f.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                return "Maintenance mode enabled."
            else:
                if os.path.exists(self.MAINTENANCE_FILE):
                    os.remove(self.MAINTENANCE_FILE)
                return "Maintenance mode disabled."
        except Exception as e:
            return f"Error: {e}"

    def clear_backups(self, admin_user):
        try:
            if not os.path.exists(self.BACKUP_DIR):
                return "Error: Backup directory not found."
            files = os.listdir(self.BACKUP_DIR)
            if not files:
                return "No backup files to clear."
            removed_count = 0
            for file in files:
                file_path = os.path.join(self.BACKUP_DIR, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    removed_count += 1
            self._log_action(admin_user, "CLEAR_BACKUPS", f"Cleared {removed_count} backup files")
            return f"Success! Cleared {removed_count} backup file(s)."
        except Exception as e:
            return f"Error: {e}"

    def delete_all_files_and_keys(self, admin_user):
        try:
            enc_files = os.listdir(self.ENCRYPTED_DIR) if os.path.exists(self.ENCRYPTED_DIR) else []
            key_files = os.listdir(self.KEYS_DIR) if os.path.exists(self.KEYS_DIR) else []
            if not enc_files and not key_files:
                return "No files or keys to delete."
            removed_count = 0
            for file in enc_files:
                file_path = os.path.join(self.ENCRYPTED_DIR, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    removed_count += 1
            for file in key_files:
                file_path = os.path.join(self.KEYS_DIR, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    removed_count += 1
            with open(self.METADATA_FILE, 'w', encoding='utf-8') as f:
                json.dump({}, f, indent=2)
            self._log_action(admin_user, "DELETE_ALL_FILES", f"Deleted all files and keys ({removed_count} items)")
            return f"Success! Deleted {len(enc_files)} file(s) and {len(key_files)} key(s)."
        except Exception as e:
            return f"Error: {e}"

    def delete_all_user_data(self, username, password):
        hashed_password = self._hash_password_new(username, password)
        legacy_hash = self._hash_password_old(password)
        
        with open(self.USERS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split(':')
                if len(parts) >= 2 and parts[0] == username:
                    if parts[1] != hashed_password and parts[1] != legacy_hash:
                        return "Error: Incorrect password."
                    break
                    
        try:
            deleted_count = {"files": 0, "keys": 0, "backups": 0}
            for file in os.listdir(self.ENCRYPTED_DIR):
                if file.startswith(f"{username}_"):
                    os.remove(os.path.join(self.ENCRYPTED_DIR, file))
                    deleted_count["files"] += 1
            for key in os.listdir(self.KEYS_DIR):
                if key.startswith(f"{username}_"):
                    os.remove(os.path.join(self.KEYS_DIR, key))
                    deleted_count["keys"] += 1
            for backup in os.listdir(self.BACKUP_DIR):
                if backup.startswith(f"{username}_"):
                    os.remove(os.path.join(self.BACKUP_DIR, backup))
                    deleted_count["backups"] += 1
                    
            with open(self.METADATA_FILE, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            keys_to_delete = [k for k in metadata.keys() if k.startswith(f"{username}_")]
            for key in keys_to_delete:
                del metadata[key]
            with open(self.METADATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
                
            self._log_action(username, "DELETE_ALL_DATA",
                             f"Deleted {deleted_count['files']} files, {deleted_count['keys']} keys, {deleted_count['backups']} backups")
            return f"Success! Deleted {deleted_count['files']} file(s), {deleted_count['keys']} key(s), and {deleted_count['backups']} backup(s)."
        except Exception as e:
            return f"Error: {e}"

    def delete_own_account(self, username, password):
        if username == self.ADMIN_USER:
            return "Error: Cannot delete admin account."
            
        hashed_password = self._hash_password_new(username, password)
        legacy_hash = self._hash_password_old(password)
        
        with open(self.USERS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split(':')
                if len(parts) >= 2 and parts[0] == username:
                    if parts[1] != hashed_password and parts[1] != legacy_hash:
                        return "Error: Incorrect password."
                    break
                    
        data_result = self.delete_all_user_data(username, password)
        if "Error" in data_result:
            return data_result
            
        try:
            with open(self.USERS_FILE, 'r', encoding='utf-8') as f:
                lines = [line for line in f if not line.startswith(f"{username}:")]
            with open(self.USERS_FILE, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            self._log_action(username, "DELETE_OWN_ACCOUNT", "User deleted their own account")
            return "Success! Your account and all data have been permanently deleted."
        except Exception as e:
            return f"Error: {e}"

    def _format_file_size(self, size_bytes):
        if size_bytes < 1024:
            return f"{size_bytes} bytes"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.2f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


class ConsoleApp:
    def __init__(self):
        self.logic = CEncryptLogic()
        self.current_user = None
        self.user_role = None
        _art = r"""
        ______            ______                            __ 
       / ____/           / ____/___  ____________  ______  / /_
      / /      ______   / __/ / __ \/ ___/ ___/ / / / __ \/ __/
     / /___   /_____/  / /___/ / / / /__/ /  / /_/ / /_/ / /_  
     \____/           /_____/_/ /_/\___/_/   \__, / .___/\__/  
                                            /____/_/           """
        self.main_banner = (
            f"\n{Fore.CYAN}==================================================================={Style.RESET_ALL}\n"
            f"{Fore.CYAN}{_art}{Style.RESET_ALL}\n"
            f"\n{Fore.GREEN}                Secure File Encryption Platform v2.0             {Style.RESET_ALL}\n"
            f"{Fore.CYAN}==================================================================={Style.RESET_ALL}\n"
        )

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def pause(self):
        input(f"\n{Fore.YELLOW}[Press Enter to continue...]{Style.RESET_ALL}")

    def print_header(self, title):
        print(f"\n{Fore.CYAN}{title}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}  {'-' * len(title)}{Style.RESET_ALL}")

    def safe_input(self, prompt):
        try:
            return input(f"  {Fore.WHITE}{prompt}{Style.RESET_ALL}").strip()
        except KeyboardInterrupt:
            print(f"\n{Fore.RED}Operation cancelled.{Style.RESET_ALL}")
            return None
        except Exception:
            return None

    def strip_quotes(self, text):
        if not text:
            return text
        text = text.strip()
        if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
            return text[1:-1]
        return text

    def _pick_file(self, title="Select a file", filetypes=None):
        """Open a native file picker dialog. Returns path or None."""
        if not _TK_AVAILABLE:
            return None
        try:
            root = tk.Tk()
            root.withdraw()
            root.update()            # flush event queue so the dialog surfaces on top
            root.attributes('-topmost', True)
            root.lift()
            if filetypes is None:
                filetypes = [("All files", "*.*")]
            path = filedialog.askopenfilename(
                parent=root,
                title=title,
                filetypes=filetypes
            )
            root.destroy()
            return path if path else None
        except Exception:
            return None

    def _pick_folder(self, title="Select save folder"):
        """Open a native folder picker dialog. Returns path or None."""
        if not _TK_AVAILABLE:
            return None
        try:
            root = tk.Tk()
            root.withdraw()
            root.update()
            root.attributes('-topmost', True)
            root.lift()
            path = filedialog.askdirectory(
                parent=root,
                title=title
            )
            root.destroy()
            return path if path else None
        except Exception:
            return None

    def safe_password(self, prompt="Password: "):
        try:
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=getpass.GetPassWarning)
                return getpass.getpass(f"  {Fore.WHITE}{prompt}{Style.RESET_ALL}").strip()
        except KeyboardInterrupt:
            print(f"\n{Fore.RED}Operation cancelled.{Style.RESET_ALL}")
            return None
        except Exception:
            return self.safe_input(prompt)

    def _format_display_name(self, filename):
        if '_' in filename:
            filename = filename.split('_', 1)[1]
        filename = filename.replace('.enc', '').replace('.key', '')
        return filename[:27] + '...' if len(filename) > 30 else filename

    def run(self):
        while True:
            self.clear_screen()
            print(self.main_banner)
            print(f"  {Fore.YELLOW}Storage:{Style.RESET_ALL} {self.logic.CSTORAGE_DIR}\n")
            print(f"    {Fore.GREEN}[1]{Style.RESET_ALL} Login")
            print(f"    {Fore.GREEN}[2]{Style.RESET_ALL} Register New User")
            print(f"    {Fore.RED}[3]{Style.RESET_ALL} Exit Application\n")
            choice = self.safe_input("Select option: ")
            
            if choice == '1':
                self.login_flow()
            elif choice == '2':
                self.register_flow()
            elif choice == '3':
                self.clear_screen()
                print(f"\n{Fore.GREEN}Thank you for using C-Encrypt!{Style.RESET_ALL}")
                print(f"{Fore.GREEN}Goodbye!{Style.RESET_ALL}\n")
                sys.exit(0)
            else:
                print(f"\n{Fore.RED}[ERROR] Invalid choice. Try again.{Style.RESET_ALL}")
                self.pause()

    def register_flow(self):
        self.clear_screen()
        self.print_header("USER REGISTRATION")
        print(f"\n{Fore.YELLOW}Password Requirements:{Style.RESET_ALL}")
        print("    * Minimum 8 characters")
        print("    * At least one uppercase letter")
        print("    * At least one number\n")
        
        username = self.safe_input("Username: ")
        if not username:
            return
            
        password = self.safe_input("Password: ")
        if not password:
            print(f"\n{Fore.RED}[ERROR] Password cannot be empty.{Style.RESET_ALL}")
            self.pause()
            return
            
        confirm = self.safe_input("Confirm Password: ")
        if password != confirm:
            print(f"\n{Fore.RED}[ERROR] Passwords don't match.{Style.RESET_ALL}")
            self.pause()
            return
            
        result = self.logic.register_user(username, password)
        if result == "Success":
            print(f"\n{Fore.GREEN}[SUCCESS] Registration complete!{Style.RESET_ALL}")
            print("\nLogging you in...")
            self.pause()
            success, role, error_msg, reset_required = self.logic.login_user(username, password)
            if success:
                self.current_user = username
                self.user_role = role
                self.clear_screen()
                print(f"\n{Fore.GREEN}[SUCCESS] Welcome, {self.current_user}!{Style.RESET_ALL}")
                self.pause()
                if reset_required:
                    self.forced_password_reset()
                if self.user_role == "ADMIN":
                    self.admin_menu()
                else:
                    self.session_menu()
            else:
                print(f"\n{Fore.RED}[ERROR] Auto-login failed. Please login manually.{Style.RESET_ALL}")
                self.pause()
        else:
            print(f"\n{Fore.RED}[ERROR] {result}{Style.RESET_ALL}")
            self.pause()

    def login_flow(self):
        self.clear_screen()
        self.print_header("USER LOGIN")
        print()
        username = self.safe_input("Username: ")
        if not username:
            return

        password = self.safe_password("Password: ")
        if not password:
            print(f"\n{Fore.RED}[ERROR] Password cannot be empty.{Style.RESET_ALL}")
            self.pause()
            return

        success, role, error_msg, reset_required = self.logic.login_user(username, password)

        if success:
            self.current_user = username
            self.user_role = role
            print(f"\n{Fore.GREEN}[SUCCESS] Welcome, {self.current_user}!{Style.RESET_ALL}")
            if role == "ADMIN":
                print(f"  {Fore.MAGENTA}[ADMIN] Administrator access granted{Style.RESET_ALL}")
            self.pause()
            if reset_required:
                self.forced_password_reset()
            if self.user_role == "ADMIN":
                self.admin_menu()
            else:
                self.session_menu()
        else:
            print(f"\n{Fore.RED}[ERROR] {error_msg}{Style.RESET_ALL}")
            self.pause()

    def forced_password_reset(self):
        while True:
            self.clear_screen()
            self.print_header("PASSWORD RESET REQUIRED")
            print(f"\n{Fore.YELLOW}Your administrator has required you to reset your password.{Style.RESET_ALL}\n")
            
            new_password = self.safe_password("New Password: ")
            if not new_password:
                print(f"\n{Fore.RED}[ERROR] Password cannot be empty. Returning to main menu.{Style.RESET_ALL}")
                self.pause()
                self.current_user = None
                self.user_role = None
                return
                
            is_strong, issues = self.logic.check_password_strength(new_password)
            if not is_strong:
                print(f"\n{Fore.RED}[ERROR] Password requirements not met:{Style.RESET_ALL}")
                for issue in issues:
                    print(f"    * {issue}")
                self.pause()
                continue
                
            confirm = self.safe_password("Confirm New Password: ")
            if new_password != confirm:
                print(f"\n{Fore.RED}[ERROR] Passwords don't match.{Style.RESET_ALL}")
                self.pause()
                continue
                
            result = self.logic.change_password(self.current_user, "", new_password)
            if "Success" in result or result == "Success":
                print(f"\n{Fore.GREEN}[SUCCESS] Password changed successfully!{Style.RESET_ALL}")
                self.pause()
                # Update reset flag to false
                self.logic.set_password_reset_required("Admin", self.current_user, required=False)
                return
            else:
                print(f"\n{Fore.RED}[ERROR] Failed to change password. Contact administrator.{Style.RESET_ALL}")
                self.pause()
                self.current_user = None
                self.user_role = None
                return

    def session_menu(self):
        while True:
            self.clear_screen()
            print(self.main_banner)
            self.print_header(f"USER DASHBOARD - {self.current_user}")
            print(f"\n{Fore.CYAN}FILE OPERATIONS              ACCOUNT & SECURITY           DANGER!{Style.RESET_ALL}")
            print(f"  {Fore.GREEN}[1]{Style.RESET_ALL} Upload File               {Fore.GREEN}[7]{Style.RESET_ALL} List My Keys            {Fore.RED}[13]{Style.RESET_ALL} Delete All My Data")
            print(f"  {Fore.GREEN}[2]{Style.RESET_ALL} Download File             {Fore.GREEN}[8]{Style.RESET_ALL} Delete a Key            {Fore.RED}[14]{Style.RESET_ALL} Delete My Account")
            print(f"  {Fore.GREEN}[3]{Style.RESET_ALL} List My Files             {Fore.GREEN}[9]{Style.RESET_ALL} Backup Keys")
            print(f"  {Fore.GREEN}[4]{Style.RESET_ALL} File Info                {Fore.GREEN}[10]{Style.RESET_ALL} Change Password")
            print(f"  {Fore.GREEN}[5]{Style.RESET_ALL} Share a Key              {Fore.GREEN}[11]{Style.RESET_ALL} Recent Activity")
            print(f"  {Fore.GREEN}[6]{Style.RESET_ALL} Delete a File            {Fore.RED}[12]{Style.RESET_ALL} Logout\n")
            
            choice = self.safe_input("Select option: ")
            if choice == '1':
                self.upload_flow()
            elif choice == '2':
                self.download_flow()
            elif choice == '3':
                self.list_files_flow()
            elif choice == '4':
                self.file_info_flow()
            elif choice == '5':
                self.share_flow()
            elif choice == '6':
                self.delete_file_flow()
            elif choice == '7':
                self.list_keys_flow()
            elif choice == '8':
                self.delete_key_flow()
            elif choice == '9':
                self.backup_keys_flow()
            elif choice == '10':
                self.change_password_flow()
            elif choice == '11':
                self.recent_activity_flow()
            elif choice == '12':
                self.logic._log_action(self.current_user, "LOGOUT", "User logged out")
                self.current_user = None
                self.user_role = None
                print(f"\n{Fore.GREEN}[SUCCESS] Logged out.{Style.RESET_ALL}")
                self.pause()
                break
            elif choice == '13':
                self.delete_all_data_flow()
            elif choice == '14':
                self.delete_own_account_flow()
            else:
                print(f"\n{Fore.RED}[ERROR] Invalid choice. Try again.{Style.RESET_ALL}")
                self.pause()

    def admin_menu(self):
        while True:
            self.clear_screen()
            self.print_header(f"ADMIN PANEL - {self.current_user}")
            print(f"\n{Fore.CYAN}USER MANAGEMENT                FILE & LOG MANAGEMENT{Style.RESET_ALL}")
            print(f"  {Fore.GREEN}[1]{Style.RESET_ALL} View All Users              {Fore.GREEN}[5]{Style.RESET_ALL} Delete Any File")
            print(f"  {Fore.GREEN}[2]{Style.RESET_ALL} Delete User Account         {Fore.GREEN}[6]{Style.RESET_ALL} View All Logs")
            print(f"  {Fore.GREEN}[3]{Style.RESET_ALL} Force Password Reset        {Fore.GREEN}[7]{Style.RESET_ALL} Export Logs")
            print(f"  {Fore.GREEN}[4]{Style.RESET_ALL} View All Files              {Fore.GREEN}[8]{Style.RESET_ALL} Clear All Logs")
            print(f"                            {Fore.GREEN}[9]{Style.RESET_ALL} Clear All Backups")
            print(f"                            {Fore.RED}[10]{Style.RESET_ALL} Delete All Files & Keys")
            print(f"\n{Fore.CYAN}SYSTEM ADMINISTRATION{Style.RESET_ALL}")
            print(f"  {Fore.GREEN}[11]{Style.RESET_ALL} System Statistics         {Fore.GREEN}[14]{Style.RESET_ALL} System Cleanup Utility")
            print(f"  {Fore.GREEN}[12]{Style.RESET_ALL} User Activity Summary     {Fore.GREEN}[15]{Style.RESET_ALL} Maintenance Mode")
            print(f"  {Fore.GREEN}[13]{Style.RESET_ALL} Export Metadata           {Fore.RED}[16]{Style.RESET_ALL} Logout\n")
            
            choice = self.safe_input("Select option: ")
            if choice == '1':
                self.view_all_users_detailed()
            elif choice == '2':
                self.delete_user_flow()
            elif choice == '3':
                self.force_reset_flow()
            elif choice == '4':
                self.view_all_files()
            elif choice == '5':
                self.admin_delete_file_flow()
            elif choice == '6':
                self.logs_flow()
            elif choice == '7':
                self.export_logs_flow()
            elif choice == '8':
                self.clear_logs_flow()
            elif choice == '9':
                self.clear_backups_flow()
            elif choice == '10':
                self.delete_all_files_and_keys_flow()
            elif choice == '11':
                self.system_stats()
            elif choice == '12':
                self.user_activity_summary_flow()
            elif choice == '13':
                self.export_metadata_flow()
            elif choice == '14':
                self.cleanup_utility_flow()
            elif choice == '15':
                self.maintenance_mode_flow()
            elif choice == '16':
                self.logic._log_action(self.current_user, "LOGOUT", "Admin logged out")
                self.current_user = None
                self.user_role = None
                print(f"\n{Fore.GREEN}[SUCCESS] Logged out.{Style.RESET_ALL}")
                self.pause()
                break
            else:
                print(f"\n{Fore.RED}[ERROR] Invalid choice. Try again.{Style.RESET_ALL}")
                self.pause()

    def _show_progress_bar(self, message, duration=2.0):
        print(f"\n{Fore.CYAN}{message}{Style.RESET_ALL}")
        bar_length = 50
        for i in range(bar_length + 1):
            percent = (i / bar_length) * 100
            filled = f"{Fore.GREEN}█{Style.RESET_ALL}" * i
            empty = f"{Fore.LIGHTBLACK_EX}░{Style.RESET_ALL}" * (bar_length - i)
            print(f"\r  [{filled}{empty}] {percent:.0f}%", end='', flush=True)
            time.sleep(duration / bar_length)
        print()

    def upload_flow(self):
        self.clear_screen()
        self.print_header("UPLOAD FILE")
        if self.logic.is_maintenance_mode():
            print(f"\n{Fore.RED}Uploads are currently disabled during maintenance.{Style.RESET_ALL}")
            self.pause()
            return

        file_path = None

        if _TK_AVAILABLE:
            print(f"\n{Fore.CYAN}Opening file picker...{Style.RESET_ALL}")
            file_path = self._pick_file(title="Select file to encrypt and upload")
            if file_path:
                print(f"  {Fore.GREEN}Selected:{Style.RESET_ALL} {file_path}")
            else:
                print(f"  {Fore.YELLOW}No file selected. Enter path manually.{Style.RESET_ALL}")

        if not file_path:
            print(f"\n{Fore.YELLOW}Enter the file path (drag & drop or type it):{Style.RESET_ALL}")
            file_path = self.safe_input("File Path: ")
            if not file_path:
                return
            file_path = self.strip_quotes(file_path)

        if not os.path.exists(file_path):
            print(f"\n{Fore.RED}[ERROR] File not found: {file_path}{Style.RESET_ALL}")
            self.pause()
            return

        file_size = os.path.getsize(file_path)
        if file_size > self.logic.MAX_FILE_SIZE:
            print(f"\n{Fore.RED}[ERROR] File too large ({self.logic._format_file_size(file_size)}). Max allowed is 50 MB.{Style.RESET_ALL}")
            self.pause()
            return

        self._show_progress_bar("Encrypting and uploading file...", 1.5)
        result = self.logic.upload_file(self.current_user, file_path)
        self._display_result(result)
        self.pause()

    def list_files_flow(self):
        self.clear_screen()
        self.print_header("YOUR ENCRYPTED FILES")
        files = self.logic.get_user_files(self.current_user)
        print()
        if not files:
            print("  No files found.")
        else:
            for i, f in enumerate(files, 1):
                display_name = self._format_display_name(f)
                tag = f" {Fore.YELLOW}(shared){Style.RESET_ALL}" if not f.startswith(f"{self.current_user}_") else ""
                print(f"  {Fore.GREEN}[{i}]{Style.RESET_ALL} {display_name}{tag}")
        self.pause()

    def file_info_flow(self):
        self.clear_screen()
        self.print_header("FILE INFORMATION")
        files = self.logic.get_user_files(self.current_user)
        if not files:
            print(f"\nNo files available.")
            self.pause()
            return
        print(f"\n{Fore.YELLOW}SELECT FILE{Style.RESET_ALL}")
        for i, f in enumerate(files, 1):
            print(f"  {Fore.GREEN}[{i}]{Style.RESET_ALL} {self._format_display_name(f)}")
        print()
        idx = self._get_valid_index(f"Select file (1-{len(files)}): ", len(files))
        if idx is None:
            return
            
        selected = files[idx]
        original_name = self._format_display_name(selected)
        owner = selected.split('_')[0] if '_' in selected else self.current_user
        metadata_key = selected.replace('.enc', '')
        parts = metadata_key.split('_', 1)
        
        metadata = None
        if len(parts) == 2:
            owner, base_name = parts
            try:
                with open(self.logic.METADATA_FILE, 'r', encoding='utf-8') as f:
                    all_metadata = json.load(f)
                metadata = all_metadata.get(f"{owner}_{base_name}")
            except Exception:
                pass

        print(f"\n{Fore.CYAN}File:{Style.RESET_ALL} {original_name}")
        if metadata:
            print(f"  {Fore.CYAN}Upload Time:{Style.RESET_ALL} {metadata.get('upload_time', 'Unknown')}")
            size_bytes = metadata.get('size', 0)
            print(f"  {Fore.CYAN}Size:{Style.RESET_ALL} {self.logic._format_file_size(size_bytes)}")
            print(f"  {Fore.CYAN}Encrypted:{Style.RESET_ALL} Yes")
            if metadata.get('hash'):
                print(f"  {Fore.CYAN}Integrity:{Style.RESET_ALL} Protected")
        else:
            print("  No metadata available.")
        self.pause()

    def _get_valid_index(self, prompt, max_index):
        choice = self.safe_input(prompt)
        if not choice:
            return None
        try:
            idx = int(choice) - 1
            if 0 <= idx < max_index:
                return idx
            raise ValueError()
        except (ValueError, IndexError):
            print(f"\n{Fore.RED}[ERROR] Invalid selection. Try again.{Style.RESET_ALL}")
            self.pause()
            return None

    def download_flow(self):
        self.clear_screen()
        self.print_header("DOWNLOAD & DECRYPT FILE")
        files = self.logic.get_user_files(self.current_user)
        file_idx = self._select_from_list(files, "file")
        if file_idx is None:
            return
        keys = self.logic.get_user_keys(self.current_user)
        key_idx = self._select_from_list(keys, "key")
        if key_idx is None:
            return

        # Ask where to save
        save_dir = None
        if _TK_AVAILABLE:
            print(f"\n{Fore.YELLOW}A folder picker will open — choose where to save the decrypted file.{Style.RESET_ALL}")
            print(f"  {Fore.CYAN}(Cancel to save to default cstorage/decrypted/ folder){Style.RESET_ALL}\n")
            input(f"  {Fore.WHITE}Press Enter to open folder picker...{Style.RESET_ALL}")
            save_dir = self._pick_folder(title="Choose folder to save decrypted file")
            if save_dir:
                print(f"\n  {Fore.GREEN}Save to:{Style.RESET_ALL} {save_dir}")
            else:
                print(f"\n  {Fore.YELLOW}No folder selected. Saving to default decrypted folder.{Style.RESET_ALL}")

        self._show_progress_bar("Downloading and decrypting file...", 1.5)
        key_path = os.path.join(self.logic.KEYS_DIR, keys[key_idx])
        result = self.logic.download_file(self.current_user, files[file_idx], key_path, save_dir=save_dir)
        self._display_result(result)
        self.pause()

    def share_flow(self):
        self.clear_screen()
        self.print_header("SHARE ENCRYPTION KEY")
        keys = self.logic.get_user_keys(self.current_user)
        idx = self._select_from_list(keys, "key")
        if idx is None:
            return
        print()
        target = self.safe_input("Share with username: ")
        if not target:
            return
        print("\nProcessing...")
        result = self.logic.share_key(self.current_user, keys[idx], target)
        self._display_result(result)
        self.pause()

    def delete_file_flow(self):
        self.clear_screen()
        self.print_header("DELETE FILE")
        files = self.logic.get_user_files(self.current_user)
        own_files = [f for f in files if f.startswith(f"{self.current_user}_")]
        idx = self._select_from_list(own_files, "file")
        if idx is None:
            return
        display_name = self._format_display_name(own_files[idx])
        if self._confirm_action(f"Delete '{display_name}' permanently?"):
            result = self.logic.delete_file(self.current_user, own_files[idx])
            self._display_result(result)
        else:
            print(f"\n{Fore.YELLOW}[INFO] Deletion cancelled.{Style.RESET_ALL}")
            self.pause()

    def delete_key_flow(self):
        self.clear_screen()
        self.print_header("DELETE ENCRYPTION KEY")
        keys = self.logic.get_user_keys(self.current_user)
        idx = self._select_from_list(keys, "key")
        if idx is None:
            return
        display_name = self._format_display_name(keys[idx])
        print(f"\n{Fore.RED}WARNING: Delete key '{display_name}' permanently?{Style.RESET_ALL}")
        print("  You won't be able to decrypt the file without this key.\n")
        if self.safe_input("Type 'y' to confirm: ").lower() == 'y':
            result = self.logic.delete_key(self.current_user, keys[idx])
            self._display_result(result)
        else:
            print(f"\n{Fore.YELLOW}[INFO] Deletion cancelled.{Style.RESET_ALL}")
            self.pause()

    def delete_user_flow(self):
        self.clear_screen()
        self.print_header("DELETE USER ACCOUNT")
        print(f"\n{Fore.RED}WARNING: This will permanently delete the user and all data.{Style.RESET_ALL}\n")
        target = self.safe_input("Enter username to delete: ")
        if not target:
            return
        print(f"\nConfirm deletion of user '{target}'")
        if self.safe_input("Type 'y' to confirm: ").lower() == 'y':
            result = self.logic.delete_user_account(self.current_user, target)
            self._display_result(result)
        else:
            print(f"\n{Fore.YELLOW}[INFO] Deletion cancelled.{Style.RESET_ALL}")
            self.pause()

    def admin_delete_file_flow(self):
        self.clear_screen()
        self.print_header("DELETE ANY FILE")
        files = self.logic.get_all_files()
        idx = self._select_from_list(files, "file")
        if idx is None:
            return
        selected = files[idx]
        print(f"\nDelete '{selected}'?")
        if self.safe_input("Type 'y' to confirm: ").lower() == 'y':
            result = self.logic.admin_delete_any_file(self.current_user, selected)
            self._display_result(result)
        else:
            print(f"\n{Fore.YELLOW}[INFO] Deletion cancelled.{Style.RESET_ALL}")
            self.pause()

    def export_logs_flow(self):
        self.clear_screen()
        self.print_header("EXPORT LOGS")
        print("\nExporting logs...\n")
        result = self.logic.export_logs()
        self._display_result(result)
        self.pause()

    def export_metadata_flow(self):
        self.clear_screen()
        self.print_header("EXPORT METADATA")
        print("\nExporting metadata...\n")
        result = self.logic.export_metadata()
        self._display_result(result)
        self.pause()

    def force_reset_flow(self):
        self.clear_screen()
        self.print_header("FORCE PASSWORD RESET")
        print(f"\n{Fore.RED}WARNING: This will immediately reset the user's password.{Style.RESET_ALL}\n")
        target = self.safe_input("Enter username: ")
        if not target:
            return
        if not self.logic._check_user_exists(target):
            print(f"\n{Fore.RED}[ERROR] User '{target}' not found.{Style.RESET_ALL}")
            self.pause()
            return
        if target == self.logic.ADMIN_USER:
            print(f"\n{Fore.RED}[ERROR] Cannot reset admin password.{Style.RESET_ALL}")
            self.pause()
            return
            
        print(f"\n{Fore.YELLOW}Password Requirements:{Style.RESET_ALL}")
        print("    * Minimum 8 characters")
        print("    * At least one uppercase letter")
        print("    * At least one number\n")
        new_password = self.safe_password("New Password: ")
        if not new_password:
            return
            
        result = self.logic.reset_user_password(self.current_user, target, new_password)
        if result == "Success":
            print(f"\n{Fore.GREEN}[SUCCESS] Password reset for '{target}'!{Style.RESET_ALL}")
            print(f"  {Fore.YELLOW}New Password: {new_password}{Style.RESET_ALL}")
        else:
            self._display_result(result)
        self.pause()

    def delete_all_data_flow(self):
        self.clear_screen()
        self.print_header("DELETE ALL MY DATA")
        print(f"\n{Fore.RED}⚠️  CRITICAL WARNING ⚠️{Style.RESET_ALL}")
        print("\nThis will permanently delete:")
        print("    - ALL your encrypted files")
        print("    - ALL your encryption keys (owned and shared)")
        print("    - ALL your backups")
        print("\nThis action CANNOT be undone!")
        print("  Your account will remain active but all data will be lost.\n")
        
        confirm1 = self.safe_input("Type 'DELETE MY DATA' to confirm: ")
        if confirm1 != "DELETE MY DATA":
            print(f"\n{Fore.YELLOW}[INFO] Operation cancelled.{Style.RESET_ALL}")
            self.pause()
            return
            
        password = self.safe_password("\nEnter your password to confirm: ")
        if not password:
            print(f"\n{Fore.YELLOW}[INFO] Operation cancelled.{Style.RESET_ALL}")
            self.pause()
            return
            
        result = self.logic.delete_all_user_data(self.current_user, password)
        self._display_result(result)
        self.pause()

    def delete_own_account_flow(self):
        self.clear_screen()
        self.print_header("DELETE MY ACCOUNT")
        print(f"\n{Fore.RED}⚠️  CRITICAL WARNING ⚠️{Style.RESET_ALL}")
        print("\nThis will permanently:")
        print("    - DELETE your account")
        print("    - DELETE all your files and keys")
        print("    - DELETE all your backups")
        print("    - LOG YOU OUT immediately")
        print("\nThis action is IRREVERSIBLE!")
        print("  You will need to register again to use this system.\n")
        
        confirm1 = self.safe_input("Type 'DELETE MY ACCOUNT' to confirm: ")
        if confirm1 != "DELETE MY ACCOUNT":
            print(f"\n{Fore.YELLOW}[INFO] Operation cancelled.{Style.RESET_ALL}")
            self.pause()
            return
            
        password = self.safe_password("\nEnter your password to confirm: ")
        if not password:
            print(f"\n{Fore.YELLOW}[INFO] Operation cancelled.{Style.RESET_ALL}")
            self.pause()
            return
            
        confirm2 = self.safe_input("\nAre you absolutely sure? (yes/no): ")
        if confirm2.lower() != "yes":
            print(f"\n{Fore.YELLOW}[INFO] Operation cancelled.{Style.RESET_ALL}")
            self.pause()
            return
            
        result = self.logic.delete_own_account(self.current_user, password)
        if "Success" in result:
            print(f"\n{Fore.GREEN}[SUCCESS] {result}{Style.RESET_ALL}")
            print("\nYou will now be logged out.")
            self.pause()
            self.current_user = None
            self.user_role = None
        else:
            self._display_result(result)
            self.pause()

    def list_keys_flow(self):
        self.clear_screen()
        self.print_header("YOUR ENCRYPTION KEYS")
        keys = self.logic.get_user_keys(self.current_user)
        print()
        if not keys:
            print("  No keys found.")
        else:
            for i, k in enumerate(keys, 1):
                display_name = self._format_display_name(k)
                tag = f" {Fore.YELLOW}(shared){Style.RESET_ALL}" if not k.startswith(f"{self.current_user}_") else ""
                print(f"  {Fore.GREEN}[{i}]{Style.RESET_ALL} {display_name}{tag}")
        self.pause()

    def backup_keys_flow(self):
        self.clear_screen()
        self.print_header("BACKUP ENCRYPTION KEYS")
        print("\nThis will export all your keys to a backup file.\n")
        confirm = self.safe_input("Continue? (y/n): ")
        if confirm.lower() == 'y':
            result = self.logic.backup_user_keys(self.current_user)
            self._display_result(result)
        else:
            print(f"\n{Fore.YELLOW}[INFO] Backup cancelled.{Style.RESET_ALL}")
            self.pause()

    def change_password_flow(self):
        self.clear_screen()
        self.print_header("CHANGE PASSWORD")
        print()
        old_password = self.safe_password("Current Password: ")
        if not old_password:
            return
        new_password = self.safe_password("New Password: ")
        if not new_password:
            return
            
        is_strong, issues = self.logic.check_password_strength(new_password)
        if not is_strong:
            print(f"\n{Fore.RED}[ERROR] Password requirements not met:{Style.RESET_ALL}")
            for issue in issues:
                print(f"    * {issue}")
            self.pause()
            return
            
        confirm = self.safe_password("Confirm New Password: ")
        if new_password != confirm:
            print(f"\n{Fore.RED}[ERROR] Passwords don't match.{Style.RESET_ALL}")
            self.pause()
            return
            
        result = self.logic.change_password(self.current_user, old_password, new_password)
        if result == "Success":
            print(f"\n{Fore.GREEN}[SUCCESS] Password changed successfully!{Style.RESET_ALL}")
        else:
            self._display_result(result)
        self.pause()

    def recent_activity_flow(self):
        self.clear_screen()
        self.print_header("RECENT ACTIVITY")
        activities = self.logic.get_recent_activity(self.current_user)
        print()
        if not activities:
            print("  No recent activity.")
        else:
            for activity in activities:
                print(f"  {activity}")
        self.pause()

    def view_all_users_detailed(self):
        self.clear_screen()
        self.print_header("ALL USERS - DETAILED VIEW")
        users = self.logic.get_all_users_detailed()
        print()
        for user in users:
            print(f"  {Fore.CYAN}Username:{Style.RESET_ALL} {user['username']}")
            print(f"  {Fore.CYAN}Role:{Style.RESET_ALL} {user['role']}")
            print(f"  {Fore.CYAN}Files:{Style.RESET_ALL} {user['files']} | {Fore.CYAN}Keys:{Style.RESET_ALL} {user['keys']}")
            print()
        self.pause()

    def view_all_files(self):
        self.clear_screen()
        self.print_header("ALL ENCRYPTED FILES")
        files = self.logic.get_all_files()
        print()
        if not files:
            print("  No files in storage.")
        else:
            for f in files:
                print(f"  * {f}")
        self.pause()

    def logs_flow(self):
        self.clear_screen()
        self.print_header("SYSTEM LOGS")
        logs = self.logic.get_logs()
        print(f"\n{logs}")
        self.pause()

    def clear_logs_flow(self):
        self.clear_screen()
        self.print_header("CLEAR LOGS")
        print(f"\n{Fore.RED}WARNING: This action is permanent.{Style.RESET_ALL}\n")
        if self.safe_input("Type 'y' to confirm: ").lower() == 'y':
            result = self.logic.clear_logs()
            print(f"\n{Fore.GREEN}[SUCCESS] {result}{Style.RESET_ALL}")
            self.logic._log_action(self.current_user, "CLEAR_LOGS", "All logs cleared")
        else:
            print(f"\n{Fore.YELLOW}[INFO] Action cancelled.{Style.RESET_ALL}")
        self.pause()

    def clear_backups_flow(self):
        self.clear_screen()
        self.print_header("CLEAR ALL BACKUPS")
        print(f"\n{Fore.RED}WARNING: This will permanently delete all backup files.{Style.RESET_ALL}")
        print("  This includes:")
        print("    - Key backups")
        print("    - Log exports")
        print("    - Metadata exports\n")
        if self.safe_input("Type 'y' to confirm: ").lower() == 'y':
            result = self.logic.clear_backups(self.current_user)
            self._display_result(result)
        else:
            print(f"\n{Fore.YELLOW}[INFO] Action cancelled.{Style.RESET_ALL}")
        self.pause()

    def delete_all_files_and_keys_flow(self):
        self.clear_screen()
        self.print_header("DELETE ALL FILES & KEYS")
        print(f"\n{Fore.RED}⚠️  CRITICAL WARNING ⚠️{Style.RESET_ALL}")
        print("\nThis will permanently delete:")
        print("    - ALL encrypted files")
        print("    - ALL encryption keys")
        print("    - ALL file metadata")
        print("\nThis action CANNOT be undone!")
        print("  All users will lose access to their files.\n")
        
        confirm1 = self.safe_input("Type 'DELETE ALL' to confirm: ")
        if confirm1 != "DELETE ALL":
            print(f"\n{Fore.YELLOW}[INFO] Operation cancelled.{Style.RESET_ALL}")
            self.pause()
            return
            
        confirm2 = self.safe_input("Are you absolutely sure? (yes/no): ")
        if confirm2.lower() != "yes":
            print(f"\n{Fore.YELLOW}[INFO] Operation cancelled.{Style.RESET_ALL}")
            self.pause()
            return
            
        result = self.logic.delete_all_files_and_keys(self.current_user)
        self._display_result(result)
        self.pause()

    def system_stats(self):
        self.clear_screen()
        self.print_header("SYSTEM STATISTICS")
        print()
        users = self.logic.get_all_users()
        files = self.logic.get_all_files()
        keys = os.listdir(self.logic.KEYS_DIR) if os.path.exists(self.logic.KEYS_DIR) else []
        
        print(f"  {Fore.CYAN}Total Users:{Style.RESET_ALL}        {len(users)}")
        print(f"  {Fore.CYAN}Total Files:{Style.RESET_ALL}        {len(files)}")
        print(f"  {Fore.CYAN}Total Keys:{Style.RESET_ALL}         {len(keys)}")
        print()
        print(f"  {Fore.CYAN}Encrypted Path:{Style.RESET_ALL}     {self.logic.ENCRYPTED_DIR}")
        print(f"  {Fore.CYAN}Decrypted Path:{Style.RESET_ALL}     {self.logic.DECRYPTED_DIR}")
        self.pause()

    def user_activity_summary_flow(self):
        self.clear_screen()
        self.print_header("USER ACTIVITY SUMMARY")
        activity = self.logic.get_user_activity_summary()
        print()
        if not activity:
            print("  No activity data available.")
        else:
            for username, stats in activity.items():
                print(f"  {Fore.CYAN}User:{Style.RESET_ALL} {username}")
                print(f"    {Fore.CYAN}Logins:{Style.RESET_ALL} {stats['logins']} | {Fore.CYAN}Uploads:{Style.RESET_ALL} {stats['uploads']}")
                print(f"    {Fore.CYAN}Downloads:{Style.RESET_ALL} {stats['downloads']} | {Fore.CYAN}Deletes:{Style.RESET_ALL} {stats['deletes']}")
                print()
        self.pause()

    def cleanup_utility_flow(self):
        self.clear_screen()
        self.print_header("SYSTEM CLEANUP UTILITY")
        print("\nScanning for orphaned files...\n")
        orphaned_enc, orphaned_keys = self.logic.find_orphaned_files()
        total = len(orphaned_enc) + len(orphaned_keys)
        
        if total == 0:
            print("  No orphaned files found. System is clean.")
            self.pause()
            return
            
        print(f"  Found {len(orphaned_enc)} orphaned encrypted files")
        print(f"  Found {len(orphaned_keys)} orphaned key files")
        print(f"\n{Fore.YELLOW}Total: {total} orphaned files{Style.RESET_ALL}\n")
        
        if orphaned_enc:
            print("  Encrypted files:")
            for f in orphaned_enc[:10]:
                print(f"    - {f}")
            if len(orphaned_enc) > 10:
                print(f"    ... and {len(orphaned_enc) - 10} more")
                
        if orphaned_keys:
            print("\n  Key files:")
            for k in orphaned_keys[:10]:
                print(f"    - {k}")
            if len(orphaned_keys) > 10:
                print(f"    ... and {len(orphaned_keys) - 10} more")
                
        print(f"\n{Fore.RED}WARNING: This will permanently delete these files.{Style.RESET_ALL}\n")
        if self.safe_input("Type 'y' to confirm: ").lower() == 'y':
            result = self.logic.cleanup_orphaned_files(self.current_user, orphaned_enc, orphaned_keys)
            self._display_result(result)
        else:
            print(f"\n{Fore.YELLOW}[INFO] Cleanup cancelled.{Style.RESET_ALL}")
        self.pause()

    def maintenance_mode_flow(self):
        self.clear_screen()
        self.print_header("SYSTEM MAINTENANCE MODE")
        is_active = self.logic.is_maintenance_mode()
        status = f"{Fore.RED}ENABLED{Style.RESET_ALL}" if is_active else f"{Fore.GREEN}DISABLED{Style.RESET_ALL}"
        print(f"\nCurrent Status: {status}\n")
        print("  [1] Enable Maintenance Mode")
        print("  [2] Disable Maintenance Mode")
        print("  [3] Cancel\n")
        
        choice = self.safe_input("Select option: ")
        if choice == '1':
            result = self.logic.set_maintenance_mode(True)
            print(f"\n{Fore.GREEN}[SUCCESS] {result}{Style.RESET_ALL}")
        elif choice == '2':
            result = self.logic.set_maintenance_mode(False)
            print(f"\n{Fore.GREEN}[SUCCESS] {result}{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.YELLOW}[INFO] No changes made.{Style.RESET_ALL}")
        self.pause()

    def _display_result(self, result, success_key="Success"):
        if success_key in result:
            print(f"\n{Fore.GREEN}[SUCCESS] {result}{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}[ERROR] {result}{Style.RESET_ALL}")

    def _confirm_action(self, message, confirm_word="y"):
        print(f"\n{Fore.RED}WARNING: {message}{Style.RESET_ALL}")
        print("  This action cannot be undone.\n")
        return self.safe_input(f"Type '{confirm_word}' to confirm: ").lower() == confirm_word.lower()

    def _select_from_list(self, items, item_type="item"):
        if not items:
            print(f"\nNo {item_type}s available.")
            self.pause()
            return None
            
        print(f"\n{Fore.YELLOW}SELECT {item_type.upper()}{Style.RESET_ALL}")
        for i, item in enumerate(items, 1):
            display = self._format_display_name(item) if item_type in ["file", "key"] else item
            if item_type in ["file", "key"]:
                tag = f" {Fore.YELLOW}(shared){Style.RESET_ALL}" if not item.startswith(f"{self.current_user}_") else ""
            else:
                tag = ""
            print(f"  {Fore.GREEN}[{i}]{Style.RESET_ALL} {display}{tag}")
        print()
        return self._get_valid_index(f"Select {item_type} (1-{len(items)}): ", len(items))


if __name__ == "__main__":
    try:
        app = ConsoleApp()
        app.run()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Program interrupted.{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}Fatal error: {e}{Style.RESET_ALL}")
        sys.exit(1)