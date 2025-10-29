import streamlit as st


client = st.session_state["api_client"]

@st.dialog("Delete User Confirmation")
def delete_user_by_id_dialog(user_id: int):
    """Dialog to confirm user deletion by admin."""
    
    st.write(f"Are you sure you want to delete the user with ID `{user_id}`?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Confirm", use_container_width=True):
            result = client.delete_user_by_id(user_id)
            if verify_error(result):
                return
            st.success("User deleted successfully.")
            st.session_state.pop("fetched_user", None)
            st.rerun()
    with col2:
        if st.button("Cancel", use_container_width=True):
            st.info("User deletion cancelled.")
            st.session_state["show_delete_user_by_id_dialog"] = False
            st.rerun()

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
    
    if "show_delete_user_by_id_dialog" not in st.session_state:
        st.session_state["show_delete_user_by_id_dialog"] = False
    
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
                result_user_list = client.read_all_users(**filters)
                if verify_error(result_user_list):
                    return
                
                st.session_state["users_list"] = result_user_list
        
        result_user_list = st.session_state["users_list"]
        
        # --- Display ---
        st.divider()
        st.subheader("Users List")
        
        if not result_user_list:
            st.info("No users found with the current filters.")
        
        for user in result_user_list:
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
                    result_user = client.read_user_by_id(user_id_input)
                    if verify_error(result_user):
                        return
                    
                    st.session_state["fetched_user"] = result_user
            
            result_user = st.session_state.get("fetched_user")
        
        if st.session_state.get("fetched_user"):
            st.divider()
            st.subheader("User Details")
            
            info_col1, info_col2 = st.columns(2)
            with info_col1:
                st.markdown(f"**Username:** {result_user.get('username')}")
                st.markdown(f"**First name:** {result_user.get('first_name')}")
                st.markdown(f"**Email**: {result_user.get('email')}")
                st.markdown(f"**Active:** {result_user.get('is_active')}")
            
            with info_col2:
                st.markdown(f"**Role:** {result_user.get('role')}")
                st.markdown(f"**Last name:** {result_user.get('last_name')}")
                st.markdown(f"**Phone number:** {result_user.get('phone_number')}")
                st.markdown(f"**ID:** {result_user.get('id')}")
                
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
                        updated_data = {}
                        for f,v in fields.items():
                            if v != result_user.get(f):
                                updated_data[f] = v
                    
                        if not updated_data:
                            st.info("No changes detected.")
                        else:
                            result_message = client.update_user_by_id(user_id_input,
                                                              updated_data)
                            if verify_error(result_message):
                                return
                            st.success("User updated successfully.")
                            st.session_state.pop("fetched_user", None)
                            st.rerun()
                            
            if st.button("Delete User"):
                st.session_state["show_delete_user_by_id_dialog"] = True
            
            if st.session_state["show_delete_user_by_id_dialog"]:
                delete_user_by_id_dialog(user_id_input)