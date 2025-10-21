import httpx
import os
import streamlit as st
from datetime import datetime, timedelta, timezone
from typing import Any

from todo_client.utils.config import API_BASE_URL


ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

class APIClient:
    """An API client to interact with the backend server."""
    
    def __init__(self):
        self.client = httpx.Client(base_url=API_BASE_URL,
                                   timeout=10.0)
        
    # ---------------------------- Helper Methods ---------------------------- #
    def _get_auth_headers(self) -> dict[str, str]:
        """Get authorization headers from the streamlit session state."""
        
        token = st.session_state.get("auth_token")
        if token:
            # Vrify token expiration
            if self._is_token_expired():
                self.logout()
                st.error("Expired session. Please log in again.")
                st.rerun()  # Rerun to reflect logout
            
            return {"Authorization": f"Bearer {token}"}
        
        return {}
    
    def _is_token_expired(self) -> bool:
        """Verify if the current token is expired."""
        
        login_time_str = st.session_state.get("login_time")
        if not login_time_str:
            return True  # No login time means no valid session
        
        login_time = datetime.fromisoformat(login_time_str)
        expiration_time = login_time + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        return datetime.now(timezone.utc) > expiration_time
    
    def _request(self, method: str, url: str, secure: bool, **kwarrgs) -> dict:
        """Generic method to make API requests."""
        
        # Prepare headers
        headers = kwarrgs.pop("headers", {})
        if secure:
            headers.update(self._get_auth_headers())
            
        try:
            # Make the request
            response = self.client.request(method, url, headers=headers, **kwarrgs)
            response.raise_for_status()

            # Successful response
            if response.status_code >= 200 and response.status_code < 300:
                return response.json() if response.content else {"message": "Success"}
        
        except httpx.HTTPStatusError as e:
            # Handle HTTP errors
            if e.response.status_code == 401:
                self.logout()
                st.error("Unauthorized access. Please log in again.")
                st.rerun()  # Rerun to reflect logout
                return  {"error": "Unauthorized session cleared", "status_code": 401}
            
            # Other HTTP errors
            error_message = e.response.json().get(
                "detail", e.response.text
            ) if e.response.content else str(e)
            
            return {"error": error_message, "status_code": e.response.status_code}
        
        # Handle Request exceptions
        except httpx.RequestError as e:
            st.error(f"Network error or API unreachable: {e}")
            return {"error": "API unreachable", "status_code": 503}
    
    # ---------------------------- Authentication ---------------------------- #
    def login(self, username: str, password: str) -> dict | bool:
        """Login a user and store the auth token in session state."""
        
        url = "/auth/token"
        data = {"username": username, "password": password}
        
        result = self._request("POST", url, secure=False, data=data)

        if "error" not in result:
            # Store token and login time in session state
            st.session_state["auth_token"] = result.get("access_token")
            st.session_state["login_time"] = datetime.now(timezone.utc).isoformat()
            st.session_state["username"] = username
            return True
        
        # Return error
        return False
    
    def register(self, data: dict[str, Any]) -> dict | bool:
        """Register a new user."""
        
        url = "/auth/register"
        result = self._request("POST", url, secure=False, json=data)
        
        if "error" not in result:
            return True
        
        # Return error
        return result
    
    def logout(self) -> None:
        """Logout the current user by clearing session state."""
        keys_to_remove = ["auth_token", "login_time", "username", "user_data"]
        for key in keys_to_remove:
            if key in st.session_state:
                del st.session_state[key]
                
    def read_user_me(self) -> dict:
        """Fetch the current user's profile data."""
        
        url = "/users/me"
        result = self._request("GET", url, secure=True)
        return result