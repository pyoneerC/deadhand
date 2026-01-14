"""
Visual Cryptography con QR Code
Divide un QR en 2 shares que parecen ruido
Superponés las transparencias → aparece el QR → escaneás → seed phrase

Uso:
python visual_crypto_qr.py "abandon ability able about above absent absorb abstract absurd abuse access accident"

Genera:
- qr_original.png    → El QR original (NO guardar, solo para demo)
- qr_share1.png      → Imprimí en transparencia (parece arte abstracto)
- qr_share2.png      → Guardá en caja fuerte o dale a heredero
- qr_combined.png    → Simulación de superposición
"""

import qrcode
from PIL import Image
import numpy as np
import random
import sys

def create_qr(text, size=200):
    """Crea un QR code de la seed phrase"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # Alta corrección de errores
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img = img.convert('1')  # Convertir a blanco y negro puro
    
    return img

def split_to_visual_shares(img):
    """
    Divide imagen en 2 shares usando Visual Cryptography.
    """
    width, height = img.size
    pixels = np.array(img)
    
    # Cada pixel se convierte en bloque 2x2
    share1 = np.zeros((height * 2, width * 2), dtype=np.uint8)
    share2 = np.zeros((height * 2, width * 2), dtype=np.uint8)
    
    for y in range(height):
        for x in range(width):
            sy, sx = y * 2, x * 2
            
            # Elegir patrón random
            pattern_type = random.randint(0, 1)
            
            if pattern_type == 0:
                base = np.array([[0, 255], [255, 0]])  # Diagonal /
            else:
                base = np.array([[255, 0], [0, 255]])  # Diagonal \
            
            if pixels[y, x]:  # Pixel BLANCO
                # Ambos shares tienen mismo patrón → superposición = gris (claro)
                share1[sy:sy+2, sx:sx+2] = base
                share2[sy:sy+2, sx:sx+2] = base
            else:  # Pixel NEGRO
                # Shares tienen patrones opuestos → superposición = negro
                share1[sy:sy+2, sx:sx+2] = base
                share2[sy:sy+2, sx:sx+2] = 255 - base  # Invertido
    
    return Image.fromarray(share1), Image.fromarray(share2)

def combine_shares(share1, share2):
    """Simula superponer las transparencias"""
    arr1 = np.array(share1)
    arr2 = np.array(share2)
    
    # Superposición = AND (donde ambos son blancos = blanco, sino negro)
    combined = np.minimum(arr1, arr2)
    
    return Image.fromarray(combined)

def main(seed_phrase):
    print("🔐 Visual Cryptography QR Generator")
    print("=" * 50)
    print(f"Seed phrase: {seed_phrase[:20]}...")
    print()
    
    # Paso 1: Crear QR
    print("1️⃣ Generando QR code...")
    qr = create_qr(seed_phrase)
    qr.save("qr_original.png")
    print(f"   → qr_original.png ({qr.size[0]}x{qr.size[1]})")
    
    # Paso 2: Dividir en shares
    print("2️⃣ Dividiendo en 2 shares...")
    share1, share2 = split_to_visual_shares(qr)
    share1.save("qr_share1.png")
    share2.save("qr_share2.png")
    print(f"   → qr_share1.png ({share1.size[0]}x{share1.size[1]}) - IMPRIMÍ EN TRANSPARENCIA")
    print(f"   → qr_share2.png ({share2.size[0]}x{share2.size[1]}) - DALE A TU HEREDERO")
    
    # Paso 3: Combinar (simulación)
    print("3️⃣ Simulando superposición...")
    combined = combine_shares(share1, share2)
    combined.save("qr_combined.png")
    print(f"   → qr_combined.png - EL QR APARECE!")
    
    print()
    print("=" * 50)
    print("✅ LISTO!")
    print()
    print("📋 Instrucciones:")
    print("   1. Imprimí qr_share1.png en transparencia (acetato)")
    print("   2. Imprimí qr_share2.png en transparencia (acetato)")
    print("   3. Superponé las dos transparencias")
    print("   4. Escaneá el QR que aparece")
    print("   5. → Tu seed phrase!")
    print()
    print("🖼️ Podés colgar share1 en un cuadro.")
    print("   Nadie sabe que es tu seed phrase.")
    print("   Parece arte abstracto.")
    print()
    print("⚠️  ELIMINÁ qr_original.png - No lo guardes!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Demo con seed phrase de ejemplo
        seed = "abandon ability able about above absent absorb abstract absurd abuse access accident"
        print("Usando seed phrase de ejemplo...")
        print("Para tu seed real: python visual_crypto_qr.py \"tu seed phrase\"")
        print()
    else:
        seed = sys.argv[1]
    
    main(seed)
