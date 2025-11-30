"""
SAGE FILES - Humanizer Module
Adds natural variation and imperfections to make content feel more human
"""

import random
import re
from datetime import datetime, timedelta
from typing import List, Tuple


class MetadataHumanizer:
    """Humanize video metadata to avoid AI detection patterns"""
    
    # Title variations
    TITLE_PREFIXES = [
        "", "", "",  # Most titles have no prefix
        "The ", "How ", "Why ", "What ",
    ]
    
    TITLE_SUFFIXES = [
        "", "", "", "",  # Most titles have no suffix
        " (Full Story)", " - Documentary", " | Deep Dive",
        " - The Truth", " Explained"
    ]
    
    # Description templates with variations
    DESCRIPTION_INTROS = [
        "In this video, we explore",
        "Today we're diving into",
        "Let's talk about",
        "This is the story of",
        "Ever wondered about",
        "Here's something fascinating:",
        "",  # Sometimes no intro
    ]
    
    # Emoji variations (use sparingly)
    EMOJIS = ["🔍", "📊", "💡", "🎯", "⚡", "🌟", "📈", "🔥", ""]
    
    def humanize_title(self, title: str) -> str:
        """Add subtle variations to a title"""
        # Randomly add prefix/suffix
        if random.random() < 0.2:
            title = random.choice(self.TITLE_PREFIXES) + title
        
        if random.random() < 0.15:
            title = title + random.choice(self.TITLE_SUFFIXES)
        
        # Occasionally adjust capitalization
        if random.random() < 0.1:
            title = title.title()
        
        return title
    
    def humanize_description(self, description: str, title: str = "") -> str:
        """Add natural variations to description"""
        lines = description.split('\n')
        result = []
        
        # Maybe add intro
        if random.random() < 0.4:
            intro = random.choice(self.DESCRIPTION_INTROS)
            if intro:
                result.append(intro + " " + title.lower() + ".\n")
        
        # Process lines with subtle changes
        for line in lines:
            # Random line breaks
            if random.random() < 0.1:
                result.append("")
            
            # Maybe add emoji (sparingly)
            if random.random() < 0.05:
                line = random.choice(self.EMOJIS) + " " + line
            
            result.append(line)
        
        # Random spacing at end
        if random.random() < 0.3:
            result.append("")
        
        return '\n'.join(result)
    
    def humanize_tags(self, tags: List[str]) -> List[str]:
        """Shuffle and vary tags"""
        # Shuffle order
        tags = list(tags)
        random.shuffle(tags)
        
        # Sometimes add/remove a tag
        if random.random() < 0.2 and len(tags) > 5:
            tags.pop(random.randint(0, len(tags) - 1))
        
        return tags
    
    def humanize_filename(self, filename: str) -> str:
        """Add natural variation to filenames"""
        # Sometimes use different separators
        if random.random() < 0.3:
            filename = filename.replace('_', '-')
        
        # Sometimes lowercase
        if random.random() < 0.2:
            filename = filename.lower()
        
        # Sometimes add version number
        if random.random() < 0.1:
            base, ext = filename.rsplit('.', 1)
            filename = f"{base}_v{random.randint(1,3)}.{ext}"
        
        return filename


class ScheduleHumanizer:
    """Create human-like publishing schedules"""
    
    def __init__(self, videos_per_week: int = 2):
        self.videos_per_week = videos_per_week
    
    def get_next_publish_time(self, last_publish: datetime = None) -> datetime:
        """Get a human-like next publish time"""
        if last_publish is None:
            last_publish = datetime.now()
        
        # Base interval (days between videos)
        base_interval = 7 / self.videos_per_week
        
        # Add randomness (-12 to +24 hours)
        random_hours = random.uniform(-12, 24)
        interval = timedelta(days=base_interval, hours=random_hours)
        
        next_time = last_publish + interval
        
        # Adjust to reasonable hours (10 AM - 8 PM)
        hour = random.randint(10, 20)
        minute = random.choice([0, 15, 30, 45, 5, 10, 20, 35, 50])
        
        next_time = next_time.replace(hour=hour, minute=minute, second=0)
        
        # Avoid weekends sometimes
        if next_time.weekday() >= 5 and random.random() < 0.6:
            # Move to Monday
            days_until_monday = 7 - next_time.weekday()
            next_time += timedelta(days=days_until_monday)
        
        return next_time
    
    def generate_schedule(self, num_videos: int, start_date: datetime = None) -> List[datetime]:
        """Generate a schedule for multiple videos"""
        if start_date is None:
            start_date = datetime.now()
        
        schedule = []
        current = start_date
        
        for _ in range(num_videos):
            next_time = self.get_next_publish_time(current)
            schedule.append(next_time)
            current = next_time
        
        return schedule


