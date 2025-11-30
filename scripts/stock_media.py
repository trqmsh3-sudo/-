"""
SAGE FILES - Stock Media Downloader
Downloads B-roll and images from Pexels API
"""

import os
import re
import requests
from pathlib import Path
from typing import List, Optional


class StockMediaDownloader:
    """Download stock media from Pexels"""
    
    PEXELS_API_URL = "https://api.pexels.com/videos/search"
    PEXELS_PHOTOS_URL = "https://api.pexels.com/v1/search"
    
    def __init__(self, api_key: str = None):
        """
        Initialize downloader
        
        Args:
            api_key: Pexels API key (or reads from config/pexels_key.txt)
        """
        self.api_key = api_key or self._load_api_key()
        if not self.api_key:
            raise ValueError("Pexels API key not found! Create config/pexels_key.txt with your key.")
        
        self.headers = {"Authorization": self.api_key}
        print(f"📥 Stock Media Downloader initialized")
    
    def _load_api_key(self) -> Optional[str]:
        """Load API key from config file"""
        key_paths = [
            "config/pexels_key.txt",
            "../config/pexels_key.txt",
            "pexels_key.txt"
        ]
        
        for path in key_paths:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    return f.read().strip()
        
        # Try environment variable
        return os.environ.get('PEXELS_API_KEY')
    
    def search_videos(self, query: str, per_page: int = 15, orientation: str = "landscape") -> List[dict]:
        """
        Search for videos on Pexels
        
        Args:
            query: Search term
            per_page: Number of results
            orientation: landscape, portrait, or square
        
        Returns:
            List of video data dictionaries
        """
        params = {
            "query": query,
            "per_page": per_page,
            "orientation": orientation
        }
        
        try:
            response = requests.get(self.PEXELS_API_URL, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("videos", [])
        except Exception as e:
            print(f"   ⚠️ Error searching videos: {e}")
            return []
    
    def search_photos(self, query: str, per_page: int = 10, orientation: str = "landscape") -> List[dict]:
        """
        Search for photos on Pexels
        
        Args:
            query: Search term
            per_page: Number of results
            orientation: landscape, portrait, or square
        
        Returns:
            List of photo data dictionaries
        """
        params = {
            "query": query,
            "per_page": per_page,
            "orientation": orientation
        }
        
        try:
            response = requests.get(self.PEXELS_PHOTOS_URL, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("photos", [])
        except Exception as e:
            print(f"   ⚠️ Error searching photos: {e}")
            return []
    
    def download_video(self, video_data: dict, output_path: str, quality: str = "hd") -> Optional[str]:
        """
        Download a video file
        
        Args:
            video_data: Video data from search results
            output_path: Where to save the file
            quality: hd, sd, or uhd
        
        Returns:
            Path to downloaded file or None if failed
        """
        # Find the right quality file
        video_files = video_data.get("video_files", [])
        
        # Sort by quality preference
        quality_order = {"uhd": 3, "hd": 2, "sd": 1}
        target_quality = quality_order.get(quality, 2)
        
        best_file = None
        best_score = -1
        
        for vf in video_files:
            q = vf.get("quality", "").lower()
            score = quality_order.get(q, 0)
            
            # Prefer the target quality, but accept others
            if score == target_quality:
                best_file = vf
                break
            elif score > best_score:
                best_file = vf
                best_score = score
        
        if not best_file:
            print(f"   ⚠️ No suitable video file found")
            return None
        
        # Download
        try:
            url = best_file.get("link")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return output_path
        except Exception as e:
            print(f"   ⚠️ Error downloading video: {e}")
            return None
    
    def download_photo(self, photo_data: dict, output_path: str, size: str = "large") -> Optional[str]:
        """
        Download a photo file
        
        Args:
            photo_data: Photo data from search results
            output_path: Where to save the file
            size: original, large2x, large, medium, small, portrait, landscape, tiny
        
        Returns:
            Path to downloaded file or None if failed
        """
        src = photo_data.get("src", {})
        url = src.get(size) or src.get("large") or src.get("original")
        
        if not url:
            print(f"   ⚠️ No suitable photo URL found")
            return None
        
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return output_path
        except Exception as e:
            print(f"   ⚠️ Error downloading photo: {e}")
            return None
    
    def download_for_script(self, script_path: str, output_dir: str = "04_Archive/raw_footage",
                           max_videos: int = 80, max_photos: int = 20) -> dict:
        """
        Download media for a script based on keywords
        
        Args:
            script_path: Path to the script file
            output_dir: Base output directory
            max_videos: Maximum videos to download
            max_photos: Maximum photos to download
        
        Returns:
            Dictionary with download statistics
        """
        # Read script
        with open(script_path, 'r', encoding='utf-8') as f:
            script_text = f.read()
        
        # Extract topic from filename
        topic_slug = Path(script_path).stem.replace('_script', '').replace('_', ' ')
        safe_topic = re.sub(r'[^\w\s-]', '', topic_slug).lower().replace(' ', '_')
        
        # Create output directories
        videos_dir = os.path.join(output_dir, safe_topic, "videos")
        images_dir = os.path.join(output_dir, safe_topic, "images")
        os.makedirs(videos_dir, exist_ok=True)
        os.makedirs(images_dir, exist_ok=True)
        
        print(f"\n📥 Downloading media for: {topic_slug}")
        print(f"   Output: {output_dir}/{safe_topic}/")
        
        # Extract keywords from script
        keywords = self._extract_keywords(script_text, topic_slug)
        print(f"   Keywords: {', '.join(keywords[:10])}...")
        
        stats = {"videos": 0, "photos": 0, "failed": 0}
        
        # Download videos
        print(f"\n📹 Downloading videos...")
        video_count = 0
        
        for keyword in keywords:
            if video_count >= max_videos:
                break
            
            videos = self.search_videos(keyword, per_page=5)
            
            for i, video in enumerate(videos):
                if video_count >= max_videos:
                    break
                
                filename = f"{video_count:02d}_{keyword.replace(' ', '_')[:30]}.mp4"
                output_path = os.path.join(videos_dir, filename)
                
                if os.path.exists(output_path):
                    video_count += 1
                    continue
                
                print(f"   [{video_count+1}/{max_videos}] {keyword}...")
                result = self.download_video(video, output_path)
                
                if result:
                    stats["videos"] += 1
                    video_count += 1
                else:
                    stats["failed"] += 1
        
        # Download photos
        print(f"\n🖼️ Downloading photos...")
        photo_count = 0
        
        for keyword in keywords[:10]:  # Fewer photo keywords
            if photo_count >= max_photos:
                break
            
            photos = self.search_photos(keyword, per_page=3)
            
            for photo in photos:
                if photo_count >= max_photos:
                    break
                
                filename = f"{photo_count:02d}_{keyword.replace(' ', '_')[:30]}.jpg"
                output_path = os.path.join(images_dir, filename)
                
                if os.path.exists(output_path):
                    photo_count += 1
                    continue
                
                print(f"   [{photo_count+1}/{max_photos}] {keyword}...")
                result = self.download_photo(photo, output_path)
                
                if result:
                    stats["photos"] += 1
                    photo_count += 1
                else:
                    stats["failed"] += 1
        
        print(f"\n✅ Download complete!")
        print(f"   Videos: {stats['videos']}")
        print(f"   Photos: {stats['photos']}")
        print(f"   Failed: {stats['failed']}")
        
        return stats
    
    def _extract_keywords(self, script_text: str, topic: str) -> List[str]:
        """Extract search keywords from script"""
        # Base keywords from topic
        keywords = [topic]
        
        # Common documentary B-roll terms
        generic_terms = [
            "technology office", "business meeting", "data visualization",
            "code programming", "smartphone usage", "social media",
            "city skyline", "modern architecture", "people working",
            "digital transformation", "startup office", "stock market",
            "server room", "artificial intelligence", "machine learning"
        ]
        
        # Extract specific terms from script
        # Look for company names, technologies, etc.
        tech_terms = re.findall(r'\b(TikTok|Facebook|Google|Apple|Microsoft|Amazon|Netflix|YouTube|Instagram|Twitter|ByteDance|algorithm|AI|app|smartphone|social media|viral|growth|billion|million)\b', script_text, re.IGNORECASE)
        
        # Add unique terms
        seen = set()
        for term in tech_terms:
            term_lower = term.lower()
            if term_lower not in seen:
                keywords.append(term_lower)
                seen.add(term_lower)
        
        # Add generic terms
        keywords.extend(generic_terms)
        
        # Remove duplicates while preserving order
        unique_keywords = []
        seen = set()
        for kw in keywords:
            if kw.lower() not in seen:
                unique_keywords.append(kw)
                seen.add(kw.lower())
        
        return unique_keywords


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Download stock media for a script")
    parser.add_argument("--script", required=True, help="Path to script file")
    parser.add_argument("--output", default="04_Archive/raw_footage", help="Output directory")
    parser.add_argument("--max-videos", type=int, default=80, help="Maximum videos to download")
    parser.add_argument("--max-photos", type=int, default=20, help="Maximum photos to download")
    
    args = parser.parse_args()
    
    downloader = StockMediaDownloader()
    downloader.download_for_script(args.script, args.output, args.max_videos, args.max_photos)

