import streamlit as st
import os
from dotenv import load_dotenv

from todo_client.utils.api_client import APIClient


# ==================== Initialize session state variables ==================== #
if st.session_state.get("auth_token") is None:
    st.session_state["auth_token"] = None
    
if st.session_state.get("login_time") is None:
    st.session_state["login_time"] = None
    
if st.session_state.get("username") is None:
    st.session_state["username"] = None
    
if st.session_state.get("api_client") is None:
    st.session_state["api_client"] = APIClient()

# ========================= Load environment variables ======================= #
load_dotenv()
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# ============================ Home Page Content ============================= #
def home_page_content():
    """Function to display the content of the home page."""
    
    # Title
    st.title("Home Page")
    # Description
    st.markdown("Placeholder for home page content.")

if __name__ == "__main__":
    # Page config
    st.set_page_config(
        page_title="Todo App",
        page_icon=":streamlit:",
        layout="centered",
        initial_sidebar_state="auto"
    )
    
    # Navigation
    pages = [
        st.Page(
            home_page_content,
            title="Home Page",
            icon="🏠"
        )
    ]
    
    # Run the App
    app_navigation = st.navigation(pages=pages, position="sidebar")
    app_navigation.run()