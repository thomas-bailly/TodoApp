import streamlit as st


client = st.session_state["api_client"]

def login_page_content() -> None:
    """Render the login page content."""
    
    st.title("🔑 Login")
    st.write("Please enter your credentials to log in.")
    
    # Login form
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_button = st.form_submit_button("Login")
        
        if submit_button:
            success = client.login(username, password)
            if success:
                st.session_state["login_success"] = True
                st.rerun()  # Rerun to reflect login
            else:
                st.error("Login failed. Please check your credentials.")
    
        if st.session_state.get("login_success"):
            st.success("Logged successful!")
    
    # Register form
    st.markdown("---")
    st.title("📝 Register")
    st.write("Don't have an account? Register below.")
    
    with st.form("register_form"):
        reg_username = st.text_input("Username (new account)", key="reg_username")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        reg_email = st.text_input("Email", key="reg_email")
        reg_role = st.selectbox("Role", options=["user", "admin"], key="reg_role")
        register_button = st.form_submit_button("Register")
        
        if register_button:
            data = {
                "username": reg_username,
                "password": reg_password,
                "email": reg_email,
                "role": reg_role
            }
            
            result = client.register(data)
            if result is True:
                st.success("Registration successful! You can now log in.")
            else:
                st.error(f"Registration failed: {result.get('error', 'Unknown error')}")