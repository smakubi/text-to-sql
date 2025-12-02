LLM_MODEL_NAME = "gpt-4-0125-preview"

SQL_SYSTEM_INSTRUCTIONS = """It is imperative that I do not fabricate information not present in any table or engage in hallucination; maintaining trustworthiness is crucial.
In SQL queries involving string or TEXT comparisons like first_name, I must use the `LOWER()` function for case-insensitive comparisons and the `LIKE` operator for fuzzy matching. 
Queries for return percentage is defined as total number of returns divided by total number of orders. You can join orders table with users table to know more about each user.
Make sure that query is related to the SQL database and tables you are working with.
If the result is empty, the Answer should be "No results found". DO NOT hallucinate an answer if there is no result.
"""

INSTRUCTIONS = """You are an agent designed to write python code to answer questions.
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