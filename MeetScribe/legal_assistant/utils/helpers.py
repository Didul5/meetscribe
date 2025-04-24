"""
Helper utilities for the Legal Assistant application.
"""
import streamlit as st
import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

def generate_unique_id(prefix: str = "") -> str:
    """Generate a unique ID with an optional prefix."""
    return f"{prefix}{uuid.uuid4().hex[:8]}"

def format_timestamp(timestamp: str) -> str:
    """Format a timestamp into a readable format."""
    # Handle various timestamp formats
    if ":" in timestamp:  # Already in MM:SS or HH:MM:SS format
        return timestamp
    
    try:
        # Try to convert from seconds
        seconds = float(timestamp)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        
        if hours > 0:
            return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
        else:
            return f"{int(minutes):02d}:{int(seconds):02d}"
    except (ValueError, TypeError):
        # If conversion fails, return the original
        return timestamp

def extract_speakers_from_transcript(transcript_data: Dict[str, Any]) -> List[str]:
    """Extract unique speakers from a transcript."""
    speakers = set()
    
    if isinstance(transcript_data, dict) and "transcript" in transcript_data:
        for entry in transcript_data["transcript"]:
            if "speaker" in entry:
                speakers.add(entry["speaker"])
    
    return list(speakers)

def calculate_meeting_duration(transcript_data: Dict[str, Any]) -> int:
    """Calculate meeting duration in seconds from transcript timestamps."""
    if not transcript_data or "transcript" not in transcript_data:
        return 0
    
    transcript = transcript_data["transcript"]
    if not transcript:
        return 0
    
    # Try to get the last timestamp
    try:
        last_entry = transcript[-1]
        last_timestamp = last_entry.get("timestamp", "00:00:00")
        
        # Convert HH:MM:SS to seconds
        parts = last_timestamp.split(":")
        if len(parts) == 3:
            hours, minutes, seconds = parts
            total_seconds = int(hours) * 3600 + int(minutes) * 60 + int(seconds)
        elif len(parts) == 2:
            minutes, seconds = parts
            total_seconds = int(minutes) * 60 + int(seconds)
        else:
            total_seconds = 0
        
        return total_seconds
    except (IndexError, ValueError):
        return 0

def save_to_local_storage(key: str, data: Any) -> bool:
    """Save data to browser's local storage."""
    try:
        # Convert data to JSON string
        if not isinstance(data, str):
            data = json.dumps(data)
        
        # Use Streamlit's JavaScript to save to local storage
        js = f"""
        <script>
        localStorage.setItem("{key}", JSON.stringify({data}));
        </script>
        """
        st.components.v1.html(js, height=0)
        return True
    except Exception:
        return False

def load_from_local_storage(key: str) -> Optional[Any]:
    """Load data from browser's local storage."""
    try:
        # Use Streamlit's JavaScript to load from local storage
        js = f"""
        <script>
        const data = localStorage.getItem("{key}");
        const communicationElement = document.getElementById("data-{key}");
        communicationElement.textContent = data;
        </script>
        <div id="data-{key}" style="display:none;"></div>
        """
        component = st.components.v1.html(js, height=0)
        
        # Get data from the hidden div
        data = component.get("data-" + key)
        if data:
            return json.loads(data)
        return None
    except Exception:
        return None

def format_legal_reference(reference_type: str, reference_id: str) -> str:
    """Format a legal reference with proper citation style."""
    if reference_type == "statute":
        return f"{reference_id} (as amended)"
    elif reference_type == "case":
        parts = reference_id.split("v")
        if len(parts) == 2:
            return f"{parts[0].strip()} v. {parts[1].strip()}"
        else:
            return reference_id
    elif reference_type == "regulation":
        return f"Regulation {reference_id}"
    else:
        return reference_id

def extract_key_metrics_from_transcript(transcript_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract key metrics from a transcript, such as:
    - Meeting duration
    - Number of participants
    - Average speaking time per participant
    - Keywords mentioned
    """
    metrics = {
        "duration": 0,
        "participant_count": 0,
        "speaking_distribution": {},
        "keywords": {}
    }
    
    if not transcript_data or "transcript" not in transcript_data:
        return metrics
    
    transcript = transcript_data["transcript"]
    if not transcript:
        return metrics
    
    # Calculate duration
    metrics["duration"] = calculate_meeting_duration(transcript_data)
    
    # Count participants and speaking time
    speakers = {}
    keyword_map = {
        "compliance": ["compliance", "regulation", "regulatory", "law", "legal", "requirement"],
        "risk": ["risk", "threat", "liability", "exposure", "danger", "hazard"],
        "contract": ["contract", "agreement", "license", "clause", "term", "provision"],
        "litigation": ["litigation", "lawsuit", "case", "court", "plaintiff", "defendant", "sue"],
        "ip": ["ip", "intellectual property", "patent", "trademark", "copyright", "trade secret"]
    }
    
    keyword_counts = {k: 0 for k in keyword_map.keys()}
    
    for entry in transcript:
        # Count speakers
        speaker = entry.get("speaker", "Unknown")
        if speaker not in speakers:
            speakers[speaker] = 0
        
        # Add speaking time (rough estimate)
        text = entry.get("text", "")
        word_count = len(text.split())
        speakers[speaker] += word_count
        
        # Count keywords
        lower_text = text.lower()
        for category, keywords in keyword_map.items():
            for keyword in keywords:
                if keyword in lower_text:
                    keyword_counts[category] += 1
    
    metrics["participant_count"] = len(speakers)
    metrics["speaking_distribution"] = speakers
    metrics["keywords"] = keyword_counts
    
    return metrics
