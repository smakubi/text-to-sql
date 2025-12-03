import json
import os
import hashlib
import streamlit as st
import jwt
from datetime import datetime, timedelta

USERS_FILE = "users.json"
SECRET_KEY = "vortex-secret-key-change-me" # In production, use st.secrets
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days

def hash_password(password):
    """Hash a password for storing."""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Load users from the JSON file."""
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_user(username, password, first_name="", last_name=""):
    """Save a new user to the JSON file."""
    users = load_users()
    if username in users:
        return False, "User already exists"
    
    users[username] = {
        "password": hash_password(password),
        "first_name": first_name,
        "last_name": last_name
    }
    
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)
    return True, "User created successfully"

def get_user_info(username):
    """Get user details."""
    users = load_users()
    if username in users:
        return {
            "first_name": users[username].get("first_name", ""),
            "last_name": users[username].get("last_name", "")
        }
    # Check if it's admin
    if username == st.secrets.get("auth", {}).get("username", "admin"):
        return {"first_name": "Admin", "last_name": "User"}
        
    return {"first_name": "", "last_name": ""}

def verify_user(username, password):
    """Verify user credentials."""
    # First check secrets/admin (Hardcoded fallback)
    valid_user = st.secrets.get("auth", {}).get("username", "admin")
    valid_pass = st.secrets.get("auth", {}).get("password", "admin")
    
    if username == valid_user and password == valid_pass:
        return True

    # Then check local users
    users = load_users()
    if username in users:
        if users[username]["password"] == hash_password(password):
            return True
            
    return False

def update_user_settings(username, settings):
    """Update settings for a specific user."""
    users = load_users()
    if username not in users:
        # If it's the admin user or a secrets user, we can't save to json easily unless we create an entry
        # For now, let's only support saving for users in the json file or create a placeholder
        if username == st.secrets.get("auth", {}).get("username", "admin"):
             # Create a special entry for admin settings if not exists
             if username not in users:
                 users[username] = {"password": ""} # Dummy password for admin in file
    
    if "settings" not in users[username]:
        users[username]["settings"] = {}
        
    users[username]["settings"].update(settings)
    
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)
    return True

def get_user_settings(username):
    """Get settings for a specific user."""
    users = load_users()
    if username in users:
        return users[username].get("settings", {})
    return {}

def create_access_token(data: dict):
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str):
    """Verify a JWT access token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except jwt.PyJWTError:
        return None
