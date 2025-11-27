"""
Recording Patterns - Define different camera recording behaviors
"""
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class PatternType(Enum):
    """Types of recording patterns"""
    CONTINUOUS = "continuous"
    MOTION_TRIGGERED = "motion_triggered"
    EVENT_TRIGGERED = "event_triggered"
    RANDOM_ON_OFF = "random_on_off"

@dataclass
class RecordingEvent:
    """Represents a scheduled recording event"""
    start_time: datetime
    duration_minutes: float
    filename: str

def create_pattern(pattern_type: str, config: Dict, start_time: datetime, end_time: datetime) -> List[RecordingEvent]:
    """Factory function to create recording schedule based on pattern"""
    try:
        if pattern_type == PatternType.CONTINUOUS.value:
            return _generate_continuous(config, start_time, end_time)
        elif pattern_type == PatternType.MOTION_TRIGGERED.value:
            return _generate_motion(config, start_time, end_time)
        elif pattern_type == PatternType.EVENT_TRIGGERED.value:
            return _generate_event(config, start_time, end_time)
        elif pattern_type == PatternType.RANDOM_ON_OFF.value:
            return _generate_random(config, start_time, end_time)
        else:
            logger.warning(f"Unknown pattern: {pattern_type}, defaulting to continuous")
            return _generate_continuous(config, start_time, end_time)
    except Exception as e:
        logger.error(f"Error generating pattern {pattern_type}: {e}")
        return []

def _generate_continuous(config: Dict, start_time: datetime, end_time: datetime) -> List[RecordingEvent]:
    """Generate continuous recording events back-to-back"""
    events = []
    current_time = start_time
    duration_range = config.get('video_duration_range', [15, 15])
    
    while current_time < end_time:
        # Calculate duration
        duration = random.uniform(duration_range[0], duration_range[1])
        
        # Check if exceeds end_time
        if current_time + timedelta(minutes=duration) > end_time:
            duration = (end_time - current_time).total_seconds() / 60
            if duration < 0.1: # Skip if too short
                break
                
        events.append(RecordingEvent(
            start_time=current_time,
            duration_minutes=duration,
            filename="" # Will be generated later
        ))
        
        current_time += timedelta(minutes=duration)
        
    return events

def _generate_motion(config: Dict, start_time: datetime, end_time: datetime) -> List[RecordingEvent]:
    """Generate motion triggered events with idle gaps"""
    events = []
    current_time = start_time
    video_range = config.get('video_duration_range', [5, 20])
    idle_range = config.get('idle_duration_range', [10, 30])
    
    while current_time < end_time:
        # Idle period first
        idle = random.uniform(idle_range[0], idle_range[1])
        current_time += timedelta(minutes=idle)
        
        if current_time >= end_time:
            break
            
        # Recording period
        duration = random.uniform(video_range[0], video_range[1])
        
        if current_time + timedelta(minutes=duration) > end_time:
            duration = (end_time - current_time).total_seconds() / 60
            
        if duration > 0.1:
            events.append(RecordingEvent(
                start_time=current_time,
                duration_minutes=duration,
                filename=""
            ))
            
        current_time += timedelta(minutes=duration)
        
    return events

def _generate_event(config: Dict, start_time: datetime, end_time: datetime) -> List[RecordingEvent]:
    """Generate sparse event triggered recordings"""
    # Similar to motion but longer idle times
    events = []
    current_time = start_time
    video_range = config.get('video_duration_range', [3, 10])
    idle_range = config.get('idle_duration_range', [20, 60])
    
    while current_time < end_time:
        idle = random.uniform(idle_range[0], idle_range[1])
        current_time += timedelta(minutes=idle)
        
        if current_time >= end_time:
            break
            
        duration = random.uniform(video_range[0], video_range[1])
        
        if current_time + timedelta(minutes=duration) > end_time:
            duration = (end_time - current_time).total_seconds() / 60
            
        if duration > 0.1:
            events.append(RecordingEvent(
                start_time=current_time,
                duration_minutes=duration,
                filename=""
            ))
            
        current_time += timedelta(minutes=duration)
        
    return events

def _generate_random(config: Dict, start_time: datetime, end_time: datetime) -> List[RecordingEvent]:
    """Generate random on/off periods"""
    events = []
    current_time = start_time
    
    while current_time < end_time:
        # Determine state: On or Off
        is_on = random.choice([True, False])
        period_duration = random.uniform(60, 240) # 1-4 hours block
        
        block_end = min(current_time + timedelta(minutes=period_duration), end_time)
        
        if is_on:
            # Generate continuous videos within this block
            block_events = _generate_continuous(config, current_time, block_end)
            events.extend(block_events)
            
        current_time = block_end
        
    return events
