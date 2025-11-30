"""
SAGE FILES - Logo Downloader
Downloads company logos from various sources
"""

import os
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO


# Companies and their logo sources
COMPANIES = {
    'tiktok': 'https://logo.clearbit.com/tiktok.com',
    'bytedance': 'https://logo.clearbit.com/bytedance.com',
    'facebook': 'https://logo.clearbit.com/facebook.com',
    'meta': 'https://logo.clearbit.com/meta.com',
    'instagram': 'https://logo.clearbit.com/instagram.com',
    'youtube': 'https://logo.clearbit.com/youtube.com',
    'google': 'https://logo.clearbit.com/google.com',
    'apple': 'https://logo.clearbit.com/apple.com',
    'microsoft': 'https://logo.clearbit.com/microsoft.com',
    'amazon': 'https://logo.clearbit.com/amazon.com',
    'netflix': 'https://logo.clearbit.com/netflix.com',
    'twitter': 'https://logo.clearbit.com/twitter.com',
    'tesla': 'https://logo.clearbit.com/tesla.com',
    'nvidia': 'https://logo.clearbit.com/nvidia.com',
    'openai': 'https://logo.clearbit.com/openai.com',
    'uber': 'https://logo.clearbit.com/uber.com',
    'wework': 'https://logo.clearbit.com/wework.com',
    'theranos': None,  # Company defunct, will create text logo
    'ftx': None,  # Company defunct
    'nokia': 'https://logo.clearbit.com/nokia.com',
    'spotify': 'https://logo.clearbit.com/spotify.com',
    'snapchat': 'https://logo.clearbit.com/snapchat.com',
    'linkedin': 'https://logo.clearbit.com/linkedin.com',
    'reddit': 'https://logo.clearbit.com/reddit.com',
    'discord': 'https://logo.clearbit.com/discord.com',
    'twitch': 'https://logo.clearbit.com/twitch.tv',
    'airbnb': 'https://logo.clearbit.com/airbnb.com',
    'samsung': 'https://logo.clearbit.com/samsung.com',
    'huawei': 'https://logo.clearbit.com/huawei.com',
}


def create_text_logo(name: str, output_path: str, size: int = 400):
    """Create a simple text-based logo"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Try to load a font
    font_size = size // 4
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()
    
    # Draw text centered
    text = name.upper()
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    # Draw shadow
    draw.text((x + 2, y + 2), text, font=font, fill=(50, 50, 50, 255))
    # Draw text
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
    
    img.save(output_path, 'PNG')
    print(f"   ✅ Created text logo: {name}")


def download_logo(name: str, url: str, output_path: str) -> bool:
    """Download a logo from URL"""
    if not url:
        return False
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Open and convert to RGBA
        img = Image.open(BytesIO(response.content))
        img = img.convert('RGBA')
        
        # Resize if too small
        if img.width < 200 or img.height < 200:
            ratio = max(200 / img.width, 200 / img.height)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        # Save
        img.save(output_path, 'PNG')
        print(f"   ✅ Downloaded: {name}")
        return True
    
    except Exception as e:
        print(f"   ⚠️ Failed to download {name}: {e}")
        return False


def download_all_logos(output_dir: str = "assets/logos"):
    """Download all company logos"""
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n🏷️ Downloading logos to {output_dir}/")
    print("=" * 50)
    
    stats = {"downloaded": 0, "created": 0, "failed": 0}
    
    for name, url in COMPANIES.items():
        output_path = os.path.join(output_dir, f"{name}.png")
        
        # Skip if already exists
        if os.path.exists(output_path):
            print(f"   ⏭️ Skipping {name} (already exists)")
            continue
        
        if url:
            success = download_logo(name, url, output_path)
            if success:
                stats["downloaded"] += 1
            else:
                # Create text logo as fallback
                create_text_logo(name, output_path)
                stats["created"] += 1
        else:
            # No URL, create text logo
            create_text_logo(name, output_path)
            stats["created"] += 1
    
    print("\n" + "=" * 50)
    print(f"✅ Done!")
    print(f"   Downloaded: {stats['downloaded']}")
    print(f"   Created: {stats['created']}")
    print(f"   Failed: {stats['failed']}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Download company logos")
    parser.add_argument("--output", default="assets/logos", help="Output directory")
    
    args = parser.parse_args()
    download_all_logos(args.output)