class ScriptHumanizer:
    """Add natural imperfections to scripts"""
    
    # Filler phrases that humans use
    FILLERS = [
        "you know,",
        "I mean,",
        "basically,",
        "actually,",
        "honestly,",
        "interestingly,",
        "look,",
        "here's the thing:",
    ]
    
    # Self-corrections
    CORRECTIONS = [
        ("was", "was... well, actually it was"),
        ("is", "is—or rather, was"),
        ("million", "million... no wait, billion"),
    ]
    
    # Personal asides
    ASIDES = [
        "(and this part really surprised me)",
        "(which is kind of wild when you think about it)",
        "(I had to double-check this)",
        "(stay with me here)",
    ]
    
    def add_natural_pauses(self, text: str) -> str:
        """Add pause markers for more natural speech"""
        # Add pauses after certain words
        pause_after = ['.', '?', '!', '—', ':']
        
        for char in pause_after:
            if random.random() < 0.3:
                text = text.replace(char + ' ', char + ' ... ')
        
        return text
    
    def add_filler_phrases(self, text: str, frequency: float = 0.05) -> str:
        """Occasionally add filler phrases"""
        sentences = text.split('. ')
        result = []
        
        for sentence in sentences:
            if random.random() < frequency and len(sentence) > 20:
                filler = random.choice(self.FILLERS)
                # Insert filler at beginning or after first few words
                words = sentence.split()
                if len(words) > 5:
                    insert_pos = random.randint(2, 4)
                    words.insert(insert_pos, filler)
                    sentence = ' '.join(words)
            result.append(sentence)
        
        return '. '.join(result)
    
    def add_personal_asides(self, text: str, frequency: float = 0.02) -> str:
        """Add occasional personal comments"""
        sentences = text.split('. ')
        result = []
        
        for sentence in sentences:
            result.append(sentence)
            if random.random() < frequency:
                result.append(random.choice(self.ASIDES))
        
        return '. '.join(result)
    
    def humanize_script(self, script: str, intensity: float = 0.5) -> str:
        """Apply humanization to a script"""
        # Scale frequency by intensity
        script = self.add_filler_phrases(script, frequency=0.05 * intensity)
        script = self.add_personal_asides(script, frequency=0.02 * intensity)
        
        return script


# Convenience functions
def humanize_metadata(title: str, description: str, tags: List[str]) -> Tuple[str, str, List[str]]:
    """Humanize all metadata at once"""
    h = MetadataHumanizer()
    return (
        h.humanize_title(title),
        h.humanize_description(description, title),
        h.humanize_tags(tags)
    )


def get_publish_schedule(num_videos: int, videos_per_week: int = 2) -> List[datetime]:
    """Get a human-like publish schedule"""
    h = ScheduleHumanizer(videos_per_week)
    return h.generate_schedule(num_videos)


if __name__ == "__main__":
    # Test humanization
    print("🧠 Testing Humanizer\n")
    
    # Test title
    title = "The Rise and Fall of TikTok"
    h = MetadataHumanizer()
    for _ in range(5):
        print(f"   Title: {h.humanize_title(title)}")
    
    # Test schedule
    print("\n📅 Sample Schedule:")
    schedule = get_publish_schedule(5)
    for i, dt in enumerate(schedule):
        print(f"   Video {i+1}: {dt.strftime('%A, %B %d at %I:%M %p')}")

