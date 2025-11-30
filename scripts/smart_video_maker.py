"""
SAGE FILES - Smart Video Maker
Creates professional documentary-style videos with synchronized visuals
"""

import os
import re
import random
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path

from moviepy import (
    VideoFileClip, AudioFileClip, ImageClip, TextClip,
    CompositeVideoClip, ColorClip, concatenate_videoclips
)
from PIL import Image, ImageDraw, ImageFont
import numpy as np

try:
    from visual_cue_parser import VisualCueParser, VisualCue, VisualType, print_cue_summary
except ImportError:
    from .visual_cue_parser import VisualCueParser, VisualCue, VisualType, print_cue_summary


# === CONFIGURATION ===
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
FPS = 30

MIN_CLIP_DURATION = 2.0
MAX_CLIP_DURATION = 4.0
TARGET_CLIP_DURATION = 3.0

# Visual mix targets (percentages)
VISUAL_MIX = {
    'broll': 60,
    'logo': 15,
    'text': 15,
    'image': 5,
    'screenshot': 5,
}

# Colors
COLORS = {
    'background': (15, 15, 20),
    'accent': (0, 150, 255),
    'text': (255, 255, 255),
    'text_shadow': (0, 0, 0),
    'gradient_top': (20, 20, 30),
    'gradient_bottom': (5, 5, 10),
}


