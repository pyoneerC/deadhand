import random
import argparse
from PIL import Image
import os

def split_image(image_path, output_prefix):
    # Load image and convert to Black and White (1-bit)
    img = Image.open(image_path).convert('1')
    width, height = img.size
    
    # Create two shares (double sized for visual crystallography)
    # Standard 2x2 visual crypto: 
    # Black pixel becomes [1,0,0,1] and [0,1,1,0]
    # White pixel becomes [1,0,0,1] and [1,0,0,1]
    share1 = Image.new('1', (width * 2, height * 2))
    share2 = Image.new('1', (width * 2, height * 2))
    
    for x in range(width):
        for y in range(height):
            pixel = img.getpixel((x, y))
            
            # Sub-pixels
            # Patterns: 0 = White, 1 = Black
            p1 = [(1,0), (0,1)] # Pattern A
            p2 = [(0,1), (1,0)] # Pattern B
            
            coin = random.random() > 0.5
            
            if pixel == 0: # Black
                pattern1 = p1 if coin else p2
                pattern2 = p2 if coin else p1 # Complementary
            else: # White
                pattern1 = p1 if coin else p2
                pattern2 = p1 if coin else p2 # Identical
                
            # Draw sub-pixels
            for i in range(2):
                for j in range(2):
                    share1.putpixel((x*2 + i, y*2 + j), pattern1[i][j])
                    share2.putpixel((x*2 + i, y*2 + j), pattern2[i][j])
                    
    share1.save(f"{output_prefix}_share1.png")
    share2.save(f"{output_prefix}_share2.png")
    print(f"Shares saved as {output_prefix}_share1.png and {output_prefix}_share2.png")

def combine_shares(share1_path, share2_path, output_path):
    s1 = Image.open(share1_path).convert('1')
    s2 = Image.open(share2_path).convert('1')
    
    if s1.size != s2.size:
        raise ValueError("Shares must be the same size")
        
    width, height = s1.size
    combined = Image.new('1', (width, height))
    
    for x in range(width):
        for y in range(height):
            p1 = s1.getpixel((x, y))
            p2 = s2.getpixel((x, y))
            # Binary OR (combined black if either is black)
            # In '1' mode, 0 is Black, 255 is White. So we use min() for black-priority
            combined.putpixel((x, y), min(p1, p2))
            
    combined.save(output_path)
    print(f"Combined image saved as {output_path}")

def main():
    parser = argparse.ArgumentParser(description="deadhand Optical Splitting CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Split
    split_parser = subparsers.add_parser("split", help="Split an image into 2 noise shares")
    split_parser.add_argument("image", help="Input image (best if B&W / QR code)")
    split_parser.add_argument("--out", default="share", help="Prefix for output shares")

    # Combine
    combine_parser = subparsers.add_parser("combine", help="Digitally combine 2 shares")
    combine_parser.add_argument("share1", help="First share PNG")
    combine_parser.add_argument("share2", help="Second share PNG")
    combine_parser.add_argument("--out", default="revealed.png", help="Output filename")

    args = parser.parse_args()

    if args.command == "split":
        try:
            split_image(args.image, args.out)
        except Exception as e:
            print(f"Error: {e}")
            if "PIL" in str(e):
                print("Suggestion: pip install Pillow")

    elif args.command == "combine":
        try:
            combine_shares(args.share1, args.share2, args.out)
        except Exception as e:
            print(f"Error: {e}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
