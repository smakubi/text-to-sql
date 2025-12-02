
import urllib.parse
import certifi
from langchain import hub
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_community.agent_toolkits import create_sql_agent
from langchain.agents.agent_types import AgentType
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.chat_models import ChatOpenAI
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import create_react_agent, AgentExecutor
from langchain_experimental.tools import PythonREPLTool
from langchain.memory import ConversationBufferMemory
from constants import LLM_MODEL_NAME, INSTRUCTIONS, SQL_SYSTEM_INSTRUCTIONS
from database import get_connection_string
import streamlit as st


OPENAI_API_KEY = st.secrets["openai"]["OPENAI_API_KEY"]

def initialize_python_agent(agent_llm_name: str = LLM_MODEL_NAME):
    """
    Create an agent for Python-related tasks.

    Args:
        agent_llm_name (str): The name or identifier of the language model for the agent.
    Returns:
        AgentExecutor: An agent executor configured for Python-related tasks.
    """
    base_prompt = hub.pull("langchain-ai/openai-functions-template")
    prompt = base_prompt.partial(instructions=INSTRUCTIONS)
    tools = [PythonREPLTool()]
    agent = create_openai_functions_agent(ChatOpenAI(model=agent_llm_name, temperature=0, openai_api_key=OPENAI_API_KEY), tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    return agent_executor


def initialize_sql_agent(db_config):
    """Initialize SQL agent with proper validation"""
    required_fields = ['USER', 'PASSWORD', 'HOST', 'DATABASE', 'PORT']
    
    # Validate config
    if not db_config or not isinstance(db_config, dict):
        raise ValueError("Invalid database configuration")
        
    # Check required fields
    if "SQLite" in db_config.get('TYPE', 'MySQL'):
        if not db_config.get('DATABASE'):
             raise ValueError("Missing required field: DATABASE (Path)")
    elif "Snowflake" in db_config.get('TYPE', 'MySQL'):
        for field in ['USER', 'PASSWORD', 'HOST']:
            if field not in db_config or not db_config[field]:
                raise ValueError(f"Missing required field: {field}")
    elif "Databricks" in db_config.get('TYPE', 'MySQL'):
        for field in ['HOST', 'HTTP_PATH', 'PASSWORD']:
            if field not in db_config or not db_config[field]:
                raise ValueError(f"Missing required field: {field}")
    else:
        for field in required_fields:
            if field not in db_config or not db_config[field]:
                raise ValueError(f"Missing required field: {field}")
    
    try:
        # Initialize LLM first
        llm = ChatOpenAI(
            temperature=0,
            model=LLM_MODEL_NAME,
            openai_api_key=OPENAI_API_KEY
        )
        
        # Create database connection string using shared utility
        connection_string = get_connection_string(db_config)
        
        db = SQLDatabase.from_uri(connection_string)
        
        # Create toolkit with LLM
        toolkit = SQLDatabaseToolkit(
            db=db,
            llm=llm
        )
        
        # Use in-memory history instead of SQL-backed history to avoid permission issues
        from langchain_community.chat_message_histories import ChatMessageHistory
        message_history = ChatMessageHistory()
        memory = ConversationBufferMemory(memory_key="chat_history", input_key='input', chat_memory=message_history, return_messages=True)

        # Create and return agent
        return create_sql_agent(
            llm=llm,
            toolkit=toolkit,
            agent_type="openai-tools",
            prefix=SQL_SYSTEM_INSTRUCTIONS,
            agent_executor_kwargs={"memory": memory},
            verbose=True
        )
    except Exception as e:
        raise ValueError(f"Failed to initialize SQL agent: {str(e)}")
