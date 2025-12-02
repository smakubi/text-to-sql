import json
import os
import hashlib
import streamlit as st

USERS_FILE = "users.json"

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

def save_user(username, password):
    """Save a new user to the JSON file."""
    users = load_users()
    if username in users:
        return False, "User already exists"
    
    users[username] = {
        "password": hash_password(password)
    }
    
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)
    return True, "User created successfully"

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
