import streamlit as st
import os
from dotenv import load_dotenv


def home_page_content():
    """Function to display the content of the home page."""
    
    # Title
    st.title("Home Page")
    # Description
    st.markdown("Placeholder for home page content.")

load_dotenv()
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

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