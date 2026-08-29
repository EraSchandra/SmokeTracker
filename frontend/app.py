import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import plotly.express as px

API_URL = "http://127.0.0.1:8000/logs"

# Session state initialization
if 'edit_log_id' not in st.session_state:
    st.session_state.edit_log_id = None
if 'delete_log_id' not in st.session_state:
    st.session_state.delete_log_id = None

st.set_page_config(
    page_title="SmokeTracker AI",
    page_icon="🚭",
    layout="wide"
)

st.title("🚭 SmokeTracker AI")
st.caption("AI-powered Smoking Habit Analysis")

# Sidebar for data entry
with st.sidebar:
    st.header("Log a Smoke 📝")
    
    with st.form("log_form"):
        cigarettes = st.number_input("Number of Cigarettes", min_value=1, value=1)
        mood = st.selectbox("Mood", ["Stressed", "Bored", "Social", "Happy", "Anxious", "Other"])
        stress_level = st.slider("Stress Level (1-10)", min_value=1, max_value=10, value=5)
        location = st.text_input("Location (e.g., Home, Work, Bar)")
        reason = st.text_area("Reason / Triggers")
        
        submitted = st.form_submit_button("Log Entry")
        
        if submitted:
            payload = {
                "cigarettes": cigarettes,
                "mood": mood,
                "stress_level": stress_level,
                "location": location,
                "reason": reason,
                "smoked_at": datetime.now().isoformat()
            }
            try:
                res = requests.post(API_URL, json=payload)
                if res.status_code == 200:
                    st.success("Log saved successfully!")
                    st.rerun()
                else:
                    st.error("Failed to save log.")
            except Exception as e:
                st.error(f"Error connecting to server: {e}")

# Main Dashboard Content
try:
    response = requests.get(API_URL)
    response.raise_for_status()
    logs = response.json()
except Exception as e:
    st.error(f"Error fetching data: {e}")
    logs = []

if not logs:
    st.info("No logs found. Start by adding a log in the sidebar!")
