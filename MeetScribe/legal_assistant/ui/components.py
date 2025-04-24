"""
Reusable UI components for the Legal Assistant application.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List, Optional, Tuple, Callable
import pandas as pd
import time
from datetime import datetime

from config import LEGAL_DOMAINS
from models.legal_tasks import LegalAction, LegalInsight, MeetingRecord

class Dashboard:
    """Dashboard UI components for displaying legal insights."""
    
    @staticmethod
    def header():
        """Display the application header."""
        col1, col2 = st.columns([1, 5])
        
        with col1:
            st.image("https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/2696.png", width=80)
        
        with col2:
            st.title("LegalMind Assistant")
            st.markdown("### AI-Powered Legal Assistant for Meeting Analysis")
    
    @staticmethod
    def sidebar():
        """Render the sidebar navigation."""
        with st.sidebar:
            st.image("https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/72x72/1f4d1.png", width=50)
            st.title("Navigation")
            
            # Main navigation
            selected = st.radio(
                "Go to",
                options=["Dashboard", "Join Meeting", "Meeting History", "Action Items", "Legal Insights", "Settings"],
                index=0
            )
            
            st.divider()
            
            # Domain filters for relevant pages
            if selected in ["Action Items", "Legal Insights"]:
                st.subheader("Filter by Domain")
                domain_filters = {}
                
                for key, name in LEGAL_DOMAINS.items():
                    domain_filters[key] = st.checkbox(name, value=True)
                
                st.session_state.domain_filters = domain_filters
            
            # Quick access to recent meetings
            if "meetings" in st.session_state and len(st.session_state.meetings) > 0:
                st.subheader("Recent Meetings")
                for i, meeting in enumerate(st.session_state.meetings[:3]):
                    if st.button(f"{meeting.title[:20]}...", key=f"recent_meeting_{i}"):
                        st.session_state.selected_meeting = meeting.id
                        st.session_state.current_page = "Meeting Details"
            
            st.divider()
            st.info("LegalMind Assistant v1.0.0")
            
            return selected
    
    @staticmethod
    def metrics_overview(task_manager):
        """Display high-level metrics for the dashboard."""
        # Get metrics data
        total_meetings = len(task_manager.meetings)
        total_actions = len(task_manager.actions)
        total_insights = len(task_manager.insights)
        pending_actions = sum(1 for action in task_manager.actions if action.status == "pending")
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Meetings Analyzed", total_meetings)
        
        with col2:
            st.metric("Action Items", total_actions, f"{pending_actions} pending")
        
        with col3:
            st.metric("Legal Insights", total_insights)
        
        with col4:
            # Calculate completion rate
            if total_actions > 0:
                completion_rate = round(((total_actions - pending_actions) / total_actions) * 100)
                st.metric("Task Completion", f"{completion_rate}%")
            else:
                st.metric("Task Completion", "N/A")
    
    @staticmethod
    def domain_distribution_chart(task_manager):
        """Display a chart showing the distribution of actions across legal domains."""
        # Count actions by domain
        domain_counts = {}
        for domain_key in LEGAL_DOMAINS.keys():
            domain_counts[domain_key] = len(task_manager.get_actions_by_domain(domain_key))
        
        # Prepare data for chart
        df = pd.DataFrame({
            "Domain": [LEGAL_DOMAINS[k] for k in domain_counts.keys()],
            "Actions": list(domain_counts.values())
        })
        
        # Create chart
        fig = px.bar(
            df, 
            x="Domain", 
            y="Actions",
            title="Actions by Legal Domain",
            color="Domain",
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        
        fig.update_layout(
            height=400,
            xaxis_title="",
            yaxis_title="Number of Actions",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def priority_distribution_chart(task_manager):
        """Display a chart showing the distribution of actions by priority."""
        # Count actions by priority
        priority_counts = {"high": 0, "medium": 0, "low": 0}
        for action in task_manager.actions:
            if action.priority in priority_counts:
                priority_counts[action.priority] += 1
        
        # Prepare data for chart
        labels = ["High", "Medium", "Low"]
        values = [priority_counts["high"], priority_counts["medium"], priority_counts["low"]]
        colors = ["#FF5733", "#FFC300", "#36A2EB"]
        
        # Create chart
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=.4,
            marker_colors=colors
        )])
        
        fig.update_layout(
            title_text="Actions by Priority",
            height=400,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def recent_meetings_table(task_manager):
        """Display a table of recent meetings."""
        if not task_manager.meetings:
            st.info("No meetings have been analyzed yet. Join a meeting to get started.")
            return
        
        # Create a dataframe from meetings
        meetings_data = []
        for meeting in task_manager.meetings:
            meetings_data.append({
                "Date": meeting.date,
                "Title": meeting.title,
                "Actions": len(task_manager.get_actions_by_meeting(meeting.id)),
                "Insights": len(task_manager.get_insights_by_meeting(meeting.id)),
                "ID": meeting.id
            })
        
        df = pd.DataFrame(meetings_data)
        
        # Display as a table with a link to details
        st.subheader("Recent Meetings")
        
        # Use Streamlit's built-in table for simplicity
        for i, row in df.iterrows():
            col1, col2, col3, col4 = st.columns([2, 5, 2, 2])
            with col1:
                st.write(row["Date"])
            with col2:
                st.write(row["Title"])
            with col3:
                st.write(f"{row['Actions']} actions")
            with col4:
                if st.button("View Details", key=f"view_meeting_{row['ID']}"):
                    st.session_state.selected_meeting = row["ID"]
                    st.session_state.current_page = "Meeting Details"
            st.divider()


class MeetingUI:
    """UI components for meeting-related functionality."""
    
    @staticmethod
    def join_meeting_form():
        """Display form for joining a meeting."""
        st.subheader("Join a Meeting")
        
        meeting_method = st.radio(
            "Select meeting type",
            options=["Direct Meeting Link", "Connect via Zoom OAuth", "Google Meet"],
            horizontal=True
        )
        
        if meeting_method == "Direct Meeting Link":
            with st.form("join_meeting_form"):
                meeting_link = st.text_input("Meeting Link", placeholder="https://zoom.us/j/123456789")
                bot_name = st.text_input("Bot Name", value="LegalMind Assistant")
                
                col1, col2 = st.columns(2)
                with col1:
                    audio_required = st.checkbox("Audio Required", value=True)
                with col2:
                    video_required = st.checkbox("Video Required", value=False)
                
                submitted = st.form_submit_button("Join Meeting")
                
                if submitted and meeting_link:
                    return {
                        "meeting_link": meeting_link,
                        "bot_name": bot_name,
                        "audio_required": audio_required,
                        "video_required": video_required
                    }
        
        elif meeting_method == "Connect via Zoom OAuth":
            st.info("Connect your Zoom account to join meetings directly.")
            
            if st.button("Connect Zoom Account"):
                # This would trigger the OAuth flow in a real app
                st.session_state.show_zoom_oauth = True
            
            if st.session_state.get("show_zoom_oauth", False):
                with st.form("zoom_oauth_form"):
                    st.write("Authenticate with Zoom")
                    zoom_email = st.text_input("Zoom Email")
                    zoom_password = st.text_input("Zoom Password", type="password")
                    submitted = st.form_submit_button("Authenticate")
                    
                    if submitted and zoom_email and zoom_password:
                        # This would actually use the Zoom OAuth client in a real app
                        st.success("Authentication successful! You can now select a meeting.")
                        st.session_state.zoom_authenticated = True
                        st.session_state.show_zoom_oauth = False
                        st.rerun()
            
            if st.session_state.get("zoom_authenticated", False):
                st.write("Select a meeting to join:")
                # This would show actual meetings from the Zoom API in a real app
                meeting_options = [
                    "Weekly Team Sync - 10:00 AM",
                    "Client Consultation - 2:30 PM",
                    "Board Meeting - 4:00 PM"
                ]
                
                selected_meeting = st.selectbox("Available Meetings", meeting_options)
                
                if st.button("Join Selected Meeting"):
                    return {
                        "meeting_link": f"https://zoom.us/j/123456789?meeting={selected_meeting}",
                        "bot_name": "LegalMind Assistant",
                        "audio_required": True,
                        "video_required": False
                    }
        
        elif meeting_method == "Google Meet":
            with st.form("google_meet_form"):
                meeting_link = st.text_input("Google Meet Link", placeholder="https://meet.google.com/abc-defg-hij")
                bot_name = st.text_input("Bot Name", value="LegalMind Assistant")
                
                col1, col2 = st.columns(2)
                with col1:
                    audio_required = st.checkbox("Audio Required", value=True)
                with col2:
                    video_required = st.checkbox("Video Required", value=False)
                
                submitted = st.form_submit_button("Join Meeting")
                
                if submitted and meeting_link:
                    return {
                        "meeting_link": meeting_link,
                        "bot_name": bot_name,
                        "audio_required": audio_required,
                        "video_required": video_required
                    }
        
        return None
    
    @staticmethod
    def meeting_joined_status(bot_id, bot_status=None):
        """Display the status of a joined meeting."""
        st.subheader("Meeting Status")
        
        # Container for status updates
        status_container = st.empty()
        
        with status_container.container():
            st.success("Bot successfully joined the meeting!")
            st.write(f"Bot ID: {bot_id}")
            
            if bot_status:
                st.write(f"Status: {bot_status.get('status', 'Unknown')}")
                if "message" in bot_status:
                    st.write(f"Message: {bot_status['message']}")
            
            st.divider()
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Refresh Status"):
                    return "refresh"
            with col2:
                if st.button("Leave Meeting", type="primary"):
                    return "leave"
            
            # Add a progress placeholder for transcript processing
            st.write("Listening to meeting and processing transcript...")
            progress_bar = st.progress(0)
            
            # Simulate progress (would be updated with real progress in a production app)
            for i in range(100):
                time.sleep(0.05)
                progress_bar.progress(i + 1)
        
        return None
    
    @staticmethod
    def transcript_view(transcript_data):
        """Display the meeting transcript."""
        st.subheader("Meeting Transcript")
        
        if not transcript_data or "transcript" not in transcript_data:
            st.info("No transcript data available yet.")
            return
        
        transcript = transcript_data["transcript"]
        
        if not transcript:
            st.info("Transcript is empty. The meeting may have just started.")
            return
        
        # Display transcript in a nicer format
        for entry in transcript:
            col1, col2 = st.columns([1, 5])
            
            with col1:
                # Display speaker icon and name
                speaker = entry.get("speaker", "Unknown")
                timestamp = entry.get("timestamp", "00:00:00")
                st.markdown(f"**{speaker}** *[{timestamp}]*")
            
            with col2:
                # Display the spoken text
                st.write(entry.get("text", ""))
            
            st.divider()
        
        # Display summary if available
        if "summary" in transcript_data:
            st.subheader("Meeting Summary")
            st.write(transcript_data["summary"])


class ActionItemsUI:
    """UI components for displaying and managing action items."""
    
    @staticmethod
    def action_list(task_manager, filtered_domains=None):
        """Display a list of action items with filtering and sorting options."""
        st.subheader("Legal Action Items")
        
        # Get all actions
        all_actions = task_manager.actions
        
        if not all_actions:
            st.info("No action items have been generated yet. Join a meeting to get started.")
            return
        
        # Filter by domain if specified
        if filtered_domains:
            all_actions = [a for a in all_actions if a.domain in filtered_domains]
        
        # Filter and sort controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_filter = st.multiselect(
                "Status",
                options=["pending", "in_progress", "completed", "cancelled"],
                default=["pending", "in_progress"]
            )
        
        with col2:
            priority_filter = st.multiselect(
                "Priority",
                options=["high", "medium", "low"],
                default=["high", "medium", "low"]
            )
        
        with col3:
            sort_by = st.selectbox(
                "Sort by",
                options=["Priority (High to Low)", "Priority (Low to High)", "Status", "Created (Newest)", "Created (Oldest)"]
            )
        
        # Apply filters
        filtered_actions = [
            action for action in all_actions 
            if action.status in status_filter and action.priority in priority_filter
        ]
        
        # Apply sorting
        if sort_by == "Priority (High to Low)":
            priority_map = {"high": 0, "medium": 1, "low": 2}
            filtered_actions.sort(key=lambda x: priority_map.get(x.priority, 99))
        elif sort_by == "Priority (Low to High)":
            priority_map = {"low": 0, "medium": 1, "high": 2}
            filtered_actions.sort(key=lambda x: priority_map.get(x.priority, 99))
        elif sort_by == "Status":
            status_map = {"pending": 0, "in_progress": 1, "completed": 2, "cancelled": 3}
            filtered_actions.sort(key=lambda x: status_map.get(x.status, 99))
        elif sort_by == "Created (Newest)":
            filtered_actions.sort(key=lambda x: x.created_at, reverse=True)
        elif sort_by == "Created (Oldest)":
            filtered_actions.sort(key=lambda x: x.created_at)
        
        # Display actions
        for action in filtered_actions:
            ActionItemsUI.action_card(action, task_manager)
    
    @staticmethod
    def action_card(action, task_manager):
        """Display a single action item as a card."""
        # Set colors based on priority
        priority_colors = {
            "high": "#FF5733",
            "medium": "#FFC300",
            "low": "#36A2EB"
        }
        
        # Set status badges
        status_badges = {
            "pending": "🟠 Pending",
            "in_progress": "🔵 In Progress",
            "completed": "🟢 Completed",
            "cancelled": "⚫ Cancelled"
        }
        
        # Create card using Streamlit components
        with st.container():
            # Card header with priority indicator
            header_col1, header_col2, header_col3 = st.columns([5, 3, 2])
            
            with header_col1:
                domain_name = LEGAL_DOMAINS.get(action.domain, action.domain)
                st.markdown(f"### {action.title}")
                st.markdown(f"*{domain_name}*")
            
            with header_col2:
                st.markdown(f"**Status:** {status_badges.get(action.status, action.status)}")
                if action.deadline:
                    st.markdown(f"**Deadline:** {action.deadline}")
            
            with header_col3:
                priority_color = priority_colors.get(action.priority, "#777777")
                st.markdown(
                    f"""
                    <div style="
                        background-color: {priority_color}; 
                        color: white; 
                        padding: 5px 10px; 
                        border-radius: 5px; 
                        text-align: center;
                        margin-top: 10px;
                    ">
                        {action.priority.upper()} Priority
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            
            # Card body
            st.markdown(action.description)
            
            # Card footer with actions
            footer_col1, footer_col2, footer_col3, footer_col4 = st.columns([3, 2, 2, 2])
            
            with footer_col1:
                assignee = action.assignee or "Unassigned"
                st.markdown(f"**Assignee:** {assignee}")
            
            with footer_col2:
                if action.status != "in_progress" and st.button("Start", key=f"start_{action.id}"):
                    task_manager.update_action_status(action.id, "in_progress")
                    st.rerun()
            
            with footer_col3:
                if action.status != "completed" and st.button("Complete", key=f"complete_{action.id}"):
                    task_manager.update_action_status(action.id, "completed")
                    st.rerun()
            
            with footer_col4:
                if action.status != "cancelled" and st.button("Cancel", key=f"cancel_{action.id}"):
                    task_manager.update_action_status(action.id, "cancelled")
                    st.rerun()
            
            st.divider()


