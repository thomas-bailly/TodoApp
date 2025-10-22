import streamlit as st
import time

def profile_page_content() -> None:
    """Render the profile page content."""
    
    client = st.session_state["api_client"]
    st.title("👤 Profile")
    
    # Fetch user's profile data
    user_data = client.read_user_me()
    
    # Error handling
    if "error" in user_data:
        st.error(f"Unable to fetch profile : {user_data.get('error')}")
        if user_data.get("status_code") == 401:
            st.warning("Expired session. Please log in again.")
        return
    
    # Informations
    st.header(f"Welcome {user_data.get("username")}")
    st.markdown("----")
    
    st.subheader("Your Information")
    info_col1, info_col2 = st.columns(2)
    
    with info_col1:
        st.markdown(f"**Username:** {user_data.get("username")}")
        st.markdown(f"**First name:** {user_data.get("first_name")}")
        st.markdown(f"**Email**: {user_data.get("email")}")
        
    with info_col2:
        st.markdown(f"**Role:** {user_data.get("role")}")
        st.markdown(f"**Last name:** {user_data.get("last_name")}")
        st.markdown(f"**Phone number:** {user_data.get("phone_number")}")
        
    st.markdown("----")
    
    # Account management
    st.subheader("Account management")
    # Edit profile form
    with st.expander("✏️ Edit Profile"):
        with st.form("edit_profile_form"):
            
            # Input fields
            fields = {
                "username":st.text_input(
                    "Username", value=user_data.get("username") or ""
                    ),
                "email":st.text_input(
                    "Email", value=user_data.get("email") or ""
                    ),
                "phone_number":st.text_input(
                    "Phone number", value=user_data.get("phone_number") or ""
                    ),
                "first_name":st.text_input(
                    "First name", value=user_data.get("first_name") or ""
                    ),
                "last_name":st.text_input(
                    "Last name", value=user_data.get("phone_number") or ""
                    )   
            }
            # Submit button
            edit_submitted = st.form_submit_button("Save changes")
            
            # Handle submission
            if edit_submitted:
                
                # Prepare data for request
                updated_data = {
                    f:v for f,v in fields.items() if v != "" 
                    and v != user_data.get(f)
                }
                
                result = client.update_user_me(updated_data)
                
                if "error" in result:
                    st.error(f"Update failed: {result['error']}")
                else:
                    st.success("Profile updated successfully")
                    time.sleep(1)
                    st.rerun()
    
    # Change password form            
    with st.expander("✏️ Change Password"):
        with st.form("change_password_form"):
            # Input fields
            old_password = st.text_input("Old Password", value="", type="password")
            new_password = st.text_input("New Password", value="", type="password")
            password_submitted = st.form_submit_button("Save changes")
            
            # Handle submission
            if password_submitted:
                st.info("Change Password feature comming soon 🚧")
                
                # Prepare data for request
                password_data = {
                    "old_password": old_password,
                    "new_password": new_password
                }
                
    if st.button("Logout", icon="⬅️"):
        client.logout()
        st.session_state["login_success"] = None
        st.rerun()