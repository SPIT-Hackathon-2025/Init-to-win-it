from flask import Flask, request, jsonify
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain import hub
from langchain_openai import ChatOpenAI
from composio_langchain import ComposioToolSet
import os
from dotenv import load_dotenv
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

# Load environment variables
load_dotenv()

# Get API keys from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
FRIEND_API_KEY = os.getenv('FRIEND_API_KEY')
YOUR_API_KEY = os.getenv('YOUR_API_KEY')
FRIEND_EMAIL = os.getenv('FRIEND_EMAIL')

# Set OpenAI API key
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

def initialize_agent():
    llm = ChatOpenAI()
    prompt = hub.pull("hwchase17/openai-functions-agent")
    
    your_toolset = ComposioToolSet(api_key=YOUR_API_KEY)
    
    gmail_tools = ['GMAIL_SEND_EMAIL', 'GMAIL_CREATE_EMAIL_DRAFT']
    google_docs_tools = [
        'GOOGLEDOCS_CREATE_DOCUMENT',
        'GOOGLEDOCS_UPDATE_EXISTING_DOCUMENT',
        'GOOGLEDOCS_GET_DOCUMENT_BY_ID',
        'GOOGLEDOCS_CREATE_DOCUMENT_MARKDOWN',
        'GOOGLEDOCS_UPDATE_DOCUMENT_MARKDOWN'
    ]
    
    your_tools = your_toolset.get_tools(actions=[*google_docs_tools, *gmail_tools])
    your_agent = create_openai_functions_agent(llm, your_tools, prompt)
    return AgentExecutor(agent=your_agent, tools=your_tools, verbose=True)

def extract_email(text):
    """Extract email addresses from text using regex."""
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    return emails

def analyze_prompt(text):
    """Analyze prompt for user intentions."""
    create_doc = any(keyword in text.lower() for keyword in ['create doc', 'make doc', 'write doc', 'generate doc'])
    send_email = any(keyword in text.lower() for keyword in ['send', 'email', 'mail'])
    return create_doc, send_email

@app.route('/create-doc', methods=['POST'])
def create_document():
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        
        # Extract emails from prompt
        emails = extract_email(prompt)
        email_list = emails if emails else [FRIEND_EMAIL]
        
        executor = initialize_agent()
        
        # Create a specific task that ensures document creation and sharing
        task = f"""
        Follow these steps exactly:
        1. Create a new Google Doc with content based on these requirements:
        {prompt}
        
        2. After creating the document, you must:
           - Share the document with all of these emails: {', '.join(email_list)}
           - Send an email to all recipients ({', '.join(email_list)}) that includes:
             * The link to the created document
             * A brief summary of what was created
             * Any specific instructions from the original prompt
        
        3. Make sure to:
           - Set document permissions so recipients can access it
           - Include the document link in the email
           - Confirm once both document creation and email sending are complete
        
        Execute these steps and provide me with the document link and confirmation of email sending.
        """
        
        # Execute the task
        result = executor.invoke({"input": task})
        
        return jsonify({
            "status": "success",
            "result": result['output'],
            "recipients": email_list,
            "message": "Document created and shared with all specified recipients"
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5002)
