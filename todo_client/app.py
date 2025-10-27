import streamlit as st

from todo_client.utils.api_client import APIClient

# ==================== Initialize session state variables ==================== #
if st.session_state.get("auth_token") is None:
    st.session_state["auth_token"] = None
    
if st.session_state.get("login_time") is None:
    st.session_state["login_time"] = None
    
if st.session_state.get("username") is None:
    st.session_state["username"] = None
    
if st.session_state.get("user_role") is None:
    st.session_state["user_role"] = None

if st.session_state.get("login_success") is None:
    st.session_state["login_success"] = None

if st.session_state.get("api_client") is None:
    st.session_state["api_client"] = APIClient()
    
if st.session_state.get("show_logout_dialog") is None:
    st.session_state["show_logout_dialog"] = False

# ============================== Pages Content =============================== #
from todo_client.pages.login import login_page_content
from todo_client.pages.profile import profile_page_content
from todo_client.pages.todos import todos_page_content
from todo_client.pages.admin import admin_page_content

def home_page_content():
    """Function to display the content of the home page."""
    
    # Title
    st.title("Home Page")
    # Description
    st.markdown("Placeholder for home page content.")
    
# ========================= Logout Handler Function ========================== #
@st.dialog("Logout Confirmation", dismissible=False)
def logout_handler():
    """Execute logout and redirect to the home page."""

    st.write("Are you sure you want to logout?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Confirm", use_container_width=True):
            st.session_state["login_success"] = None
            client = st.session_state.get("api_client")
            client.logout()
            st.session_state["show_logout_dialog"] = False
            st.rerun()
    with col2:
        if st.button("Cancel", use_container_width=True):
            st.info("Work in progress...")
            st.session_state["show_logout_dialog"] = False
            st.rerun()
            

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
                st.Page(todos_page_content, title="Todos", icon="📝"),
            ]
        )
        
        if st.session_state.get("user_role") == "admin":
            pages.append(st.Page(admin_page_content, icon="🛡️", title="Admin"))
            
        if st.sidebar.button("Logout", icon="⬅️", width="content"):
            st.session_state["show_logout_dialog"] = True
        
    else:
        pages.append(st.Page(login_page_content, title="Login",icon="🔑"))
    
    if st.session_state.get("show_logout_dialog"):
        logout_handler()
    
    # Run the App
    app_navigation = st.navigation(pages=pages, position="sidebar")
    app_navigation.run()