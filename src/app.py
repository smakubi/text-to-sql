import streamlit as st
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_core.messages import AIMessage, HumanMessage
from langchain_community.chat_message_histories import ChatMessageHistory
import warnings

# Internal modules
from llm_agent import initialize_sql_agent, initialize_python_agent
from helper import display_code_plots, display_text_with_images, inject_custom_css
from database import test_connection, get_snowflake_schemas
from auth import verify_user, save_user, update_user_settings, get_user_settings, get_user_info

# Suppress warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="databricks.sql")
warnings.filterwarnings("ignore", message="Parameter '_user_agent_entry' is deprecated")

# Page Config
st.set_page_config(page_title="Vortex", page_icon="◈", layout="wide")
OPENAI_API_KEY = st.secrets["openai"]["OPENAI_API_KEY"]

def init_session_state():
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "db_connected" not in st.session_state:
        st.session_state.db_connected = False
    if "db_config" not in st.session_state:
        st.session_state.db_config = {
            'TYPE': 'MySQL',
            'USER': '',
            'PASSWORD': '',
            'HOST': '',
            'PORT': '3306',
            'DATABASE': '',
            'HTTP_PATH': '',
            'CATALOG': '',
            'WAREHOUSE': '',
            'ROLE': '',
            'SCHEMA': 'PUBLIC'
        }
    if "databases" not in st.session_state:
        st.session_state.databases = []
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = False
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "current_user" not in st.session_state:
        st.session_state.current_user = None
    if "current_user_fullname" not in st.session_state:
        st.session_state.current_user_fullname = None
    if "view_mode" not in st.session_state:
        st.session_state.view_mode = "chat" # chat or profile
    if "saved_connections" not in st.session_state:
        st.session_state.saved_connections = {}
    
    # Agent Memory
    if "agent_memory_sql" not in st.session_state:
        st.session_state.agent_memory_sql = None
    if "agent_memory_python" not in st.session_state:
        st.session_state.agent_memory_python = None
    if "sql_agent" not in st.session_state:
        st.session_state.sql_agent = None
    if "python_agent" not in st.session_state:
        st.session_state.python_agent = None

