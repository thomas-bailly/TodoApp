import streamlit as st


client = st.session_state["api_client"]

def admin_page_content():
    
    st.title("🛡️ Admin")
    st.write("Work in progress...🚧")
    
    tab1, tab2, tab3 = st.tabs(["All Users", "User", "Todo"])
    
    with tab1:
        col1, col2, col3, col4, col5 = st.columns(5, vertical_alignment="bottom")
        with col1:
            username_filter = st.text_input("Username")
        
        with col2:
            role_filter = st.selectbox(
                "Role",
                options=["", "user", "admin"]
            )
        
        with col3:
            is_active_filter = st.selectbox(
                "Active",
                options=["", True, False]
            )
        
        with col4:
            filter_button = st.button("Filter", use_container_width=True)
            
        with col5:
            reset_button = st.button("Reset", use_container_width=True)
            
        if "users_list" not in st.session_state:
            with st.spinner("Loading Users..."):
                st.session_state["users_list"] = []
        
        