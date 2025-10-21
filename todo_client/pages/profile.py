import streamlit as st


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
    
    # Extract data
    username = user_data.get("username")
    email = user_data.get("email")
    phone_number = user_data.get("phone_number")
    first_name = user_data.get("first_name")
    last_name = user_data.get("last_name")
    role = user_data.get("role")
    
    # Informations
    st.header(f"Welcome, {username}")
    st.markdown("----")
    
    st.subheader("Your Information")
    info_col1, info_col2 = st.columns(2)
    
    with info_col1:
        st.markdown(f"**Username:** {username}")
        st.markdown(f"**First name:** {first_name}")
        st.markdown(f"**Email**: {email}")
        
    with info_col2:
        st.markdown(f"**Role:** {role}")
        st.markdown(f"**Last name:** {last_name}")
        st.markdown(f"**Phone number:** {phone_number}")
        
    st.markdown("----")
    
    # Account management
    st.subheader("Account management")
    manage_col1, manage_col2, manage_col3 = st.columns(3)
    with manage_col1:
        if st.button("Logout"):
            client.logout()
            st.session_state["login_success"] = None
            st.rerun()
    
    with manage_col2:
        if st.button("Edit Profile", help="Opens a secure form."):
            st.info("Profile editing feature coming soon 🚧")
    
    with manage_col3:
        if st.button("Change Password", help="Opens a secure form."):
            st.info("Password changing featur coming soon 🚧")