"""
Audio Steganography - Esconder texto en archivos WAV
Usando LSB (Least Significant Bit)

Instalación:
pip install numpy scipy

Uso:
python audio_steg.py encode audio.wav "mi mensaje secreto" output.wav
python audio_steg.py decode output.wav
"""

import numpy as np
from scipy.io import wavfile
import sys

def text_to_bits(text):
    """Convierte texto a bits"""
    bits = []
    for char in text:
        char_bits = bin(ord(char))[2:].zfill(8)
        bits.extend([int(b) for b in char_bits])
    return bits

def bits_to_text(bits):
    """Convierte bits a texto"""
    chars = []
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        if len(byte) == 8:
            char_code = int(''.join(map(str, byte)), 2)
            if char_code == 0:  # Null terminator
                break
            chars.append(chr(char_code))
    return ''.join(chars)

def encode_audio(audio_path, message, output_path):
    """Esconde un mensaje en un archivo WAV"""
    
    # Leer audio
    sample_rate, audio_data = wavfile.read(audio_path)
    
    # Convertir a array modificable
    if audio_data.dtype == np.int16:
        audio = audio_data.astype(np.int32)
    else:
        audio = audio_data.copy()
    
    # Si es stereo, usar solo canal izquierdo para datos
    if len(audio.shape) > 1:
        audio_flat = audio[:, 0].flatten()
    else:
        audio_flat = audio.flatten()
    
    # Preparar mensaje con terminador
    message_with_end = message + '\x00'  # Null terminator
    bits = text_to_bits(message_with_end)
    
    print(f"Mensaje: {len(message)} caracteres")
    print(f"Bits a esconder: {len(bits)}")
    print(f"Samples disponibles: {len(audio_flat)}")
    
    if len(bits) > len(audio_flat):
        raise ValueError("Audio muy corto para el mensaje")
    
    # Esconder bits en LSB
    for i, bit in enumerate(bits):
        # Limpiar LSB y setear el bit del mensaje
        audio_flat[i] = (audio_flat[i] & ~1) | bit
    
    # Reconstruir audio
    if len(audio.shape) > 1:
        audio[:, 0] = audio_flat[:len(audio)]
        output = audio.astype(audio_data.dtype)
    else:
        output = audio_flat.astype(audio_data.dtype)
    
    # Guardar
    wavfile.write(output_path, sample_rate, output)
    print(f"✅ Mensaje escondido en: {output_path}")

def decode_audio(audio_path, max_chars=1000):
    """Extrae mensaje escondido de un archivo WAV"""
    
    # Leer audio
    sample_rate, audio_data = wavfile.read(audio_path)
    
    # Flatten
    if len(audio_data.shape) > 1:
        audio_flat = audio_data[:, 0].flatten()
    else:
        audio_flat = audio_data.flatten()
    
    # Extraer LSBs
    bits = []
    for i in range(min(max_chars * 8, len(audio_flat))):
        bits.append(audio_flat[i] & 1)
    
    # Convertir a texto
    message = bits_to_text(bits)
    return message

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso:")
        print("  Encode: python audio_steg.py encode input.wav 'mensaje' output.wav")
        print("  Decode: python audio_steg.py decode audio.wav")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "encode":
        if len(sys.argv) != 5:
            print("Uso: python audio_steg.py encode input.wav 'mensaje' output.wav")
            sys.exit(1)
        encode_audio(sys.argv[2], sys.argv[3], sys.argv[4])
        
    elif command == "decode":
        message = decode_audio(sys.argv[2])
        print(f"📩 Mensaje extraído: {message}")
    
    else:
        print(f"Comando desconocido: {command}")
