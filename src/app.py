# libs
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
import certifi  # Cross-platform SSL certificate authority bundle

OPENAI_API_KEY = st.secrets["openai"]["OPENAI_API_KEY"]
st.set_page_config(page_title="SQL and Python Agent", layout="wide")

def inject_custom_css(is_dark_mode):
    if is_dark_mode:
        colors = {
            "bg_app": "#18181B",      # Zinc 950 (Softer black)
            "bg_sidebar": "#27272A",  # Zinc 800
            "text": "#FAFAFA",        # Zinc 50
            "card_bg": "#27272A",
            "card_border": "#3F3F46", # Zinc 700
            "input_bg": "#3F3F46",
            "input_border": "#52525B",# Zinc 600
            "input_text": "#FAFAFA",
            "primary": "#3B82F6",     # Solid Blue 500
            "button_text": "#FFFFFF"
        }
    else:
        colors = {
            "bg_app": "#FFFFFF",
            "bg_sidebar": "#F4F4F5",  # Zinc 100
            "text": "#18181B",        # Zinc 900
            "card_bg": "#FFFFFF",
            "card_border": "#E4E4E7", # Zinc 200
            "input_bg": "#FFFFFF",
            "input_border": "#D4D4D8",# Zinc 300
            "input_text": "#18181B",
            "primary": "#2563EB",     # Solid Blue 600
            "button_text": "#FFFFFF"
        }

    st.markdown(f"""
    <style>
        /* Import Google Font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        
        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
            color: {colors['text']};
        }}
        
        /* App Background */
        .stApp {{
            background-color: {colors['bg_app']};
        }}
        
        /* Title - Solid Color, No Gradient */
        h1 {{
            color: {colors['text']};
            font-weight: 800;
            padding-bottom: 10px;
        }}
        
        /* Card-like styling for chat messages */
        .stChatMessage {{
            background-color: {colors['card_bg']};
            border: 1px solid {colors['card_border']};
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 10px;
            box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        }}
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {{
            background-color: {colors['bg_sidebar']};
            border-right: 1px solid {colors['card_border']};
        }}
        
        /* Custom Button - Solid Color */
        div.stButton > button {{
            background-color: {colors['primary']};
            color: {colors['button_text']};
            border: none;
            border-radius: 8px;
            padding: 0.6rem 1.2rem;
            font-weight: 600;
            transition: all 0.2s ease;
            width: 100%;
        }}
        
        div.stButton > button:hover {{
            opacity: 0.9;
            transform: translateY(-1px);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }}
        
        /* Input fields */
        .stTextInput input {{
            border-radius: 8px;
            border: 1px solid {colors['input_border']};
            background-color: {colors['input_bg']};
            color: {colors['input_text']};
        }}
        
        .stTextInput input:focus {{
            border-color: {colors['primary']};
            box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
        }}
        
        /* Text color overrides */
        p, label, .stMarkdown {{
            color: {colors['text']} !important;
        }}
        
        /* Welcome Banner */
        .welcome-banner {{
            background-color: {colors['card_bg']};
            border: 1px solid {colors['card_border']};
            border-left: 5px solid {colors['primary']};
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        
        /* Chat Input Styling */
        .stChatInput textarea {{
            background-color: {colors['input_bg']} !important;
            color: {colors['input_text']} !important;
            border: 1px solid {colors['input_border']} !important;
        }}
        
        /* Fix for the bottom container background to match app background */
        [data-testid="stBottom"], footer, header {{
            background-color: {colors['bg_app']} !important;
        }}
        
        [data-testid="stBottom"] > div {{
            background-color: {colors['bg_app']} !important;
        }}
        
        /* Ensure the main container background is consistent */
        .stApp > header {{
            background-color: {colors['bg_app']} !important;
        }}
        
        .stApp {{
            background-color: {colors['bg_app']};
        }}
        
        /* Chat Input Container */
        .stChatInput {{
            background-color: {colors['bg_app']} !important;
        }}
        
        .stChatInputContainer {{
            background-color: {colors['bg_app']} !important;
        }}
    </style>
    """, unsafe_allow_html=True)

