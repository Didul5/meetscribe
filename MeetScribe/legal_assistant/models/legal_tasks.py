"""
Legal task definitions and handlers for processing meeting insights.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

@dataclass
class LegalAction:
    """Represents a legal follow-up action derived from meeting insights."""
    id: str
    domain: str
    title: str
    description: str
    priority: str  # "high", "medium", "low"
    deadline: Optional[str] = None
    status: str = "pending"  # "pending", "in_progress", "completed", "cancelled"
    assignee: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert action to dictionary."""
        return {
            "id": self.id,
            "domain": self.domain,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "deadline": self.deadline,
            "status": self.status,
            "assignee": self.assignee,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

@dataclass
class LegalInsight:
    """Represents a legal insight derived from meeting analysis."""
    id: str
    domain: str
    title: str
    description: str
    source_meeting: str
    importance: str  # "critical", "high", "medium", "low"
    tags: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert insight to dictionary."""
        return {
            "id": self.id,
            "domain": self.domain,
            "title": self.title,
            "description": self.description,
            "source_meeting": self.source_meeting,
            "importance": self.importance,
            "tags": self.tags,
            "created_at": self.created_at
        }

@dataclass
class MeetingRecord:
    """Represents a processed meeting record."""
    id: str
    title: str
    date: str
    bot_id: str
    participants: List[str]
    duration: int  # in seconds
    transcript_summary: str
    domains_processed: List[str]
    has_action_items: bool
    has_insights: bool
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert meeting record to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "date": self.date,
            "bot_id": self.bot_id,
            "participants": self.participants,
            "duration": self.duration,
            "transcript_summary": self.transcript_summary,
            "domains_processed": self.domains_processed,
            "has_action_items": self.has_action_items,
            "has_insights": self.has_insights,
            "created_at": self.created_at
        }

class LegalTaskManager:
    """Manages legal tasks, insights and meeting records."""
    
    def __init__(self):
        self.actions = []
        self.insights = []
        self.meetings = []
    
    def add_meeting(self, meeting: MeetingRecord) -> str:
        """Add a meeting record and return its ID."""
        self.meetings.append(meeting)
        return meeting.id
    
    def add_action(self, action: LegalAction) -> str:
        """Add an action and return its ID."""
        self.actions.append(action)
        return action.id
    
    def add_insight(self, insight: LegalInsight) -> str:
        """Add an insight and return its ID."""
        self.insights.append(insight)
        return insight.id
    
    def process_ai_results(self, meeting_id: str, meeting_title: str, 
                          ai_results: Dict[str, Any]) -> Dict[str, List[str]]:
        """Process AI analysis results to create actions and insights."""
        action_ids = []
        insight_ids = []
        
        # Extract domain-specific results
        domains_processed = []
        for domain_key, domain_results in ai_results.get("domains", {}).items():
            domains_processed.append(domain_key)
            
            # Process actions
            if isinstance(domain_results, dict) and "action_items" in domain_results:
                for i, action_item in enumerate(domain_results["action_items"]):
                    if isinstance(action_item, str):
                        # Simple string action
                        action = LegalAction(
                            id=f"act-{meeting_id}-{domain_key}-{i}",
                            domain=domain_key,
                            title=action_item[:50] + "..." if len(action_item) > 50 else action_item,
                            description=action_item,
                            priority="medium"  # Default priority
                        )
                    elif isinstance(action_item, dict):
                        # Structured action
                        action = LegalAction(
                            id=f"act-{meeting_id}-{domain_key}-{i}",
                            domain=domain_key,
                            title=action_item.get("title", "Untitled Action"),
                            description=action_item.get("description", ""),
                            priority=action_item.get("priority", "medium"),
                            deadline=action_item.get("deadline")
                        )
                    
                    action_ids.append(self.add_action(action))
            
            # Process key issues as insights
            if isinstance(domain_results, dict) and "key_issues" in domain_results:
                for i, issue in enumerate(domain_results["key_issues"]):
                    if isinstance(issue, str):
                        insight = LegalInsight(
                            id=f"ins-{meeting_id}-{domain_key}-{i}",
                            domain=domain_key,
                            title=issue[:50] + "..." if len(issue) > 50 else issue,
                            description=issue,
                            source_meeting=meeting_id,
                            importance="medium",
                            tags=[domain_key]
                        )
                    elif isinstance(issue, dict):
                        insight = LegalInsight(
                            id=f"ins-{meeting_id}-{domain_key}-{i}",
                            domain=domain_key,
                            title=issue.get("title", "Untitled Insight"),
                            description=issue.get("description", ""),
                            source_meeting=meeting_id,
                            importance=issue.get("importance", "medium"),
                            tags=[domain_key] + issue.get("tags", [])
                        )
                    
                    insight_ids.append(self.add_insight(insight))
        
        # Create meeting record
        meeting = MeetingRecord(
            id=meeting_id,
            title=meeting_title,
            date=datetime.now().strftime("%Y-%m-%d"),
            bot_id=meeting_id,  # Using meeting_id as bot_id for simplicity
            participants=[],  # Would extract from transcript in real app
            duration=0,  # Would calculate from transcript in real app
            transcript_summary=ai_results.get("summary", "No summary available"),
            domains_processed=domains_processed,
            has_action_items=len(action_ids) > 0,
            has_insights=len(insight_ids) > 0
        )
        
        self.add_meeting(meeting)
        
        return {
            "action_ids": action_ids,
            "insight_ids": insight_ids,
            "meeting_id": meeting_id
        }
    
    def get_meeting_by_id(self, meeting_id: str) -> Optional[MeetingRecord]:
        """Get a meeting record by ID."""
        for meeting in self.meetings:
            if meeting.id == meeting_id:
                return meeting
        return None
    
    def get_actions_by_meeting(self, meeting_id: str) -> List[LegalAction]:
        """Get all actions associated with a meeting."""
        return [action for action in self.actions if meeting_id in action.id]
    
    def get_insights_by_meeting(self, meeting_id: str) -> List[LegalInsight]:
        """Get all insights associated with a meeting."""
        return [insight for insight in self.insights if insight.source_meeting == meeting_id]
    
    def get_actions_by_domain(self, domain: str) -> List[LegalAction]:
        """Get all actions for a specific legal domain."""
        return [action for action in self.actions if action.domain == domain]
    
    def get_insights_by_domain(self, domain: str) -> List[LegalInsight]:
        """Get all insights for a specific legal domain."""
        return [insight for insight in self.insights if insight.domain == domain]
    
    def update_action_status(self, action_id: str, status: str, assignee: Optional[str] = None) -> bool:
        """Update the status of an action."""
        for action in self.actions:
            if action.id == action_id:
                action.status = status
                if assignee:
                    action.assignee = assignee
                action.updated_at = datetime.now().isoformat()
                return True
        return False