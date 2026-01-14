"""Test audio steganography"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from scipy.io import wavfile
import numpy as np

print("=== AUDIO STEG TEST ===")
print()

# 1. Leer audio original
print("1. Leyendo song.wav...")
rate1, data1 = wavfile.read('song.wav')
print(f"   Sample rate: {rate1}")
print(f"   Shape: {data1.shape}")
print(f"   Dtype: {data1.dtype}")
print()

# 2. Leer audio con secreto
print("2. Leyendo song_with_secret.wav...")
rate2, data2 = wavfile.read('song_with_secret.wav')
print(f"   Sample rate: {rate2}")
print(f"   Shape: {data2.shape}")
print()

# 3. Comparar
print("3. Comparando archivos...")
if data1.shape == data2.shape:
    diff = np.sum(data1 != data2)
    print(f"   Samples diferentes: {diff}")
    print(f"   Total samples: {data1.size}")
else:
    print("   Shapes diferentes!")
print()

# 4. Extraer mensaje
print("4. Extrayendo mensaje secreto...")
if len(data2.shape) > 1:
    audio_flat = data2[:, 0].flatten()
else:
    audio_flat = data2.flatten()

bits = []
for i in range(1000 * 8):  # Max 1000 chars
    bits.append(audio_flat[i] & 1)

# Bits a texto
chars = []
for i in range(0, len(bits), 8):
    byte = bits[i:i+8]
    if len(byte) == 8:
        char_code = int(''.join(map(str, byte)), 2)
        if char_code == 0:
            break
        chars.append(chr(char_code))

# save message to file
with open('secret.txt', 'w') as f:
    f.write(''.join(chars))

message = ''.join(chars)
print(f"   MENSAJE: {message}")
print()
print("=== DONE ===")