# Theme Toggle
with st.sidebar:
    st.title("⚙️ Appearance")
    is_dark_mode = st.toggle("🌙 Dark Mode", value=True)
    st.markdown("---")

inject_custom_css(is_dark_mode)

def reset_conversation():
    st.session_state.messages = []
    if 'db_config' in st.session_state:
        try:
            st.session_state.agent_memory_sql = initialize_sql_agent(st.session_state.db_config)
            st.session_state.agent_memory_python = initialize_python_agent()
            st.session_state.sql_agent = st.session_state.agent_memory_sql
            st.session_state.python_agent = st.session_state.agent_memory_python
        except:
            pass # Handle case where config is invalid
    else:
        st.warning("Please configure database credentials first")

# 1. Initialize session state.
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

# 2. Sidebar user inputs.
st.sidebar.title("🔌 Connect Database")
st.sidebar.markdown("Configure your **MySQL** connection below to start analyzing data.")
st.sidebar.subheader("Connection Details", divider="rainbow")

user = st.sidebar.text_input("User", value=st.session_state.db_config['USER'], placeholder="root")
password = st.sidebar.text_input("Password", type="password", value=st.session_state.db_config['PASSWORD'], placeholder="********")
host = st.sidebar.text_input("Host", value=st.session_state.db_config['HOST'], placeholder="localhost")
port = st.sidebar.text_input("Port", value=st.session_state.db_config['PORT'], placeholder="3306")

# 3. Single dynamic button label.
button_label = "🚀 Connect & Save" if not st.session_state.db_connected else "🔄 Update Connection"

def test_connection(config):
    """Check DB connectivity and, if successful, fetch all databases."""
    try:
        connection_string = (
            f"mysql+pymysql://{config['USER']}:{urllib.parse.quote_plus(config['PASSWORD'])}"
            f"@{config['HOST']}:{config['PORT']}/"
            f"?ssl_ca={certifi.where()}&ssl_verify_cert=true&ssl_verify_identity=true"
        )
        engine = create_engine(connection_string)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        # If we succeed, fetch list of databases for the dropdown
        try:
            connection = mysql.connector.connect(
                host=config['HOST'],
                user=config['USER'],
                password=config['PASSWORD'],
                port=config['PORT'],
                ssl_ca=certifi.where(),  # Works on Mac, Linux, Windows
                ssl_verify_cert=True,
                ssl_verify_identity=True
            )
            if connection.is_connected():
                cursor = connection.cursor()
                cursor.execute("SHOW DATABASES")
                dbs = [db[0] for db in cursor.fetchall() 
                       if db[0] not in ('sys', 'mysql','performance_schema','information_schema', 'METRICS_SCHEMA')]
                cursor.close()
                connection.close()
                return True, dbs
        except Error as e:
            st.sidebar.error(f"Error fetching databases: {e}")
            return False, []
    except Exception as e:
        st.sidebar.error(f"Connection test failed: {str(e)}")
        return False, []
    return False, []

# 4. Single button to connect/update.
if st.sidebar.button(button_label):
    if all([user, password, host, port]):
        new_config = {
            'USER': user,
            'PASSWORD': password,
            'HOST': host,
            'PORT': port,
            # DATABASE will be selected from dropdown below, so leave it blank initially
            'DATABASE': ''
        }
        with st.spinner("Testing connection..."):
            ok, db_list = test_connection(new_config)
        if ok:
            st.session_state.db_config = new_config
            st.session_state.db_connected = True
            # Store database list in session for the dropdown
            st.session_state.databases = db_list
            st.sidebar.success("✅ Connected successfully!")
        else:
            st.session_state.db_connected = False
            st.session_state.databases = []
    else:
        st.sidebar.error("⚠️ All fields are required")

