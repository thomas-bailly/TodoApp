import streamlit as st

def todos_page_content() -> None:
    """Render the todos page content."""
    
    client = st.session_state["api_client"]
    st.title("📝 Todos")
    st.write("Placeholder text")