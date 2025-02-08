from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain import hub
from langchain_openai import ChatOpenAI
from composio_langchain import ComposioToolSet, Action, App
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API keys from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
FRIEND_API_KEY = os.getenv('FRIEND_API_KEY')
YOUR_API_KEY = os.getenv('YOUR_API_KEY')
FRIEND_EMAIL = os.getenv('FRIEND_EMAIL')

# Set OpenAI API key
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

llm = ChatOpenAI()
prompt = hub.pull("hwchase17/openai-functions-agent")

# Initialize tools for both users
your_toolset = ComposioToolSet(api_key=YOUR_API_KEY)

# Define tools by category - only keep what we need
gmail_tools = [
    'GMAIL_SEND_EMAIL',
    'GMAIL_CREATE_EMAIL_DRAFT'
]

google_docs_tools = [
    'GOOGLEDOCS_CREATE_DOCUMENT',
    'GOOGLEDOCS_UPDATE_EXISTING_DOCUMENT',
    'GOOGLEDOCS_GET_DOCUMENT_BY_ID',
    'GOOGLEDOCS_CREATE_DOCUMENT_MARKDOWN',
    'GOOGLEDOCS_UPDATE_DOCUMENT_MARKDOWN'
]

# Only create tools for yourself
your_tools = your_toolset.get_tools(actions=[
    *google_docs_tools,
    *gmail_tools
])

# Create only your agent
your_agent = create_openai_functions_agent(llm, your_tools, prompt)
your_executor = AgentExecutor(agent=your_agent, tools=your_tools, verbose=True)

# Simplified workflow - just create doc and email
try:
    # Step 1: Create document
    create_doc_task = """
    Create a new Google Doc titled 'Important Document'. Now in the doc add a nice sample template for an investor pitch and send the doc to asim.shah22@spit.ac.in 
    """
    
    doc_result = your_executor.invoke({"input": create_doc_task})
    print("Document creation result:", doc_result)
    
    # Step 2: Send email with document content
    email_task = f"""
    Send an email to {FRIEND_EMAIL} with:
    Subject: Important Document
    Body: Here is the important document content:

    {doc_result['output']}
    """
    
    email_result = your_executor.invoke({"input": email_task})
    print("Email notification result:", email_result)

except Exception as e:
    print(f"Error during document workflow: {str(e)}")
