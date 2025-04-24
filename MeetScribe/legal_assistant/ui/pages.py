"""
Page definitions for the Legal Assistant application.
"""
import streamlit as st
from typing import Dict, Any, List, Optional
import time
import uuid
from datetime import datetime

from config import LEGAL_DOMAINS
from ui.components import Dashboard, MeetingUI, ActionItemsUI, InsightsUI, MeetingDetailsUI
from services.meetstream import MeetStreamClient
from services.ai_processor import AIProcessor
from models.legal_tasks import LegalTaskManager, MeetingRecord

class PageManager:
    """
    Manages page rendering and navigation for the application.
    """
    
    def __init__(self):
        # Initialize services
        self.meetstream = MeetStreamClient()
        self.ai_processor = AIProcessor()
        
        # Initialize or get task manager from session state
        if "task_manager" not in st.session_state:
            st.session_state.task_manager = LegalTaskManager()
        self.task_manager = st.session_state.task_manager
        
        # Initialize session state variables if not already set
        if "current_page" not in st.session_state:
            st.session_state.current_page = "Dashboard"
        
        if "bot_id" not in st.session_state:
            st.session_state.bot_id = None
        
        if "domain_filters" not in st.session_state:
            st.session_state.domain_filters = {domain: True for domain in LEGAL_DOMAINS.keys()}
    
    def render(self):
        """Render the current page based on session state."""
        # Always show the header and sidebar
        Dashboard.header()
        selected_navigation = Dashboard.sidebar()
        
        # Update current page based on navigation selection
        if selected_navigation:
            st.session_state.current_page = selected_navigation
        
        # Render the appropriate page
        if st.session_state.current_page == "Dashboard":
            self.render_dashboard()
        elif st.session_state.current_page == "Join Meeting":
            self.render_join_meeting()
        elif st.session_state.current_page == "Meeting History":
            self.render_meeting_history()
        elif st.session_state.current_page == "Action Items":
            self.render_action_items()
        elif st.session_state.current_page == "Legal Insights":
            self.render_legal_insights()
        elif st.session_state.current_page == "Settings":
            self.render_settings()
        elif st.session_state.current_page == "Meeting Details":
            self.render_meeting_details()
        else:
            self.render_dashboard()  # Default to dashboard
    
    def render_dashboard(self):
        """Render the dashboard page."""
        st.subheader("Legal Department Dashboard")
        
        # Display metrics and stats
        Dashboard.metrics_overview(self.task_manager)
        
        # Two-column layout for charts
        col1, col2 = st.columns(2)
        
        with col1:
            Dashboard.domain_distribution_chart(self.task_manager)
        
        with col2:
            Dashboard.priority_distribution_chart(self.task_manager)
        
        # Recent meetings table
        Dashboard.recent_meetings_table(self.task_manager)
    
    """
    Update to fix the 'experimental_rerun' error in Streamlit
    """
    def render_join_meeting(self):
        """Render the join meeting page."""
        st.subheader("Join a Meeting")
        
        # If bot is already in a meeting
        if st.session_state.bot_id:
            bot_status = None
            try:
                bot_status = self.meetstream.get_bot_status(st.session_state.bot_id)
            except Exception as e:
                st.error(f"Error getting bot status: {str(e)}")
            
            # Display meeting status
            with st.container():
                st.success("Bot successfully joined the meeting!")
                st.write(f"Bot ID: {st.session_state.bot_id}")
                
                if bot_status:
                    st.write(f"Status: {bot_status.get('status', 'Unknown')}")
                    if "message" in bot_status:
                        st.write(f"Message: {bot_status['message']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Refresh Status"):
                        st.rerun()  # Use st.rerun() instead of st.experimental_rerun()
                with col2:
                    if st.button("Leave Meeting", type="primary"):
                        try:
                            # Remove the bot
                            remove_result = self.meetstream.remove_bot(st.session_state.bot_id)
                            st.success("Bot successfully left the meeting!")
                            
                            # Try to get the transcript 
                            try:
                                transcript_data = self.meetstream.get_transcript(st.session_state.bot_id)
                                
                                # Process transcript with AI
                                if transcript_data and "transcript" in transcript_data and transcript_data["transcript"]:
                                    st.info("Processing meeting transcript with AI...")
                                    
                                    # Create meeting record
                                    meeting_id = f"meeting_{int(time.time())}"
                                    meeting_title = f"Legal Meeting on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                                    
                                    # Process with AI
                                    ai_results = self.ai_processor.process_transcript(transcript_data)
                                    process_results = self.task_manager.process_ai_results(meeting_id, meeting_title, ai_results)
                                    
                                    st.success(f"Meeting analyzed successfully! Generated {len(process_results.get('action_ids', []))} action items and {len(process_results.get('insight_ids', []))} insights.")
                                    
                                    # Go to meeting details page
                                    st.session_state.bot_id = None
                                    st.session_state.selected_meeting = meeting_id
                                    st.session_state.current_page = "Meeting Details"
                                    st.rerun()  # Use st.rerun() instead of st.experimental_rerun()
                                else:
                                    st.warning("No transcript content was found to process.")
                                    st.session_state.bot_id = None
                                    st.rerun()  # Use st.rerun() instead of st.experimental_rerun()
                            except Exception as e:
                                st.warning(f"Could not process transcript: {str(e)}")
                                st.session_state.bot_id = None
                                st.rerun()  # Use st.rerun() instead of st.experimental_rerun()
                        except Exception as e:
                            st.error(f"Error removing bot from meeting: {str(e)}")
                            st.session_state.bot_id = None
                            st.rerun()  # Use st.rerun() instead of st.experimental_rerun()
            
            # Show the transcript
            st.divider()
            st.subheader("Meeting Transcript (Live)")
            
            try:
                with st.spinner("Loading transcript..."):
                    transcript_data = self.meetstream.get_transcript(st.session_state.bot_id)
                
                if transcript_data and "transcript" in transcript_data and transcript_data["transcript"]:
                    st.success(f"Transcript available with {len(transcript_data['transcript'])} entries!")
                    
                    # Create a container for the transcript with scrollable height
                    with st.container():
                        # Add a light background to the transcript area
                        st.markdown("""
                        <style>
                        .transcript-container {
                            background-color: #f9f9f9;
                            border-radius: 10px;
                            padding: 15px;
                            margin-bottom: 20px;
                            max-height: 400px;
                            overflow-y: auto;
                        }
                        </style>
                        """, unsafe_allow_html=True)
                        
                        st.markdown('<div class="transcript-container">', unsafe_allow_html=True)
                        
                        # Display each transcript entry
                        for entry in transcript_data["transcript"]:
                            col1, col2 = st.columns([1, 5])
                            with col1:
                                speaker = entry.get("speaker", "Unknown")
                                timestamp = entry.get("timestamp", "00:00:00")
                                st.markdown(f"**{speaker}** *[{timestamp}]*")
                            with col2:
                                st.write(entry.get("text", ""))
                            st.divider()
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Add a button to process the transcript without leaving the meeting
                    if st.button("Process This Transcript for Insights"):
                        try:
                            st.info("Processing meeting transcript with AI...")
                            
                            # Create meeting record
                            meeting_id = f"meeting_{int(time.time())}"
                            meeting_title = f"Live Meeting on {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                            
                            # Process with AI
                            ai_results = self.ai_processor.process_transcript(transcript_data)
                            process_results = self.task_manager.process_ai_results(meeting_id, meeting_title, ai_results)
                            
                            st.success(f"Meeting analyzed successfully! Generated {len(process_results.get('action_ids', []))} action items and {len(process_results.get('insight_ids', []))} insights.")
                            
                            # Show a button to view the processed meeting
                            if st.button("View Analysis Results"):
                                st.session_state.selected_meeting = meeting_id
                                st.session_state.current_page = "Meeting Details"
                                st.rerun()  # Use st.rerun() instead of st.experimental_rerun()
                                
                        except Exception as e:
                            st.error(f"Error processing transcript: {str(e)}")
                else:
                    st.info("""
                    Waiting for transcript content... 
                    
                    Speak in the meeting to generate content for transcription.
                    Once you've spoken, click "Refresh Status" to see the transcript.
                    """)
                    
                    # Show a progress bar to indicate waiting
                    progress_bar = st.progress(0)
                    for i in range(100):
                        time.sleep(0.01)  # Quick animation for feedback
                        progress_bar.progress(i + 1)
                    
            except Exception as e:
                st.warning("Could not retrieve transcript. Make sure there is speech in the meeting.")
                st.code(str(e), language="python")
        
        # If no bot is in a meeting, show the join form
        else:
            with st.form("join_meeting_form"):
                st.write("Enter meeting details to join:")
                
                meeting_link = st.text_input(
                    "Meeting Link", 
                    value="https://us05web.zoom.us/j/8683456190?pwd=35KKzhBlEbKccw7ITAgTBaDJlnLsVt.1",
                    placeholder="https://zoom.us/j/123456789 or https://meet.google.com/abc-defg-hij"
                )
                
                bot_name = st.text_input("Bot Name", value="LegalMind Assistant")
                
                col1, col2 = st.columns(2)
                with col1:
                    audio_required = st.checkbox("Audio Required", value=True)
                with col2:
                    video_required = st.checkbox("Video Required", value=False)
                
                submitted = st.form_submit_button("Join Meeting")
                
                if submitted and meeting_link:
                    try:
                        with st.spinner("Joining meeting..."):
                            # Create the bot
                            result = self.meetstream.create_bot(
                                meeting_link=meeting_link,
                                bot_name=bot_name,
                                audio_required=audio_required,
                                video_required=video_required,
                                live_transcription=True
                            )
                        
                        if "bot_id" in result:
                            st.session_state.bot_id = result["bot_id"]
                            st.success(f"Successfully joined meeting with bot ID: {result['bot_id']}")
                            st.rerun()  # Use st.rerun() instead of st.experimental_rerun()
                        else:
                            st.error(f"Failed to join meeting: {result}")
                    except Exception as e:
                        st.error(f"Error joining meeting: {str(e)}")
            
            # Show additional tips
            with st.expander("Tips for successful meeting analysis"):
                st.markdown("""
                - Ensure there is clear speech in the meeting for transcription
                - Speak about legal topics such as compliance, contracts, or legal risks
                - Mention specific dates, actions, or requirements to get better insights
                - Click "Refresh Status" if the transcript doesn't appear immediately
                - Process the transcript to generate legal insights and action items
                """)
    
    def render_meeting_history(self):
        """Render the meeting history page."""
        st.subheader("Meeting History")
        
        if not self.task_manager.meetings:
            st.info("No meetings have been analyzed yet. Join a meeting to get started.")
            return
        
        # Search and filter options
        search = st.text_input("Search meetings", "")
        
        # Display meetings as cards
        for meeting in self.task_manager.meetings:
            # Apply search filter if provided
            if search and search.lower() not in meeting.title.lower():
                continue
            
            with st.container():
                col1, col2, col3 = st.columns([4, 4, 2])
                
                with col1:
                    st.markdown(f"### {meeting.title}")
                    st.write(f"Date: {meeting.date}")
                
                with col2:
                    action_count = len(self.task_manager.get_actions_by_meeting(meeting.id))
                    insight_count = len(self.task_manager.get_insights_by_meeting(meeting.id))
                    
                    st.write(f"Actions: {action_count}")
                    st.write(f"Insights: {insight_count}")
                
                with col3:
                    if st.button("View Details", key=f"view_{meeting.id}"):
                        st.session_state.selected_meeting = meeting.id
                        st.session_state.current_page = "Meeting Details"
                        st.rerun()
            
            st.divider()
    
    def render_action_items(self):
        """Render the action items page."""
        st.subheader("Legal Action Items")
        
        # Get active domain filters
        active_domains = [domain for domain, is_active in st.session_state.domain_filters.items() if is_active]
        
        # Display action items list with filtering
        ActionItemsUI.action_list(self.task_manager, active_domains)
    
    def render_legal_insights(self):
        """Render the legal insights page."""
        st.subheader("Legal Insights")
        
        # Get active domain filters
        active_domains = [domain for domain, is_active in st.session_state.domain_filters.items() if is_active]
        
        # Display insights list with filtering
        InsightsUI.insights_list(self.task_manager, active_domains)
    
    def render_settings(self):
        """Render the settings page."""
        st.subheader("Application Settings")
        
        # API Configuration
        st.markdown("### API Configuration")
        
        with st.expander("MeetStream API Settings"):
            st.text_input("API URL", value="https://api-meetstream-tst-hackathon.meetstream.ai/api/v1", disabled=True)
            st.text_input("API Key", value="ms_XQmQZPip5wmTPMNqlgUVwhqLpsnxW1sy", type="password", disabled=True)
        
        with st.expander("Zoom OAuth Settings"):
            st.text_input("Client ID", value="qTMTHsydSyGrXnmOGtDFw", disabled=True)
            st.text_input("Client Secret", value="99DaYLDDtH4lsOg9T3TgdLQTxcigtBP2", type="password", disabled=True)
        
        with st.expander("OpenAI API Settings"):
            st.text_input("API Key", value="sk-proj-bv5SVUAncVdkNdYJB70UehV0HyHL4PG...", type="password", disabled=True)
            st.selectbox("Model", options=["gpt-4", "gpt-3.5-turbo"], index=0, disabled=True)
        
        # Webhook Settings
        st.markdown("### Webhook Settings")
        
        with st.expander("Webhook URLs"):
            st.text_input("Base URL", value="https://webhook.site/acf36d25-ec4d-4b4f-b7b4-99037150b25b", disabled=True)
            st.text_input("Transcript URL", value="https://webhook.site/acf36d25-ec4d-4b4f-b7b4-99037150b25b/transcripts", disabled=True)
            st.text_input("Actions URL", value="https://webhook.site/acf36d25-ec4d-4b4f-b7b4-99037150b25b/actions", disabled=True)
        
        # App Settings
        st.markdown("### Application Settings")
        
        with st.expander("UI Settings"):
            st.checkbox("Dark Mode", value=False)
            st.checkbox("Enable Notifications", value=True)
        
        # Demo options
        st.markdown("### Demo Options")
        
        with st.expander("Demo Data"):
            if st.button("Load Demo Data"):
                st.info("Loading demo data...")
                self._load_demo_data()
                st.success("Demo data loaded successfully!")
                st.rerun()
            
            if st.button("Clear All Data"):
                st.session_state.task_manager = LegalTaskManager()
                self.task_manager = st.session_state.task_manager
                st.success("All data cleared successfully!")
                st.rerun()
    
    def render_meeting_details(self):
        """Render the meeting details page."""
        meeting_id = st.session_state.get("selected_meeting")
        if not meeting_id:
            st.error("No meeting selected.")
            return
        
        # Back button
        if st.button("← Back to Meetings"):
            st.session_state.current_page = "Meeting History"
            st.rerun()
        
        # Show meeting details
        MeetingDetailsUI.meeting_details(meeting_id, self.task_manager)
    
    def _load_demo_data(self):
        """Load demo data for testing the application."""
        # Create a demo meeting
        meeting_id = "demo_meeting_1"
        meeting_title = "Weekly Legal Team Sync - April 23, 2025"
        
        # Create some demo domains data
        demo_domains = {
            "compliance": {
                "key_issues": [
                    "GDPR compliance issues with new customer data collection forms",
                    "Potential safety regulation violations in manufacturing facility B",
                    "Ethics concerns regarding marketing campaign targeting vulnerable populations"
                ],
                "action_items": [
                    "Review GDPR requirements for customer forms",
                    "Schedule safety inspection for manufacturing facility B",
                    "Convene ethics committee to review marketing campaign"
                ],
                "deadlines": [
                    "GDPR compliance report due by May 15, 2025",
                    "Safety inspection must be completed within 2 weeks"
                ],
                "legal_requirements": [
                    "GDPR Article 7 requirements for consent",
                    "OSHA workplace safety standards section 1910.132"
                ],
                "summary": "Several compliance issues were identified requiring immediate attention"
            },
            "contracts": {
                "key_issues": [
                    "SaaS vendor agreement renewal approaching with unfavorable terms",
                    "Missing IP assignment clauses in contractor agreements",
                    "Inconsistent force majeure clauses across supplier contracts"
                ],
                "action_items": [
                    "Renegotiate SaaS vendor agreement",
                    "Update contractor agreement template with proper IP clauses",
                    "Standardize force majeure language across supplier contracts"
                ],
                "deadlines": [
                    "SaaS agreement expires on June 30, 2025",
                    "Contractor agreement updates needed by end of month"
                ],
                "legal_requirements": [
                    "IP assignment requirements under current copyright law",
                    "Contract enforceability standards"
                ],
                "summary": "Contract inconsistencies and approaching renewals require attention"
            }
        }
        
        # Create an AI results structure
        ai_results = {
            "summary": "The legal team discussed several critical compliance issues, contract renewals, and potential IP concerns that require immediate attention. GDPR compliance with new data collection methods was identified as high priority, along with safety concerns at manufacturing facility B. Contract renewals for key SaaS vendors need to be renegotiated with more favorable terms, and IP assignment clauses should be standardized across all contractor agreements.",
            "domains": demo_domains,
            "processed_at": datetime.now().isoformat(),
            "model_used": "gpt-4"
        }
        
        # Process the results to create actions and insights
        self.task_manager.process_ai_results(meeting_id, meeting_title, ai_results)