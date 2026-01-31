import wave
import argparse
import sys
import os

def hide_text(audio_path, text, output_path):
    # Convert text to bits
    bits = bin(int.from_bytes(text.encode('utf-8'), 'big'))[2:].zfill(len(text) * 8)
    # Add a null terminator (8 zeros) so we know when to stop reading
    bits += '00000000'
    
    with wave.open(audio_path, 'rb') as audio:
        params = audio.getparams()
        frames = bytearray(audio.readframes(audio.getnframes()))

    if len(bits) > len(frames):
        raise ValueError("Audio file too small to hide this much text")

    # Embed bits into least significant bit of each byte
    for i, bit in enumerate(bits):
        frames[i] = (frames[i] & ~1) | int(bit)

    with wave.open(output_path, 'wb') as output:
        output.setparams(params)
        output.writeframes(frames)

def extract_text(audio_path):
    with wave.open(audio_path, 'rb') as audio:
        frames = bytearray(audio.readframes(audio.getnframes()))

    bits = ""
    for frame in frames:
        bits += str(frame & 1)

    # Convert bits to bytes
    bytes_list = []
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        if byte == '00000000':  # Null terminator
            break
        bytes_list.append(int(byte, 2))

    return bytes(bytes_list).decode('utf-8')

def main():
    parser = argparse.ArgumentParser(description="deadhand Acoustic Masking CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Hide
    hide_parser = subparsers.add_parser("hide", help="Hide text in a WAV file")
    hide_parser.add_argument("audio", help="Input WAV file")
    hide_parser.add_argument("text", help="Text to hide")
    hide_parser.add_argument("output", help="Output WAV file")

    # Extract
    extract_parser = subparsers.add_parser("extract", help="Extract text from a WAV file")
    extract_parser.add_argument("audio", help="WAV file containing secret")

    args = parser.parse_args()

    if args.command == "hide":
        try:
            hide_text(args.audio, args.text, args.output)
            print(f"Success! Secret hidden in {args.output}")
            print("WARNING: Do not compress this file (MP3, WhatsApp, etc) or the data will be destroyed.")
        except Exception as e:
            print(f"Error: {e}")

    elif args.command == "extract":
        try:
            secret = extract_text(args.audio)
            print(f"\nExtracted Secret: {secret}")
        except Exception as e:
            print(f"Error: {e}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