class SmartVideoMaker:
    """Creates professional videos with synchronized visuals"""
    
    def __init__(self, assets_dir: str = "assets", archive_dir: str = "04_Archive"):
        """
        Initialize the video maker
        
        Args:
            assets_dir: Directory containing logos, fonts, etc.
            archive_dir: Directory containing B-roll footage
        """
        self.assets_dir = Path(assets_dir)
        self.archive_dir = Path(archive_dir)
        self.logos_dir = self.assets_dir / "logos"
        self.broll_dir = self.archive_dir / "raw_footage"
        
        # Track used clips to avoid repetition
        self.used_clips = set()
        self.used_logos = set()
        self.last_visual_type = None
        self.last_broll_file = None
        self.last_logo_file = None
        
        print(f"🎬 Smart Video Maker initialized")
        print(f"   Logos: {self.logos_dir}")
        print(f"   B-roll: {self.broll_dir}")
    
    def create_gradient_background(self, duration: float) -> ColorClip:
        """Create a gradient background clip"""
        # Create gradient image
        img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT))
        draw = ImageDraw.Draw(img)
        
        for y in range(VIDEO_HEIGHT):
            ratio = y / VIDEO_HEIGHT
            r = int(COLORS['gradient_top'][0] * (1 - ratio) + COLORS['gradient_bottom'][0] * ratio)
            g = int(COLORS['gradient_top'][1] * (1 - ratio) + COLORS['gradient_bottom'][1] * ratio)
            b = int(COLORS['gradient_top'][2] * (1 - ratio) + COLORS['gradient_bottom'][2] * ratio)
            draw.line([(0, y), (VIDEO_WIDTH, y)], fill=(r, g, b))
        
        return ImageClip(np.array(img)).with_duration(duration)
    
    def create_text_overlay(self, text: str, duration: float) -> CompositeVideoClip:
        """Create a text overlay with gradient background"""
        # Background
        bg = self.create_gradient_background(duration)
        
        # Create text image with PIL (more reliable than TextClip)
        img = Image.new('RGBA', (VIDEO_WIDTH, VIDEO_HEIGHT), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Try to load a font, fall back to default
        font_size = 80
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
            except:
                font = ImageFont.load_default()
        
        # Calculate text position (centered)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (VIDEO_WIDTH - text_width) // 2
        y = (VIDEO_HEIGHT - text_height) // 2
        
        # Draw shadow
        shadow_offset = 3
        draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=COLORS['text_shadow'])
        
        # Draw text
        draw.text((x, y), text, font=font, fill=COLORS['text'])
        
        text_clip = ImageClip(np.array(img)).with_duration(duration)
        
        return CompositeVideoClip([bg, text_clip])
    
    def create_logo_clip(self, logo_name: str, duration: float) -> CompositeVideoClip:
        """Create a logo clip on gradient background"""
        # Check if we just showed this logo
        if logo_name == self.last_logo_file:
            # Return a different visual instead
            return self.create_gradient_background(duration)
        
        self.last_logo_file = logo_name
        
        # Background
        bg = self.create_gradient_background(duration)
        
        # Find logo file
        logo_path = self.logos_dir / logo_name
        if not logo_path.exists():
            # Try without extension
            for ext in ['.png', '.jpg', '.jpeg', '.webp']:
                test_path = self.logos_dir / f"{logo_name.replace('.png', '')}{ext}"
                if test_path.exists():
                    logo_path = test_path
                    break
        
        if not logo_path.exists():
            print(f"   ⚠️ Logo not found: {logo_name}")
            return bg
        
        try:
            # Load and resize logo
            logo_img = Image.open(logo_path).convert('RGBA')
            
            # Resize to fit (max 400px)
            max_size = 400
            ratio = min(max_size / logo_img.width, max_size / logo_img.height)
            new_size = (int(logo_img.width * ratio), int(logo_img.height * ratio))
            logo_img = logo_img.resize(new_size, Image.Resampling.LANCZOS)
            
            # Create centered logo on transparent background
            full_img = Image.new('RGBA', (VIDEO_WIDTH, VIDEO_HEIGHT), (0, 0, 0, 0))
            x = (VIDEO_WIDTH - logo_img.width) // 2
            y = (VIDEO_HEIGHT - logo_img.height) // 2
            full_img.paste(logo_img, (x, y), logo_img)
            
            logo_clip = ImageClip(np.array(full_img)).with_duration(duration)
            
            return CompositeVideoClip([bg, logo_clip])
        
        except Exception as e:
            print(f"   ⚠️ Error loading logo {logo_name}: {e}")
            return bg
    
    def load_broll_clip(self, search_term: str, duration: float, topic_folder: str = None) -> VideoFileClip:
        """
        Load a B-roll clip matching the search term
        
        Args:
            search_term: Keywords to match
            duration: Target duration
            topic_folder: Specific folder to search in
        """
        # Find B-roll directory
        if topic_folder:
            broll_path = self.broll_dir / topic_folder / "videos"
        else:
            # Search all topic folders
            broll_path = self.broll_dir
        
        if not broll_path.exists():
            print(f"   ⚠️ B-roll path not found: {broll_path}")
            return self.create_gradient_background(duration)
        
        # Find matching clips
        search_words = search_term.lower().split()
        matching_clips = []
        
        for video_file in broll_path.rglob("*.mp4"):
            filename = video_file.stem.lower()
            # Check if any search word matches
            if any(word in filename for word in search_words):
                # Skip if we just used this clip
                if str(video_file) != self.last_broll_file:
                    matching_clips.append(video_file)
        
        # If no matches, get any clip we haven't used recently
        if not matching_clips:
            all_clips = list(broll_path.rglob("*.mp4"))
            matching_clips = [c for c in all_clips if str(c) != self.last_broll_file]
            if not matching_clips:
                matching_clips = all_clips
        
        if not matching_clips:
            print(f"   ⚠️ No B-roll found for: {search_term}")
            return self.create_gradient_background(duration)
        
        # Select a random matching clip
        clip_path = random.choice(matching_clips)
        self.last_broll_file = str(clip_path)
        
        try:
            clip = VideoFileClip(str(clip_path))
            
            # Trim to duration
            if clip.duration > duration:
                # Random start point
                max_start = clip.duration - duration
                start = random.uniform(0, max_start) if max_start > 0 else 0
                clip = clip.subclipped(start, start + duration)
            elif clip.duration < duration:
                # Loop if too short
                clip = clip.with_duration(duration)
            
            # Resize to fit
            clip = clip.resized((VIDEO_WIDTH, VIDEO_HEIGHT))
            
            # Random subtle effect
            effects = ['none', 'none', 'none', 'slow']  # 25% chance of slow motion
            effect = random.choice(effects)
            if effect == 'slow':
                clip = clip.with_speed_scaled(0.8)
                clip = clip.with_duration(duration)
            
            return clip
        
        except Exception as e:
            print(f"   ⚠️ Error loading B-roll {clip_path}: {e}")
            return self.create_gradient_background(duration)
    
    def create_video(self, 
                     script_path: str,
                     audio_path: str,
                     output_dir: str = "01_Pending_Approval",
                     title: str = None,
                     draft_mode: bool = False) -> str:
        """
        Create a complete video from script and audio
        
        Args:
            script_path: Path to the script file
            audio_path: Path to the voiceover audio
            output_dir: Where to save the video
            title: Video title (for filename)
            draft_mode: If True, render at 720p for speed
        
        Returns:
            Path to the created video
        """
        print("\n" + "=" * 60)
        print("🎬 SMART VIDEO MAKER")
        print("=" * 60)
        
        # Load audio
        print(f"\n🎙️  Loading audio...")
        audio = AudioFileClip(audio_path)
        total_duration = audio.duration
        print(f"   Duration: {total_duration:.1f}s ({total_duration/60:.1f} min)")
        
        # Parse script for visual cues
        print(f"\n📝 Parsing script...")
        with open(script_path, 'r', encoding='utf-8') as f:
            script_text = f.read()
        
        parser = VisualCueParser()
        cues = parser.parse_script(script_text)
        print_cue_summary(cues)
        
        # Determine topic folder for B-roll
        topic_folder = None
        for folder in self.broll_dir.iterdir():
            if folder.is_dir():
                topic_folder = folder.name
                break
        
        # Load B-roll clips
        print(f"\n📹 Loading B-roll clips...")
        broll_files = list(self.broll_dir.rglob("*.mp4"))
        print(f"   Found {len(broll_files)} clips")
        
        # Create video segments
        print(f"\n🎬 Creating segments...")
        segments = []
        timeline = parser.get_timeline(cues, total_duration)
        
        # Reset tracking
        self.used_clips = set()
        self.used_logos = set()
        self.last_visual_type = None
        self.last_broll_file = None
        self.last_logo_file = None
        
        # Fill gaps in timeline
        filled_timeline = self._fill_timeline_gaps(timeline, total_duration)
        
        for i, segment in enumerate(filled_timeline):
            start = segment['start']
            end = segment['end']
            duration = end - start
            
            if duration <= 0:
                continue
            
            visual_type = segment['type']
            content = segment['content']
            
            # Progress indicator
            progress = (i + 1) / len(filled_timeline) * 100
            print(f"   [{progress:.1f}%] Segment {i+1}/{len(filled_timeline)}: {visual_type} - {content[:40]}...")
            
            # Create the appropriate clip type
            if visual_type == 'logo':
                clip = self.create_logo_clip(content, duration)
            elif visual_type == 'text':
                clip = self.create_text_overlay(content, duration)
            elif visual_type == 'broll':
                clip = self.load_broll_clip(content, duration, topic_folder)
            else:
                clip = self.create_gradient_background(duration)
            
            # Set timing
            clip = clip.with_start(start)
            segments.append(clip)
            
            self.last_visual_type = visual_type
        
        print(f"   ✅ Created {len(segments)} segments")
        
        # Composite all segments
        print(f"\n⏳ Assembling video...")
        
        # Create base video
        base = self.create_gradient_background(total_duration)
        all_clips = [base] + segments
        
        video = CompositeVideoClip(all_clips, size=(VIDEO_WIDTH, VIDEO_HEIGHT))
        video = video.with_audio(audio)
        video = video.with_duration(total_duration)
        
        # Generate output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if title:
            safe_title = re.sub(r'[^\w\s-]', '', title).lower().replace(' ', '_')
            filename = f"{timestamp}_{safe_title}_SMART.mp4"
        else:
            filename = f"{timestamp}_video_SMART.mp4"
        
        output_path = os.path.join(output_dir, filename)
        os.makedirs(output_dir, exist_ok=True)
        
        # Render settings
        if draft_mode:
            print(f"\n⏳ Exporting DRAFT (720p)...")
            video = video.resized(height=720)
        else:
            print(f"\n⏳ Exporting video (this may take a while)...")
        
        video.write_videofile(
            output_path,
            fps=FPS,
            codec='libx264',
            audio_codec='aac',
            preset='medium' if draft_mode else 'slow',
            threads=4
        )
        
        # Cleanup
        video.close()
        audio.close()
        for seg in segments:
            try:
                seg.close()
            except:
                pass
        
        print(f"\n" + "=" * 60)
        print(f"✅ VIDEO CREATED: {output_path}")
        print("=" * 60)
        
        return output_path
    
    def _fill_timeline_gaps(self, timeline: List[Dict], total_duration: float) -> List[Dict]:
        """Fill gaps in the timeline with B-roll"""
        if not timeline:
            # No cues - fill entire video with B-roll
            return [{
                'start': 0,
                'end': total_duration,
                'type': 'broll',
                'content': 'digital transformation',
                'priority': 1
            }]
        
        filled = []
        current_time = 0
        
        generic_broll = [
            'digital transformation', 'tech office', 'data visualization',
            'business meeting', 'cityscape', 'abstract technology',
            'code on screen', 'modern office', 'people working'
        ]
        
        for segment in sorted(timeline, key=lambda x: x['start']):
            # Fill gap before this segment
            if segment['start'] > current_time + 0.5:
                filled.append({
                    'start': current_time,
                    'end': segment['start'],
                    'type': 'broll',
                    'content': random.choice(generic_broll),
                    'priority': 1
                })
            
            filled.append(segment)
            current_time = segment['end']
        
        # Fill gap at the end
        if current_time < total_duration - 0.5:
            filled.append({
                'start': current_time,
                'end': total_duration,
                'type': 'broll',
                'content': random.choice(generic_broll),
                'priority': 1
            })
        
        return filled


