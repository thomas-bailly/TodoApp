import streamlit as st


client = st.session_state["api_client"]

def verify_error(result: list[dict] | dict) -> bool:
    """Check API result and display any error message."""
    if not isinstance(result, dict):
        return False
    
    status_code = result.get("status_code")
    if status_code is None:
        return False
    st.error(f"Error: {result.get('error')} [status code: {status_code}]")
    if status_code == 401:
        st.warning("Expired session. Please log in again.")
        return True

def admin_page_content():
    
    st.title("🛡️ Admin")
    st.write("Work in progress...🚧")
    
    if "users_filters" not in st.session_state:
        st.session_state["users_filters"] = {"role": None, "username": None,
                                          "is_active": None}
    
    filters = st.session_state.get('users_filters')
    
    tab1, tab2, tab3 = st.tabs(["All Users", "User", "Todo"])
    
    with tab1:
        col1, col2, col3, col4, col5 = st.columns(5, vertical_alignment="bottom")
        with col1:
            username_filter = st.text_input("Username",
                                            help="Find usernames that start with the pattern provided.")
        
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
            if st.button("Filter", use_container_width=True):
                username = username_filter.strip() or None if username_filter else None
                role = None if role_filter == "" else role_filter
                is_active = None if is_active_filter == "" else is_active_filter
                st.session_state["users_filters"] = {
                    "username": username,
                    "role": role,
                    "is_active": is_active
                }
                st.session_state.pop("users_list", None)
                st.rerun()
            
        with col5:
            if st.button("Reset", use_container_width=True):
                st.session_state["users_filters"] = {
                    "username": None,
                    "role": None,
                    "is_active": None
                }
                st.session_state.pop("users_list", None)
                st.rerun()
            
        if "users_list" not in st.session_state:
            with st.spinner("Loading Users..."):
                result = client.read_all_users(**filters)
                if verify_error(result):
                    return
                
                st.session_state["users_list"] = result
        
        result = st.session_state["users_list"]
        
        # --- Display ---
        st.divider()
        st.subheader("Users List")
        
        if not result:
            st.info("No users found with the current filters.")
        
        for user in result:
            user_text = f"**{user.get('username')}** - Role: **{user.get('role')}**"
            user_text += f"- Active: **{user.get('is_active')}** - ID: `{user.get('id')}`"
            
            st.write(user_text)
            
    with tab2:
        col1, col2 = st.columns(2, vertical_alignment="bottom")
        with col1:
            user_id_input = st.number_input(
                "User ID",
                value=None,
                step=1,
                help="Enter the ID of the user to fetch details."
            )
        with col2:
            if st.button("Fetch User", use_container_width=True):
                if user_id_input is None:
                    st.warning("Please provide a User ID.")
                else:
                    result = client.read_user_by_id(user_id_input)
                    if verify_error(result):
                        return
                    
                    st.session_state["fetched_user"] = result
            
            result = st.session_state.get("fetched_user")
        
        if result:
            st.divider()
            st.subheader("User Details")
            
            info_col1, info_col2 = st.columns(2)
            with info_col1:
                st.markdown(f"**Username:** {result.get('username')}")
                st.markdown(f"**First name:** {result.get('first_name')}")
                st.markdown(f"**Email**: {result.get('email')}")
                st.markdown(f"**Active:** {result.get('is_active')}")
            
            with info_col2:
                st.markdown(f"**Role:** {result.get('role')}")
                st.markdown(f"**Last name:** {result.get('last_name')}")
                st.markdown(f"**Phone number:** {result.get('phone_number')}")
                st.markdown(f"**ID:** {result.get('id')}")
                
            st.divider()
            with st.expander("🛠️ Edit User"):
                with st.form("edit_user_form"):
                    # Input fields
                    fields = {
                        "is_active": st.selectbox(
                            "Active Status",
                            options=[True, False]
                        ),
                        "role": st.selectbox(
                            "Role",
                            options=["user", "admin"]
                        )
                    }
                    # Submit button
                    if st.form_submit_button("Update User"):
                        st.info("Work in progress...")