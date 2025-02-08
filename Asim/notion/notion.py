from flask import Flask, request, jsonify
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from composio_langchain import ComposioToolSet
from langchain.prompts import PromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize LangChain and Composio components
llm = ChatOpenAI()
prompt = hub.pull("hwchase17/openai-functions-agent")

# Initialize Gemini
gemini = ChatGoogleGenerativeAI(
    model="gemini-pro",
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# Define the output schema for task extraction with strict formatting
response_schemas = [
    ResponseSchema(
        name="name",
        description="The name or title of the task. Should be clear and concise."
    ),
    ResponseSchema(
        name="deadline",
        description="The deadline date in DD-MM-YYYY format. If a relative date is given, convert it based on the current date. If no date is specified, use 'N/A'."
    ),
    ResponseSchema(
        name="status",
        description="The current status of the task. Must be exactly one of: ['Not Started', 'In Progress', 'Completed']. Default to 'Not Started' if unclear."
    ),
    ResponseSchema(
        name="priority",
        description="The priority level of the task. Must be exactly one of: ['High', 'Medium', 'Low']. Default to 'Medium' if unclear."
    ),
    ResponseSchema(
        name="category",
        description="The category of the task. Must be one of: ['Development', 'Design', 'Marketing', 'Documentation', 'Testing', 'Operations', 'Other']. Use 'Other' if unclear."
    )
]

output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

def get_current_context():
    """Get current date and time context"""
    now = datetime.now()
    return {
        'current_date': now.strftime('%d-%m-%Y'),
        'current_day': now.strftime('%A'),
        'current_time': now.strftime('%H:%M'),
    }

# Create the enhanced extraction prompt template
extraction_prompt = PromptTemplate(
    template="""
    Current Context:
    - Today's Date: {current_date}
    - Day: {current_day}
    - Current Time: {current_time}

    Extract exactly 5 task-related fields from the following email body using these strict guidelines:

    1. name: 
       - Clear, descriptive task title
       - Capitalize first letter of each word
       - Maximum 50 characters

    2. deadline:
       - Must be in DD - MM - YYYY format
       - Convert relative dates based on current date:
         * "tomorrow" → calculate from current date
         * "next week" → current date + 7 days
         * "end of month" → last day of current month
         * If only day of week is mentioned, use the next occurrence
       - Use 'N/A' if no deadline is mentioned
       - Ensure the deadline is strictly greater than the current date and time; if not, adjust it to tomorrow's date
       - Ensure there are spaces around the dashes

    3. status:
       - Must be EXACTLY one of: ['Not Started', 'In Progress', 'Completed']
       - Default to 'Not Started' if unclear
       - Look for keywords like "started", "working on", "completed", "done"

    4. priority:
       - Must be EXACTLY one of: ['High', 'Medium', 'Low']
       - Default to 'Medium' if unclear
       - Keywords mapping:
         * High: "urgent", "asap", "critical", "important"
         * Low: "when possible", "no rush", "backlog"
         * Medium: everything else

    5. category:
       - Must be EXACTLY one of: ['Development', 'Design', 'Marketing', 'Documentation', 'Testing', 'Operations', 'Other']
       - Use 'Other' if unclear
       - Look for technical keywords to determine category

    Rules:
    - Extract exactly these 5 fields, no more, no less
    - If multiple values could apply, select the most appropriate one
    - Never leave any field empty - use 'N/A' for deadline if not found
    - Standardize all text fields according to the format specified
    - If the email mentions multiple tasks, extract information only for the primary/first task

    Email body:
    {email_body}

    {format_instructions}
    """,
    input_variables=["email_body", "current_date", "current_day", "current_time"],
    partial_variables={"format_instructions": output_parser.get_format_instructions()}
)

composio_toolset = ComposioToolSet(api_key=os.getenv("COMPOSIO_API_KEY"))

# Get Notion-specific tools
tools = composio_toolset.get_tools(actions=[
    'NOTION_INSERT_ROW_DATABASE',
    'NOTION_QUERY_DATABASE',
])

agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

def extract_task_info(email_body):
    """Extract task information from email body using Gemini."""
    try:
        # Get current context
        context = get_current_context()
        
        # Generate the extraction prompt with context
        extraction_input = extraction_prompt.format(
            email_body=email_body,
            current_date=context['current_date'],
            current_day=context['current_day'],
            current_time=context['current_time']
        )
        
        # Get Gemini's response
        response = gemini.invoke(extraction_input)
        
        # Parse the response
        extracted_data = output_parser.parse(response.content)
        
        return extracted_data
    
    except Exception as e:
        raise Exception(f"Failed to extract task information: {str(e)}")

@app.route('/tasks', methods=['POST'])
def create_task():
    try:
        data = request.json
        
        if 'email_body' not in data:
            return jsonify({
                'error': 'Missing email_body in request'
            }), 400
        
        # Extract task information from email body
        extracted_info = extract_task_info(data['email_body'])
        
        # Prepare task creation prompt
        task_prompt = f"""
        Insert a new row into the Notion database with the following properties:
        
        - **Name** (Type: Title): {extracted_info['name']}
        - **Deadline** (Type: Rich Text): {extracted_info['deadline']}
        - **Status** (Type: Rich Text): {extracted_info['status']}
        - **Priority** (Type: Rich Text): {extracted_info['priority']}
        - **Category** (Type: Rich Text): {extracted_info['category']}
        
        Use the database ID: {os.getenv('NOTION_DATABASE_ID')}
        """
        
        # Execute the task creation
        result = agent_executor.invoke({"input": task_prompt})
        
        return jsonify({
            'message': 'Task created successfully',
            'extracted_info': extracted_info,
            'result': result
        }), 201
    
    except Exception as e:
        return jsonify({
            'error': f'Failed to create task: {str(e)}'
        }), 500

@app.route('/tasks', methods=['GET'])
def get_tasks():
    try:
        query_prompt = f"Fetch all rows from the Notion database with database ID: {os.getenv('NOTION_DATABASE_ID')}"
        result = agent_executor.invoke({"input": query_prompt})
        
        return jsonify({
            'tasks': result
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': f'Failed to fetch tasks: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=8080)