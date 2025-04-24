"""
Updated MeetStream API integration to handle the actual transcript format.
"""
import requests
import json
import time
from typing import Dict, Any, Optional, List, Tuple

from config import MEETSTREAM_API_URL, MEETSTREAM_API_KEY, TRANSCRIPT_WEBHOOK_URL

class MeetStreamClient:
    """Client for interacting with the MeetStream API."""
    
    def __init__(self):
        self.api_url = MEETSTREAM_API_URL
        self.api_key = MEETSTREAM_API_KEY
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Token {self.api_key}"  # Make sure there's a space after "Token"
        }
    
    def create_bot(self, meeting_link: str, bot_name: str = "LegalMind Assistant", 
                  audio_required: bool = True, video_required: bool = False,
                  live_transcription: bool = True) -> Dict[str, Any]:
        """Create a bot to join a meeting."""
        endpoint = f"{self.api_url}/api/v1/bots/create_bot"
        
        # Basic payload structure from Postman collection
        payload = {
            "meeting_link": meeting_link,
            "bot_name": bot_name,
            "audio_required": audio_required,
            "video_required": video_required
        }
        
        # Add live transcription webhook if requested
        if live_transcription and TRANSCRIPT_WEBHOOK_URL:
            payload["live_transcription_required"] = {
                "webhook_url": TRANSCRIPT_WEBHOOK_URL
            }
        
        try:
            print(f"Creating bot with endpoint: {endpoint}")
            print(f"Headers: {self.headers}")
            print(f"Payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(endpoint, headers=self.headers, json=payload)
            
            print(f"Response status code: {response.status_code}")
            print(f"Response content: {response.text}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to create bot: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg = f"{error_msg}. Status code: {e.response.status_code}. Response: {e.response.text}"
            raise Exception(error_msg)
    
    def get_bot_status(self, bot_id: str) -> Dict[str, Any]:
        """Get the current status of a bot."""
        endpoint = f"{self.api_url}/api/v1/bots/{bot_id}/status"
        
        try:
            print(f"Getting bot status with endpoint: {endpoint}")
            response = requests.get(endpoint, headers=self.headers)
            print(f"Response status code: {response.status_code}")
            print(f"Response content: {response.text}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to get bot status: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg = f"{error_msg}. Status code: {e.response.status_code}. Response: {e.response.text}"
            raise Exception(error_msg)
    
    def get_transcript(self, bot_id: str) -> Dict[str, Any]:
        """Get the transcript from a meeting."""
        endpoint = f"{self.api_url}/api/v1/bots/{bot_id}/get_transcript"
        
        try:
            print(f"Getting transcript with endpoint: {endpoint}")
            response = requests.get(endpoint, headers=self.headers)
            print(f"Response status code: {response.status_code}")
            print(f"Response content: {response.text}")
            
            # If we get a 404 with "Recording not found", handle gracefully
            if response.status_code == 404 and "Recording not found" in response.text:
                return {
                    "transcript": [], 
                    "message": "Recording not found or not ready yet. There may not be any speech to transcribe, or the transcript is still processing."
                }
            
            response.raise_for_status()
            
            # Process the transcript data based on the actual format received
            # The format we're receiving is a list of transcript entries
            raw_transcript = response.json()
            
            # Convert to the format expected by our application
            processed_transcript = self._process_transcript_format(raw_transcript)
            
            return processed_transcript
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to get transcript: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg = f"{error_msg}. Status code: {e.response.status_code}. Response: {e.response.text}"
            raise Exception(error_msg)
    
    def _process_transcript_format(self, raw_transcript: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process the raw transcript data into the format expected by our application.
        
        The raw format is a list of entries like:
        [
            {
                "speaker": "Bhavin Jaiswal",
                "transcript": "Hello. Am I audible? Hello.",
                "words": [...],
                "timestamp": "2025-04-24T06:53:07.884429"
            },
            ...
        ]
        
        We need to convert this to:
        {
            "transcript": [
                {
                    "speaker": "Bhavin Jaiswal",
                    "timestamp": "00:00:31",
                    "text": "Hello. Am I audible? Hello."
                },
                ...
            ]
        }
        """
        if not raw_transcript:
            return {"transcript": []}
            
        processed_entries = []
        
        # Get the start time from the first entry to calculate relative timestamps
        try:
            start_time = raw_transcript[0].get("words", [])[0].get("start", 0) if raw_transcript[0].get("words") else 0
        except (IndexError, KeyError):
            start_time = 0
            
        for entry in raw_transcript:
            # Extract timestamp in seconds from the words field if available
            timestamp_seconds = 0
            if entry.get("words") and len(entry["words"]) > 0:
                timestamp_seconds = entry["words"][0].get("start", 0) - start_time
                
            # Format timestamp as MM:SS
            minutes = int(timestamp_seconds // 60)
            seconds = int(timestamp_seconds % 60)
            formatted_timestamp = f"{minutes:02d}:{seconds:02d}"
            
            processed_entries.append({
                "speaker": entry.get("speaker", "Unknown"),
                "timestamp": formatted_timestamp,
                "text": entry.get("transcript", "")
            })
            
        return {"transcript": processed_entries}
    
    def remove_bot(self, bot_id: str) -> Dict[str, Any]:
        """Remove a bot from a meeting."""
        endpoint = f"{self.api_url}/api/v1/bots/{bot_id}/remove_bot"
        
        try:
            print(f"Removing bot with endpoint: {endpoint}")
            response = requests.get(endpoint, headers=self.headers)  # Note: Using GET as per Postman collection
            print(f"Response status code: {response.status_code}")
            print(f"Response content: {response.text}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to remove bot: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg = f"{error_msg}. Status code: {e.response.status_code}. Response: {e.response.text}"
            raise Exception(error_msg)