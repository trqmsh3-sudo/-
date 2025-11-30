"""
SAGE FILES - Free Voiceover Generator
Uses Edge-TTS (Microsoft) for 100% free, high-quality text-to-speech
"""

import asyncio
import edge_tts
import os
from datetime import datetime


class FreeVoiceGenerator:
    """Generate voiceovers using Edge-TTS (free)"""
    
    # Recommended voices for documentary style
    VOICES = {
        'adam': 'en-US-AdamMultilingualNeural',      # Deep, authoritative
        'andrew': 'en-US-AndrewNeural',              # Natural, warm
        'brian': 'en-US-BrianNeural',                # Clear, professional
        'christopher': 'en-US-ChristopherNeural',    # Mature, trustworthy
        'eric': 'en-US-EricNeural',                  # Calm, measured
        'guy': 'en-US-GuyNeural',                    # Friendly, engaging
        'roger': 'en-US-RogerNeural',                # Deep, cinematic
        'steffan': 'en-US-SteffanNeural',            # Young, dynamic
    }
    
    def __init__(self, voice: str = 'andrew'):
        """
        Initialize the voice generator
        
        Args:
            voice: Voice name (adam, andrew, brian, etc.) or full voice ID
        """
        if voice.lower() in self.VOICES:
            self.voice = self.VOICES[voice.lower()]
        else:
            self.voice = voice
        
        print(f"🎙️ Voice Generator initialized with: {self.voice}")
    
    async def generate_async(self, text: str, output_path: str, rate: str = "+0%", pitch: str = "+0Hz") -> str:
        """
        Generate voiceover asynchronously
        
        Args:
            text: The text to convert to speech
            output_path: Where to save the audio file
            rate: Speech rate adjustment (e.g., "+10%", "-5%")
            pitch: Pitch adjustment (e.g., "+5Hz", "-10Hz")
        
        Returns:
            Path to the generated audio file
        """
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        
        # Create the TTS communicate object
        communicate = edge_tts.Communicate(text, self.voice, rate=rate, pitch=pitch)
        
        # Generate and save
        await communicate.save(output_path)
        
        print(f"✅ Voiceover saved to: {output_path}")
        return output_path
    
    def generate(self, text: str, output_path: str, rate: str = "+0%", pitch: str = "+0Hz") -> str:
        """
        Generate voiceover (synchronous wrapper)
        
        Args:
            text: The text to convert to speech
            output_path: Where to save the audio file
            rate: Speech rate adjustment
            pitch: Pitch adjustment
        
        Returns:
            Path to the generated audio file
        """
        return asyncio.run(self.generate_async(text, output_path, rate, pitch))
    
    @staticmethod
    async def list_voices(language: str = "en") -> list:
        """List available voices for a language"""
        voices = await edge_tts.list_voices()
        filtered = [v for v in voices if v['Locale'].startswith(language)]
        return filtered
    
    @staticmethod
    def print_voices(language: str = "en"):
        """Print available voices"""
        voices = asyncio.run(FreeVoiceGenerator.list_voices(language))
        print(f"\n🎤 Available {language} voices:\n")
        for v in voices:
            gender = "👨" if v['Gender'] == 'Male' else "👩"
            print(f"  {gender} {v['ShortName']}: {v['LocalName']}")


def generate_voiceover(script_path: str, output_dir: str = "04_Archive/audio", 
                       voice: str = "andrew", title: str = None) -> str:
    """
    Main function to generate voiceover from a script file
    
    Args:
        script_path: Path to the script text file
        output_dir: Directory to save the audio
        voice: Voice to use
        title: Optional title for the filename
    
    Returns:
        Path to the generated audio file
    """
    # Read script
    with open(script_path, 'r', encoding='utf-8') as f:
        script_text = f.read()
    
    # Clean script - remove visual cues and stage directions
    import re
    clean_text = re.sub(r'\[.*?\]', '', script_text)  # Remove [VISUAL CUE] markers
    clean_text = re.sub(r'\(.*?\)', '', clean_text)   # Remove (stage directions)
    clean_text = re.sub(r'\n{3,}', '\n\n', clean_text)  # Normalize line breaks
    clean_text = clean_text.strip()
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if title:
        safe_title = re.sub(r'[^\w\s-]', '', title).lower().replace(' ', '_')
        filename = f"{timestamp}_{safe_title}_voiceover.mp3"
    else:
        filename = f"{timestamp}_voiceover.mp3"
    
    output_path = os.path.join(output_dir, filename)
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate
    generator = FreeVoiceGenerator(voice)
    generator.generate(clean_text, output_path)
    
    return output_path


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate voiceover from script")
    parser.add_argument("--script", required=True, help="Path to script file")
    parser.add_argument("--output", default="04_Archive/audio", help="Output directory")
    parser.add_argument("--voice", default="andrew", help="Voice to use")
    parser.add_argument("--title", help="Title for the filename")
    parser.add_argument("--list-voices", action="store_true", help="List available voices")
    
    args = parser.parse_args()
    
    if args.list_voices:
        FreeVoiceGenerator.print_voices()
    else:
        output = generate_voiceover(args.script, args.output, args.voice, args.title)
        print(f"\n🎉 Done! Audio saved to: {output}")

