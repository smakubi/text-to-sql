import urllib.parse
from langchain import hub 
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.agents import create_sql_agent
from langchain.agents.agent_types import AgentType
from langchain.memory import ConversationBufferMemory 
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.chat_message_histories import SQLChatMessageHistory 
from langchain_community.utilities import SQLDatabase
from langchain_experimental.tools import PythonREPLTool
from langchain.chat_models import ChatOpenAI
from constants import LLM_MODEL_NAME
import streamlit as st

CUSTOM_SUFFIX = """Begin!

Relevant pieces of previous conversation:
{chat_history}
(Note: Only reference this information if it is relevant to the current query.)

Question: {input}
Thought Process: It is imperative that I do not fabricate information not present in any table or engage in hallucination; maintaining trustworthiness is crucial.
In SQL queries involving string or TEXT comparisons like first_name, I must use the `LOWER()` function for case-insensitive comparisons and the `LIKE` operator for fuzzy matching. 
Queries for return percentage is defined as total number of returns divided by total number of orders. You can join orders table with users table to know more about each user.
Make sure that query is related to the SQL database and tables you are working with.
If the result is empty, the Answer should be "No results found". DO NOT hallucinate an answer if there is no result.

My final response should STRICTLY be the output of SQL query.

{agent_scratchpad}
"""

OPENAI_API_KEY = st.secrets["openai"]["OPENAI_API_KEY"]

langchain_chat_kwargs = {
    "temperature": 0,
    "max_tokens": 4000,
    "verbose": True,
}
chat_openai_model_kwargs = {
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": -1,
}

def get_chat_openai(model_name):
    """
    Returns an instance of the ChatOpenAI class initialized with the specified model name.
    Args:
        model_name (str): The name of the model to use.
    Returns:
        ChatOpenAI: An instance of the ChatOpenAI class.
    """
    llm = ChatOpenAI(
        model_name=model_name,
        model_kwargs=chat_openai_model_kwargs,
        **langchain_chat_kwargs
    )
    return llm


def get_sql_toolkit(tool_llm_name: str):
    """
    Instantiates a SQLDatabaseToolkit object with the specified language model.
    This function creates a SQLDatabaseToolkit object configured with a language model
    obtained by the provided model name. The SQLDatabaseToolkit facilitates SQL query
    generation and interaction with a database.

    Args:
        tool_llm_name (str): The name or identifier of the language model to be used.
    Returns:
        SQLDatabaseToolkit: An instance of SQLDatabaseToolkit initialized with the provided language model.
    """
    llm_tool = get_chat_openai(model_name=tool_llm_name)
    toolkit = SQLDatabaseToolkit(db=db, llm=llm_tool)
    return toolkit


def get_agent_llm(agent_llm_name: str):
    """
    Retrieve a language model agent for conversational tasks.

    Args:
        agent_llm_name (str): The name or identifier of the language model for the agent.
    Returns:
        ChatOpenAI: A language model agent configured for conversational tasks.
    """
    llm_agent = get_chat_openai(model_name=agent_llm_name)
    return llm_agent


def initialize_python_agent(agent_llm_name: str = LLM_MODEL_NAME):
    """
    Create an agent for Python-related tasks.

    Args:
        agent_llm_name (str): The name or identifier of the language model for the agent.
    Returns:
        AgentExecutor: An agent executor configured for Python-related tasks.
    """
    instructions = """You are an agent designed to write python code to answer questions.
            You have access to a python REPL, which you can use to execute python code.
            If you get an error, debug your code and try again.
            You might know the answer without running any code, but you should still run the code to get the answer.
            If it does not seem like you can write code to answer the question, just return "I don't know" as the answer.
            Always output the python code only.
            Generate the code <code> for plotting the previous data in plotly, in the format requested. 
            The solution should be given using plotly and only plotly. Do not use matplotlib.
            Return the code <code> in the following
            format ```python <code>```
            """
    base_prompt = hub.pull("langchain-ai/openai-functions-template")
    prompt = base_prompt.partial(instructions=instructions)
    tools = [PythonREPLTool()]
    agent = create_openai_functions_agent(ChatOpenAI(model=agent_llm_name, temperature=0), tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    return agent_executor


def initialize_sql_agent(db_config):
    """Initialize SQL agent with proper validation"""
    required_fields = ['USER', 'PASSWORD', 'HOST', 'DATABASE', 'PORT']
    
    # Validate config
    if not db_config or not isinstance(db_config, dict):
        raise ValueError("Invalid database configuration")
        
    # Check required fields
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
        
        # Create database connection
        password = urllib.parse.quote_plus(db_config['PASSWORD'])
        connection_string = (
            f"mysql+pymysql://{db_config['USER']}:{password}@"
            f"{db_config['HOST']}:{db_config['PORT']}/{db_config['DATABASE']}"
        )
        
        db = SQLDatabase.from_uri(connection_string)
        
        # Create toolkit with LLM
        toolkit = SQLDatabaseToolkit(
            db=db,
            llm=llm
        )
        
        message_history = SQLChatMessageHistory(
            session_id="my-session",
            connection_string = (
            f"mysql+pymysql://{db_config['USER']}:{password}@"
            f"{db_config['HOST']}:{db_config['PORT']}/{db_config['DATABASE']}"), #added recently
            table_name="message_store",
            session_id_field_name="session_id"
        )
        memory = ConversationBufferMemory(memory_key="chat_history", input_key='input', chat_memory=message_history, return_messages=False) #added recently

        # Create and return agent
        return create_sql_agent(
            llm=llm,
            toolkit=toolkit,
            agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            input_variables=["input", "agent_scratchpad", "chat_history"], #added recently
            suffix=CUSTOM_SUFFIX, #added recently
            memory=memory, #added recently
            agent_executor_kwargs={"memory": memory}, #added recently
            verbose=True,
            handle_parsing_errors=True
        )
    except Exception as e:
        raise ValueError(f"Failed to initialize SQL agent: {str(e)}")