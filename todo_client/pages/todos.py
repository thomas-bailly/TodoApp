import streamlit as st

def todos_page_content() -> None:
    """Render the todos page content."""
    
    client = st.session_state["api_client"]
    st.title("📝 Todos")
    
    result = client.read_all_todos()
    if isinstance(result, dict):
        status_code = result.get("status_code")
        st.error(f"Error: {result.get("error")} [status code: {status_code}]")
        if status_code == 401:
            st.warning("Expired session. Please log in again.")
    
    if not result:
        st.info("Congratulations! You don't have any more tasks to complete.")
        return
    
    st.header(f"Your Todos ({len(result)})")
    st.markdown("---")
    col1, col2, col3 = st.columns(3, vertical_alignment="bottom")
    
    with col1:
        complete_opt = st.selectbox("Complete", ["--", False, True])
        
    with col2:
        search_opt = st.text_input("Start with:", help="Search todos by title or description")
    
    with col3:
        if st.button("Filter", width=100):
            st.info("Filter feature comming soon")
    
    for i, todo in enumerate(result):
        
        extender_text = f"**{todo.get('title')}** - Priority: **{todo.get('priority')}**"
        extender_text += f" (ID: {todo.get('id')})"
        extender_icon = "✅" if todo.get('complete') is True else "⏳"
        
        with st.expander(extender_text, icon=extender_icon):
            st.write(f"**Description:** {todo.get('description')}")
            
            ext_col1, ext_col2 = st.columns(2)
            with ext_col1:
                st.button("Edit", key=f"edit_{i}", width=200)
            with ext_col2:
                st.button("Delete", key=f"delete_{i}", width=200)