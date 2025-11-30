"""
SAGE FILES - Visual Cue Parser
Analyzes scripts and generates visual cues for video editing
"""

import re
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum


class VisualType(Enum):
    BROLL = "broll"
    LOGO = "logo"
    TEXT = "text"
    IMAGE = "image"
    SCREENSHOT = "screenshot"


@dataclass
class VisualCue:
    """Represents a visual element to show at a specific time"""
    timestamp: float          # When to show (seconds)
    duration: float           # How long to show
    visual_type: VisualType   # Type of visual
    content: str              # Search term, logo name, or text to display
    priority: int = 1         # Higher = more important (1-5)
    source_text: str = ""     # The script text that triggered this cue


class VisualCueParser:
    """Parse scripts and extract visual cues"""
    
    # Logo triggers - keywords that should show company logos
    LOGO_TRIGGERS = {
        'tiktok': 'tiktok.png',
        'bytedance': 'bytedance.png',
        'facebook': 'facebook.png',
        'meta': 'meta.png',
        'instagram': 'instagram.png',
        'youtube': 'youtube.png',
        'google': 'google.png',
        'apple': 'apple.png',
        'microsoft': 'microsoft.png',
        'amazon': 'amazon.png',
        'netflix': 'netflix.png',
        'twitter': 'twitter.png',
        'x.com': 'twitter.png',
        'tesla': 'tesla.png',
        'nvidia': 'nvidia.png',
        'openai': 'openai.png',
        'uber': 'uber.png',
        'wework': 'wework.png',
        'theranos': 'theranos.png',
        'ftx': 'ftx.png',
        'nokia': 'nokia.png',
        'spotify': 'spotify.png',
        'snapchat': 'snapchat.png',
        'linkedin': 'linkedin.png',
        'reddit': 'reddit.png',
        'discord': 'discord.png',
        'twitch': 'twitch.png',
        'airbnb': 'airbnb.png',
        'samsung': 'samsung.png',
        'huawei': 'huawei.png',
    }
    
    # Number patterns that should be shown as text overlays
    NUMBER_PATTERNS = [
        r'\$[\d,.]+\s*(billion|million|trillion|B|M|K)?',  # Money
        r'[\d,.]+\s*(billion|million|trillion|percent|%)',  # Large numbers
        r'\d{4}',  # Years
        r'#\d+',   # Rankings
    ]
    
    # Context keywords for B-roll searches
    CONTEXT_BROLL = {
        'algorithm': ['code on screen', 'data visualization', 'machine learning graphics'],
        'addiction': ['person scrolling phone', 'teenager on phone dark room', 'worried teenager'],
        'growth': ['stock market charts', 'growth chart', 'business meeting'],
        'china': ['Beijing skyline', 'China flag', 'Chinese tech office'],
        'government': ['US Capitol building', 'government hearing', 'politician speaking'],
        'brain': ['brain scan', 'neural network', 'brain dopamine visualization'],
        'phone': ['smartphone screen', 'finger scrolling phone', 'crowd using phones'],
        'money': ['money counting', 'stock market', 'business charts'],
        'data': ['server room', 'data center', 'digital data visualization'],
        'social media': ['social media apps', 'smartphone notifications', 'people on phones'],
        'startup': ['startup office', 'tech office modern', 'business meeting'],
        'viral': ['viral videos montage', 'trending content', 'social media feed'],
        'privacy': ['surveillance cameras', 'digital eye', 'data being recorded'],
        'mental health': ['mental health statistics', 'worried teenager', 'hospital medical'],
        'competition': ['comparison chart', 'apps comparison', 'business competition'],
        'user': ['person using phone', 'young people using phones', 'crowd of people using phones'],
        'download': ['app store', 'download button', 'smartphone app interface'],
        'scroll': ['infinite scroll animation', 'finger scrolling phone', 'smartphone feed'],
        'watch': ['clock time lapse', 'timer stopwatch', 'person watching screen'],
        'dopamine': ['brain dopamine visualization', 'slot machine spinning', 'reward graphics'],
    }
    
    def __init__(self, words_per_minute: float = 150):
        """
        Initialize parser
        
        Args:
            words_per_minute: Average speaking rate for timing calculations
        """
        self.wpm = words_per_minute
        self.seconds_per_word = 60 / words_per_minute
    
    def parse_script(self, script_text: str) -> List[VisualCue]:
        """
        Parse a script and extract visual cues
        
        Args:
            script_text: The full script text
        
        Returns:
            List of VisualCue objects sorted by timestamp
        """
        cues = []
        
        # Clean the script
        clean_script = self._clean_script(script_text)
        words = clean_script.split()
        total_words = len(words)
        
        print(f"📝 Parsing script ({total_words} words)...")
        
        # Process each word and its context
        for i, word in enumerate(words):
            timestamp = i * self.seconds_per_word
            context = ' '.join(words[max(0, i-5):min(len(words), i+5)])
            
            # Check for logo triggers
            word_lower = word.lower().strip('.,!?":;()[]')
            if word_lower in self.LOGO_TRIGGERS:
                cues.append(VisualCue(
                    timestamp=timestamp,
                    duration=3.0,
                    visual_type=VisualType.LOGO,
                    content=self.LOGO_TRIGGERS[word_lower],
                    priority=4,
                    source_text=context
                ))
            
            # Check for number patterns (text overlays)
            for pattern in self.NUMBER_PATTERNS:
                match = re.search(pattern, context, re.IGNORECASE)
                if match and abs(context.find(match.group()) - context.find(word)) < 20:
                    cues.append(VisualCue(
                        timestamp=timestamp,
                        duration=2.5,
                        visual_type=VisualType.TEXT,
                        content=match.group(),
                        priority=3,
                        source_text=context
                    ))
                    break
            
            # Check for context-based B-roll
            for keyword, broll_terms in self.CONTEXT_BROLL.items():
                if keyword in context.lower():
                    import random
                    cues.append(VisualCue(
                        timestamp=timestamp,
                        duration=3.0,
                        visual_type=VisualType.BROLL,
                        content=random.choice(broll_terms),
                        priority=2,
                        source_text=context
                    ))
                    break
        
        # Parse explicit [VISUAL CUE] markers
        explicit_cues = self._parse_explicit_cues(script_text)
        cues.extend(explicit_cues)
        
        # Remove duplicates and sort
        cues = self._deduplicate_cues(cues)
        cues.sort(key=lambda x: x.timestamp)
        
        # Ensure visual density
        cues = self._ensure_visual_density(cues, total_words * self.seconds_per_word)
        
        print(f"✅ Generated {len(cues)} visual cues")
        return cues
    
    def _clean_script(self, script_text: str) -> str:
        """Remove markers and clean script for word counting"""
        clean = re.sub(r'\[.*?\]', '', script_text)
        clean = re.sub(r'\(.*?\)', '', clean)
        clean = re.sub(r'\s+', ' ', clean)
        return clean.strip()
    
    def _parse_explicit_cues(self, script_text: str) -> List[VisualCue]:
        """Parse [VISUAL CUE: ...] markers in the script"""
        cues = []
        pattern = r'\[VISUAL(?:\s+CUE)?:\s*([^\]]+)\]'
        
        # Find position of each marker
        clean_before = ""
        for match in re.finditer(pattern, script_text, re.IGNORECASE):
            # Calculate timestamp based on words before this marker
            text_before = script_text[:match.start()]
            clean_before = self._clean_script(text_before)
            word_count = len(clean_before.split()) if clean_before else 0
            timestamp = word_count * self.seconds_per_word
            
            content = match.group(1).strip()
            
            # Determine visual type from content
            visual_type = VisualType.BROLL
            if any(logo in content.lower() for logo in self.LOGO_TRIGGERS):
                visual_type = VisualType.LOGO
            elif content.startswith('"') or content.startswith("'"):
                visual_type = VisualType.TEXT
            
            cues.append(VisualCue(
                timestamp=timestamp,
                duration=3.0,
                visual_type=visual_type,
                content=content,
                priority=5,  # Explicit cues have highest priority
                source_text=content
            ))
        
        return cues
    
    def _deduplicate_cues(self, cues: List[VisualCue]) -> List[VisualCue]:
        """Remove duplicate cues that are too close together"""
        if not cues:
            return cues
        
        cues.sort(key=lambda x: (x.timestamp, -x.priority))
        result = [cues[0]]
        
        for cue in cues[1:]:
            last = result[-1]
            # Skip if same type and within 2 seconds
            if (cue.visual_type == last.visual_type and 
                abs(cue.timestamp - last.timestamp) < 2.0):
                # Keep the higher priority one
                if cue.priority > last.priority:
                    result[-1] = cue
            else:
                result.append(cue)
        
        return result
    
    def _ensure_visual_density(self, cues: List[VisualCue], total_duration: float) -> List[VisualCue]:
        """Ensure there are no long gaps without visuals"""
        MAX_GAP = 4.0  # Maximum seconds without a visual change
        
        if not cues:
            return cues
        
        result = list(cues)
        
        # Check for gaps and fill with generic B-roll
        generic_broll = [
            'digital transformation', 'tech office', 'data visualization',
            'business meeting', 'cityscape', 'abstract technology'
        ]
        
        i = 0
        while i < len(result) - 1:
            gap = result[i + 1].timestamp - (result[i].timestamp + result[i].duration)
            if gap > MAX_GAP:
                # Insert filler B-roll
                import random
                filler = VisualCue(
                    timestamp=result[i].timestamp + result[i].duration + 0.5,
                    duration=min(3.0, gap - 1.0),
                    visual_type=VisualType.BROLL,
                    content=random.choice(generic_broll),
                    priority=1,
                    source_text="[auto-generated filler]"
                )
                result.insert(i + 1, filler)
            i += 1
        
        # Check gap at the end
        if result:
            last_end = result[-1].timestamp + result[-1].duration
            if total_duration - last_end > MAX_GAP:
                import random
                result.append(VisualCue(
                    timestamp=last_end + 0.5,
                    duration=min(3.0, total_duration - last_end - 1.0),
                    visual_type=VisualType.BROLL,
                    content=random.choice(generic_broll),
                    priority=1,
                    source_text="[auto-generated filler]"
                ))
        
        return result
    
    def get_timeline(self, cues: List[VisualCue], total_duration: float) -> List[Dict]:
        """
        Create a timeline of visual segments
        
        Args:
            cues: List of visual cues
            total_duration: Total video duration in seconds
        
        Returns:
            List of timeline segments with start, end, and visual info
        """
        if not cues:
            return []
        
        timeline = []
        cues_sorted = sorted(cues, key=lambda x: x.timestamp)
        
        for i, cue in enumerate(cues_sorted):
            # Determine end time
            if i < len(cues_sorted) - 1:
                end_time = min(cue.timestamp + cue.duration, cues_sorted[i + 1].timestamp)
            else:
                end_time = min(cue.timestamp + cue.duration, total_duration)
            
            timeline.append({
                'start': cue.timestamp,
                'end': end_time,
                'type': cue.visual_type.value,
                'content': cue.content,
                'priority': cue.priority
            })
        
        return timeline


