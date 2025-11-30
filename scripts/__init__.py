"""
SAGE FILES - YouTube Automation Scripts
"""

from .voiceover_free import FreeVoiceGenerator, generate_voiceover
from .visual_cue_parser import VisualCueParser, VisualCue, VisualType
from .smart_video_maker import SmartVideoMaker, create_video
from .stock_media import StockMediaDownloader
from .humanizer import MetadataHumanizer, ScheduleHumanizer, ScriptHumanizer

__all__ = [
    'FreeVoiceGenerator',
    'generate_voiceover',
    'VisualCueParser',
    'VisualCue',
    'VisualType',
    'SmartVideoMaker',
    'create_video',
    'StockMediaDownloader',
    'MetadataHumanizer',
    'ScheduleHumanizer',
    'ScriptHumanizer',
]