class InsightsUI:
    """UI components for displaying legal insights."""
    
    @staticmethod
    def insights_list(task_manager, filtered_domains=None):
        """Display a list of legal insights with filtering options."""
        st.subheader("Legal Insights")
        
        # Get all insights
        all_insights = task_manager.insights
        
        if not all_insights:
            st.info("No insights have been generated yet. Join a meeting to get started.")
            return
        
        # Filter by domain if specified
        if filtered_domains:
            all_insights = [i for i in all_insights if i.domain in filtered_domains]
        
        # Filter and sort controls
        col1, col2 = st.columns(2)
        
        with col1:
            importance_filter = st.multiselect(
                "Importance",
                options=["critical", "high", "medium", "low"],
                default=["critical", "high", "medium", "low"]
            )
        
        with col2:
            sort_by = st.selectbox(
                "Sort by",
                options=["Importance (High to Low)", "Importance (Low to High)", "Created (Newest)", "Created (Oldest)"]
            )
        
        # Apply filters
        filtered_insights = [
            insight for insight in all_insights 
            if insight.importance in importance_filter
        ]
        
        # Apply sorting
        if sort_by == "Importance (High to Low)":
            importance_map = {"critical": 0, "high": 1, "medium": 2, "low": 3}
            filtered_insights.sort(key=lambda x: importance_map.get(x.importance, 99))
        elif sort_by == "Importance (Low to High)":
            importance_map = {"low": 0, "medium": 1, "high": 2, "critical": 3}
            filtered_insights.sort(key=lambda x: importance_map.get(x.importance, 99))
        elif sort_by == "Created (Newest)":
            filtered_insights.sort(key=lambda x: x.created_at, reverse=True)
        elif sort_by == "Created (Oldest)":
            filtered_insights.sort(key=lambda x: x.created_at)
        
        # Display insights
        for insight in filtered_insights:
            InsightsUI.insight_card(insight)
    
    @staticmethod
    def insight_card(insight):
        """Display a single insight as a card."""
        # Set colors based on importance
        importance_colors = {
            "critical": "#FF5733",
            "high": "#FFC300",
            "medium": "#36A2EB",
            "low": "#3CBA9F"
        }
        
        # Create card using Streamlit components
        with st.container():
            # Card header with importance indicator
            header_col1, header_col2 = st.columns([7, 3])
            
            with header_col1:
                domain_name = LEGAL_DOMAINS.get(insight.domain, insight.domain)
                st.markdown(f"### {insight.title}")
                st.markdown(f"*{domain_name}*")
            
            with header_col2:
                importance_color = importance_colors.get(insight.importance, "#777777")
                st.markdown(
                    f"""
                    <div style="
                        background-color: {importance_color}; 
                        color: white; 
                        padding: 5px 10px; 
                        border-radius: 5px; 
                        text-align: center;
                        margin-top: 10px;
                    ">
                        {insight.importance.upper()} Importance
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            
            # Card body
            st.markdown(insight.description)
            
            # Card footer with tags
            st.write("Tags:")
            tag_cols = st.columns(len(insight.tags) if insight.tags else 1)
            
            for i, tag in enumerate(insight.tags):
                with tag_cols[i]:
                    st.markdown(
                        f"""
                        <div style="
                            background-color: #f0f0f0; 
                            padding: 3px 8px; 
                            border-radius: 15px; 
                            text-align: center;
                            font-size: 0.8em;
                        ">
                            {tag}
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
            
            st.divider()


class MeetingDetailsUI:
    """UI components for displaying detailed meeting information."""
    
    @staticmethod
    def meeting_details(meeting_id, task_manager):
        """Display detailed information about a specific meeting."""
        meeting = task_manager.get_meeting_by_id(meeting_id)
        
        if not meeting:
            st.error("Meeting not found.")
            return
        
        # Meeting header
        st.title(meeting.title)
        st.write(f"Meeting Date: {meeting.date}")
        
        # Tabs for different views
        tab1, tab2, tab3 = st.tabs(["Summary", "Action Items", "Insights"])
        
        with tab1:
            MeetingDetailsUI.summary_tab(meeting, task_manager)
        
        with tab2:
            MeetingDetailsUI.actions_tab(meeting_id, task_manager)
        
        with tab3:
            MeetingDetailsUI.insights_tab(meeting_id, task_manager)
    
    @staticmethod
    def summary_tab(meeting, task_manager):
        """Display the meeting summary tab."""
        st.subheader("Meeting Summary")
        st.write(meeting.transcript_summary)
        
        # Meeting stats
        st.subheader("Meeting Statistics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            action_count = len(task_manager.get_actions_by_meeting(meeting.id))
            st.metric("Action Items", action_count)
        
        with col2:
            insight_count = len(task_manager.get_insights_by_meeting(meeting.id))
            st.metric("Legal Insights", insight_count)
        
        with col3:
            domains_count = len(meeting.domains_processed)
            st.metric("Legal Domains", domains_count)
        
        # Activity by domain chart
        domain_actions = {}
        domain_insights = {}
        
        for domain in LEGAL_DOMAINS.keys():
            if domain in meeting.domains_processed:
                # Count actions for this domain
                actions = [a for a in task_manager.get_actions_by_meeting(meeting.id) if a.domain == domain]
                domain_actions[domain] = len(actions)
                
                # Count insights for this domain
                insights = [i for i in task_manager.get_insights_by_meeting(meeting.id) if i.domain == domain]
                domain_insights[domain] = len(insights)
        
        # Create dataframe for chart
        chart_data = []
        for domain in domain_actions.keys():
            chart_data.append({
                "Domain": LEGAL_DOMAINS[domain],
                "Type": "Actions",
                "Count": domain_actions[domain]
            })
            chart_data.append({
                "Domain": LEGAL_DOMAINS[domain],
                "Type": "Insights",
                "Count": domain_insights.get(domain, 0)
            })
        
        df = pd.DataFrame(chart_data)
        
        if not df.empty:
            st.subheader("Activity by Legal Domain")
            
            fig = px.bar(
                df,
                x="Domain",
                y="Count",
                color="Type",
                barmode="group",
                color_discrete_sequence=["#36A2EB", "#FF6384"]
            )
            
            fig.update_layout(
                height=400,
                xaxis_title="",
                yaxis_title="Count"
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def actions_tab(meeting_id, task_manager):
        """Display the meeting action items tab."""
        actions = task_manager.get_actions_by_meeting(meeting_id)
        
        if not actions:
            st.info("No action items were generated for this meeting.")
            return
        
        # Display each action
        for action in actions:
            ActionItemsUI.action_card(action, task_manager)
    
    @staticmethod
    def insights_tab(meeting_id, task_manager):
        """Display the meeting insights tab."""
        insights = task_manager.get_insights_by_meeting(meeting_id)
        
        if not insights:
            st.info("No insights were generated for this meeting.")
            return
        
        # Display each insight
        for insight in insights:
            InsightsUI.insight_card(insight)