else:
    df = pd.DataFrame(logs)
    df['smoked_at'] = pd.to_datetime(df['smoked_at'])
    df['date'] = df['smoked_at'].dt.date
    
    # Filter out invalid stress levels for calculations
    valid_stress_df = df[(df['stress_level'] >= 1) & (df['stress_level'] <= 10)]
    
    # Calculate metrics
    # Use timezone-aware today matching the server's time
    today = datetime.now().date()
    today_logs = df[df['smoked_at'].dt.date == today]
    total_cigarettes_today = today_logs['cigarettes'].sum() if not today_logs.empty else 0
    total_cigarettes_all = df['cigarettes'].sum()
    avg_stress = valid_stress_df['stress_level'].mean() if not valid_stress_df.empty else 0

    
    # Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🚬 Cigarettes Today", int(total_cigarettes_today))
    with col2:
        st.metric("📊 Total Cigarettes (All Time)", int(total_cigarettes_all))
    with col3:
        st.metric("🧠 Avg Stress Level", f"{avg_stress:.1f}/10")
    with col4:
        st.metric("📝 Total Entries", len(logs))
        
    st.divider()

    # Charts Row
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.subheader("Cigarettes Over Time")
        daily_counts = df.groupby('date')['cigarettes'].sum().reset_index()
        fig_trend = px.line(daily_counts, x='date', y='cigarettes', markers=True)
        st.plotly_chart(fig_trend, use_container_width=True)
        
    with chart_col2:
        st.subheader("Smoking by Mood")
        mood_counts = df.groupby('mood')['cigarettes'].sum().reset_index()
        fig_mood = px.pie(mood_counts, values='cigarettes', names='mood', hole=0.4)
        st.plotly_chart(fig_mood, use_container_width=True)
        
    st.divider()
    
    # AI Insights Section
    st.subheader("🧠 AI Insights")
    if st.button("Analyze My Patterns"):
        with st.spinner("Analyzing your data patterns..."):
            try:
                insights_res = requests.get(f"{API_URL}/insights")
                if insights_res.status_code == 200:
                    data = insights_res.json()
                    st.info(data.get("insight", "No insights available."))
                    st.caption("⚠️ Note: This AI analysis observes your logged data trends and is not medical advice or a medical diagnosis.")
                else:
                    st.error("Failed to generate insights.")
            except Exception as e:
                st.error(f"Error connecting to AI service: {e}")
                
    st.divider()
    
    # Data Table
    st.subheader("Recent Logs")
    
    # Sort logs manually by smoked_at descending for display
    sorted_logs = sorted(logs, key=lambda x: x['smoked_at'], reverse=True)
    
    for log in sorted_logs:
        log_id = log['id']
        
        # Display either the edit form or the standard view
        if st.session_state.edit_log_id == log_id:
            with st.container(border=True):
                st.write(f"**Editing Log ID {log_id}**")
                with st.form(f"edit_form_{log_id}"):
                    edit_cigs = st.number_input("Cigarettes", min_value=1, value=log['cigarettes'])
                    mood_options = ["Stressed", "Bored", "Social", "Happy", "Anxious", "Other"]
                    default_mood_idx = mood_options.index(log['mood']) if log['mood'] in mood_options else 0
                    edit_mood = st.selectbox("Mood", mood_options, index=default_mood_idx)
                    
                    # Safely handle stress levels out of bounds in existing data when rendering form
                    safe_stress = log['stress_level']
                    if safe_stress < 1: safe_stress = 1
                    if safe_stress > 10: safe_stress = 10
                    edit_stress = st.slider("Stress Level (1-10)", min_value=1, max_value=10, value=safe_stress)
                    
                    edit_loc = st.text_input("Location", value=log['location'])
                    edit_reason = st.text_area("Reason", value=log['reason'])
                    edit_time = st.text_input("Time (ISO)", value=log['smoked_at'])
                    
                    col_save, col_cancel = st.columns([1, 4])
                    with col_save:
                        if st.form_submit_button("Save"):
                            payload = {
                                "cigarettes": edit_cigs,
                                "mood": edit_mood,
                                "stress_level": edit_stress,
                                "location": edit_loc,
                                "reason": edit_reason,
                                "smoked_at": edit_time
                            }
                            try:
                                res = requests.put(f"{API_URL}/{log_id}", json=payload)
                                if res.status_code == 200:
                                    st.session_state.edit_log_id = None
                                    st.success("Updated successfully!")
                                    st.rerun()
                                else:
                                    st.error(f"Failed: {res.text}")
                            except Exception as e:
                                st.error(f"Error: {e}")
                    with col_cancel:
                        if st.form_submit_button("Cancel"):
                            st.session_state.edit_log_id = None
                            st.rerun()
                            
        elif st.session_state.delete_log_id == log_id:
            with st.container(border=True):
                st.warning(f"Are you sure you want to delete this log from {log['smoked_at']}?")
                col_yes, col_no = st.columns([1, 4])
                with col_yes:
                    if st.button("Yes, Delete", key=f"del_yes_{log_id}"):
                        try:
                            res = requests.delete(f"{API_URL}/{log_id}")
                            if res.status_code == 200:
                                st.session_state.delete_log_id = None
                                st.success("Deleted successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to delete.")
                        except Exception as e:
                            st.error(f"Error: {e}")
                with col_no:
                    if st.button("Cancel", key=f"del_no_{log_id}"):
                        st.session_state.delete_log_id = None
                        st.rerun()
                        
        else:
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([4, 2, 1, 1])
                parsed_time = datetime.fromisoformat(log['smoked_at']).strftime("%Y-%m-%d %H:%M")
                
                with c1:
                    st.write(f"🚬 **{log['cigarettes']}** | 🧠 Stress: **{log['stress_level']}/10** | 📍 {log['location']}")
                    st.caption(f"{parsed_time} - {log['reason']}")
                with c2:
                    st.write(f"*{log['mood']}*")
                with c3:
                    if st.button("Edit", key=f"edit_{log_id}"):
                        st.session_state.edit_log_id = log_id
                        st.rerun()
                with c4:
                    if st.button("Delete", key=f"del_{log_id}", type="primary"):
                        st.session_state.delete_log_id = log_id
                        st.rerun()