# 5. If connected, show the databases in a dropdown for selection.
if st.session_state.db_connected and st.session_state.databases:
    st.sidebar.markdown("---")
    db_choice = st.sidebar.selectbox(
        "📂 Select Database",
        options=st.session_state.databases,
        index=st.session_state.databases.index(st.session_state.db_config['DATABASE'])
        if st.session_state.db_config['DATABASE'] in st.session_state.databases else 0
    )
    
    if db_choice and db_choice != st.session_state.db_config['DATABASE']:
        # Update the config to the selected DB
        st.session_state.db_config['DATABASE'] = db_choice
        try:
            st.session_state.sql_agent = initialize_sql_agent(st.session_state.db_config)
            st.session_state.python_agent = initialize_python_agent()
            st.sidebar.success(f"Active Database: {db_choice}")
        except Exception as e:
            st.session_state.db_config['DATABASE'] = ''
            st.sidebar.error(f"Connection to {db_choice} failed: {str(e)}")

    # Add Reset Button to Sidebar
    st.sidebar.markdown("---")
    if st.sidebar.button("🗑️ Reset Conversation"):
        reset_conversation()
        st.rerun()

# Main page
st.title("SQL & Python AI Agent 🤖")
st.markdown("""
    <div class="welcome-banner">
        <p style='font-size: 1.1rem; margin: 0;'>
            <strong>Welcome!</strong> This intelligent agent transforms your natural language questions into 
            <strong>SQL queries</strong> and <strong>Python visualizations</strong>. 
            Connect your database in the sidebar to get started.
        </p>
    </div>
""", unsafe_allow_html=True)

if st.session_state.db_connected and st.session_state.db_config['DATABASE']:
    st.write(
        f"Using database: `{st.session_state.db_config['DATABASE']}` "
        f"at `{st.session_state.db_config['HOST']}:{st.session_state.db_config['PORT']}`"
    )
else:
    st.warning("Not connected. Provide credentials and click the button in the sidebar.")

# Initialize all session state variables
if 'db_connection' not in st.session_state:
    st.session_state.db_connection = None
if 'agent_memory_sql' not in st.session_state:
    st.session_state.agent_memory_sql = None
if 'agent_memory_python' not in st.session_state:
    st.session_state.agent_memory_python = None
if 'connection_tested' not in st.session_state:
    st.session_state.connection_tested = False

# Add connection management functions
def create_db_connection(config):
    """Create and return database connection"""
    try:
        connection_string = (
            f"mysql+pymysql://{config['USER']}:{config['PASSWORD']}@"
            f"{config['HOST']}:{config['PORT']}/{config['DATABASE']}"
            f"?ssl_ca={certifi.where()}&ssl_verify_cert=true&ssl_verify_identity=true"
        )
        engine = create_engine(connection_string, pool_pre_ping=True)
        db = SQLDatabase.from_uri(connection_string)
        return db
    except Exception as e:
        st.sidebar.error(f"Failed to create connection: {str(e)}")
        return None

def verify_connection():
    """Verify database connection is active"""
    if not st.session_state.get('db_config'):
        st.error("Database configuration not found")
        return False
    
    if not st.session_state.get('db_connection'):
        st.error("No active database connection")
        return False
        
    try:
        # Test connection with a simple query
        st.session_state.db_connection.run("SELECT 1")
        return True
    except:
        # Try to reconnect
        st.session_state.db_connection = create_db_connection(st.session_state.db_config)
        return st.session_state.db_connection is not None

def execute_query(query):
    """Execute query with connection verification"""
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        if verify_connection():
            try:
                result = st.session_state.db_connection.run(query)
                return result
            except exc.SQLAlchemyError as e:
                retry_count += 1
                if retry_count == max_retries:
                    st.error(f"Query failed after {max_retries} attempts: {str(e)}")
                    return None
                time.sleep(1)  # Wait before retry
        else:
            st.error("Connection verification failed")
            return None

# Suppress warnings
warnings.filterwarnings("ignore")

# Configure paths
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.join(current_dir, "..")
sys.path.insert(0, parent_dir)

# Set environment variables
os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY


# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Initialize agents only after credentials are available
if 'db_config' in st.session_state:
    if 'agent_memory_sql' not in st.session_state:
        st.session_state.agent_memory_sql = initialize_sql_agent(st.session_state.db_config)
    if 'agent_memory_python' not in st.session_state:
        st.session_state.agent_memory_python = initialize_python_agent()
    
    if 'sql_agent' not in st.session_state:
        st.session_state.sql_agent = st.session_state.agent_memory_sql
    if 'python_agent' not in st.session_state:
        st.session_state.python_agent = st.session_state.agent_memory_python
