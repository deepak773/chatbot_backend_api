from sqlalchemy import create_engine
from langchain.agents import create_sql_agent
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.sql_database import SQLDatabase
import os

def create_sql_engine(database_url):
    engine = create_engine(database_url)
    return engine

# Function to retrieve table names
def get_table_names(engine):
    with engine.connect() as connection:
        # Query to get all table names in the current schema
        query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
        """
        result = connection.execute(query)
        return [row[0] for row in result]

def get_chat_model(MODEL, OPENAI_API_KEY, temperature):
    # Initialize the language model (OpenAI GPT-4)
    llm = ChatOpenAI(temperature=temperature,
                 openai_api_key=OPENAI_API_KEY,  # Your OpenAI API key
                 model=MODEL)
    return llm

def get_sql_agent(engine, prompt, llm):
    # Wrap the engine in Langchain's SQLDatabase
    db = SQLDatabase(engine)
    # Define a custom prompt template
    custom_prompt = PromptTemplate(
        input_variables=["query"],  # Placeholder for user input
        template=prompt
    )
    # Create the LLMChain with the custom prompt and LLM
    llm_chain = LLMChain(llm=llm, prompt=custom_prompt)

    # Create the SQL agent using the LLM and database
    agent = create_sql_agent(llm=llm, db=db, verbose=True)
    return agent

def get_response_from_agent(agent, query):
    response = agent.invoke(query)
    return response['output']