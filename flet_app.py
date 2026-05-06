import flet as ft
import secrets
import os
import base64
import hashlib
import wave
import math
import random
from PIL import Image
import io
import datetime

# --- Internal Backend Imports ---
try:
    from app.database import SessionLocal, engine, Base
    from app.models import User
    from app.services import send_email
    from app.crypto import encrypt_shard, encrypt_token
except ImportError:
    # Fallback placeholders if running outside the full repo structure
    User = None
    SessionLocal = None
    send_email = lambda *args: True
    encrypt_shard = lambda s, t: s
    print("Warning: Backend modules not found. Running in standalone mode.")

# --- Shamir's Secret Sharing Constants ---
PRIME = 2**4423 - 1 

# --- SSS Logic ---
def _eval_at(poly, x, prime):
    accum = 0
    for coeff in reversed(poly):
        accum = (accum * x + coeff) % prime
    return accum

def split_secret(secret_int, n, k, prime):
    if k > n:
        raise ValueError("k must be <= n")
    poly = [secret_int] + [secrets.randbelow(prime) for _ in range(k - 1)]
    points = [(i, _eval_at(poly, i, prime)) for i in range(1, n + 1)]
    return points

def _inverse(n, prime):
    return pow(n, prime - 2, prime)

def recover_secret(shares, prime):
    if len(shares) < 2:
        raise ValueError("Need at least 2 shares")
    secret = 0
    for i, (x_i, y_i) in enumerate(shares):
        numerator = 1
        denominator = 1
        for j, (x_j, y_j) in enumerate(shares):
            if i == j:
                continue
            numerator = (numerator * (0 - x_j)) % prime
            denominator = (denominator * (x_i - x_j)) % prime
        lagrange = (y_i * numerator * _inverse(denominator, prime)) % prime
        secret = (secret + lagrange) % prime
    return secret

# --- Audio Steganography Logic ---
def hide_text_in_audio(audio_path, text, output_path):
    bits = bin(int.from_bytes(text.encode('utf-8'), 'big'))[2:].zfill(len(text) * 8)
    bits += '00000000'
    with wave.open(audio_path, 'rb') as audio:
        params = audio.getparams()
        frames = bytearray(audio.readframes(audio.getnframes()))
    if len(bits) > len(frames):
        raise ValueError("Audio file too small")
    for i, bit in enumerate(bits):
        frames[i] = (frames[i] & ~1) | int(bit)
    with wave.open(output_path, 'wb') as output:
        output.setparams(params)
        output.writeframes(frames)

def extract_text_from_audio(audio_path):
    with wave.open(audio_path, 'rb') as audio:
        frames = bytearray(audio.readframes(audio.getnframes()))
    bits = ""
    for frame in frames:
        bits += str(frame & 1)
    bytes_list = []
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        if byte == '00000000':
            break
        bytes_list.append(int(byte, 2))
    return bytes(bytes_list).decode('utf-8')

# --- Visual Cryptography Logic ---
def split_image_vc(image_path, output_dir):
    img = Image.open(image_path).convert('1')
    width, height = img.size
    share1 = Image.new('1', (width * 2, height * 2))
    share2 = Image.new('1', (width * 2, height * 2))
    p1 = [(1,0), (0,1)]
    p2 = [(0,1), (1,0)]
    for x in range(width):
        for y in range(height):
            pixel = img.getpixel((x, y))
            coin = random.random() > 0.5
            if pixel == 0:
                pattern1 = p1 if coin else p2
                pattern2 = p2 if coin else p1
            else:
                pattern1 = p1 if coin else p2
                pattern2 = p1 if coin else p2
            for i in range(2):
                for j in range(2):
                    share1.putpixel((x*2 + i, y*2 + j), pattern1[i][j])
                    share2.putpixel((x*2 + i, y*2 + j), pattern2[i][j])
    path1 = os.path.join(output_dir, "share1.png")
    path2 = os.path.join(output_dir, "share2.png")
    share1.save(path1)
    share2.save(path2)
    return path1, path2