else:
    st.warning("Please configure database credentials first")


def generate_response(code_type, input_text):
    """Generate responses for both general and database-specific queries"""
    
    # General greetings and help messages
    greetings = ['hello', 'hi', 'hey', 'help', 'what can you do']
    if input_text.lower() in greetings:
        return """Hello! I am a SQL and Python agent designed to help you with:
            1. SQL queries and database analysis
            2. Python data visualization
            3. General database questions

            To get started with database operations, please configure your database connection in the sidebar.
            You can also ask me general questions about SQL, Python, or data analysis!
        """
    
    # Check if database is configured
    if not st.session_state.get('sql_agent'):
        return "Please configure and connect to a database using the sidebar before running queries."

    # Sanitize input
    local_prompt = unidecode.unidecode(input_text)
    
    if code_type == "python":
        try:
            # First get SQL query result
            sql_response = st.session_state.sql_agent.invoke({"input": local_prompt})
            if not sql_response or 'output' not in sql_response:
                return "Failed to get SQL query results"
                
            local_response = sql_response['output']
            print("SQL Response->", local_response)
            
            # Check for invalid/error responses
            exclusion_keywords = ["please provide", "don't know", "more context", 
                                "provide more", "vague request", "no results"]
            if any(keyword in local_response.lower() for keyword in exclusion_keywords):
                return "Unable to generate visualization - no valid data returned from query"
            
            # Generate visualization
            viz_prompt = {"input": "Write code in python to plot the following data\n\n" + local_response}
            return st.session_state.python_agent.invoke(viz_prompt)
            
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return "Failed to generate visualization"
            
    else:  # SQL query
        try:
            return st.session_state.sql_agent.run(local_prompt)
        except Exception as e:
            print(f"SQL query error: {str(e)}")
            return """Failed to execute SQL query. Ensure you have enough OpenAI API credits. This is most likely to be the issue."""




# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] in ("assistant", "error"):
            display_text_with_images(message["content"])
        elif message["role"] == "plot":
            exec(message["content"])
        else:
            st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Please ask your question:"):
    # Display user message in chat
    with st.chat_message("user", avatar="🚀"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    keywords = ["plot", "graph", "chart", "diagram", "visualize", "visualisation", "show"]
    if any(keyword in prompt.lower() for keyword in keywords):
        prev_context = ""
        for msg in reversed(st.session_state.messages):
            if msg["role"] == "assistant":
                prev_context = msg["content"] + "\n\n" + prev_context
                break
        if prev_context:
            prompt += f"\n\nGiven previous agent responses:\n{prev_context}\n"
        response = generate_response("python", prompt)
        if response == "NO_RESPONSE":
            response = "Please try again with a re-phrased query and more context"
            with st.chat_message("error"):
                display_text_with_images(response)
            st.session_state.messages.append({"role": "error", "content": response})
        else:
            code = display_code_plots(response['output'])
            try:
                code = f"import pandas as pd\n{code.replace('fig.show()', '')}"
                code += "st.plotly_chart(fig, theme='streamlit', use_container_width=True)"
                exec(code)
                st.session_state.messages.append({"role": "plot", "content": code})
            except:
                response = "Please try again with a re-phrased query and more context"
                with st.chat_message("error"):
                    display_text_with_images(response)
                st.session_state.messages.append({"role": "error", "content": response})
    else:
        if len(st.session_state.messages) > 1:
            context_length = 0
            prev_context = ""
            for msg in reversed(st.session_state.messages):
                if context_length > 1:
                    break
                if msg["role"] == "assistant":
                    prev_context = msg["content"] + "\n\n" + prev_context
                    context_length += 1
            response = generate_response("sql", f"{prompt}\n\nGiven previous agent responses:\n{prev_context}\n")
        else:
            response = generate_response("sql", prompt)
        with st.chat_message("assistant", avatar="❇️"):
            display_text_with_images(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

# Initialize session state for query
if 'query' not in st.session_state:
    st.session_state.query = ''

# Initialize session state with unique widget keys
if 'query_input_key' not in st.session_state:
    st.session_state.query_input_key = 0
