#!/usr/bin/env python3
"""
Camera Simulator Configuration Wizard
Interactive tool to generate config.yaml
"""
import os
import sys
import yaml
from pathlib import Path

def input_default(prompt, default):
    """Get input with default value"""
    result = input(f"{prompt} [{default}]: ").strip()
    return result if result else default

def select_option(prompt, options):
    """Select from a list of options"""
    print(f"\n{prompt}")
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt['name']}")
    
    while True:
        try:
            choice = int(input(f"Select (1-{len(options)}): "))
            if 1 <= choice <= len(options):
                return options[choice-1]
        except ValueError:
            pass
        print("Invalid selection. Please try again.")

PROFILES = {
    'hikvision': {
        'name': 'Hikvision (NAS/NVR Style)',
        'naming_template': 'ch{channel}_{date}_{time}_{type}.mp4',
        'directory_structure': '{date}/',
        'segment_duration': 10
    },
    'dahua': {
        'name': 'Dahua (NAS/NVR Style)',
        'naming_template': '{time}.mp4',
        'directory_structure': '{date}/{channel}/',
        'segment_duration': 60
    },
    'imou': {
        'name': 'Imou (Export Style)',
        'naming_template': '{time}.mp4',
        'directory_structure': '{date}/',
        'segment_duration': 10
    },
    'ezviz': {
        'name': 'Ezviz (Export Style)',
        'naming_template': '{date}_{time}.mp4',
        'directory_structure': '{date}/',
        'segment_duration': 10
    },
    'tapo': {
        'name': 'TP-Link Tapo (SD Card Style)',
        'naming_template': '{date}_{time}_tp00001.mp4',
        'directory_structure': '{date}/',
        'segment_duration': 30
    },
    'generic': {
        'name': 'Generic / Custom',
        'naming_template': '{name}_{timestamp}.mp4',
        'directory_structure': '',
        'segment_duration': 15
    }
}

PATTERNS = [
    {'name': 'Continuous (24/7 Recording)', 'id': 'continuous'},
    {'name': 'Motion Triggered (Smart Event)', 'id': 'motion_triggered'},
    {'name': 'Event Triggered (Sparse)', 'id': 'event_triggered'},
    {'name': 'Random On/Off', 'id': 'random_on_off'}
]

def main():
    print("="*50)
    print("📹  CAMERA SIMULATOR WIZARD")
    print("="*50)
    print("This tool will help you generate a config.yaml file.\n")

    # 1. Source Video
    print("--- 1. Source Video ---")
    source_video = input_default("Path to source video file", "source_videos/test.mp4")
    if not os.path.exists(source_video):
        print(f"Warning: {source_video} does not exist yet. Make sure to create it before running.")

    # 2. Output Directory
    print("\n--- 2. Output Directory ---")
    output_base = input_default("Base output directory", "output")

    # 3. Camera Brand (Profile)
    print("\n--- 3. Camera Brand ---")
    profile_opts = [{'name': v['name'], 'key': k} for k, v in PROFILES.items()]
    selected_profile = select_option("Select Camera Brand:", profile_opts)
    profile_key = selected_profile['key']
    profile_data = PROFILES[profile_key]

    # 4. Recording Pattern
    print("\n--- 4. Recording Pattern ---")
    selected_pattern = select_option("Select Recording Pattern:", PATTERNS)
    
    # 5. Number of Cameras
    print("\n--- 5. Scale ---")
    num_cameras = int(input_default("Number of cameras to simulate", "1"))

    # 6. Duration
    print("\n--- 6. Simulation Settings ---")
    duration = float(input_default("Run duration (hours, 0=infinite)", "24"))
    real_time = input_default("Run in real-time? (y/n)", "y").lower().startswith('y')

    # Generate Config
    config = {
        'simulator': {
            'run_duration_hours': duration,
            'status_interval_seconds': 60,
            'cleanup_old_files': True,
            'retention_count': 100
        },
        'cameras': []
    }

    print(f"\nGenerating config for {num_cameras} cameras...")

    for i in range(1, num_cameras + 1):
        cam_name = f"Camera{i:02d}"
        
        # Determine duration range based on profile
        segment_duration = profile_data['segment_duration']
        
        cam_config = {
            'name': cam_name,
            'source_video': source_video,
            'output_folder': os.path.join(output_base, cam_name),
            'pattern': selected_pattern['id'],
            'profile': profile_key, # Store profile name
            'naming_template': profile_data['naming_template'],
            'directory_structure': profile_data['directory_structure'],
            'config': {
                'use_real_time': real_time
            }
        }

        # Adjust duration based on pattern
        if selected_pattern['id'] == 'continuous':
            cam_config['config']['video_duration_range'] = [segment_duration, segment_duration]
        else:
            # For motion/event, use shorter clips
            cam_config['config']['video_duration_range'] = [2, segment_duration]
            cam_config['config']['idle_duration_range'] = [5, 30]

        config['cameras'].append(cam_config)

    # Save
    output_file = 'config.yaml'
    if os.path.exists(output_file):
        overwrite = input_default(f"{output_file} already exists. Overwrite? (y/n)", "n")
        if not overwrite.lower().startswith('y'):
            output_file = 'config_new.yaml'

    with open(output_file, 'w') as f:
        yaml.dump(config, f, sort_keys=False)

    print(f"\n✅ Configuration saved to {output_file}")
    print(f"Run simulator with: python simulator.py -c {output_file}")

if __name__ == "__main__":
    main()
