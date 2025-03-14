import os
import sys
import warnings
import streamlit as st
import unidecode
import mysql.connector
from mysql.connector import Error
from langchain_community.utilities import SQLDatabase
import urllib.parse
from helper import display_code_plots, display_text_with_images
from llm_agent import initialize_python_agent, initialize_sql_agent
from constants import LLM_MODEL_NAME
from sqlalchemy import create_engine, exc, text
import pymysql
import time

st.set_page_config(page_title="SQL and Python Agent")
# MAIN PAGE
st.title("SQL and Python Agent")

# 1. Initialize session state here.
if "db_config" not in st.session_state:
    st.session_state.db_config = {
        'USER': '',
        'PASSWORD': '',
        'HOST': 'localhost',
        'DATABASE': '',
        'PORT': '3306'
    }

if "db_connected" not in st.session_state:
    st.session_state.db_connected = False

if 'databases' not in st.session_state:
    st.session_state.databases = []


# SIDE BAR
st.sidebar.title("DATABASE CONFIGURATION")
st.sidebar.subheader("Enter MySQL connection details:", divider=True)
user = st.sidebar.text_input("User", value=st.session_state.db_config['USER'])
password = st.sidebar.text_input("Password", type="password", value=st.session_state.db_config['PASSWORD'])
host = st.sidebar.text_input("Host", value=st.session_state.db_config['HOST'])
port = st.sidebar.text_input("Port", value=st.session_state.db_config['PORT'])


# # 3. Single dynamic button label.
# button_label = "Save and Connect" if not st.session_state.db_connected else "Update Connection"


# def test_connection(config):
#     """Check DB connectivity and, if successful, fetch all databases."""
#     try:
#         connection_string = (
#             f"mysql+pymysql://{config['USER']}:{urllib.parse.quote_plus(config['PASSWORD'])}"
#             f"@{config['HOST']}:{config['PORT']}/"
#         )
#         engine = create_engine(connection_string)
#         with engine.connect() as conn:
#             conn.execute(text("SELECT 1"))

#         # If we succeed, fetch list of databases for the dropdown
#         try:
#             connection = mysql.connector.connect(
#                 host=config['HOST'],
#                 user=config['USER'],
#                 password=config['PASSWORD'],
#                 port=config['PORT']
#             )
#             if connection.is_connected():
#                 cursor = connection.cursor()
#                 cursor.execute("SHOW DATABASES")
#                 dbs = [db[0] for db in cursor.fetchall() 
#                        if db[0] not in ('sys', 'mysql','performance_schema','information_schema')]
#                 cursor.close()
#                 connection.close()
#                 return True, dbs
#         except Error as e:
#             st.sidebar.error(f"Error fetching databases: {e}")
#             return False, []
#     except Exception as e:
#         st.sidebar.error(f"Connection test failed: {str(e)}")
#         return False, []
#     return False, []
# # CHAT INPUT

# if prompt := st.chat_input("Please ask your question:"):
#    with st.chat_message("user", avatar="🚀"):
#      st.markdown(prompt)