def login_page():
    """Render the login page."""
    # Adaptive colors based on dark mode
    is_dark = st.session_state.get('dark_mode', False)
    text_secondary = "#a0a0b0" if is_dark else "#6b7280"
    divider_color = "rgba(255, 255, 255, 0.1)" if is_dark else "#e5e7eb"
    
    st.markdown(f"""
        <style>
            .login-container {{
                max-width: 420px;
                margin: 0 auto;
                padding: 2rem;
            }}
            .login-header {{
                text-align: center;
                margin-bottom: 2rem;
            }}
            .login-header h1 {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                font-size: 3.5rem;
                font-weight: 700;
                color: #667eea;
                margin-bottom: 0.5rem;
                letter-spacing: -0.02em;
            }}
            .login-header p {{
                color: {text_secondary};
                font-size: 1.1rem;
            }}
            .login-card {{
                background: white;
                border-radius: 16px;
                padding: 2rem;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                border: 1px solid rgba(0, 0, 0, 0.05);
            }}
            .social-divider {{
                display: flex;
                align-items: center;
                text-align: center;
                margin: 1.5rem 0;
                color: {text_secondary};
                font-size: 0.875rem;
            }}
            .social-divider::before,
            .social-divider::after {{
                content: '';
                flex: 1;
                border-bottom: 1px solid {divider_color};
            }}
            .social-divider::before {{
                margin-right: 1rem;
            }}
            .social-divider::after {{
                margin-left: 1rem;
            }}
        </style>
        <div class="login-header">
            <h1><span style="color: #667eea;">◈</span> Vortex</h1>
            <p>Transform natural language into powerful SQL queries</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Login", use_container_width=True)
                
                if submit:
                    if verify_user(username, password):
                        st.session_state.authenticated = True
                        st.session_state.current_user = username
                        
                        # Get full name
                        user_info = get_user_info(username)
                        full_name = f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}".strip()
                        if not full_name:
                            full_name = username
                        st.session_state.current_user_fullname = full_name
                        
                        # Load user settings
                        settings = get_user_settings(username)
                        if "saved_connections" in settings:
                            st.session_state.saved_connections = settings["saved_connections"]
                        # Backward compatibility: check for single db_config and migrate it
                        elif "db_config" in settings:
                            st.session_state.saved_connections = {"Default": settings["db_config"]}
                            
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
        
        with tab2:
            with st.form("signup_form"):
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    first_name = st.text_input("First Name")
                with col_s2:
                    last_name = st.text_input("Last Name")
                    
                new_user = st.text_input("New Username")
                new_pass = st.text_input("New Password", type="password")
                confirm_pass = st.text_input("Confirm Password", type="password")
                submit_signup = st.form_submit_button("Sign Up", use_container_width=True)
                
                if submit_signup:
                    if new_pass != confirm_pass:
                        st.error("Passwords do not match")
                    elif not new_user or not new_pass:
                        st.error("Username and password are required")
                    else:
                        success, msg = save_user(new_user, new_pass, first_name, last_name)
                        if success:
                            st.success(msg)
                            st.info("Please switch to the Login tab to log in.")
                        else:
                            st.error(msg)
        
        if "auth" not in st.secrets:
            st.info("Default credentials: **admin** / **admin**")

        st.markdown('<div class="social-divider">or continue with</div>', unsafe_allow_html=True)

        # Social Login Buttons (Placeholders)
        # We use columns to create a grid layout for the buttons
        sc1, sc2 = st.columns(2)
        
        with sc1:
            if st.button("🔍 Google", use_container_width=True):
                st.toast("Google login coming soon!")
            if st.button("📷 Instagram", use_container_width=True):
                st.toast("Instagram login coming soon!")
                
        with sc2:
            if st.button("📘 Facebook", use_container_width=True):
                st.toast("Facebook login coming soon!")
            if st.button("💼 LinkedIn", use_container_width=True):
                st.toast("LinkedIn login coming soon!")

def reset_conversation():
    """Reset the conversation history."""
    st.session_state.messages = []
    st.session_state.agent_memory_sql = None
    st.session_state.agent_memory_python = None
    st.session_state.sql_agent = None
    st.session_state.python_agent = None
    # Re-initialize agents if connected
    if st.session_state.db_connected:
        try:
            st.session_state.sql_agent = initialize_sql_agent(st.session_state.db_config)
            st.session_state.python_agent = initialize_python_agent()
            st.session_state.agent_memory_sql = st.session_state.sql_agent
            st.session_state.agent_memory_python = st.session_state.python_agent
        except Exception as e:
            st.error(f"Error re-initializing agents: {e}")

def render_top_bar():
    """Render the top navigation bar."""
    col1, col2 = st.columns([6, 1])
    with col1:
        pass # Spacer
    with col2:
        if st.session_state.authenticated:
            display_name = st.session_state.get("current_user_fullname") or st.session_state.current_user
            with st.popover(f"👤 {display_name}"):
                if st.button("👤 Profile", use_container_width=True):
                    st.session_state.view_mode = "profile"
                    st.rerun()
                if st.button("💬 Chat", use_container_width=True):
                    st.session_state.view_mode = "chat"
                    st.rerun()
                st.markdown("---")
                if st.button("🚪 Logout", use_container_width=True):
                    st.session_state.authenticated = False
                    st.session_state.current_user = None
                    st.session_state.current_user_fullname = None
                    st.session_state.view_mode = "chat"
                    st.rerun()

def render_profile():
    """Render the user profile page."""
    display_name = st.session_state.get("current_user_fullname") or st.session_state.current_user
    st.markdown(f"""
        <div class="sticky-header">
            <h1><span style="color: #667eea; margin-right: 8px;">👤</span>{display_name}</h1>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f'<h3>👋 Welcome, {display_name}!</h3>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown('<h3>💾 Saved Database Configurations</h3>', unsafe_allow_html=True)
    
    if not st.session_state.saved_connections:
        st.info("No saved connections yet. Connect to a database in the sidebar to save one.")
    else:

        # Use a list to track deletions to avoid modifying dict during iteration
        connection_to_delete = None
        
        for name, config in st.session_state.saved_connections.items():
            with st.expander(f"🗄️ {name}"):
                with st.form(key=f"edit_form_{name}"):
                    # Type Selection
                    db_type_options = ["MySQL", "PostgreSQL", "SQL Server", "SQLite", "Snowflake", "Databricks"]
                    current_index = 0
                    if config.get('TYPE') in db_type_options:
                        current_index = db_type_options.index(config.get('TYPE'))
                    
                    new_type = st.selectbox("Database Type", db_type_options, index=current_index, key=f"type_{name}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        new_host = st.text_input("Host", value=config.get('HOST', ''), key=f"host_{name}")
                        new_port = st.text_input("Port", value=config.get('PORT', ''), key=f"port_{name}")
                        new_user = st.text_input("User", value=config.get('USER', ''), key=f"user_{name}")
                    with col2:
                        new_db = st.text_input("Database / Path", value=config.get('DATABASE', ''), key=f"db_{name}")
                        new_schema = st.text_input("Schema", value=config.get('SCHEMA', ''), key=f"schema_{name}")
                        new_pass = st.text_input("Password", value=config.get('PASSWORD', ''), type="password", key=f"pass_{name}")
                    
                    # Initialize advanced vars
                    new_warehouse = config.get('WAREHOUSE', '')
                    new_role = config.get('ROLE', '')
                    new_http = config.get('HTTP_PATH', '')
                    new_catalog = config.get('CATALOG', '')

                    # Advanced Settings
                    if st.checkbox("Show Advanced Settings (Snowflake/Databricks)", key=f"adv_{name}"):
                        new_warehouse = st.text_input("Warehouse", value=new_warehouse, key=f"wh_{name}")
                        new_role = st.text_input("Role", value=new_role, key=f"role_{name}")
                        new_http = st.text_input("HTTP Path", value=new_http, key=f"http_{name}")
                        new_catalog = st.text_input("Catalog", value=new_catalog, key=f"cat_{name}")

                    if st.form_submit_button("Save Changes"):
                        # Update config
                        updated_config = config.copy()
                        updated_config.update({
                            'TYPE': new_type,
                            'HOST': new_host,
                            'PORT': new_port,
                            'USER': new_user,
                            'DATABASE': new_db,
                            'SCHEMA': new_schema,
                            'PASSWORD': new_pass,
                            'WAREHOUSE': new_warehouse,
                            'ROLE': new_role,
                            'HTTP_PATH': new_http,
                            'CATALOG': new_catalog
                        })
                        st.session_state.saved_connections[name] = updated_config
                        if st.session_state.current_user:
                            update_user_settings(st.session_state.current_user, {"saved_connections": st.session_state.saved_connections})
                        st.success("Settings updated!")
                        st.rerun()

                if st.button("Delete Connection", key=f"del_{name}"):
                    connection_to_delete = name

        if connection_to_delete:
            del st.session_state.saved_connections[connection_to_delete]
            # Update persistent storage
            if st.session_state.current_user:
                update_user_settings(st.session_state.current_user, {"saved_connections": st.session_state.saved_connections})
            st.success(f"Deleted connection: {connection_to_delete}")
            st.rerun()
    
    st.markdown("---")
    if st.button("← Back to Chat"):
        st.session_state.view_mode = "chat"
        st.rerun()

def render_sidebar():
    """Render the sidebar configuration."""
    with st.sidebar:
        # Theme Toggle
        st.markdown('<p class="sidebar-section-title">⚙️ Appearance</p>', unsafe_allow_html=True)
        dark_mode = st.toggle("Dark Mode", value=st.session_state.dark_mode, key="dark_mode_toggle")
        if dark_mode != st.session_state.dark_mode:
            st.session_state.dark_mode = dark_mode
            st.rerun()

        st.markdown("---")
        st.markdown('<p class="sidebar-section-title">🗄️ Connect Database</p>', unsafe_allow_html=True)
        
        # Load Saved Connections
        saved_names = ["New Connection"] + list(st.session_state.saved_connections.keys())
        selected_conn = st.selectbox("Load Saved Connection", saved_names)
        
        if selected_conn != "New Connection":
            # If we just switched to this connection, load it into db_config
            # We use a session state variable to track the last loaded connection to avoid constant reloading
            if st.session_state.get("last_loaded_conn") != selected_conn:
                st.session_state.db_config = st.session_state.saved_connections[selected_conn].copy()
                st.session_state.last_loaded_conn = selected_conn
                st.rerun()
        else:
            if st.session_state.get("last_loaded_conn") != "New Connection":
                 st.session_state.last_loaded_conn = "New Connection"
                 # Optional: Reset config? For now, let's keep current values to allow "Save As" behavior
        
        st.markdown("Configure your connection below to start analyzing data.")
        st.markdown('<p class="sidebar-subheading">Connection Details</p>', unsafe_allow_html=True)
        
        # Connection Name Input
        conn_name_val = selected_conn if selected_conn != "New Connection" else "My Connection"
        connection_name = st.text_input("Connection Name (for saving)", value=conn_name_val)

        # Database Type Selection
        db_type_options = ["MySQL", "PostgreSQL", "SQL Server", "SQLite", "Snowflake", "Databricks"]
        current_type_index = 0
        if st.session_state.db_config['TYPE'] in db_type_options:
            current_type_index = db_type_options.index(st.session_state.db_config['TYPE'])
            
        db_type = st.selectbox("Database Type", db_type_options, index=current_type_index)

        # Handle Type Change & Default Ports
        if db_type != st.session_state.db_config['TYPE']:
            st.session_state.db_config['TYPE'] = db_type
            defaults = {
                "PostgreSQL": '5432',
                "SQL Server": '1433',
                "MySQL": '3306',
                "Databricks": '443'
            }
            if db_type in defaults:
                st.session_state.db_config['PORT'] = defaults[db_type]
            st.rerun()

        # Dynamic Inputs based on DB Type
        config = st.session_state.db_config
        
        if "SQLite" in db_type:
            config['DATABASE'] = st.text_input("Database Path", value=config['DATABASE'] or 'data.db', placeholder="/path/to/database.db")
        elif "Snowflake" in db_type:
            config['USER'] = st.text_input("User", value=config['USER'], placeholder="username")
            config['PASSWORD'] = st.text_input("Password", type="password", value=config['PASSWORD'], placeholder="********")
            config['HOST'] = st.text_input("Account Identifier", value=config['HOST'], placeholder="orgname-accountname")
            config['WAREHOUSE'] = st.text_input("Warehouse", value=config.get('WAREHOUSE', ''), placeholder="COMPUTE_WH")
            config['ROLE'] = st.text_input("Role", value=config.get('ROLE', ''), placeholder="ACCOUNTADMIN")
        elif "Databricks" in db_type:
            config['HOST'] = st.text_input("Server Hostname", value=config['HOST'], placeholder="adb-....net")
            config['HTTP_PATH'] = st.text_input("HTTP Path", value=config.get('HTTP_PATH', ''), placeholder="/sql/1.0/warehouses/...")
            config['PASSWORD'] = st.text_input("Access Token", type="password", value=config['PASSWORD'], placeholder="dapi...")
            config['CATALOG'] = st.text_input("Catalog", value=config.get('CATALOG', ''), placeholder="hive_metastore")
            config['USER'] = "token"
            config['PORT'] = "443"
        else:
            config['USER'] = st.text_input("User", value=config['USER'], placeholder="root/postgres/sa")
            config['PASSWORD'] = st.text_input("Password", type="password", value=config['PASSWORD'], placeholder="********")
            config['HOST'] = st.text_input("Host", value=config['HOST'], placeholder="localhost")
            config['PORT'] = st.text_input("Port", value=config['PORT'], placeholder="3306/5432/1433")

        # Connect Button
        button_label = "Connect & Save" if not st.session_state.db_connected else "Update Connection"
        if st.button(button_label):
            with st.spinner("Testing connection..."):
                ok, db_list = test_connection(config)
                if ok:
                    st.session_state.db_connected = True
                    st.session_state.databases = db_list
                    st.success("Connected successfully!")
                    
                    # Save connection to session state
                    if connection_name:
                        st.session_state.saved_connections[connection_name] = config.copy()
                        st.toast(f"Connection '{connection_name}' saved!")
                    
                    # Auto-save to profile if user is logged in
                    if st.session_state.current_user:
                        update_user_settings(st.session_state.current_user, {"saved_connections": st.session_state.saved_connections})
                    
                    # Initialize agents immediately for SQLite or if no DB selection needed
                    if "SQLite" in db_type:
                         try:
                            st.session_state.sql_agent = initialize_sql_agent(st.session_state.db_config)
                            st.session_state.python_agent = initialize_python_agent()
                            st.session_state.agent_memory_sql = st.session_state.sql_agent
                            st.session_state.agent_memory_python = st.session_state.python_agent
                         except Exception as e:
                            st.error(f"Failed to initialize agents: {e}")
                else:
                    st.session_state.db_connected = False
                    st.session_state.databases = []
                    st.error(f"Connection failed: {db_list[0] if db_list else 'Unknown error'}")

        # Database Selection
        if st.session_state.db_connected and "SQLite" not in db_type:
            st.markdown("---")
            db_options = st.session_state.databases
            current_db = st.session_state.db_config['DATABASE']
            index = db_options.index(current_db) if current_db in db_options else 0
            
            selected_db = st.selectbox("Select Database", options=db_options, index=index)
            
            if selected_db != st.session_state.db_config['DATABASE']:
                st.session_state.db_config['DATABASE'] = selected_db
                # Reset schema if DB changes
                if 'SCHEMA' in st.session_state.db_config:
                     st.session_state.db_config['SCHEMA'] = 'PUBLIC'

            # Snowflake Schema Selection
            if "Snowflake" in db_type and selected_db:
                schemas = get_snowflake_schemas(st.session_state.db_config, selected_db)
                if schemas:
                    current_schema = st.session_state.db_config.get('SCHEMA', 'PUBLIC')
                    if current_schema not in schemas:
                        current_schema = schemas[0]
                    
                    selected_schema = st.selectbox("Select Schema", options=schemas, index=schemas.index(current_schema))
                    st.session_state.db_config['SCHEMA'] = selected_schema
                else:
                    st.session_state.db_config['SCHEMA'] = 'PUBLIC'

            # Initialize Agents on DB Selection
            if st.session_state.db_config['DATABASE']:
                try:
                    st.session_state.sql_agent = initialize_sql_agent(st.session_state.db_config)
                    st.session_state.python_agent = initialize_python_agent()
                    st.session_state.agent_memory_sql = st.session_state.sql_agent
                    st.session_state.agent_memory_python = st.session_state.python_agent
                    
                    st.success(f"Active Database: {st.session_state.db_config['DATABASE']}")
                    if "Snowflake" in db_type:
                        st.success(f"Active Schema: {st.session_state.db_config.get('SCHEMA', 'PUBLIC')}")
                except Exception as e:
                    st.error(f"Agent Initialization Failed: {e}")

        st.markdown("---")
        if st.button("🔄 Reset Conversation"):
            reset_conversation()
            st.rerun()

def render_chat():
    """Render the main chat interface."""
    # Sticky Header with gradient title
    st.markdown("""
        <div class="sticky-header">
            <h1><span style="color: #667eea; margin-right: 8px;">◈</span>Vortex</h1>
        </div>
    """, unsafe_allow_html=True)
    
    # Welcome Banner with modern styling
    st.markdown("""
    <div class="welcome-banner">
        <h3>✨ Welcome to Vortex</h3>
        <p>Transform your natural language questions into powerful SQL queries and beautiful Python visualizations. 
        Connect your database using the sidebar to get started.</p>
    </div>
    """, unsafe_allow_html=True)

    # Status Indicator
    if st.session_state.db_connected and st.session_state.db_config['DATABASE']:
        db_info = f"Using database: `{st.session_state.db_config['DATABASE']}`"
        if "Snowflake" in st.session_state.db_config['TYPE']:
             db_info += f" (Schema: `{st.session_state.db_config.get('SCHEMA', 'PUBLIC')}`)"
        st.caption(db_info)
    else:
        st.warning("Not connected. Provide credentials and click the button in the sidebar.")

    # Chat History
    for message in st.session_state.messages:
        role = message["role"]
        avatar = "🚀" if role == "user" else "✨"
        with st.chat_message(role, avatar=avatar):
            if role == "assistant":
                display_text_with_images(message["content"])
                code_plot = display_code_plots(message["content"])
                if code_plot:
                    try:
                        exec(code_plot)
                    except Exception as e:
                        st.error(f"Error executing plot code: {e}")
            else:
                st.markdown(message["content"])

    # Chat Input
    if prompt := st.chat_input("Please ask your question:"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="🚀"):
            st.markdown(prompt)

        with st.chat_message("assistant", avatar="✨"):
            if not st.session_state.db_connected or not st.session_state.sql_agent:
                response = "Please configure and connect to a database using the sidebar before running queries."
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            else:
                st_callback = StreamlitCallbackHandler(st.container())
                try:
                    # Determine intent (simple keyword check for now, could be LLM router)
                    if "plot" in prompt.lower() or "graph" in prompt.lower() or "chart" in prompt.lower():
                        # Chain of Agents: SQL Agent (Get Data) -> Python Agent (Visualize)
                        
                        # Step 1: Fetch Data
                        st.markdown('<h5>🔍 Fetching data...</h5>', unsafe_allow_html=True)
                        fetch_prompt = (
                            f"Please fetch the data required to answer this request: '{prompt}'. "
                            "Do not generate any plots or images yourself. "
                            "Just output the relevant data in a structured text format (like a table or list) "
                            "so that it can be visualized by another tool."
                        )
                        
                        # We use the callback handler here to show the SQL agent's thinking process (tool calls).
                        # We cannot use st.status because StreamlitCallbackHandler uses expanders, and nested expanders are not supported.
                        sql_response = st.session_state.sql_agent.invoke(
                            {"input": fetch_prompt}, 
                            {"callbacks": [StreamlitCallbackHandler(st.container())]}
                        )
                        data_context = sql_response['output']
                        st.markdown('<h5 style="color: #22c55e;">✅ Data fetched!</h5>', unsafe_allow_html=True)

                        # Step 2: Visualize Data
                        visualize_prompt = (
                            f"User Request: {prompt}\n\n"
                            f"Here is the data fetched from the database:\n{data_context}\n\n"
                            "Please write Python code using Plotly to create the requested visualization based on this data. "
                            "Do not use sample data; use the data provided above."
                        )
                        
                        response = st.session_state.python_agent.invoke(
                            {"input": visualize_prompt}, 
                            {"callbacks": [st_callback]}
                        )
                        output = response['output']
                    else:
                        response = st.session_state.sql_agent.invoke(
                            {"input": prompt}, 
                            {"callbacks": [st_callback]}
                        )
                        output = response['output']

                    st.markdown(output)
                    
                    # Handle plots if present in output
                    code_plot = display_code_plots(output)
                    if code_plot:
                        try:
                            exec(code_plot)
                        except Exception as e:
                            st.error(f"Error executing plot code: {e}")
                            
                    st.session_state.messages.append({"role": "assistant", "content": output})

                except Exception as e:
                    error_msg = f"An error occurred: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

def main():
    init_session_state()
    inject_custom_css(st.session_state.dark_mode)
    
    if not st.session_state.authenticated:
        login_page()
    else:
        render_sidebar()
        render_top_bar()
        if st.session_state.view_mode == "profile":
            render_profile()
        else:
            render_chat()

if __name__ == "__main__":
    main()
