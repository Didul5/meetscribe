"""
AI processing service to analyze meeting transcripts and extract legal insights.
"""
import openai
import json
from typing import Dict, Any, List, Optional, Tuple
import time
from datetime import datetime

from config import OPENAI_API_KEY, OPENAI_MODEL, LEGAL_DOMAINS

class AIProcessor:
    """Processes meeting transcripts using OpenAI to extract legal insights."""
    
    def __init__(self):
        self.api_key = OPENAI_API_KEY
        self.model = OPENAI_MODEL
        openai.api_key = self.api_key
    
    def process_transcript(self, transcript_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a transcript to extract legal insights and action items."""
        try:
            # Extract transcript content
            if isinstance(transcript_data, dict) and "transcript" in transcript_data:
                transcript_entries = transcript_data["transcript"]
            else:
                transcript_entries = transcript_data
            
            # Format transcript for AI processing
            formatted_transcript = self._format_transcript(transcript_entries)
            
            # Process with OpenAI
            results = {}
            for domain_key, domain_name in LEGAL_DOMAINS.items():
                domain_prompt = self._get_domain_prompt(domain_key, domain_name, formatted_transcript)
                domain_results = self._call_openai(domain_prompt)
                results[domain_key] = domain_results
            
            # Generate overall summary
            summary_prompt = self._get_summary_prompt(formatted_transcript)
            summary = self._call_openai(summary_prompt)
            
            # Combine and return results
            return {
                "summary": summary,
                "domains": results,
                "processed_at": datetime.now().isoformat(),
                "model_used": self.model
            }
        except Exception as e:
            return {
                "error": str(e),
                "processed_at": datetime.now().isoformat()
            }
    
    def _format_transcript(self, transcript_entries: List[Dict[str, Any]]) -> str:
        """Format transcript entries into a readable string."""
        formatted_text = "MEETING TRANSCRIPT:\n\n"
        
        for entry in transcript_entries:
            speaker = entry.get("speaker", "Unknown")
            timestamp = entry.get("timestamp", "00:00:00")
            text = entry.get("text", "")
            
            formatted_text += f"[{timestamp}] {speaker}: {text}\n"
        
        return formatted_text
    
    def _get_domain_prompt(self, domain_key: str, domain_name: str, transcript: str) -> str:
        """Generate a prompt specific to a legal domain."""
        domain_descriptions = {
            "compliance": "Identify any compliance issues, regulatory concerns, ethical considerations, or workplace safety matters mentioned in the meeting.",
            "contracts": "Extract information about contracts, renewals, legal documents, software licenses, or tech agreements discussed in the meeting.",
            "ip_tech": "Identify discussions about intellectual property, software licensing, data privacy, cybersecurity, or technology law matters.",
            "governance": "Extract information about board governance, shareholder matters, corporate structure, business strategy, or finance law topics.",
            "litigation": "Identify any mentions of disputes, internal investigations, legal proceedings, or merger and acquisition activities."
        }
        
        prompt = f"""
        You are a specialized legal AI assistant focused on {domain_name}.
        
        {domain_descriptions.get(domain_key, "")}
        
        Based on the following meeting transcript, please:
        1. Identify key issues, risks, or opportunities relevant to {domain_name}
        2. Extract action items that legal staff should follow up on
        3. Note any deadlines or important dates mentioned
        4. Highlight any specific legal or regulatory requirements discussed
        
        Format your response as JSON with the following structure:
        {{
            "key_issues": [list of issues identified],
            "action_items": [list of specific actions with priority levels],
            "deadlines": [list of dates and associated tasks],
            "legal_requirements": [list of legal or regulatory requirements mentioned],
            "summary": "A brief summary of findings for this domain"
        }}
        
        If there is no relevant information for this domain, include an empty list for each category and note that in the summary.
        
        {transcript}
        """
        return prompt
    
    def _get_summary_prompt(self, transcript: str) -> str:
        """Generate a prompt for creating an overall legal summary."""
        prompt = f"""
        You are a senior legal advisor to the executive team.
        
        Based on the following meeting transcript, please provide a comprehensive legal summary addressing:
        1. The most critical legal issues discussed in the meeting
        2. High-priority action items that require immediate attention
        3. Strategic legal considerations for the business
        4. Risk assessment of issues mentioned
        
        Format your response as a professional executive summary that could be presented to senior leadership.
        Keep your response concise but thorough.
        
        {transcript}
        """
        return prompt
    
    def _call_openai(self, prompt: str) -> Any:
        """Call OpenAI API with the given prompt."""
        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a specialized legal AI assistant for corporate legal departments."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1000
            )
            
            # Extract and parse response content
            result_text = response.choices[0].message.content.strip()
            
            # If result is JSON, parse it
            if result_text.startswith('{') and result_text.endswith('}'):
                try:
                    return json.loads(result_text)
                except json.JSONDecodeError:
                    pass
            
            return result_text
            
        except Exception as e:
            return f"Error processing with AI: {str(e)}"