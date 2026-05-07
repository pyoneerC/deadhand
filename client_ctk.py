import customtkinter as ctk
from customtkinter import filedialog
import json
import os
import time
import hashlib
from datetime import datetime, timedelta
from PIL import Image, ImageTk

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
        self.geometry("900x600")
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
        self.btn_beneficiaries = self.create_sidebar_btn("Beneficiary Status", 2, self.show_beneficiary_view)
        
        # Tools
        ctk.CTkLabel(self.sidebar, text="TOOLS", font=("Geist", 10, "bold"), text_color="#555").grid(row=3, column=0, padx=20, pady=(15, 0), sticky="w")
        self.btn_audio = self.create_sidebar_btn("Audio Steganography", 4, self.show_audio_steg_view)
        self.btn_visual = self.create_sidebar_btn("Visual Steganography", 5, self.show_visual_steg_view)
        
        # System
        ctk.CTkLabel(self.sidebar, text="SYSTEM", font=("Geist", 10, "bold"), text_color="#555").grid(row=7, column=0, padx=20, pady=(15, 0), sticky="w")
        self.btn_settings = self.create_sidebar_btn("Vault Settings", 8, self.show_settings_view)
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
        if not self.state.get("vault_exists", False):
            self.sidebar.grid_remove() # Hide sidebar during setup
            self.btn_toggle_sidebar.pack_forget() # Hide hamburger
            self.show_setup_intro()
        else:
            self.show_heartbeat_view()
            self.start_countdown_timer()

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

    def load_state(self):
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r") as f:
                    return json.load(f)
            except:
                pass
        return {"vault_exists": False, "vault_name": "My Vault", "license": "", "email": "", "status": "pending", "deadline": 0}

    def save_state(self):
        with open(STATE_FILE, "w") as f:
            json.dump(self.state, f)

    def clear_main(self):
        for widget in self.main_content.winfo_children():
            widget.destroy()

    def factory_reset(self):
        self.state = {"vault_exists": False, "vault_name": "My Vault", "license": "", "email": "", "status": "pending", "deadline": 0}
        self.save_state()
        self.sidebar.grid_remove()
        self.show_setup_intro()

    # ================= SETUP FLOW =================
    def show_setup_intro(self):
        self.clear_main()
        ctk.CTkLabel(self.main_content, text="No Vault Found", font=FONT_TITLE, text_color=TEXT_COLOR).pack(pady=(100, 10))
        ctk.CTkLabel(self.main_content, text="You have not initialized a Deadhand Vault on this device.", font=FONT_MAIN, text_color=MUTED_TEXT).pack(pady=(0, 40))
        
        ctk.CTkButton(self.main_content, text="Create New Vault", font=FONT_BOLD, fg_color=ACCENT_COLOR, text_color="#ffffff", hover_color="#cc4400", width=250, height=45, corner_radius=4, command=self.show_setup_step1).pack()

    def show_setup_step1(self):
        self.clear_main()
        ctk.CTkLabel(self.main_content, text="1. Secure Cryptographic Split", font=FONT_TITLE, text_color=TEXT_COLOR).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(self.main_content, text="Enter the seed phrase or secret you wish to protect.", font=FONT_MAIN, text_color=MUTED_TEXT).pack(anchor="w", pady=(0, 20))

        self.seed_input = ctk.CTkTextbox(self.main_content, width=500, height=100, fg_color="#181818", border_color="#333", border_width=1)
        self.seed_input.pack(anchor="w", pady=(0, 20))

        ctk.CTkButton(self.main_content, text="Generate Shards (Simulate PDFs)", font=FONT_BOLD, fg_color="#333", hover_color="#444", command=self.simulate_shards).pack(anchor="w", pady=(0, 20))
        
        self.shard_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.shard_frame.pack(anchor="w", fill="x")

        self.next_btn1 = ctk.CTkButton(self.main_content, text="Continue", fg_color=ACCENT_COLOR, hover_color="#cc4400", state="disabled", corner_radius=4, command=self.show_setup_step2)
        self.next_btn1.pack(anchor="w", pady=30)

    def simulate_shards(self):
        for widget in self.shard_frame.winfo_children():
            widget.destroy()
        
        base = hashlib.sha256(self.seed_input.get("1.0", "end").encode()).hexdigest()[:16]
        ctk.CTkLabel(self.shard_frame, text=f"📄 Shard 1 Generated: 1-{base}", font=FONT_MONO, text_color=ACCENT_COLOR).pack(anchor="w")
        ctk.CTkLabel(self.shard_frame, text=f"📄 Shard 2 Generated: 2-{base}", font=FONT_MONO, text_color=ACCENT_COLOR).pack(anchor="w")
        ctk.CTkLabel(self.shard_frame, text=f"📄 Shard 3 Generated: 3-{base}", font=FONT_MONO, text_color=ACCENT_COLOR).pack(anchor="w")
        self.next_btn1.configure(state="normal")

    def show_setup_step2(self):
        self.clear_main()
        ctk.CTkLabel(self.main_content, text="2. License & Beneficiary", font=FONT_TITLE, text_color=TEXT_COLOR).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(self.main_content, text="Validate your sovereign license and assign your heir.", font=FONT_MAIN, text_color=MUTED_TEXT).pack(anchor="w", pady=(0, 30))

        ctk.CTkLabel(self.main_content, text="Deadhand License Key (24 chars):", font=FONT_BOLD).pack(anchor="w", pady=(0, 5))
        self.key_input = ctk.CTkEntry(self.main_content, width=500, height=40, fg_color="#181818", border_color="#333", show="*")
        self.key_input.pack(anchor="w", pady=(0, 20))

        ctk.CTkLabel(self.main_content, text="Beneficiary Email:", font=FONT_BOLD).pack(anchor="w", pady=(0, 5))
        self.email_input = ctk.CTkEntry(self.main_content, width=500, height=40, fg_color="#181818", border_color="#333", placeholder_text="heir@example.com")
        self.email_input.pack(anchor="w", pady=(0, 20))

        self.setup_err = ctk.CTkLabel(self.main_content, text="", text_color="#e11d48")
        self.setup_err.pack(anchor="w")

        ctk.CTkButton(self.main_content, text="Initialize Vault", font=FONT_BOLD, fg_color=ACCENT_COLOR, hover_color="#cc4400", width=200, height=45, corner_radius=4, command=self.finalize_setup).pack(anchor="w", pady=20)

    def finalize_setup(self):
        key = self.key_input.get().strip()
        email = self.email_input.get().strip()

        if len(key) != 24:
            self.setup_err.configure(text="Invalid License Key. Must be exactly 24 characters.")
            return
        if "@" not in email:
            self.setup_err.configure(text="Invalid Email Address.")
            return

        self.state["vault_exists"] = True
        self.state["license"] = key
        self.state["email"] = email
        self.state["status"] = "pending"
        self.state["deadline"] = time.time() + (90 * 24 * 3600) # 90 days from now
        self.save_state()

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
            self.timer_label.configure(text="DISPATCH TRIGGERED", text_color="#e11d48")
            self.progress_bar.configure(progress_color="#e11d48")
            self.progress_bar.set(0)
            self.pulse_btn.configure(state="disabled")
        else:
            # Update visual progress bar
            total_seconds = 90 * 24 * 3600
            ratio = diff / total_seconds
            self.progress_bar.set(ratio)
            
            # Change color to red if below 10%
            if ratio < 0.1:
                self.progress_bar.configure(progress_color="#e11d48")
            else:
                self.progress_bar.configure(progress_color=ACCENT_COLOR)

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

        # Mock button to simulate beneficiary clicking the email
        ctk.CTkButton(self.main_content, text="[DEV] Simulate Beneficiary Clicking Verification Link", fg_color="transparent", border_width=1, border_color="#333", text_color=MUTED_TEXT, hover_color="#222", command=self.mock_validate_email).pack(anchor="w", pady=40)

    def mock_validate_email(self):
        self.state["status"] = "validated"
        self.save_state()
        self.show_beneficiary_view()

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
        ctk.CTkEntry(self.main_content, width=500, fg_color="#181818", border_color="#333").pack(anchor="w", pady=(0, 15))

        ctk.CTkLabel(self.main_content, text="Enter Shard 2:", font=FONT_BOLD).pack(anchor="w")
        ctk.CTkEntry(self.main_content, width=500, fg_color="#181818", border_color="#333").pack(anchor="w", pady=(0, 20))

        def mock_recover():
            self.rec_out.configure(text="[SUCCESS] Master Secret Reconstructed:\napple banana cherry dog elephant fox grape horse igloo ...", text_color="#10b981")

        ctk.CTkButton(self.main_content, text="Reconstruct Master Secret", font=FONT_BOLD, fg_color="#e11d48", hover_color="#9f1239", command=mock_recover).pack(anchor="w", pady=(0, 20))

        self.rec_out = ctk.CTkLabel(self.main_content, text="", font=FONT_MONO, justify="left")
        self.rec_out.pack(anchor="w")

    # ================= VAULT SETTINGS =================
    def show_settings_view(self):
        self.clear_main()
        ctk.CTkLabel(self.main_content, text="Vault Settings", font=FONT_TITLE, text_color=TEXT_COLOR).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(self.main_content, text="Modify your sovereign vault parameters and beneficiary details.", font=FONT_MAIN, text_color=MUTED_TEXT).pack(anchor="w", pady=(0, 30))

        # Vault Name
        ctk.CTkLabel(self.main_content, text="Vault Name:", font=FONT_BOLD).pack(anchor="w", pady=(0, 5))
        name_input = ctk.CTkEntry(self.main_content, width=500, fg_color="#181818", border_color="#333")
        name_input.insert(0, self.state.get("vault_name", "My Vault"))
        name_input.pack(anchor="w", pady=(0, 15))

        # Beneficiary Email
        ctk.CTkLabel(self.main_content, text="Beneficiary Email:", font=FONT_BOLD).pack(anchor="w", pady=(0, 5))
        email_input = ctk.CTkEntry(self.main_content, width=500, fg_color="#181818", border_color="#333")
        email_input.insert(0, self.state.get("email", ""))
        email_input.pack(anchor="w", pady=(0, 15))

        # Encrypted Payload
        ctk.CTkLabel(self.main_content, text="Encrypted Message (Shard C):", font=FONT_BOLD).pack(anchor="w", pady=(0, 5))
        payload_input = ctk.CTkTextbox(self.main_content, width=500, height=100, fg_color="#181818", border_color="#333")
        payload_input.insert("1.0", self.state.get("payload", ""))
        payload_input.pack(anchor="w", pady=(0, 20))

        def save_settings():
            self.state["vault_name"] = name_input.get().strip()
            
            new_email = email_input.get().strip()
            # If email changed, reset status to pending
            if new_email != self.state.get("email"):
                self.state["status"] = "pending"
                
            self.state["email"] = new_email
            self.state["payload"] = payload_input.get("1.0", "end-1c").strip()
            self.save_state()
            
            save_lbl.configure(text="[SUCCESS] Vault Settings Saved", text_color="#10b981")

        ctk.CTkButton(self.main_content, text="Save Changes", font=FONT_BOLD, fg_color=ACCENT_COLOR, text_color="#ffffff", hover_color="#cc4400", corner_radius=4, command=save_settings).pack(anchor="w", pady=(0, 10))
        
        save_lbl = ctk.CTkLabel(self.main_content, text="", font=FONT_MONO)
        save_lbl.pack(anchor="w")

if __name__ == "__main__":
    app = DeadhandObsidian()
    app.mainloop()
