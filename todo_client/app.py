import streamlit as st
from pathlib import Path

from todo_client.utils.api_client import APIClient

# ==================== Initialize session state variables ==================== #
if st.session_state.get("auth_token") is None:
    st.session_state["auth_token"] = None
    
if st.session_state.get("login_time") is None:
    st.session_state["login_time"] = None
    
if st.session_state.get("username") is None:
    st.session_state["username"] = None

if st.session_state.get("login_success") is None:
    st.session_state["login_success"] = None

if st.session_state.get("api_client") is None:
    st.session_state["api_client"] = APIClient()

# ============================== Pages Content =============================== #
from todo_client.pages.login import login_page_content
from todo_client.pages.profile import profile_page_content

def home_page_content():
    """Function to display the content of the home page."""
    
    # Title
    st.title("Home Page")
    # Description
    st.markdown("Placeholder for home page content.")
    
# ========================= Logout Handler Function ========================== #

def logout_handler():
    """Execute logout and redirect to the home page."""

    st.session_state["login_success"] = None
    client = st.session_state.get("api_client")
    client.logout()
    
    st.switch_page(app_navigation)

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
    
    if st.session_state.get("auth_token"):
        pages.extend(
            [
                st.Page(profile_page_content, title="Profile", icon="👤"),
                st.Page(logout_handler, title="Logout", icon="⬅️")
            ]
        )
    else:
        pages.append(st.Page(login_page_content, title="Login",icon="🔑"))
    
    # Run the App
    app_navigation = st.navigation(pages=pages, position="sidebar")
    app_navigation.run()