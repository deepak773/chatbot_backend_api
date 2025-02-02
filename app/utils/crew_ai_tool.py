from crewai import Agent, Crew, Process, Task
from crewai_tools import tool
from langchain.schema import AgentFinish
from langchain.schema.output import LLMResult
from langchain_community.tools.sql_database.tool import (
    InfoSQLDatabaseTool,
    ListSQLDatabaseTool,
    QuerySQLCheckerTool,
    QuerySQLDataBaseTool,
)
from langchain_community.utilities.sql_database import SQLDatabase
from langchain.chat_models import ChatOpenAI
from app.config import settings
import ast
from textwrap import dedent

DATABASE_URL = f"postgresql://{settings.db_user}:{settings.db_password}@{settings.db_host}/{settings.db_name}?sslmode=require"
db = SQLDatabase.from_uri(DATABASE_URL)

def get_chat_model(MODEL, OPENAI_API_KEY, temperature):
    # Initialize the language model (OpenAI GPT-4)
    llm = ChatOpenAI(temperature=temperature,
                 openai_api_key=OPENAI_API_KEY,  # Your OpenAI API key
                 model=MODEL)
    return llm

@tool("list_tables")
def list_tables() -> str:
    """List the available tables in the database"""
    return ListSQLDatabaseTool(db=db).invoke("")

@tool("tables_schema")
def tables_schema(tables: str) -> str:
    """
    Input is a comma-separated list of tables, output is the schema, column descriptions, and sample rows for those tables.
    Be sure that the tables actually exist by calling 'list_tables' first!
    Example Input: table1, table2, table3
    """
    def get_column_descriptions(table_name: str) -> str:
        query = f"""
        SELECT
            c.column_name,
            c.data_type,
            COALESCE(pgd.description, 'No description') AS description
        FROM
            information_schema.columns c
        LEFT JOIN
            pg_catalog.pg_statio_all_tables st ON c.table_schema = st.schemaname AND c.table_name = st.relname
        LEFT JOIN
            pg_catalog.pg_description pgd ON pgd.objoid = st.relid AND pgd.objsubid = c.ordinal_position
        WHERE
            c.table_name = '{table_name}';
        """
        # Run the query
        results = db.run(query)
        results = ast.literal_eval(results)
        print(type(results))
        output=""
        for column in results:
            output = output + f"{column[0]} - {column[2]}\n"
        return output
    # Use the InfoSQLDatabaseTool to fetch schema and sample rows
    tool = InfoSQLDatabaseTool(db=db)
    schema_output = tool.invoke(tables)
    # Fetch column descriptions for each table
    table_list = [table.strip() for table in tables.split(",")]
    descriptions_output = ""
    for table in table_list:
        descriptions_output = f"Column descriptions for table '{table}' in format 'Column Name - Column Description':\n"
        descriptions_output += get_column_descriptions(table) + "\n"
    # Combine the schema output with the column descriptions
    return schema_output + "\n" + descriptions_output

@tool("execute_sql")
def execute_sql(sql_query: str) -> str:
    """Execute a SQL query against the database. Returns the result"""
    return QuerySQLDataBaseTool(db=db).invoke(sql_query)

@tool("check_sql")
def check_sql(sql_query: str) -> str:
    """
    Use this tool to double check if your query is correct before executing it. Always use this tool before executing
    a query with 'execute_sql'.
    """
    llm = get_chat_model(settings.MODEL, settings.OPENAI_API_KEY, settings.temperature)
    return QuerySQLCheckerTool(db=db, llm=llm).invoke({"query": sql_query})


llm = get_chat_model(settings.MODEL, settings.OPENAI_API_KEY, settings.temperature)
sql_dev = Agent(
    role="Senior Database Developer",
    goal="Construct and execute SQL queries based on a request",
    backstory=dedent(
        """
        You are an experienced database engineer who is master at creating efficient and complex SQL queries.
        You have a deep understanding of how different databases work and how to optimize queries.
        Use the `list_tables` to find available tables.
        Use the `tables_schema` to understand the metadata for the tables.
        Use the `execute_sql` to check your queries for corrections.
        Use the `check_sql` to execute queries against the database.
        """
    ),
    llm=llm,
    tools=[list_tables, tables_schema, execute_sql, check_sql],
    allow_delegation=False,
)

data_analyst = Agent(
    role="Senior Data Analyst",
    goal="You receive data from the database developer and analyze it",
    backstory=dedent(
        """
        You have deep experience with analyzing datasets.
        Your work is always based on the provided data and is clear,
        easy-to-understand and to the point. You have attention to details and always produce very clear understanding
        of the data which easily understood by the user.
        If you get the data which is large means more than 1 row of data, then make it in a markdown table format.
        If data is only one row then describe it in pointers. For example: if you get a row data with lets say 20 columns,
        then make it in 5-6 pointers to cover all the data points.
        After this, also provide a paragraph by analysing the data. But, if the query is just for count or a one sentence
        response, then no need to describe just give the answer in single sentence only.
        """
    ),
    llm=llm,
    allow_delegation=False,
)

controller_agent = Agent(
    role="Controller",
    goal="Decides whether to process user input.",
    llm=llm,
    backstory=(
        "If the user input is a greeting (e.g., 'Hello', 'Hi', 'Good morning'), reply politely "
        "without running any tasks. Otherwise, delegate appropriately and return the user's request."
    ),
    allow_delegation=True
)

understand_input = Task(
    description="Analyze the user input. If it's a greeting, return 'STOP'. Otherwise, return the input unchanged.",
    agent=controller_agent,
    expected_output="Either 'STOP' for trivial inputs or the processed user request."
)


extract_data = Task(
    description="Extract data that is required for the query {query}.",
    expected_output="Database result for the query",
    agent=sql_dev,
)

analyze_data = Task(
    description="Analyze the data from the database and write an analysis for {query}",
    expected_output="Detailed analysis text",
    agent=data_analyst,
    context=[extract_data],
)

def get_crew_handle():
    crew = Crew(
        agents=[sql_dev, data_analyst],
        tasks=[extract_data, analyze_data],
        process=Process.sequential,
        verbose=2,
        memory=False,
        output_log_file="crew.log",
    )
    return crew

def process_user_request(user_input):
    # Step 1: Run the controller agent first
    crew = Crew(agents=[controller_agent], tasks=[understand_input], process=Process.sequential)
    decision = crew.kickoff(inputs={"user_input": user_input})

    if "STOP" in decision.upper():
        return "Hello! Let me know how I can assist you."

    # Step 2: Proceed only if the input is valid
    crew = Crew(
        agents=[controller_agent, sql_dev, data_analyst],
        tasks=[extract_data, analyze_data],
        process=Process.sequential,
        verbose=2,
        memory=False,
        output_log_file="crew.log",
    )
    return crew.kickoff(inputs={"user_input": user_input})
