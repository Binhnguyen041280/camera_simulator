"""
Camera Simulator - Simulates a single camera recording behavior
"""
import os
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import logging

from video_generator import VideoGenerator
from patterns import create_pattern, RecordingEvent

logger = logging.getLogger(__name__)

class CameraSimulator:
    """Simulates a single camera's recording behavior"""

    def __init__(self, name: str, config: Dict, global_config: Dict):
        self.name = name
        self.config = config
        self.global_config = global_config
        self.output_folder = config.get('output_folder', f"output/{name}")
        self.source_video = config.get('source_video')
        self.pattern_type = config.get('pattern', 'continuous')
        self.pattern_config = config.get('config', {})
        
        self.generator = VideoGenerator()
        self.events: List[RecordingEvent] = []
        self.stop_flag = False
        self.stats = {'videos_created': 0, 'errors': 0}
        
        # Ensure output folder exists
        os.makedirs(self.output_folder, exist_ok=True)

    def generate_schedule(self, start_time: datetime, duration_hours: float):
        """Generate recording schedule for the simulation period"""
        end_time = start_time + timedelta(hours=duration_hours) if duration_hours > 0 else start_time + timedelta(days=365)
        
        logger.info(f"[{self.name}] Generating schedule from {start_time} to {end_time}")
        self.events = create_pattern(
            self.pattern_type, 
            self.pattern_config, 
            start_time, 
            end_time
        )
        logger.info(f"[{self.name}] Schedule generated: {len(self.events)} events")

    def run(self):
        """Run the simulation"""
        if not self.source_video or not os.path.exists(self.source_video):
            logger.error(f"[{self.name}] Source video not found: {self.source_video}")
            return

        logger.info(f"[{self.name}] Starting simulation...")
        
        use_real_time = self.pattern_config.get('use_real_time', False)
        
        for i, event in enumerate(self.events):
            if self.stop_flag:
                break
                
            # Wait until start time if real-time mode
            if use_real_time:
                now = datetime.now()
                if event.start_time > now:
                    wait_seconds = (event.start_time - now).total_seconds()
                    if wait_seconds > 0:
                        logger.info(f"[{self.name}] Waiting {wait_seconds:.1f}s for next event...")
                        time.sleep(wait_seconds)
            
            # Generate filename
            # Format: CameraName_YYYYMMDD_HHMMSS.mp4
            timestamp_str = event.start_time.strftime("%Y%m%d_%H%M%S")
            filename = f"{self.name}_{timestamp_str}.mp4"
            output_path = os.path.join(self.output_folder, filename)
            
            logger.info(f"[{self.name}] Creating video: {filename} ({event.duration_minutes:.1f}m)")
            
            # Generate video
            success = self.generator.generate_video(
                self.source_video,
                output_path,
                event.duration_minutes * 60, # Convert to seconds
                event.start_time
            )
            
            if success:
                self.stats['videos_created'] += 1
                logger.info(f"[{self.name}] ✓ Created: {filename}")
                self._cleanup_old_files()
            else:
                self.stats['errors'] += 1
                logger.error(f"[{self.name}] ✗ Failed to create: {filename}")
                
            # Small delay to prevent CPU spike in fast mode
            if not use_real_time:
                time.sleep(0.1)

    def _cleanup_old_files(self):
        """Cleanup old files if retention count is exceeded"""
        if not self.global_config.get('cleanup_old_files', True):
            return
            
        retention = self.global_config.get('retention_count', 100)
        
        files = sorted(Path(self.output_folder).glob("*.mp4"), key=os.path.getmtime)
        
        if len(files) > retention:
            to_delete = files[:len(files) - retention]
            for f in to_delete:
                try:
                    os.remove(f)
                    logger.debug(f"[{self.name}] Deleted old file: {f.name}")
                except Exception as e:
                    logger.warning(f"[{self.name}] Failed to delete {f.name}: {e}")

    def stop(self):
        self.stop_flag = True
