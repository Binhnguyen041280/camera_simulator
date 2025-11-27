"""
Video Generator - FFmpeg wrapper for creating simulated camera videos
"""
import os
import subprocess
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class VideoGenerator:
    """Generates video files with realistic metadata for camera simulation"""

    def __init__(self):
        self._check_ffmpeg()

    def _check_ffmpeg(self):
        """Check if ffmpeg is available"""
        if shutil.which('ffmpeg') is None:
            logger.warning("FFmpeg not found! Video generation will fail.")
            logger.warning("Please install ffmpeg: sudo apt install ffmpeg (Linux) or brew install ffmpeg (Mac)")

    def generate_video(self, 
                      source_path: str, 
                      output_path: str, 
                      duration: float,
                      creation_time: datetime) -> bool:
        """
        Generate a video file with specific duration and metadata
        
        Args:
            source_path: Path to source video
            output_path: Path to output video
            duration: Duration in seconds (or minutes? logic below implies seconds usually, but let's check usage)
                      Actually usage in patterns implies minutes usually, but ffmpeg takes seconds or -t duration.
                      Let's assume the caller handles unit conversion or this takes what ffmpeg takes.
                      Looking at typical usage: -t {duration}
            creation_time: Creation timestamp for metadata
            
        Returns:
            bool: True if successful
        """
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Format timestamp for FFmpeg
            # FFmpeg expects: YYYY-MM-DD HH:MM:SS
            timestamp_str = creation_time.strftime("%Y-%m-%d %H:%M:%S")
            
            # Build command
            # -ss 0: Start from beginning (or random? For now start from 0)
            # -t duration: Duration to cut
            # -c copy: Stream copy (fast, no re-encoding)
            # -metadata creation_time: Set timestamp
            # -y: Overwrite output
            
            # Note: -c copy might not be accurate with -t if keyframes are sparse.
            # But for simulation speed, copy is best.
            
            cmd = [
                'ffmpeg',
                '-ss', '0',
                '-i', source_path,
                '-t', str(duration),
                '-c', 'copy',
                '-metadata', f'creation_time={timestamp_str}',
                '-y',
                output_path
            ]
            
            # Run silently
            result = subprocess.run(
                cmd, 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                return False
                
            # Update file system modification time to match creation_time
            # This is important for file watchers that check mtime
            ts = creation_time.timestamp()
            os.utime(output_path, (ts, ts))
            
            return True
            
        except Exception as e:
            logger.error(f"Error generating video: {e}")
            return False

    def get_video_duration(self, path: str) -> float:
        """Get duration of a video file in seconds"""
        try:
            cmd = [
                'ffprobe', 
                '-v', 'error', 
                '-show_entries', 'format=duration', 
                '-of', 'default=noprint_wrappers=1:nokey=1', 
                path
            ]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            return float(result.stdout.strip())
        except Exception:
            return 0.0