def print_cue_summary(cues: List[VisualCue]):
    """Print a summary of visual cues"""
    print("\n📊 Visual Cue Summary:")
    
    by_type = {}
    for cue in cues:
        t = cue.visual_type.value
        by_type[t] = by_type.get(t, 0) + 1
    
    type_icons = {
        'broll': '📹',
        'logo': '🏷️',
        'text': '📝',
        'image': '🖼️',
        'screenshot': '📱'
    }
    
    for t, count in sorted(by_type.items()):
        icon = type_icons.get(t, '•')
        print(f"   {icon} {t}: {count}")


if __name__ == "__main__":
    # Test with sample script
    sample_script = """
    TikTok didn't just appear out of nowhere. In 2016, a Chinese company called ByteDance 
    launched an app called Douyin. Within a year, it had 100 million users.
    
    [VISUAL CUE: ByteDance headquarters]
    
    The algorithm was different. Unlike Facebook or YouTube, TikTok didn't need you to 
    follow anyone. It learned what you wanted by watching how long you watched.
    
    By 2020, TikTok had been downloaded over 2 billion times worldwide.
    """
    
    parser = VisualCueParser()
    cues = parser.parse_script(sample_script)
    print_cue_summary(cues)
    
    print("\n📋 Timeline:")
    for cue in cues[:10]:
        print(f"   {cue.timestamp:.1f}s - {cue.visual_type.value}: {cue.content}")

