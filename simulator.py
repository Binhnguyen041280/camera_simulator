#!/usr/bin/env python3
"""
Camera Simulator - Main orchestrator for multi-camera simulation
"""
import os
import sys
import argparse
import logging
import time
import signal
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
import yaml

from video_generator import VideoGenerator
from camera import CameraSimulator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class Simulator:
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.cameras: List[CameraSimulator] = []
        self.threads: List[threading.Thread] = []
        self.running = False
        
    def _load_config(self, path: str) -> Dict:
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            sys.exit(1)

    def setup(self):
        """Initialize cameras based on config"""
        sim_config = self.config.get('simulator', {})
        cam_configs = self.config.get('cameras', [])
        
        for cam_conf in cam_configs:
            cam = CameraSimulator(
                name=cam_conf['name'],
                config=cam_conf,
                global_config=sim_config
            )
            self.cameras.append(cam)
            
        logger.info(f"Setup complete: {len(self.cameras)} cameras ready")

    def start(self, start_time: datetime = None):
        """Start simulation"""
        if not start_time:
            start_time = datetime.now()
            
        duration = self.config.get('simulator', {}).get('run_duration_hours', 24)
        
        logger.info(f"Starting simulation: start_time={start_time}, duration={duration}h")
        
        # Generate schedules
        for cam in self.cameras:
            cam.generate_schedule(start_time, duration)
            
        # Start threads
        self.running = True
        for cam in self.cameras:
            t = threading.Thread(target=cam.run)
            t.daemon = True
            t.start()
            self.threads.append(t)
            
        # Monitor loop
        try:
            while self.running:
                alive_count = sum(1 for t in self.threads if t.is_alive())
                if alive_count == 0:
                    logger.info("All cameras finished.")
                    break
                    
                self._print_status()
                time.sleep(self.config.get('simulator', {}).get('status_interval_seconds', 60))
                
        except KeyboardInterrupt:
            logger.info("Stopping simulation...")
            self.stop()

    def _print_status(self):
        print("\n" + "="*80)
        print("CAMERA STATUS:")
        total_videos = 0
        total_errors = 0
        
        for cam in self.cameras:
            v = cam.stats['videos_created']
            e = cam.stats['errors']
            total_videos += v
            total_errors += e
            # Simple status line
            print(f"  {cam.name:<20} | Videos: {v:>3} | Errors: {e:>3}")
            
        print(f"TOTAL: {total_videos} videos, {total_errors} errors")
        print("="*80 + "\n")

    def stop(self):
        self.running = False
        for cam in self.cameras:
            cam.stop()
        
        # Wait for threads
        for t in self.threads:
            t.join(timeout=1.0)

def main():
    parser = argparse.ArgumentParser(description="Camera Simulator")
    parser.add_argument('-c', '--config', default='config.yaml', help='Path to config file')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable debug logging')
    parser.add_argument('--start-time', help='Start time (YYYY-MM-DD HH:MM:SS)')
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        
    start_time = None
    if args.start_time:
        try:
            start_time = datetime.strptime(args.start_time, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            logger.error("Invalid time format. Use YYYY-MM-DD HH:MM:SS")
            sys.exit(1)

    sim = Simulator(args.config)
    sim.setup()
    sim.start(start_time)

if __name__ == "__main__":
    main()
