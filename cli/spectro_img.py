import wave
import math
import argparse
import sys
from PIL import Image

def generate_spectrogram_audio(image_path, output_path, duration=5.0, min_freq=200, max_freq=20000, sample_rate=44100):
    """
    Converts an image into a sound file where the spectrogram reveals the image.
    Each row of pixels represents a frequency, each column a moment in time.
    """
    img = Image.open(image_path).convert('L') # Convert to grayscale
    width, height = img.size
    pixels = img.load()

    # Audio parameters
    num_samples = int(duration * sample_rate)
    samples_per_pixel_col = num_samples / width
    
    # We want top of image to be high freq, bottom to be low freq
    # Frequency range is mapped to image height
    freq_step = (max_freq - min_freq) / height
    
    # Final audio buffer (16-bit PCM)
    audio_data = []
    
    print(f"Generating {duration}s audio at {sample_rate}Hz...")
    
    for i in range(num_samples):
        # Current time in seconds
        t = i / sample_rate
        # Current column in image
        col = int(i / samples_per_pixel_col)
        if col >= width: col = width - 1
        
        sample_sum = 0
        
        # For each pixel in this column, generate a sine wave
        # Optimization: only process non-black pixels
        for row in range(height):
            # Intensity 0-255
            intensity = pixels[col, row]
            if intensity > 10: # Threshold to ignore noise
                # Map row to frequency (inverted so top is high)
                freq = max_freq - (row * freq_step)
                # Amplitude proportional to intensity
                amplitude = intensity / 255.0
                # Generate sine wave for this freq at this time
                sample_sum += amplitude * math.sin(2 * math.pi * freq * t)
        
        # Normalize and clip
        # Since we might sum many waves, we need to bring it down to 16-bit range
        # Scaling by a factor to avoid blowing up
        scaled_sample = int(sample_sum * 1000) 
        if scaled_sample > 32767: scaled_sample = 32767
        elif scaled_sample < -32768: scaled_sample = -32768
        
        audio_data.append(scaled_sample)
        
        # Progress indicator
        if i % (num_samples // 10) == 0:
            print(f"{int(i/num_samples * 100)}%...")

    # Write to WAV
    with wave.open(output_path, 'wb') as wav:
        wav.setnchannels(1) # Mono
        wav.setsampwidth(2) # 16-bit
        wav.setframerate(sample_rate)
        
        # Convert audio_data to bytes
        binary_data = b''
        for sample in audio_data:
            binary_data += sample.to_bytes(2, byteorder='little', signed=True)
        wav.writeframes(binary_data)

def main():
    parser = argparse.ArgumentParser(description="Shardium Spectrogram Image Hider CLI")
    parser.add_argument("image", help="Input image file")
    parser.add_argument("output", help="Output WAV file")
    parser.add_argument("--duration", type=float, default=5.0, help="Duration in seconds (default: 5.0)")
    parser.add_argument("--min_freq", type=int, default=200, help="Min frequency in Hz (default: 200)")
    parser.add_argument("--max_freq", type=int, default=15000, help="Max frequency in Hz (default: 15000)")

    args = parser.parse_args()

    try:
        generate_spectrogram_audio(
            args.image, 
            args.output, 
            duration=args.duration,
            min_freq=args.min_freq,
            max_freq=args.max_freq
        )
        print(f"\nSuccess! Image hidden in {args.output}")
        print("To see it, open the file in a spectrogram viewer (like Audacity or Sonic Visualiser).")
        print("Note: If the result is silent or noisy, try a smaller/simpler image.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
