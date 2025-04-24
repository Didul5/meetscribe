"""
Handles Zoom OAuth authentication for meeting links and integrations.
"""
import base64
import requests
from typing import Dict, Any, Optional
import urllib.parse
import streamlit as st

from config import ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET

class ZoomOAuth:
    """Handles Zoom OAuth authentication and API interactions."""
    
    def __init__(self):
        self.client_id = ZOOM_CLIENT_ID
        self.client_secret = ZOOM_CLIENT_SECRET
        self.redirect_uri = "http://localhost:8501/zoom_callback"
        self.auth_url = "https://zoom.us/oauth/authorize"
        self.token_url = "https://zoom.us/oauth/token"
        self.api_base_url = "https://api.zoom.us/v2"
    
    def get_authorization_url(self) -> str:
        """Generate the Zoom OAuth authorization URL."""
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri
        }
        auth_url = f"{self.auth_url}?{urllib.parse.urlencode(params)}"
        return auth_url
    
    def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token."""
        auth_header = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode("utf-8")
        ).decode("utf-8")
        
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri
        }
        
        response = requests.post(self.token_url, headers=headers, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        return token_data
    
    def validate_and_store_token(self, code: str) -> bool:
        """Validate and store the access token in the session state."""
        try:
            token_data = self.exchange_code_for_token(code)
            st.session_state.zoom_token = token_data.get("access_token")
            st.session_state.zoom_refresh_token = token_data.get("refresh_token")
            st.session_state.zoom_expires_at = token_data.get("expires_in")
            st.session_state.zoom_authenticated = True
            return True
        except Exception as e:
            st.error(f"Failed to authenticate with Zoom: {str(e)}")
            return False
    
    def get_user_meetings(self) -> Optional[Dict[str, Any]]:
        """Get list of upcoming meetings for the authenticated user."""
        if not st.session_state.get("zoom_authenticated", False):
            return None
        
        token = st.session_state.get("zoom_token")
        if not token:
            return None
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(f"{self.api_base_url}/users/me/meetings", headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception:
            # Token might be expired, we'd handle refresh here in a real app
            st.warning("Your Zoom session has expired. Please log in again.")
            st.session_state.zoom_authenticated = False
            return None

    def get_meeting_details(self, meeting_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific meeting."""
        if not st.session_state.get("zoom_authenticated", False):
            return None
        
        token = st.session_state.get("zoom_token")
        if not token:
            return None
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(f"{self.api_base_url}/meetings/{meeting_id}", headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Failed to get meeting details: {str(e)}")
            return None