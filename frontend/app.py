#-------------------------------------------------------------------------------------#
# app.py
#-------------------------------------------------------------------------------------#
# SETUP:
#
# Setup venv and install the requirements
# 1. Create a virtual environment -> python -m venv venv
# 2. Activate the virtual environment -> .\venv\Scripts\Activate
# 3. Install the requirements -> pip install -r requirements.txt
# 4. Run the streamlit app -> streamlit run frontend/app.py
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
import time
from components.chat import initialize_chat
import signal
import sys
import atexit
import logging
import asyncio

# Load environment variables
load_dotenv()

# Configure page with custom theme
st.set_page_config(
    page_title="S.A.T.O.R.I. AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS for better visibility
st.markdown("""
    <style>
    .success-message { color: #28a745; }
    .error-message { color: #dc3545; }
    .info-message { color: #17a2b8; }
    .chat-message { margin: 1rem 0; padding: 0.5rem; border-radius: 0.5rem; }
    .user-message { background-color: #e9ecef; text-align: right; }
    .system-message { background-color: #f8f9fa; }
    .agent-message { background-color: #e3f2fd; }
    </style>
""", unsafe_allow_html=True)

# Title and description with loading animation
with st.spinner('🌟 Initializing S.A.T.O.R.I. AI...'):
    time.sleep(1)  # Simulate initialization
    st.title("🧠 S.A.T.O.R.I. AI")
    st.markdown("**System for Agentic Tasks, Orchestration, and Real-time Intelligence**")

# Sidebar with status indicators
with st.sidebar:
    st.header("🎯 Navigation")
    
    # System Status
    st.subheader("🔧 System Status")
    
    # Check API connection with a progress bar
    with st.spinner('Checking API connection...'):
        try:
            response = requests.get(f"http://localhost:{os.getenv('PORT', '8000')}")
            if response.status_code == 200:
                st.success("⚡ Backend API: Connected")
                st.info(f"🔄 API Version: {response.json().get('version', 'Unknown')}")
            else:
                st.error("❌ Backend API: Connection Error")
        except requests.exceptions.ConnectionError:
            st.error("❌ Backend API: Offline")
    
    # Navigation Menu
    st.subheader("📍 Menu")
    page = st.radio(
        "Select a page",
        ["🏠 Home", "🧭 Chat", "🧭 Discovery", "⚡ Tasks", "📚 Knowledge Base"]
    )

# Global declarations
global chat_instance
chat_instance = None

def cleanup():
    """Clean up resources during shutdown."""
    global chat_instance
    logger = logging.getLogger(__name__)
    logger.info("Cleaning up Streamlit application...")
    
    if chat_instance:
        asyncio.run(chat_instance.disconnect_websocket())
    
    logger.info("Streamlit application cleanup complete")

def signal_handler(signum, frame):
    """Handle system signals."""
    logger = logging.getLogger(__name__)
    logger.info(f"Received signal {signum}")
    cleanup()
    sys.exit(0)

# Register shutdown handlers
atexit.register(cleanup)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Main content with animations
if "🏠 Home" in page:
    st.header("🌟 Welcome to S.A.T.O.R.I. AI")
    
    # Feature showcase with progress bar
    with st.spinner('Loading features...'):
        time.sleep(0.5)  # Simulate loading
        st.markdown("""
        ### ✨ Core Features
        - 🤖 **Multi-Agent Orchestration**
          - Dynamic framework powered by LangGraph and LangChain
        - ⚡ **Task Automation**
          - Streamline personal and professional workflows
        - 🧠 **Real-Time Intelligence**
          - Immediate, actionable insights
        - 📚 **Knowledge Management**
          - AI-powered learning and organization
        """)

elif "🧭 Chat" in page:
    if chat_instance is None:
        chat_instance = initialize_chat()
    chat_instance.render()

elif "🧭 Discovery" in page:
    st.header("🧭 Self-Discovery & Growth")
    st.info("🚧 Coming soon... We're crafting something special!")

elif "⚡ Tasks" in page:
    st.header("⚡ Task Automation")
    st.info("🚧 Coming soon... Automation magic in progress!")

elif "📚 Knowledge Base" in page:
    st.header("📚 Knowledge Management")
    st.info("🚧 Coming soon... Building your knowledge fortress!") 