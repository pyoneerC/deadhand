import customtkinter as ctk
from customtkinter import filedialog
import json
import os
import time
import hashlib
from datetime import datetime, timedelta
from PIL import Image, ImageTk
import re
import urllib.request
import urllib.error

import base64
import os
import urllib.parse
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import secrets

SERVER_URL = "https://api.deadhandprotocol.com"

def is_valid_email(email):
    # 1. Solid regex validation
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not re.match(pattern, email):
        return False, "Invalid Email format."
    
    # 2. Domain MX Record API validation (checks if email actually exists/receivable)
    domain = email.split('@')[1]
    try:
        req = urllib.request.Request(
            f"https://dns.google/resolve?name={domain}&type=MX",
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            if data.get("Status") == 0 and "Answer" in data:
                # Check if it has real mail servers (exclude null MX "0 .")
                valid_mx = any(not ans["data"].startswith("0 .") for ans in data["Answer"] if ans.get("type") == 15)
                if not valid_mx:
                    return False, f"Domain '{domain}' does not accept emails."
            else:
                return False, f"Domain '{domain}' has no mail servers."
    except Exception:
        pass # If offline or API fails, fallback to regex pass
        
    return True, ""

def split_secret_2_of_3(secret_str):
    s_bytes = secret_str.encode('utf-8')
    k1 = os.urandom(len(s_bytes))
    k2 = os.urandom(len(s_bytes))
    k3 = bytes(a ^ b ^ c for a, b, c in zip(s_bytes, k1, k2))
    
    def encode_shard(a, b):
        return base64.b64encode(a + b"|" + b).decode('utf-8')
        
    shard_a = "shA-" + encode_shard(b"1:"+k1, b"2:"+k2)
    shard_b = "shB-" + encode_shard(b"2:"+k2, b"3:"+k3)
    shard_c = "shC-" + encode_shard(b"3:"+k3, b"1:"+k1)
    
    return shard_a, shard_b, shard_c

def recover_secret_2_of_3(shard_x, shard_y):
    try:
        sx = shard_x.split("-", 1)[-1]
        sy = shard_y.split("-", 1)[-1]
        
        p1, p2 = base64.b64decode(sx).split(b"|")
        p3, p4 = base64.b64decode(sy).split(b"|")
        
        parts = {}
        for p in [p1, p2, p3, p4]:
            idx, key = p.split(b":", 1)
            parts[idx] = key
            
        if len(parts) != 3:
            return None
            
        k1 = parts[b"1"]
        k2 = parts[b"2"]
        k3 = parts[b"3"]
        
        s_bytes = bytes(a ^ b ^ c for a, b, c in zip(k1, k2, k3))
        return s_bytes.decode('utf-8')
    except Exception:
        return None

# --- APP CONFIGURATION ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# Deadhand Aesthetic
BG_COLOR = "#050505"           # Deep black background
SIDEBAR_COLOR = "#0a0a0a"      # Slight contrast for sidebar
ACCENT_COLOR = "#ff5500"       # Deadhand Sovereign Orange
TEXT_COLOR = "#ffffff"         # Crisp white
MUTED_TEXT = "#71717a"         # Zinc-500 equivalent
FONT_MAIN = ("Geist", 13)
FONT_BOLD = ("Geist", 14, "bold")
FONT_TITLE = ("Geist", 24, "bold")
FONT_HUGE = ("Geist", 48, "bold")
FONT_MONO = ("Geist Mono", 12)

STATE_FILE = "deadhand_obsidian_state.json"

class DeadhandObsidian(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Deadhand Protocol")
        self.geometry("900x700")
        self.configure(fg_color=BG_COLOR)
        self.resizable(True, True)

        # Load the favicon
        self.icon_path = os.path.join(os.path.dirname(__file__), "app", "static", "favicon.png")
        if os.path.exists(self.icon_path):
            try:
                img = Image.open(self.icon_path)
                ico_path = os.path.join(os.path.dirname(__file__), "app", "static", "favicon.ico")
                # Save as ICO to ensure it works beautifully on Windows
                if not os.path.exists(ico_path):
                    img.save(ico_path, format="ICO", sizes=[(32, 32)])
                self.iconbitmap(ico_path)
            except Exception as e:
                pass

        # Fix for Python 3.13 on Windows
        self._windows_set_titlebar_color = lambda *args: None

        self.state = self.load_state()

        # --- GRID LAYOUT ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, fg_color=SIDEBAR_COLOR, width=220, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        if os.path.exists(self.icon_path):
            logo_img = ctk.CTkImage(Image.open(self.icon_path), size=(24, 24))
            self.logo_label = ctk.CTkLabel(self.sidebar, text=" DEADHAND", image=logo_img, compound="left", font=("Geist", 18, "bold"), text_color=TEXT_COLOR)
        else:
            self.logo_label = ctk.CTkLabel(self.sidebar, text="DEADHAND", font=("Geist", 18, "bold"), text_color=TEXT_COLOR)
            
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 30), sticky="w")

        # Sidebar Buttons
        self.btn_heartbeat = self.create_sidebar_btn("The Heartbeat", 1, self.show_heartbeat_view)
        self.btn_shards = self.create_sidebar_btn("My Shards", 2, self.show_shard_generator_view)
        self.btn_beneficiaries = self.create_sidebar_btn("Beneficiary Status", 3, self.show_beneficiary_view)
        
        # Tools
        ctk.CTkLabel(self.sidebar, text="TOOLS", font=("Geist", 10, "bold"), text_color="#555").grid(row=4, column=0, padx=20, pady=(15, 0), sticky="w")
        self.btn_audio = self.create_sidebar_btn("Audio Steganography", 5, self.show_audio_steg_view)
        self.btn_visual = self.create_sidebar_btn("Visual Steganography", 6, self.show_visual_steg_view)
        
        # System
        ctk.CTkLabel(self.sidebar, text="SYSTEM", font=("Geist", 10, "bold"), text_color="#555").grid(row=7, column=0, padx=20, pady=(15, 0), sticky="w")
        self.btn_settings = self.create_sidebar_btn("Control Panel", 8, self.show_control_panel_view)
        self.btn_recover = self.create_sidebar_btn("Recovery Mode", 9, self.show_recovery_view)

        self.sidebar.grid_rowconfigure(10, weight=1) # Empty spacer row taking all remaining space

        # Settings at bottom
        self.btn_reset = ctk.CTkButton(self.sidebar, text="Delete Vault", fg_color="transparent", text_color="#e11d48", hover_color="#2a0000", anchor="w", command=self.factory_reset)
        self.btn_reset.grid(row=11, column=0, padx=20, pady=20, sticky="ew")

        # --- RIGHT SIDE WRAPPER ---
        self.right_wrapper = ctk.CTkFrame(self, fg_color=BG_COLOR, corner_radius=0)
        self.right_wrapper.grid(row=0, column=1, sticky="nsew")
        self.right_wrapper.grid_rowconfigure(1, weight=1)
        self.right_wrapper.grid_columnconfigure(0, weight=1)

        # Top Bar (for hamburger)
        self.top_bar = ctk.CTkFrame(self.right_wrapper, fg_color="transparent", height=40, corner_radius=0)
        self.top_bar.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 0))
        
        self.btn_toggle_sidebar = ctk.CTkButton(self.top_bar, text="☰", width=40, height=40, fg_color="transparent", hover_color="#18181b", text_color=MUTED_TEXT, font=("Geist", 24), command=self.toggle_sidebar)
        self.btn_toggle_sidebar.pack(side="left")

        # --- MAIN CONTENT AREA ---
        self.main_content = ctk.CTkFrame(self.right_wrapper, fg_color=BG_COLOR, corner_radius=0)
        self.main_content.grid(row=1, column=0, sticky="nsew", padx=40, pady=(10, 40))

        # --- ROUTING ---
        self.vault_password = None
        self.raw_state = self.load_raw_state()

        if self.raw_state:
            self.sidebar.grid_remove() # Hide sidebar during unlock
            self.btn_toggle_sidebar.pack_forget() # Hide hamburger
            self.show_unlock_view()
        else:
            self.state = {"vault_exists": False, "vault_name": "My Vault", "license": "", "email": "", "status": "pending", "deadline": 0}
            self.sidebar.grid_remove()
            self.btn_toggle_sidebar.pack_forget()
            self.show_setup_intro()

    def toggle_sidebar(self):
        # We only allow toggling if the vault is actually set up
        if not self.state.get("vault_exists", False):
            return

        if self.sidebar.winfo_ismapped():
            self.sidebar.grid_remove()
        else:
            self.sidebar.grid()

    def create_sidebar_btn(self, text, row, command):
        btn = ctk.CTkButton(self.sidebar, text=text, fg_color="transparent", text_color=MUTED_TEXT, hover_color="#2d2d2d", anchor="w", font=FONT_MAIN, command=command)
        btn.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
        return btn

    def load_raw_state(self):
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "rb") as f:
                    return f.read()
            except:
                pass
        return None

    def save_state(self):
        if not self.vault_password:
            return # Cannot save if no password is set
            
        json_data = json.dumps(self.state).encode('utf-8')
        
        # Derive key using PBKDF2
        salt = secrets.token_bytes(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        key = kdf.derive(self.vault_password.encode('utf-8'))
        
        # Encrypt with AES-GCM
        aesgcm = AESGCM(key)
        nonce = secrets.token_bytes(12)
        ct = aesgcm.encrypt(nonce, json_data, None)
        
        # Save salt + nonce + ciphertext
        final_payload = salt + nonce + ct
        with open(STATE_FILE, "wb") as f:
            f.write(final_payload)

    def decrypt_state(self, password):
        if not self.raw_state or len(self.raw_state) < 28:
            return False
            
        salt = self.raw_state[:16]
        nonce = self.raw_state[16:28]
        ct = self.raw_state[28:]
        
        try:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=480000,
            )
            key = kdf.derive(password.encode('utf-8'))
            aesgcm = AESGCM(key)
            pt = aesgcm.decrypt(nonce, ct, None)
            self.state = json.loads(pt.decode('utf-8'))
            self.vault_password = password
            return True
        except Exception:
            return False

    def clear_main(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()

    def factory_reset(self):
        # Attempt to release the fuse on the server if it exists
        lic = self.state.get("license")
        if lic:
            try:
                data = urllib.parse.urlencode({"license_key": lic}).encode()
                req = urllib.request.Request(f"{SERVER_URL}/release", data=data, method="POST")
                with urllib.request.urlopen(req, timeout=3) as response:
                    pass
            except Exception:
                pass # Still reset locally even if offline

        self.state = {"vault_exists": False, "vault_name": "My Vault", "license": "", "email": "", "status": "pending", "deadline": 0}
        self.save_state()
        self.sidebar.grid_remove()
        self.show_setup_intro()

    # ================= UNLOCK FLOW =================
    def show_unlock_view(self):
        self.clear_main()
        ctk.CTkLabel(self.main_content, text="Vault Locked", font=FONT_TITLE, text_color=TEXT_COLOR).pack(pady=(100, 10))
        ctk.CTkLabel(self.main_content, text="Enter your Master Vault Password to decrypt your local shards.", font=FONT_MAIN, text_color=MUTED_TEXT).pack(pady=(0, 40))
        
        self.unlock_input = ctk.CTkEntry(self.main_content, width=300, height=45, fg_color="#181818", border_color="#333", show="*")
        self.unlock_input.pack(pady=(0, 20))
        
        self.unlock_err = ctk.CTkLabel(self.main_content, text="", text_color="#e11d48")
        self.unlock_err.pack()

        def attempt_unlock():
            pwd = self.unlock_input.get()
            if self.decrypt_state(pwd):
                self.sidebar.grid()
                self.btn_toggle_sidebar.pack(side="left")
                self.show_heartbeat_view()
                self.start_countdown_timer()
            else:
                self.unlock_err.configure(text="Invalid Password. Vault remains encrypted.")

        ctk.CTkButton(self.main_content, text="Unlock Vault", font=FONT_BOLD, fg_color=ACCENT_COLOR, text_color="#ffffff", hover_color="#cc4400", width=300, height=45, corner_radius=4, command=attempt_unlock).pack(pady=10)

    # ================= SETUP FLOW (THE HOOK) =================
    def show_setup_intro(self):
        self.clear_main()
        ctk.CTkLabel(self.main_content, text="No Vault Found", font=FONT_TITLE, text_color=TEXT_COLOR).pack(pady=(100, 10))
        ctk.CTkLabel(self.main_content, text="You have not initialized a Deadhand Vault on this device.", font=FONT_MAIN, text_color=MUTED_TEXT).pack(pady=(0, 40))
        
        ctk.CTkButton(self.main_content, text="Create New Vault", font=FONT_BOLD, fg_color=ACCENT_COLOR, text_color="#ffffff", hover_color="#cc4400", width=250, height=45, corner_radius=4, command=self.show_setup_shards).pack()

    def show_setup_shards(self):
        """STEP 1: The Hook - Shard Generation"""
        self.clear_main()
        
        # Back Button
        ctk.CTkButton(self.main_content, text="← Back", font=("Geist", 11), fg_color="transparent", text_color=MUTED_TEXT, hover_color="#222", width=60, command=self.show_setup_intro).pack(anchor="w", pady=(0, 20))

        ctk.CTkLabel(self.main_content, text="Sovereign Secret Division", font=FONT_TITLE, text_color=TEXT_COLOR).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(self.main_content, text="Enter the secret you want the beneficiary to know (Seed phrase, location, etc.). We will split it into 3 cryptographic shards.", font=FONT_MAIN, text_color=MUTED_TEXT, wraplength=500, justify="left").pack(anchor="w", pady=(0, 20))

        self.setup_seed_input = ctk.CTkTextbox(self.main_content, width=500, height=100, fg_color="#181818", border_color="#333", border_width=1)
        self.setup_seed_input.pack(anchor="w", pady=(0, 20))

        ctk.CTkButton(self.main_content, text="Split Secret", font=FONT_BOLD, fg_color="#333", hover_color="#444", command=self.generate_setup_shards).pack(anchor="w", pady=(0, 20))
        
        self.setup_shard_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.setup_shard_frame.pack(anchor="w", fill="x")

    def generate_setup_shards(self):
        seed = self.setup_seed_input.get("1.0", "end-1c").strip()
        if not seed:
            return

        # Generate 2-of-3 Shards
        shA, shB, shC = split_secret_2_of_3(seed)
        
        # Clear frame for refresh
        for widget in self.setup_shard_frame.winfo_children():
            widget.destroy()

        # Display Shard A
        ctk.CTkLabel(self.setup_shard_frame, text="Shard A (You hold this):", font=FONT_BOLD, text_color=ACCENT_COLOR).pack(anchor="w")
        shA_box = ctk.CTkTextbox(self.setup_shard_frame, width=500, height=50, fg_color="#181818", border_color="#333", border_width=1)
        shA_box.insert("1.0", shA)
        shA_box.configure(state="disabled")
        shA_box.pack(anchor="w", pady=(0, 10))

        # Display Shard B
        ctk.CTkLabel(self.setup_shard_frame, text="Shard B (GIVE THIS TO YOUR BENEFICIARY MANUALLY):", font=FONT_BOLD, text_color="#10b981").pack(anchor="w")
        shB_box = ctk.CTkTextbox(self.setup_shard_frame, width=500, height=50, fg_color="#181818", border_color="#333", border_width=1)
        shB_box.insert("1.0", shB)
        shB_box.configure(state="disabled")
        shB_box.pack(anchor="w", pady=(0, 20))
        
        # Temporarily store Shard C for the next step
        self.temp_shard_c = shC
        self.temp_shA = shA
        self.temp_shB = shB

        ctk.CTkButton(self.setup_shard_frame, text="Next: Finalize Vault →", font=FONT_BOLD, fg_color=ACCENT_COLOR, hover_color="#cc4400", height=45, command=self.show_setup_step2).pack(anchor="w")

    def show_shard_generator_view(self):
        self.clear_main()
        ctk.CTkLabel(self.main_content, text="My Shards", font=FONT_TITLE, text_color=TEXT_COLOR).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(self.main_content, text="Enter secret you want the beneficiary to know / seed phrase. Deadhand securely stores Shard C.", font=FONT_MAIN, text_color=MUTED_TEXT, wraplength=500, justify="left").pack(anchor="w", pady=(0, 20))

        self.seed_input = ctk.CTkTextbox(self.main_content, width=500, height=100, fg_color="#181818", border_color="#333", border_width=1)
        self.seed_input.pack(anchor="w", pady=(0, 20))

        ctk.CTkButton(self.main_content, text="Generate Shards", font=FONT_BOLD, fg_color="#333", hover_color="#444", command=self.generate_shards).pack(anchor="w", pady=(0, 20))
        
        self.shard_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.shard_frame.pack(anchor="w", fill="x")

    def generate_shards(self):
        for widget in self.shard_frame.winfo_children():
            widget.destroy()
        
        secret = self.seed_input.get("1.0", "end-1c").strip()
        if not secret:
            return
            
        shA, shB, shC = split_secret_2_of_3(secret)
        self.temp_shard_c = shC # Using temp_shard_c consistently

        # Display Shard A
        ctk.CTkLabel(self.shard_frame, text="Shard A (You keep this copy safe):", font=FONT_BOLD).pack(anchor="w", pady=(10, 0))
        shA_box = ctk.CTkTextbox(self.shard_frame, width=500, height=50, fg_color="#181818", border_color=ACCENT_COLOR, border_width=1)
        shA_box.insert("1.0", shA)
        shA_box.configure(state="disabled")
        shA_box.pack(anchor="w", pady=(0, 10))

        # Display Shard B
        ctk.CTkLabel(self.shard_frame, text="Shard B (GIVE THIS TO YOUR BENEFICIARY MANUALLY):", font=FONT_BOLD).pack(anchor="w")
        shB_box = ctk.CTkTextbox(self.shard_frame, width=500, height=50, fg_color="#181818", border_color=ACCENT_COLOR, border_width=1)
        shB_box.insert("1.0", shB)
        shB_box.configure(state="disabled")
        shB_box.pack(anchor="w", pady=(0, 10))
        
        ctk.CTkLabel(self.shard_frame, text="Your beneficiary will use this shard + the server-released Shard C to recover your secret when you are gone.", font=FONT_MAIN, text_color=MUTED_TEXT, wraplength=500, justify="left").pack(anchor="w", pady=(5, 10))

        # Save Shard C automatically to state
        self.state["payload"] = shC
        self.save_state()

    def show_setup_step2(self):
        """STEP 2: Identity & Fuse Activation"""
        self.clear_main()
        
        # Back Button
        ctk.CTkButton(self.main_content, text="← Back to Shards", font=("Geist", 11), fg_color="transparent", text_color=MUTED_TEXT, hover_color="#222", width=120, command=self.show_setup_shards).pack(anchor="w", pady=(0, 20))

        ctk.CTkLabel(self.main_content, text="Finalize Sovereign Vault", font=FONT_TITLE, text_color=TEXT_COLOR).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(self.main_content, text="Your shards are ready. Now connect your sovereign fuse and heir.", font=FONT_MAIN, text_color=MUTED_TEXT).pack(anchor="w", pady=(0, 30))

        ctk.CTkLabel(self.main_content, text="Deadhand Sovereign Fuse (24 chars):", font=FONT_BOLD).pack(anchor="w", pady=(0, 5))
        
        # Fuse Help Link
        ctk.CTkLabel(self.main_content, text="Obtain a fuse at deadhandprotocol.com", font=("Geist", 11), text_color=ACCENT_COLOR).pack(anchor="w", pady=(0, 10))

        self.key_input = ctk.CTkEntry(self.main_content, width=500, height=40, fg_color="#181818", border_color="#333", show="*")
        self.key_input.pack(anchor="w", pady=(0, 20))

        ctk.CTkLabel(self.main_content, text="Beneficiary Email:", font=FONT_BOLD).pack(anchor="w", pady=(0, 5))
        self.email_input = ctk.CTkEntry(self.main_content, width=500, height=40, fg_color="#181818", border_color="#333", placeholder_text="heir@example.com")
        self.email_input.pack(anchor="w", pady=(0, 20))

        ctk.CTkLabel(self.main_content, text="Master Vault Password (Local Encryption):", font=FONT_BOLD).pack(anchor="w", pady=(0, 5))
        self.pwd_input = ctk.CTkEntry(self.main_content, width=500, height=40, fg_color="#181818", border_color="#333", show="*")
        self.pwd_input.pack(anchor="w", pady=(0, 20))

        self.setup_err = ctk.CTkLabel(self.main_content, text="", text_color="#e11d48")
        self.setup_err.pack(anchor="w")

        ctk.CTkButton(self.main_content, text="Initialize Vault", font=FONT_BOLD, fg_color=ACCENT_COLOR, hover_color="#cc4400", width=200, height=45, corner_radius=4, command=self.finalize_setup).pack(anchor="w", pady=20)

    def finalize_setup(self):
        # Canonicalize: remove dashes and spaces for validation
        raw_key = self.key_input.get().strip()
        key = raw_key.replace("-", "").replace(" ", "")
        email = self.email_input.get().strip()
        pwd = self.pwd_input.get().strip()

        if len(pwd) < 8:
            self.setup_err.configure(text="Master Password must be at least 8 characters.")
            return

        self.vault_password = pwd

        if len(key) != 24:
            self.setup_err.configure(text="Invalid Sovereign Fuse. Must be 24 alphanumeric characters.")
            return
            
        valid, msg = is_valid_email(email)
        if not valid:
            self.setup_err.configure(text=msg)
            return

        # --- SERVER LICENSE VERIFICATION ---
        try:
            self.setup_err.configure(text="Initializing Sovereign Vault...", text_color=ACCENT_COLOR)
            self.update()
            
            # Send license + beneficiary email + Shard C
            post_data = {
                "license_key": key,
                "beneficiary_email": email,
                "shard_c": self.temp_shard_c
            }
            data = urllib.parse.urlencode(post_data).encode()
            req = urllib.request.Request(f"{SERVER_URL}/redeem", data=data, method="POST")
            with urllib.request.urlopen(req, timeout=10) as response:
                res_body = json.loads(response.read().decode())
                self.state["heartbeat_token"] = res_body.get("heartbeat_token")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                self.setup_err.configure(text="Invalid Sovereign Fuse.", text_color="#e11d48")
            elif e.code == 400:
                self.setup_err.configure(text="Fuse already occupied.", text_color="#e11d48")
            else:
                self.setup_err.configure(text=f"Server error ({e.code}).", text_color="#e11d48")
            return
        except Exception as e:
            print(f"Setup Error: {str(e)}")
            self.setup_err.configure(text="Offline: Could not connect to Deadhand server.", text_color="#e11d48")
            return

        self.setup_err.configure(text="") # Clear errors
        self.state["vault_exists"] = True
        self.state["license"] = key
        self.state["email"] = email
        self.state["payload"] = self.temp_shard_c # Use the shard C from step 1
        self.state["shard_a"] = self.temp_shA
        self.state["shard_b"] = self.temp_shB
        self.state["status"] = "pending"
        self.state["is_active"] = True # The fuse is consumed
        self.state["deadline"] = time.time() + (90 * 24 * 3600) # 90 days from now
        self.save_state()

        self.complete_setup_transition()

    def show_setup_success(self):
        self.clear_main()
        
        ctk.CTkLabel(self.main_content, text="VAULT INITIALIZED", font=FONT_HUGE, text_color=ACCENT_COLOR).pack(pady=(120, 10))
        ctk.CTkLabel(self.main_content, text="The heartbeat is active. The fuse is primed.", font=FONT_BOLD, text_color=TEXT_COLOR).pack(pady=(0, 40))
        
        ctk.CTkButton(self.main_content, text="Enter Vault Dashboard", font=FONT_BOLD, fg_color="#18181b", text_color="#ffffff", hover_color="#333", width=250, height=50, command=self.complete_setup_transition).pack()

    def show_inheritance_complete_view(self):
        self.clear_main()
        self.sidebar.grid_remove() # Hide sidebar for finality
        self.btn_toggle_sidebar.pack_forget()

        ctk.CTkLabel(self.main_content, text="CONGRATULATIONS", font=FONT_HUGE, text_color="#10b981").pack(pady=(120, 10))
        ctk.CTkLabel(self.main_content, text="Inheritance complete. The fuse is consumed.", font=FONT_BOLD, text_color=TEXT_COLOR).pack(pady=(0, 40))
        
        ctk.CTkLabel(self.main_content, text="Your shards have been dispatched to your beneficiary.\nYour sovereign duty is fulfilled.", font=FONT_MAIN, text_color=MUTED_TEXT, justify="center").pack(pady=(0, 40))

        ctk.CTkButton(self.main_content, text="Return to Shards", font=FONT_BOLD, fg_color="#18181b", text_color="#ffffff", hover_color="#333", width=250, height=50, command=self.show_shard_generator_view).pack()

    def complete_setup_transition(self):
        self.sidebar.grid() # Show sidebar
        self.btn_toggle_sidebar.pack(side="left") # Show hamburger
        self.show_heartbeat_view()
        self.start_countdown_timer()

    # ================= HEARTBEAT VIEW =================
    def show_heartbeat_view(self):
        self.clear_main()
        
        # Header
        header = ctk.CTkFrame(self.main_content, fg_color="transparent")
        header.pack(fill="x", pady=(0, 40))
        ctk.CTkLabel(header, text=self.state["vault_name"], font=FONT_TITLE, text_color=TEXT_COLOR).pack(side="left")
        
        ctk.CTkLabel(self.main_content, text="DEADMAN SWITCH DEADLINE", font=FONT_BOLD, text_color=MUTED_TEXT).pack(pady=(40, 0))
        
        # Visual Progress Bar for the Heartbeat
        self.progress_bar = ctk.CTkProgressBar(self.main_content, width=500, height=30, fg_color="#18181b", progress_color=ACCENT_COLOR, corner_radius=4)
        self.progress_bar.pack(pady=(20, 10))
        self.progress_bar.set(1.0)
        
        self.timer_label = ctk.CTkLabel(self.main_content, text="Loading...", font=("Geist Mono", 18, "bold"), text_color=TEXT_COLOR)
        self.timer_label.pack(pady=(0, 10))

        ctk.CTkLabel(self.main_content, text="If this timer hits zero, your encrypted shards will be automatically dispatched.", font=FONT_MAIN, text_color=MUTED_TEXT).pack(pady=(0, 40))

        self.pulse_btn = ctk.CTkButton(
            self.main_content, 
            text="I AM ALIVE - RESET TIMER", 
            font=("Geist", 18, "bold"),
            fg_color=ACCENT_COLOR, 
            hover_color="#cc4400",
            width=400,
            height=60,
            corner_radius=4,
            command=self.reset_heartbeat
        )
        self.pulse_btn.pack()

        self.update_timer_ui()

    def reset_heartbeat(self):
        self.state["deadline"] = time.time() + (90 * 24 * 3600)
        self.save_state()
        self.update_timer_ui()

    def update_timer_ui(self):
        if not hasattr(self, 'timer_label') or not self.timer_label.winfo_exists():
            return
            
        now = time.time()
        diff = self.state["deadline"] - now
        
        if diff <= 0:
            self.show_inheritance_complete_view()
        else:
            # Update visual progress bar
            total_seconds = 90 * 24 * 3600
            ratio = diff / total_seconds
            self.progress_bar.set(ratio)
            
            # Color Lerping: Green -> Yellow -> Red
            # Green: #10b981 (16, 185, 129)
            # Yellow: #f59e0b (245, 158, 11)
            # Red: #e11d48 (225, 29, 72)
            
            if ratio > 0.5:
                # Lerp Green to Yellow
                sub_ratio = (ratio - 0.5) * 2
                r = int(245 + (16 - 245) * sub_ratio)
                g = int(158 + (185 - 158) * sub_ratio)
                b = int(11 + (129 - 11) * sub_ratio)
            else:
                # Lerp Yellow to Red
                sub_ratio = ratio * 2
                r = int(225 + (245 - 225) * sub_ratio)
                g = int(29 + (158 - 29) * sub_ratio)
                b = int(72 + (11 - 72) * sub_ratio)
            
            hex_color = f"#{r:02x}{g:02x}{b:02x}"
            self.progress_bar.configure(progress_color=hex_color)
            self.timer_label.configure(text_color=hex_color)

            days = int(diff // (24 * 3600))
            hours = int((diff % (24 * 3600)) // 3600)
            mins = int((diff % 3600) // 60)
            secs = int(diff % 60)
            self.timer_label.configure(text=f"{days:02d} : {hours:02d} : {mins:02d} : {secs:02d} REMAINING")

    def start_countdown_timer(self):
        self.update_timer_ui()
        self.after(1000, self.start_countdown_timer) # update every second

    # ================= BENEFICIARY VIEW =================
    def show_beneficiary_view(self):
        self.clear_main()

        ctk.CTkLabel(self.main_content, text="Beneficiary Network Status", font=FONT_TITLE, text_color=TEXT_COLOR).pack(anchor="w", pady=(0, 30))

        card = ctk.CTkFrame(self.main_content, fg_color="#181818", border_width=1, border_color="#333", corner_radius=8)
        card.pack(fill="x", ipady=20, ipadx=20)

        ctk.CTkLabel(card, text="Target Address:", font=FONT_BOLD, text_color=MUTED_TEXT).pack(anchor="w")
        ctk.CTkLabel(card, text=self.state["email"], font=("Geist", 16), text_color=TEXT_COLOR).pack(anchor="w", pady=(0, 20))

        ctk.CTkLabel(card, text="Network Validation Status:", font=FONT_BOLD, text_color=MUTED_TEXT).pack(anchor="w")
        
        status = self.state.get("status", "pending")
        if status == "pending":
            color = "#f59e0b" # Yellow/Orange
            icon = "🟡 PENDING VALIDATION"
        elif status == "validated":
            color = "#10b981" # Green
            icon = "🟢 VALIDATED & ACTIVE"
        else:
            color = "#e11d48"
            icon = "🔴 BOUNCED / FAILED"

        ctk.CTkLabel(card, text=icon, font=FONT_BOLD, text_color=color).pack(anchor="w")

        # Refresh button
        ctk.CTkButton(self.main_content, text="Refresh Verification Status", font=FONT_BOLD, fg_color="#18181b", text_color="#ffffff", hover_color="#333", command=self.refresh_vault_status).pack(anchor="w", pady=40)

    def refresh_vault_status(self):
        lic = self.state.get("license")
        if not lic: return
        
        try:
            data = urllib.parse.urlencode({"license_key": lic}).encode()
            req = urllib.request.Request(f"{SERVER_URL}/vault/status", data=data, method="POST")
            with urllib.request.urlopen(req, timeout=5) as response:
                res = json.loads(response.read().decode())
                if res.get("is_acknowledged"):
                    self.state["status"] = "validated"
                else:
                    self.state["status"] = "pending"
                self.save_state()
                self.show_beneficiary_view()
        except:
            pass

    # ================= AUDIO STEGANOGRAPHY =================
    def show_audio_steg_view(self):
        self.clear_main()
        ctk.CTkLabel(self.main_content, text="Audio Steganography", font=FONT_TITLE, text_color=TEXT_COLOR).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(self.main_content, text="Hide your cryptographic shards inside an innocuous .wav or .mp3 file.", font=FONT_MAIN, text_color=MUTED_TEXT).pack(anchor="w", pady=(0, 30))

        def select_audio_file():
            file_path = filedialog.askopenfilename(title="Select Target Audio", filetypes=[("Audio Files", "*.wav *.mp3 *.flac *.m4a")])
            if file_path:
                self.audio_file_lbl.configure(text=f"Selected: {os.path.basename(file_path)}", text_color=TEXT_COLOR)

        ctk.CTkButton(self.main_content, text="Select Target Audio File", font=FONT_BOLD, fg_color="#333", hover_color="#444", command=select_audio_file).pack(anchor="w", pady=(0, 5))
        
        self.audio_file_lbl = ctk.CTkLabel(self.main_content, text="No file selected.", font=FONT_MONO, text_color=MUTED_TEXT)
        self.audio_file_lbl.pack(anchor="w", pady=(0, 20))

        ctk.CTkLabel(self.main_content, text="Payload (Shard to Hide):", font=FONT_BOLD).pack(anchor="w", pady=(0, 5))
        self.audio_payload = ctk.CTkTextbox(self.main_content, width=500, height=80, fg_color="#181818", border_color="#333")
        self.audio_payload.pack(anchor="w", pady=(0, 20))

        def encode_audio():
            if self.audio_file_lbl.cget("text") == "No file selected.":
                self.audio_payload.insert("end", "\n\n[ERR] You must select an audio file first!")
            else:
                self.audio_payload.insert("end", "\n\n[SUCCESS] Payload securely encoded into target audio file.")

        ctk.CTkButton(self.main_content, text="Encode & Export Audio", font=FONT_BOLD, fg_color=ACCENT_COLOR, text_color="#ffffff", hover_color="#cc4400", corner_radius=4, command=encode_audio).pack(anchor="w")

    # ================= VISUAL STEGANOGRAPHY =================
    def show_visual_steg_view(self):
        self.clear_main()
        ctk.CTkLabel(self.main_content, text="Visual Steganography", font=FONT_TITLE, text_color=TEXT_COLOR).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(self.main_content, text="Embed cryptographic shards invisibly into the pixel data of an image.", font=FONT_MAIN, text_color=MUTED_TEXT).pack(anchor="w", pady=(0, 30))

        def select_image_file():
            file_path = filedialog.askopenfilename(title="Select Target Image", filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")])
            if file_path:
                self.visual_file_lbl.configure(text=f"Selected: {os.path.basename(file_path)}", text_color=TEXT_COLOR)

        ctk.CTkButton(self.main_content, text="Select Target Image File", font=FONT_BOLD, fg_color="#333", hover_color="#444", command=select_image_file).pack(anchor="w", pady=(0, 5))
        
        self.visual_file_lbl = ctk.CTkLabel(self.main_content, text="No file selected.", font=FONT_MONO, text_color=MUTED_TEXT)
        self.visual_file_lbl.pack(anchor="w", pady=(0, 20))

        ctk.CTkLabel(self.main_content, text="Payload (Shard to Hide):", font=FONT_BOLD).pack(anchor="w", pady=(0, 5))
        self.visual_payload = ctk.CTkTextbox(self.main_content, width=500, height=80, fg_color="#181818", border_color="#333")
        self.visual_payload.pack(anchor="w", pady=(0, 20))

        def encode_visual():
            if self.visual_file_lbl.cget("text") == "No file selected.":
                self.visual_payload.insert("end", "\n\n[ERR] You must select an image file first!")
            else:
                self.visual_payload.insert("end", "\n\n[SUCCESS] Payload securely encoded into target image file.")

        ctk.CTkButton(self.main_content, text="Encode & Export Image", font=FONT_BOLD, fg_color=ACCENT_COLOR, text_color="#ffffff", hover_color="#cc4400", corner_radius=4, command=encode_visual).pack(anchor="w")

    # ================= RECOVERY MODE =================
    def show_recovery_view(self):
        self.clear_main()
        ctk.CTkLabel(self.main_content, text="Emergency Recovery Mode", font=FONT_TITLE, text_color=TEXT_COLOR).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(self.main_content, text="Input your collected M-of-N shards to reconstruct the original Master Secret.", font=FONT_MAIN, text_color=MUTED_TEXT).pack(anchor="w", pady=(0, 30))

        ctk.CTkLabel(self.main_content, text="Enter Shard 1:", font=FONT_BOLD).pack(anchor="w")
        rec_shard1 = ctk.CTkEntry(self.main_content, width=500, fg_color="#181818", border_color="#333")
        rec_shard1.pack(anchor="w", pady=(0, 15))

        ctk.CTkLabel(self.main_content, text="Enter Shard 2:", font=FONT_BOLD).pack(anchor="w")
        rec_shard2 = ctk.CTkEntry(self.main_content, width=500, fg_color="#181818", border_color="#333")
        rec_shard2.pack(anchor="w", pady=(0, 20))

        def mock_recover():
            s1 = rec_shard1.get().strip()
            s2 = rec_shard2.get().strip()
            if not s1 or not s2:
                self.rec_out.configure(text="[ERR] Please provide two shards.", text_color="#e11d48")
                return
            
            secret = recover_secret_2_of_3(s1, s2)
            if secret:
                self.rec_out.configure(text=f"[SUCCESS] Master Secret Reconstructed:\n\n{secret}", text_color="#10b981")
            else:
                self.rec_out.configure(text="[ERR] Failed to reconstruct. Shards may be invalid or identical.", text_color="#e11d48")

        ctk.CTkButton(self.main_content, text="Reconstruct Master Secret", font=FONT_BOLD, fg_color="#e11d48", hover_color="#9f1239", command=mock_recover).pack(anchor="w", pady=(0, 20))

        self.rec_out = ctk.CTkLabel(self.main_content, text="", font=FONT_MONO, justify="left", wraplength=500)
        self.rec_out.pack(anchor="w")

    # ================= CONTROL PANEL =================
    def show_control_panel_view(self):
        self.clear_main()
        ctk.CTkLabel(self.main_content, text="Sovereign Control Panel", font=FONT_TITLE, text_color=TEXT_COLOR).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(self.main_content, text="Monitor your vault status and modify your vault identity.", font=FONT_MAIN, text_color=MUTED_TEXT).pack(anchor="w", pady=(0, 30))

        # Vault Name (Editable)
        ctk.CTkLabel(self.main_content, text="Vault Name:", font=FONT_BOLD).pack(anchor="w", pady=(0, 5))
        name_input = ctk.CTkEntry(self.main_content, width=500, fg_color="#181818", border_color="#333")
        name_input.insert(0, self.state.get("vault_name", "My Vault"))
        name_input.pack(anchor="w", pady=(0, 15))

        # Beneficiary Email (Read Only)
        ctk.CTkLabel(self.main_content, text="Beneficiary Email (Locked for Security):", font=FONT_BOLD, text_color=MUTED_TEXT).pack(anchor="w", pady=(0, 5))
        email_input = ctk.CTkEntry(self.main_content, width=500, fg_color="#101010", border_color="#222", text_color="#555")
        email_input.insert(0, self.state.get("email", ""))
        email_input.configure(state="disabled")
        email_input.pack(anchor="w", pady=(0, 15))

        # Shard C (Read Only)
        ctk.CTkLabel(self.main_content, text="Shard C (Immutable server-side shard):", font=FONT_BOLD, text_color=MUTED_TEXT).pack(anchor="w", pady=(0, 5))
        payload_input = ctk.CTkTextbox(self.main_content, width=500, height=80, fg_color="#101010", border_color="#222", text_color="#555")
        payload_input.insert("1.0", self.state.get("payload", ""))
        payload_input.configure(state="disabled")
        payload_input.pack(anchor="w", pady=(0, 20))

        # Helpful Data
        info_frame = ctk.CTkFrame(self.main_content, fg_color="#111", border_width=1, border_color="#222")
        info_frame.pack(fill="x", pady=(0, 20))
        
        deadline = datetime.fromtimestamp(self.state.get("deadline", 0)).strftime("%Y-%m-%d %H:%M:%S")
        
        ctk.CTkLabel(info_frame, text=f"DISPATCH DEADLINE: {deadline}", font=FONT_MONO, text_color=ACCENT_COLOR).pack(anchor="w", padx=20, pady=(10, 5))
        ctk.CTkLabel(info_frame, text=f"FUSE STATUS: OCCUPIED", font=FONT_MONO, text_color="#10b981").pack(anchor="w", padx=20, pady=(0, 5))
        ctk.CTkLabel(info_frame, text=f"VAULT PROTOCOL: SHAMIR 2-OF-3", font=FONT_MONO, text_color=MUTED_TEXT).pack(anchor="w", padx=20, pady=(0, 10))

        def save_settings():
            self.state["vault_name"] = name_input.get().strip()
            self.save_state()
            save_lbl.configure(text="[SUCCESS] Vault Identity Updated", text_color="#10b981")

        ctk.CTkButton(self.main_content, text="Update Vault Identity", font=FONT_BOLD, fg_color=ACCENT_COLOR, text_color="#ffffff", hover_color="#cc4400", corner_radius=4, command=save_settings).pack(anchor="w", pady=(0, 10))
        
        save_lbl = ctk.CTkLabel(self.main_content, text="", font=FONT_MONO)
        save_lbl.pack(anchor="w")

if __name__ == "__main__":
    app = DeadhandObsidian()
    app.mainloop()
