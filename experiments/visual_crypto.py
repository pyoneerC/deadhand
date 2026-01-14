"""
Visual Cryptography - Dividir imagen en 2 shares
Al superponer los shares, se revela el mensaje original

Instalación:
pip install pillow numpy

Uso:
python visual_crypto.py split imagen.png
# Genera: share1.png, share2.png

python visual_crypto.py combine share1.png share2.png
# Genera: revealed.png (la imagen original!)

También podés imprimir share1 y share2 en transparencias,
superponerlas físicamente, y ver el mensaje SIN COMPUTADORA.
"""

from PIL import Image
import numpy as np
import random
import sys

def create_visual_shares(image_path, output_prefix="share"):
    """
    Divide una imagen en 2 shares usando Visual Cryptography.
    Cada share parece ruido random.
    Al superponerlos, se revela la imagen original.
    """
    
    # Cargar imagen y convertir a blanco y negro
    img = Image.open(image_path).convert('1')  # 1-bit (B&W)
    width, height = img.size
    pixels = np.array(img)
    
    print(f"Imagen: {width}x{height}")
    
    # Cada pixel original se convierte en 2x2 subpixels
    # Esto es necesario para el algoritmo
    share1 = np.zeros((height * 2, width * 2), dtype=np.uint8)
    share2 = np.zeros((height * 2, width * 2), dtype=np.uint8)
    
    # Patrones posibles para cada pixel
    # Cada patrón es un bloque 2x2
    patterns = {
        # Para pixel BLANCO: ambos shares tienen el MISMO patrón
        'white': [
            np.array([[0, 1], [1, 0]]),  # Diagonal /
            np.array([[1, 0], [0, 1]]),  # Diagonal \
        ],
        # Para pixel NEGRO: shares tienen patrones OPUESTOS
        'black_a': [
            np.array([[0, 1], [1, 0]]),
            np.array([[1, 0], [0, 1]]),
        ],
        'black_b': [
            np.array([[1, 0], [0, 1]]),
            np.array([[0, 1], [1, 0]]),
        ]
    }
    
    for y in range(height):
        for x in range(width):
            # Posición en el share (2x escala)
            sy, sx = y * 2, x * 2
            
            if pixels[y, x]:  # Pixel BLANCO (True = 255)
                # Ambos shares tienen el mismo patrón
                pattern = random.choice(patterns['white'])
                share1[sy:sy+2, sx:sx+2] = pattern * 255
                share2[sy:sy+2, sx:sx+2] = pattern * 255
            else:  # Pixel NEGRO (False = 0)
                # Shares tienen patrones complementarios
                idx = random.randint(0, 1)
                share1[sy:sy+2, sx:sx+2] = patterns['black_a'][idx] * 255
                share2[sy:sy+2, sx:sx+2] = patterns['black_b'][idx] * 255
    
    # Guardar shares
    share1_img = Image.fromarray(share1, mode='L')
    share2_img = Image.fromarray(share2, mode='L')
    
    share1_path = f"{output_prefix}1.png"
    share2_path = f"{output_prefix}2.png"
    
    share1_img.save(share1_path)
    share2_img.save(share2_path)
    
    print(f"✅ Share 1: {share1_path}")
    print(f"✅ Share 2: {share2_path}")
    print("")
    print("Para revelar el mensaje:")
    print("  1. Abrí ambos shares en un editor de imagen")
    print("  2. Poné uno encima del otro (multiply blend)")
    print("  3. O imprimí en transparencias y superponé físicamente!")
    
    return share1_path, share2_path

def combine_shares(share1_path, share2_path, output_path="revealed.png"):
    """
    Combina 2 shares para revelar la imagen original.
    Simula superponer las transparencias.
    """
    
    share1 = np.array(Image.open(share1_path).convert('L'))
    share2 = np.array(Image.open(share2_path).convert('L'))
    
    # Simular superposición (AND lógico = multiply)
    # Donde AMBOS son blancos → blanco
    # Donde cualquiera es negro → negro
    combined = np.minimum(share1, share2)
    
    # Guardar
    result = Image.fromarray(combined, mode='L')
    result.save(output_path)
    
    print(f"✅ Imagen revelada: {output_path}")
    return output_path

def create_demo():
    """Crea una imagen de demo con texto 'SECRET'"""
    
    from PIL import ImageDraw, ImageFont
    
    # Crear imagen con texto
    img = Image.new('1', (200, 80), color=1)  # Fondo blanco
    draw = ImageDraw.Draw(img)
    
    # Usar font default (o instalar uno)
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    draw.text((10, 15), "SECRET", font=font, fill=0)  # Texto negro
    
    demo_path = "demo_secret.png"
    img.save(demo_path)
    print(f"✅ Imagen de demo creada: {demo_path}")
    return demo_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Visual Cryptography Demo")
        print("=" * 40)
        print("")
        print("Uso:")
        print("  python visual_crypto.py demo")
        print("      → Crea imagen de prueba y la divide")
        print("")
        print("  python visual_crypto.py split imagen.png")
        print("      → Divide imagen en 2 shares")
        print("")
        print("  python visual_crypto.py combine share1.png share2.png")
        print("      → Combina shares para revelar imagen")
        print("")
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == "demo":
        print("🔮 Creando demo de Visual Cryptography...")
        print("")
        
        # Crear imagen demo
        demo_path = create_demo()
        
        # Dividir en shares
        create_visual_shares(demo_path, "demo_share")
        
        print("")
        print("Ahora combinamos los shares...")
        combine_shares("demo_share1.png", "demo_share2.png", "demo_revealed.png")
        
        print("")
        print("🎉 Demo completo!")
        print("   - demo_secret.png    → Imagen original")
        print("   - demo_share1.png    → Share 1 (parece ruido)")
        print("   - demo_share2.png    → Share 2 (parece ruido)")
        print("   - demo_revealed.png  → Imagen revelada")
        
    elif command == "split":
        if len(sys.argv) != 3:
            print("Uso: python visual_crypto.py split imagen.png")
            sys.exit(1)
        create_visual_shares(sys.argv[2])
        
    elif command == "combine":
        if len(sys.argv) != 4:
            print("Uso: python visual_crypto.py combine share1.png share2.png")
            sys.exit(1)
        combine_shares(sys.argv[2], sys.argv[3])
        
    else:
        print(f"Comando desconocido: {command}")
        print("Usa: demo, split, o combine")
