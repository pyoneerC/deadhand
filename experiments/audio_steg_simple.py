"""
Audio Steganography - SIN DEPENDENCIAS EXTERNAS
Solo usa 'wave' que viene con Python

Uso:
python audio_steg_simple.py encode song.wav "mi mensaje secreto" output.wav
python audio_steg_simple.py decode output.wav
"""

import wave
import struct
import sys

def text_to_bits(text):
    """Convierte texto a lista de bits"""
    bits = []
    for char in text:
        for bit in format(ord(char), '08b'):
            bits.append(int(bit))
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

def encode(input_path, message, output_path):
    """Esconde mensaje en archivo WAV"""
    
    print(f"Abriendo: {input_path}")
    
    with wave.open(input_path, 'rb') as wav_in:
        params = wav_in.getparams()
        n_frames = wav_in.getnframes()
        n_channels = wav_in.getnchannels()
        sample_width = wav_in.getsampwidth()
        
        print(f"Channels: {n_channels}")
        print(f"Sample width: {sample_width} bytes")
        print(f"Frames: {n_frames}")
        
        # Leer todos los frames
        frames = wav_in.readframes(n_frames)
    
    # Convertir a lista de samples
    if sample_width == 2:  # 16-bit audio
        fmt = f"<{len(frames)//2}h"  # Little-endian shorts
        samples = list(struct.unpack(fmt, frames))
    else:
        print(f"Error: Solo soporta 16-bit audio (este es {sample_width*8}-bit)")
        return
    
    # Preparar mensaje
    message_with_end = message + '\x00'
    bits = text_to_bits(message_with_end)
    
    print(f"Mensaje: {len(message)} caracteres")
    print(f"Bits a esconder: {len(bits)}")
    print(f"Samples disponibles: {len(samples)}")
    
    if len(bits) > len(samples):
        print("ERROR: Audio muy corto para el mensaje")
        return
    
    # Esconder bits en LSB
    for i, bit in enumerate(bits):
        samples[i] = (samples[i] & ~1) | bit
    
    # Convertir de vuelta a bytes
    new_frames = struct.pack(f"<{len(samples)}h", *samples)
    
    # Guardar
    with wave.open(output_path, 'wb') as wav_out:
        wav_out.setparams(params)
        wav_out.writeframes(new_frames)
    
    print(f"✅ Mensaje escondido en: {output_path}")

def decode(input_path, max_chars=1000):
    """Extrae mensaje de archivo WAV"""
    
    print(f"Abriendo: {input_path}")
    
    with wave.open(input_path, 'rb') as wav_in:
        n_frames = wav_in.getnframes()
        sample_width = wav_in.getsampwidth()
        frames = wav_in.readframes(n_frames)
    
    if sample_width != 2:
        print(f"Error: Solo soporta 16-bit audio")
        return ""
    
    # Convertir a samples
    fmt = f"<{len(frames)//2}h"
    samples = struct.unpack(fmt, frames)
    
    # Extraer bits LSB
    bits = []
    for i in range(min(max_chars * 8, len(samples))):
        bits.append(samples[i] & 1)
    
    # Convertir a texto
    message = bits_to_text(bits)
    return message

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Audio Steganography")
        print("=" * 40)
        print()
        print("Esconder mensaje:")
        print("  python audio_steg_simple.py encode input.wav 'mensaje' output.wav")
        print()
        print("Extraer mensaje:")
        print("  python audio_steg_simple.py decode audio.wav")
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "encode":
        if len(sys.argv) != 5:
            print("Uso: python audio_steg_simple.py encode input.wav 'mensaje' output.wav")
            sys.exit(1)
        encode(sys.argv[2], sys.argv[3], sys.argv[4])
        
    elif cmd == "decode":
        msg = decode(sys.argv[2])
        print()
        print("=" * 40)
        print(f"📩 MENSAJE EXTRAIDO:")
        print(f"   {msg}")
        print("=" * 40)
    
    else:
        print(f"Comando desconocido: {cmd}")
