#-------------------------------------------------------------------------------------#
# app.py
#-------------------------------------------------------------------------------------#
# SETUP:
#
# Setup venv and install the requirements
# 1. Create a virtual environment -> python -m venv venv
# 2. Activate the virtual environment -> .\venv\Scripts\Activate
# 3. Install the requirements -> pip install -r requirements.txt
# 4. Run the streamlit app -> streamlit run app/frontend/app.py
#
# Git Commands:
# 1. Initialize repository -> git init
# 2. Add files to staging -> git add .
# 3. Commit changes -> git commit -m "your message"
# 4. Create new branch -> git checkout -b branch-name
# 5. Switch branches -> git checkout branch-name
# 6. Push to remote -> git push -u origin branch-name
# 7. Pull latest changes -> git pull origin branch-name
# 8. Check status -> git status
# 9. View commit history -> git log
#-------------------------------------------------------------------------------------#

import streamlit as st
import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title="S.A.T.O.R.I. AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and description
st.title("S.A.T.O.R.I. AI")
st.markdown("**System for Agentic Tasks, Orchestration, and Real-time Intelligence**")

# Sidebar
with st.sidebar:
    st.header("Navigation")
    page = st.radio(
        "Select a page",
        ["Home", "Discovery", "Tasks", "Knowledge Base"]
    )

# Main content
if page == "Home":
    st.header("Welcome to S.A.T.O.R.I. AI")
    st.markdown("""
    ### Features
    - 🤖 Multi-Agent Orchestration
    - ⚡ Task Automation
    - 🧠 Real-Time Intelligence
    - 📚 Knowledge Management
    """)

    # Check API connection
    try:
        response = requests.get(f"http://localhost:{os.getenv('API_PORT', '8000')}")
        if response.status_code == 200:
            st.success("Backend API is operational")
        else:
            st.error("Backend API is not responding correctly")
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to backend API")

elif page == "Discovery":
    st.header("Self-Discovery & Growth")
    st.markdown("Coming soon...")

elif page == "Tasks":
    st.header("Task Automation")
    st.markdown("Coming soon...")

elif page == "Knowledge Base":
    st.header("Knowledge Management")
    st.markdown("Coming soon...") 