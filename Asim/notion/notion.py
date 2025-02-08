from flask import Flask, request, jsonify
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain import hub
from langchain_openai import ChatOpenAI
from composio_langchain import ComposioToolSet
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize LangChain and Composio components
llm = ChatOpenAI()
prompt = hub.pull("hwchase17/openai-functions-agent")

composio_toolset = ComposioToolSet(api_key=os.getenv("COMPOSIO_API_KEY"))

# Get Notion-specific tools
tools = composio_toolset.get_tools(actions=[
    'NOTION_INSERT_ROW_DATABASE',
    'NOTION_QUERY_DATABASE',
])

agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

@app.route('/tasks', methods=['POST'])
def create_task():
    try:
        data = request.json
        required_fields = ['name', 'deadline', 'status', 'priority', 'category']
        
        # Validate required fields
        if not all(field in data for field in required_fields):
            return jsonify({
                'error': 'Missing required fields. Required fields are: name, deadline, status, priority, category'
            }), 400

        
        task_prompt = f"""
            Insert a new row into the Notion database with the following properties:

            - **Name** (Type: Title): {data['name']}
            - **Deadline** (Type: Rich Text): {data['deadline']}
            - **Status** (Type: Rich Text): {data['status']}
            - **Priority** (Type: Rich Text): {data['priority']}
            - **Category** (Type: Rich Text): {data['category']}

            Ensure the data is properly formatted before insertion. If any field is missing, handle it gracefully to prevent errors.

            the with database ID: 194017e1ad4d81d597f4c30cec36fdc6s
            """


        # Execute the task creation
        result = agent_executor.invoke({"input": task_prompt})

        return jsonify({
            'message': 'Task created successfully',
            'result': result
        }), 201

    except Exception as e:
        return jsonify({
            'error': f'Failed to create task: {str(e)}'
        }), 500

@app.route('/tasks', methods=['GET'])
def get_tasks():
    try:
        # Prepare query prompt
        query_prompt = f"Fetch all rows from the Notion database with database ID: {os.getenv('NOTION_DATABASE_ID')}"
        
        # Execute the query
        result = agent_executor.invoke({"input": query_prompt})

        return jsonify({
            'tasks': result
        }), 200

    except Exception as e:
        return jsonify({
            'error': f'Failed to fetch tasks: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=True)