# --- Spectrogram Image Hiding Logic ---
def generate_spectro_audio(image_path, output_path, duration=5.0):
    img = Image.open(image_path).convert('L')
    width, height = img.size
    pixels = img.load()
    sample_rate = 44100
    num_samples = int(duration * sample_rate)
    samples_per_pixel_col = num_samples / width
    min_freq, max_freq = 200, 15000
    freq_step = (max_freq - min_freq) / height
    audio_data = []
    for i in range(num_samples):
        t = i / sample_rate
        col = int(i / samples_per_pixel_col)
        if col >= width: col = width - 1
        sample_sum = 0
        for row in range(height):
            intensity = pixels[col, row]
            if intensity > 10:
                freq = max_freq - (row * freq_step)
                amplitude = intensity / 255.0
                sample_sum += amplitude * math.sin(2 * math.pi * freq * t)
        scaled_sample = int(sample_sum * 1000) 
        if scaled_sample > 32767: scaled_sample = 32767
        elif scaled_sample < -32768: scaled_sample = -32768
        audio_data.append(scaled_sample)
    with wave.open(output_path, 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        binary_data = b''.join(sample.to_bytes(2, 'little', signed=True) for sample in audio_data)
        wav.writeframes(binary_data)

# --- Flet UI ---

class DeadhandApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "DEADHAND PROTOCOL - Desktop Client"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.window_width = 950
        self.page.window_height = 850
        self.page.bgcolor = "#09090b" # Zinc-950
        self.page.scroll = ft.ScrollMode.AUTO
        self.accent_color = "#10b981" # Emerald-500
        
        self.heartbeat_active = False
        self.heartbeat_value = 60
        self.db = SessionLocal() if SessionLocal else None
        
        self.setup_ui()

    def setup_ui(self):
        # Header
        header = ft.Container(
            content=ft.Column([
                ft.Text("DEADHAND PROTOCOL", size=32, weight="bold", color=self.accent_color),
                ft.Text("Autonomous Inheritance & Acoustic Masking", size=14, color=ft.Colors.GREY_500),
            ], spacing=2),
            padding=ft.Padding.only(bottom=20)
        )

        # Tab Content (Body)
        self.tab_view = ft.TabBarView(
            expand=True,
            controls=[
                self.tab_vault_manager(),
                self.tab_seed_splitter(),
                self.tab_bus_factor(),
                self.tab_visual_split(),
                self.tab_audio_mask(),
                self.tab_recovery(),
            ]
        )

        # Tabs (Header + Content Controller)
        self.tabs_control = ft.Tabs(
            length=6,
            selected_index=0,
            animation_duration=300,
            on_change=lambda e: self.on_tab_change(e),
            content=ft.Column([
                ft.TabBar(
                    tabs=[
                        ft.Tab(label="Client Vault", icon=ft.Icons.LOCK),
                        ft.Tab(label="Seed Splitter", icon=ft.Icons.SECURITY),
                        ft.Tab(label="Bus Factor", icon=ft.Icons.CALCULATE),
                        ft.Tab(label="Visual Split", icon=ft.Icons.IMAGE),
                        ft.Tab(label="Audio Mask", icon=ft.Icons.AUDIO_FILE),
                        ft.Tab(label="Recovery", icon=ft.Icons.RESTORE),
                    ]
                ),
                self.tab_view
            ], expand=True)
        )

        # Heartbeat Status Bar (Bottom)
        self.heartbeat_icon = ft.Icon(ft.Icons.FAVORITE, color=ft.Colors.GREY_800, size=20)
        self.heartbeat_text = ft.Text("HEARTBEAT: IDLE", size=12, weight="bold", color=ft.Colors.GREY_600)
        
        self.status_bar = ft.Container(
            content=ft.Row([
                ft.Row([self.heartbeat_icon, self.heartbeat_text], spacing=10),
                ft.Text("V1.0.0-CLIENT", size=10, color=ft.Colors.GREY_800)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=15,
            border=ft.border.only(top=ft.BorderSide(1, ft.Colors.GREY_900)),
            bgcolor="#0c0c0e"
        )

        self.page.add(
            ft.Container(
                content=ft.Column([
                    header,
                    self.tabs_control,
                    self.status_bar
                ], expand=True),
                padding=30,
                expand=True
            )
        )

    async def pulse_heartbeat(self):
        while self.heartbeat_active:
            self.heartbeat_icon.scale = 1.3
            self.heartbeat_icon.color = self.accent_color
            self.page.update()
            import asyncio
            await asyncio.sleep(0.3)
            self.heartbeat_icon.scale = 1.0
            self.heartbeat_icon.color = ft.Colors.RED_400 if self.heartbeat_value < 10 else self.accent_color
            self.page.update()
            await asyncio.sleep(0.7)

    async def start_heartbeat_timer(self):
        self.heartbeat_active = True
        self.heartbeat_value = 60
        self.heartbeat_text.color = self.accent_color
        import asyncio
        asyncio.create_task(self.pulse_heartbeat())
        
        while self.heartbeat_value > 0 and self.heartbeat_active:
            self.heartbeat_text.value = f"SECURITY TIMER: {self.heartbeat_value}s"
            if self.heartbeat_value <= 10:
                self.heartbeat_text.color = ft.Colors.RED_400
            self.page.update()
            await asyncio.sleep(1)
            self.heartbeat_value -= 1
        
        if self.heartbeat_value <= 0 and self.heartbeat_active:
            self.shards_output.visible = False
            self.heartbeat_text.value = "HEARTBEAT: EXPIRED - SHARDS CLEARED"
            self.heartbeat_text.color = ft.Colors.RED_700
            self.heartbeat_active = False
            self.page.update()

    def on_tab_change(self, e):
        self.tab_view.selected_index = e.control.selected_index
        self.page.update()

    def tab_vault_manager(self):
        # Local Login / Identity
        email_input = ft.TextField(label="Your Email", border_color=ft.Colors.GREY_800)
        beneficiary_input = ft.TextField(label="Beneficiary Email", border_color=ft.Colors.GREY_800)
        seed_input = ft.TextField(label="Seed Phrase (12/24 words)", multiline=True, border_color=ft.Colors.GREY_800)
        
        status_text = ft.Text("Vault Status: UNKNOWN", color=ft.Colors.GREY_500)
        vault_details = ft.Column(visible=False)
        
        def refresh_vault_status(e=None):
            if not self.db: return
            user = self.db.query(User).filter(User.email == email_input.value).first()
            if user:
                status_text.value = f"Vault Status: ACTIVE (Last Pulse: {user.last_heartbeat.strftime('%Y-%m-%d %H:%M')})"
                status_text.color = self.accent_color
                vault_details.controls = [
                    ft.Text(f"Beneficiary: {user.beneficiary_email}", size=14),
                    ft.Button("SEND HEARTBEAT PULSE", on_click=lambda e: handle_pulse(user.email), bgcolor=self.accent_color, color=ft.Colors.BLACK)
                ]
                vault_details.visible = True
            else:
                status_text.value = "Vault Status: NOT FOUND"
                status_text.color = ft.Colors.RED_400
                vault_details.visible = False
            self.page.update()

        def handle_pulse(email):
            user = self.db.query(User).filter(User.email == email).first()
            if user:
                user.last_heartbeat = datetime.datetime.now()
                self.db.commit()
                self.page.snack_bar = ft.SnackBar(ft.Text("Pulse recorded. Inheritance delayed."))
                self.page.snack_bar.open = True
                refresh_vault_status()

        def create_vault(e):
            if not email_input.value or not beneficiary_input.value or not seed_input.value:
                return
            
            try:
                # 1. Split Seed
                secret_bytes = seed_input.value.strip().encode('utf-8')
                secret_int = int.from_bytes(secret_bytes, byteorder='big')
                shards = split_secret(secret_int, 3, 2, PRIME)
                
                shard_a = f"{shards[0][0]}-{hex(shards[0][1])}"
                shard_b = f"{shards[1][0]}-{hex(shards[1][1])}"
                shard_c = f"{shards[2][0]}-{hex(shards[2][1])}"
                
                # 2. Email Shard B to Beneficiary
                email_content = f"""
                <div style="background: #09090b; color: #fff; padding: 40px; font-family: sans-serif;">
                    <h1 style="color: #10b981;">Inheritance Instruction</h1>
                    <p>You have been named a beneficiary in a Deadhand Protocol vault.</p>
                    <p>Keep this shard secure. You will need one more shard (released if heartbeats stop) to recover the seed.</p>
                    <div style="background: #18181b; padding: 20px; border-radius: 8px; font-family: monospace; border: 1px solid #27272a;">
                        <b>Shard B:</b> {shard_b}
                    </div>
                    <p style="color: #a1a1aa; font-size: 12px; margin-top: 20px;">Securely generated via Deadhand Client.</p>
                </div>
                """
                send_email(beneficiary_input.value, "Deadhand Protocol - Your Inheritance Shard", email_content)
                
                # 3. Encrypt and Store Shard C
                heartbeat_token = secrets.token_urlsafe(32)
                encrypted_shard_c = encrypt_shard(shard_c, heartbeat_token) if SessionLocal else shard_c
                
                new_user = User(
                    email=email_input.value,
                    beneficiary_email=beneficiary_input.value,
                    shard_c=encrypted_shard_c,
                    heartbeat_token=heartbeat_token,
                    is_active=True
                )
                
                self.db.add(new_user)
                self.db.commit()
                
                self.page.dialog = ft.AlertDialog(
                    title=ft.Text("Vault Activated"),
                    content=ft.Column([
                        ft.Text("Shard B has been emailed to your beneficiary."),
                        ft.Text("Shard C is encrypted and stored in your sovereign database."),
                        ft.Text("YOUR SHARD (A) - COPY AND SAVE THIS:", weight="bold"),
                        ft.Text(shard_a, selectable=True, font_family="monospace", color=self.accent_color, size=12)
                    ], tight=True),
                    actions=[ft.TextButton("I have saved Shard A", on_click=lambda _: setattr(self.page.dialog, "open", False))]
                )
                self.page.dialog.open = True
                refresh_vault_status()
            except Exception as ex:
                self.page.snack_bar = ft.SnackBar(ft.Text(f"Error: {str(ex)}"))
                self.page.snack_bar.open = True
                self.page.update()

        return ft.Container(
            content=ft.Column([
                ft.Text("Manage your sovereign inheritance vault.", size=18, weight="bold"),
                ft.Divider(color=ft.Colors.GREY_900),
                email_input,
                ft.Row([
                    ft.Button("Check My Vault", on_click=refresh_vault_status, bgcolor=self.accent_color, color=ft.Colors.BLACK),
                ]),
                status_text,
                vault_details,
                ft.Divider(height=40, color=ft.Colors.GREY_900),
                ft.Text("Setup New Vault", size=16, weight="bold"),
                beneficiary_input,
                seed_input,
                ft.Button("ACTIVATE DEADHAND VAULT", on_click=create_vault, bgcolor=ft.Colors.BLUE_900, color=ft.Colors.WHITE),
            ], scroll=ft.ScrollMode.ADAPTIVE),
            padding=20
        )

    def tab_seed_splitter(self):
        seed_input = ft.TextField(
            label="Enter 12/24 Word Seed Phrase",
            multiline=True,
            min_lines=3,
            max_lines=5,
            border_color=ft.Colors.GREY_800,
            focused_border_color=self.accent_color,
            text_style=ft.TextStyle(font_family="monospace")
        )
        
        self.shards_output = ft.Column(visible=False, spacing=10)
        
        def handle_split(e):
            secret = seed_input.value.strip()
            if not secret: return
            try:
                secret_bytes = secret.encode('utf-8')
                secret_int = int.from_bytes(secret_bytes, byteorder='big')
                if secret_int >= PRIME:
                    self.page.snack_bar = ft.SnackBar(ft.Text("Secret too long!"))
                    self.page.snack_bar.open = True
                    self.page.update()
                    return
                
                points = split_secret(secret_int, 3, 2, PRIME)
                self.shards_output.controls.clear()
                self.shards_output.controls.append(ft.Text("GENERATED SHARDS (Keep Separately):", weight="bold", color=self.accent_color))
                
                for i, (x, y) in enumerate(points):
                    share_str = f"{x}-{hex(y)}"
                    self.shards_output.controls.append(
                        ft.Container(
                            content=ft.Row([
                                ft.Text(f"Shard {chr(65+i)}: ", weight="bold"),
                                ft.Text(share_str, selectable=True, font_family="monospace", size=12, expand=True),
                                ft.IconButton(ft.Icons.COPY, on_click=lambda e, s=share_str: self.page.set_clipboard_text(s))
                            ]),
                            padding=10,
                            bgcolor=ft.Colors.GREY_900,
                            border_radius=5
                        )
                    )
                
                def confirm_security(e):
                    self.heartbeat_active = False
                    self.heartbeat_text.value = "SECURITY CONFIRMED - SHARDS PROTECTED"
                    self.heartbeat_text.color = ft.Colors.BLUE_400
                    confirm_btn.visible = False
                    self.page.update()

                confirm_btn = ft.ElevatedButton(
                    "I HAVE SECURED MY SHARDS (STOP TIMER)", 
                    on_click=confirm_security,
                    bgcolor=ft.Colors.BLUE_900,
                    color=ft.Colors.WHITE
                )
                
                self.shards_output.controls.append(confirm_btn)
                self.shards_output.visible = True
                
                import asyncio
                asyncio.create_task(self.start_heartbeat_timer())
                self.page.update()
            except Exception as ex:
                print(ex)

        return ft.Container(
            content=ft.Column([
                ft.Text("Split your seed phrase into 3 shards. Any 2 can recover it.", size=16),
                seed_input,
                ft.Button("Split Seed Phrase", on_click=handle_split, bgcolor=self.accent_color, color=ft.Colors.BLACK),
                ft.Divider(height=40, color=ft.Colors.GREY_800),
                self.shards_output
            ], scroll=ft.ScrollMode.ADAPTIVE),
            padding=20
        )

    def tab_recovery(self):
        shard1_input = ft.TextField(label="Shard 1 (e.g. 1-0xabc...)", border_color=ft.Colors.GREY_800)
        shard2_input = ft.TextField(label="Shard 2 (e.g. 2-0xdef...)", border_color=ft.Colors.GREY_800)
        
        recovered_text = ft.Text(size=18, weight="bold", color=self.accent_color, selectable=True)
        
        def handle_recover(e):
            try:
                s1 = shard1_input.value.strip()
                s2 = shard2_input.value.strip()
                x1, y1 = s1.split('-')
                x2, y2 = s2.split('-')
                shares = [(int(x1), int(y1, 16)), (int(x2), int(y2, 16))]
                
                secret_int = recover_secret(shares, PRIME)
                secret_bytes = secret_int.to_bytes((secret_int.bit_length() + 7) // 8, byteorder='big')
                recovered_text.value = f"RECOVERED: {secret_bytes.decode('utf-8')}"
                self.page.update()
            except Exception as ex:
                recovered_text.value = "Error: Invalid shards or format."
                self.page.update()

        return ft.Container(
            content=ft.Column([
                ft.Text("Enter any two shards to reconstruct the original secret.", size=16),
                shard1_input,
                shard2_input,
                ft.Button("Recover Secret", on_click=handle_recover, bgcolor=self.accent_color, color=ft.Colors.BLACK),
                ft.Divider(height=40, color=ft.Colors.GREY_800),
                recovered_text
            ]),
            padding=20
        )

    def tab_bus_factor(self):
        assets_input = ft.TextField(label="Total Crypto Assets ($)", value="0", border_color=ft.Colors.GREY_800, keyboard_type=ft.KeyboardType.NUMBER)
        access_dropdown = ft.Dropdown(
            label="People who can access your keys right now",
            options=[
                ft.dropdown.Option("0", "0 (only me)"),
                ft.dropdown.Option("1", "1 person"),
                ft.dropdown.Option("2", "2+ people"),
            ],
            value="0",
            border_color=ft.Colors.GREY_800
        )
        access_hint = ft.Text("*be honest. if they need your phone/2fa, count it as 0.", size=10, color=ft.Colors.GREY_500)
        
        storage_dropdown = ft.Dropdown(
            label="Where are seed phrases stored?",
            options=[
                ft.dropdown.Option("hardware", "hardware wallet (ledger/trezor)"),
                ft.dropdown.Option("paper", "paper / steel backup"),
                ft.dropdown.Option("cloud", "cloud / password manager (dangerous)"),
                ft.dropdown.Option("exchange", "centralized exchange (coinbase/binance)"),
                ft.dropdown.Option("memory", "brain wallet (memory only)"),
            ],
            value="hardware",
            border_color=ft.Colors.GREY_800
        )
        
        # Results area
        risk_title = ft.Text("Risk Probability: --%", size=24, weight="bold", visible=False)
        risk_desc = ft.Text("", size=14, color=ft.Colors.GREY_400, visible=False)
        
        loss_metric = ft.Text("$0", size=32, weight="bold", color=ft.Colors.RED_400)
        time_metric = ft.Text("IMMEDIATE", size=24, weight="bold")
        
        results_container = ft.Container(
            content=ft.Column([
                ft.Divider(height=40, color=ft.Colors.GREY_800),
                risk_title,
                risk_desc,
                ft.Row([
                    ft.Column([ft.Text("PROJECTED LOSS", size=10, color=ft.Colors.GREY_500), loss_metric], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Column([ft.Text("TIME UNTIL ZERO", size=10, color=ft.Colors.GREY_500), time_metric], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ], alignment=ft.MainAxisAlignment.SPACE_EVENLY, visible=False)
            ]),
            visible=False
        )
        
        def calculate_risk(e):
            try:
                amount = float(assets_input.value or 0)
            except:
                amount = 0
            access = access_dropdown.value
            storage = storage_dropdown.value
            
            score = 0
            if access == "0": score += 90
            elif access == "1": score += 40
            else: score += 10
            
            if storage == "memory" and access == "0": score = 99.9
            if storage == "cloud": score += 20
            if storage == "exchange": score += 30
            
            score = min(99.9, max(0, score))
            
            risk_title.value = f"Risk Probability: {score}%"
            risk_title.color = ft.Colors.RED_400 if score > 70 else (ft.Colors.ORANGE_400 if score > 30 else ft.Colors.GREEN_400)
            risk_title.visible = True
            
            if score > 70:
                risk_desc.value = "CRITICAL FAILURE LIKELY. You have a single point of failure."
            else:
                risk_desc.value = "Ensure your beneficiaries know the recovery procedure."
            risk_desc.visible = True
            
            loss_metric.value = f"${amount:,.0f}"
            results_container.visible = True
            results_container.content.controls[3].visible = True # Row with metrics
            
            self.page.update()

        return ft.Container(
            content=ft.Column([
                ft.Text("Calculate the probability of asset loss upon incapacitation.", size=16),
                assets_input,
                ft.Column([access_dropdown, access_hint], spacing=2),
                storage_dropdown,
                ft.Button("Calculate Risk", on_click=calculate_risk, bgcolor=self.accent_color, color=ft.Colors.BLACK),
                results_container
            ], scroll=ft.ScrollMode.ADAPTIVE),
            padding=20
        )

    def tab_audio_mask(self):
        audio_path = ft.TextField(label="Source WAV Path", border_color=ft.Colors.GREY_800)
        msg_input = ft.TextField(label="Secret Message", border_color=ft.Colors.GREY_800, password=True, can_reveal_password=True)
        
        def handle_hide(e):
            if not audio_path.value or not msg_input.value: return
            out = audio_path.value.replace(".wav", "_client_hidden.wav")
            try:
                hide_text_in_audio(audio_path.value, msg_input.value, out)
                self.page.snack_bar = ft.SnackBar(ft.Text(f"Generated: {out}"))
                self.page.snack_bar.open = True
            except Exception as ex:
                self.page.snack_bar = ft.SnackBar(ft.Text(f"Error: {str(ex)}"))
                self.page.snack_bar.open = True
            self.page.update()

        def handle_extract(e):
            if not audio_path.value: return
            try:
                msg = extract_text_from_audio(audio_path.value)
                msg_input.value = msg
            except Exception as ex:
                self.page.snack_bar = ft.SnackBar(ft.Text(f"Extraction failed: {str(ex)}"))
                self.page.snack_bar.open = True
            self.page.update()

        return ft.Container(
            content=ft.Column([
                ft.Text("Acoustic Masking (LSB Audio Steganography)", size=18, weight="bold"),
                ft.Text("Hide text in WAV files without audible distortion.", size=14, color=ft.Colors.GREY_500),
                audio_path,
                msg_input,
                ft.Row([
                    ft.Button("Hide Message", on_click=handle_hide, bgcolor=self.accent_color, color=ft.Colors.BLACK),
                    ft.OutlinedButton("Extract Message", on_click=handle_extract),
                ], spacing=10)
            ]),
            padding=20
        )

    def tab_visual_split(self):
        img_input = ft.TextField(label="Source Image Path", border_color=ft.Colors.GREY_800)
        
        def handle_visual_split(e):
            if not img_input.value: return
            try:
                # Actual logic call from split_image_vc
                p1, p2 = split_image_vc(img_input.value, ".")
                self.page.snack_bar = ft.SnackBar(ft.Text(f"Split completed. Shares saved: {p1}, {p2}"))
                self.page.snack_bar.open = True
            except Exception as ex:
                self.page.snack_bar = ft.SnackBar(ft.Text(f"Error: {str(ex)}"))
                self.page.snack_bar.open = True
            self.page.update()

        return ft.Container(
            content=ft.Column([
                ft.Text("Optical Splitting (Visual Cryptography)", size=18, weight="bold"),
                ft.Text("Split an image into two noise patterns. Reconstruct by overlaying.", size=14, color=ft.Colors.GREY_500),
                img_input,
                ft.Button("Split Image", on_click=handle_visual_split, bgcolor=self.accent_color, color=ft.Colors.BLACK),
            ]),
            padding=20
        )

def main(page: ft.Page):
    DeadhandApp(page)

if __name__ == "__main__":
    ft.run(main)
