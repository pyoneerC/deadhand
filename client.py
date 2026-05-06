import flet as ft
import os
import hashlib

def main(page: ft.Page):
    page.title = "Deadhand Sovereign Client"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.window_width = 450
    page.window_height = 750
    page.bgcolor = "#0a0a0a"
    page.fonts = {
        "Inter": "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
        "JetBrains Mono": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap"
    }
    page.theme = ft.Theme(font_family="Inter")

    # --- STATE ---
    app_state = {
        "key": None
    }

    # --- UI COMPONENTS ---
    
    # AUTH VIEW
    auth_title = ft.Text("DEADHAND", size=28, weight=ft.FontWeight.W_900, color=ft.Colors.WHITE, letter_spacing=-1)
    auth_subtitle = ft.Text("Sovereign Client", size=14, color="#a1a1aa", weight=ft.FontWeight.W_500, margin=ft.margin.only(bottom=30))
    
    key_input = ft.TextField(
        label="Enter Access Key",
        password=True,
        can_reveal_password=True,
        border_color="#27272a",
        focused_border_color="#FF5500",
        cursor_color="#FF5500",
        width=320,
        height=60,
        text_style=ft.TextStyle(font_family="JetBrains Mono"),
        border_radius=8
    )
    
    auth_error = ft.Text("", color="#e11d48", size=12)

    def on_auth_submit(e):
        if len(key_input.value) >= 16:  # basic validation for our generated keys
            app_state["key"] = key_input.value
            page.go("/split")
        else:
            auth_error.value = "Invalid or malformed key. Must be 16+ characters."
            page.update()

    auth_submit = ft.ElevatedButton(
        "Unlock Vault", 
        on_click=on_auth_submit, 
        bgcolor=ft.Colors.WHITE, 
        color=ft.Colors.BLACK,
        width=320,
        height=50,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
            text_style=ft.TextStyle(weight=ft.FontWeight.W_700, size=15)
        )
    )
    
    auth_footer = ft.Text(
        "like how it works? enter your access key\nor buy it in deadhandprotocol.com", 
        size=12, 
        color="#71717a", 
        text_align=ft.TextAlign.CENTER,
        weight=ft.FontWeight.W_500
    )

    auth_view = ft.View(
        "/",
        [
            ft.Container(
                content=ft.Column(
                    [
                        auth_title,
                        auth_subtitle,
                        key_input,
                        auth_error,
                        ft.Container(height=10),
                        auth_submit,
                        ft.Container(height=40),
                        auth_footer
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=40,
                border=ft.border.all(1, "#27272a"),
                border_radius=24,
                bgcolor="#000000",
                # Hardcoded ARGB hex for 50% opacity black, bypassing flet color functions entirely
                shadow=ft.BoxShadow(spread_radius=0, blur_radius=40, color="#80000000"),
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        bgcolor="#0a0a0a",
        padding=20
    )


    # SPLIT VIEW
    split_title = ft.Text("Split a Secret", size=24, weight=ft.FontWeight.W_800, color=ft.Colors.WHITE, margin=ft.margin.only(bottom=20))
    secret_input = ft.TextField(
        multiline=True,
        min_lines=4,
        max_lines=6,
        label="Enter your seed phrase or secret...",
        border_color="#27272a",
        focused_border_color="#FF5500",
        cursor_color="#FF5500",
        width=320,
        text_style=ft.TextStyle(font_family="JetBrains Mono", size=13),
        border_radius=8
    )

    shards_list = ft.Column(spacing=12)

    def generate_mock_shards(secret_text):
        if not secret_text:
            return []
        
        base_hash = hashlib.sha256(secret_text.encode()).hexdigest()
        shards = []
        for i in range(1, 4):
            shard_data = f"{i}-{os.urandom(4).hex()}-{base_hash[(i-1)*16:i*16]}"
            shards.append(shard_data)
        return shards

    def on_split_click(e):
        if not secret_input.value:
            return
            
        shards = generate_mock_shards(secret_input.value)
        shards_list.controls.clear()
        
        for i, shard in enumerate(shards):
            shards_list.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.ARROW_FORWARD, size=16, color="#FF5500"),
                        ft.Text(f"Shard {i+1}: {shard}", font_family="JetBrains Mono", size=11, color="#d4d4d8", selectable=True)
                    ]),
                    padding=16,
                    border=ft.border.all(1, "#27272a"),
                    border_radius=8,
                    bgcolor="#09090b"
                )
            )
        page.update()

    split_btn = ft.ElevatedButton(
        "Generate Cryptographic Shards", 
        on_click=on_split_click, 
        bgcolor="#FF5500", 
        color=ft.Colors.WHITE,
        width=320,
        height=50,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=8),
            text_style=ft.TextStyle(weight=ft.FontWeight.W_700, size=14)
        )
    )

    split_view = ft.View(
        "/split",
        [
            ft.Container(
                content=ft.Column(
                    [
                        split_title,
                        secret_input,
                        ft.Container(height=10),
                        split_btn,
                        ft.Container(height=20),
                        ft.Text("Output Shards (M-of-N):", weight=ft.FontWeight.W_600, color="#a1a1aa", size=12),
                        shards_list
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=40,
                border=ft.border.all(1, "#27272a"),
                border_radius=24,
                bgcolor="#000000",
                width=400,
                shadow=ft.BoxShadow(spread_radius=0, blur_radius=40, color="#80000000"),
            )
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        bgcolor="#0a0a0a",
        padding=20
    )

    # --- ROUTING ---
    def route_change(route):
        page.views.clear()
        page.views.append(auth_view)
        if page.route == "/split":
            page.views.append(split_view)
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

if __name__ == "__main__":
    ft.app(target=main)