def create_video(script_path: str, audio_path: str, title: str = None, 
                 output_dir: str = "01_Pending_Approval", draft: bool = False) -> str:
    """
    Convenience function to create a video
    
    Args:
        script_path: Path to script file
        audio_path: Path to voiceover audio
        title: Video title
        output_dir: Output directory
        draft: Use draft mode (720p, faster)
    
    Returns:
        Path to created video
    """
    maker = SmartVideoMaker()
    return maker.create_video(script_path, audio_path, output_dir, title, draft)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Create video from script and audio")
    parser.add_argument("--script", required=True, help="Path to script file")
    parser.add_argument("--audio", help="Path to audio file (optional, will generate if not provided)")
    parser.add_argument("--title", help="Video title")
    parser.add_argument("--output", default="01_Pending_Approval", help="Output directory")
    parser.add_argument("--draft", action="store_true", help="Draft mode (720p, faster)")
    parser.add_argument("--voice", default="andrew", help="Voice for TTS if generating audio")
    
    args = parser.parse_args()
    
    # Generate audio if not provided
    audio_path = args.audio
    if not audio_path:
        print("🎙️ Generating voiceover...")
        try:
            from voiceover_free import generate_voiceover
        except ImportError:
            from .voiceover_free import generate_voiceover
        audio_path = generate_voiceover(args.script, voice=args.voice, title=args.title)
    
    # Create video
    output = create_video(
        args.script,
        audio_path,
        args.title,
        args.output,
        args.draft
    )
    
    print(f"\n🎉 Done! Video saved to: {output}")

