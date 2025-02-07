import streamlit as st

st.set_page_config(page_title="SQL and Python Agent")
# MAIN PAGE
st.title("SQL and Python Agent")




# SIDE BAR
st.sidebar.title("DATABASE CONFIGURATION")
st.sidebar.subheader("Enter MySQL connection details:", divider=True)
user = st.sidebar.text_input("User", value=st.session_state.db_config['USER'])
password = st.sidebar.text_input("Password", type="password", value=st.session_state.db_config['PASSWORD'])
host = st.sidebar.text_input("Host", value=st.session_state.db_config['HOST'])
port = st.sidebar.text_input("Port", value=st.session_state.db_config['PORT'])

# CHAT INPUT

if prompt := st.chat_input("Please ask your question:"):
   with st.chat_message("user", avatar="🚀"):
     st.markdown(prompt)