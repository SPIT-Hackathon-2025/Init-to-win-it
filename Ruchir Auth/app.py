from flask import Flask, request, jsonify
from maal  import maal , maal ToolSet # type: ignore
from flask_cors import CORS # type: ignore
from dotenv import load_dotenv
import os
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain import hub
from langchain_openai import ChatOpenAI
from datetime import datetime
from maal _langchain import maal ToolSet, Action, App
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
MONGO_URL = os.getenv('MONGO_URL')  # Add this line
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# Initialize MongoDB connection with error handling and retry logic
def get_database():
    try:
        mongo_url = os.getenv('MONGO_URL')
        if not mongo_url:
            raise ValueError("MONGO_URL not found in environment variables")
            
        client = MongoClient(mongo_url, serverSelectionTimeoutMS=5000)
        # Force a connection to verify it works
        client.server_info()
        return client.get_database("email_db")
    except Exception as e:
        print(f"MongoDB Connection Error: {e}")
        return None

# Initialize Flask app and database
app = Flask(__name__)
CORS(app)
db = get_database()

@app.route('/api-auth', methods=['POST'])
def api_auth():
    try:
        # Get API key from request parameters
        api_key = request.json.get('api_key')
        if not api_key:
            return jsonify({"error": "API key is required"}), 400

        # Initialize maal  client
        maal  = maal (api_key=api_key)
        gmail_app = maal .apps.get(name="gmail")

        # Create integration using environment variables
        integration = maal .integrations.create(
            app_id=gmail_app.appId,
            auth_config={
                "client_id": os.getenv('GOOGLE_CLIENT_ID'),
                "client_secret": os.getenv('GOOGLE_CLIENT_SECRET'),
                "oauth_redirect_uri": "https://backend.maal .dev/api/v1/auth-apps/add",
                "scopes": "https://www.googleapis.com/auth/gmail.modify,https://www.googleapis.com/auth/userinfo.profile"
            },
            auth_mode="OAUTH2",
            force_new_integration=True,
            name="gmail_1",
            use_maal _auth=False
        )

        # Initialize toolset and get connection URL
        toolset = maal ToolSet(api_key=api_key)
        connection_request = toolset.initiate_connection(
            integration_id=integration.id,
            entity_id="default"
        )

        return jsonify({
            "redirectUrl": connection_request.redirectUrl,
            "connectedAccountId": connection_request.connectedAccountId
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get-events', methods=['POST'])
def get_events():
    try:
        api_key = request.json.get('api_key')
        if not api_key:
            return jsonify({"error": "API key is required"}), 400

        current_date = datetime.now()
        formatted_date = current_date.strftime("%Y,%m,%d,00,00,00")

        llm = ChatOpenAI()
        prompt = hub.pull("hwchase17/openai-functions-agent")

        maal _toolset = maal ToolSet(api_key=api_key)
        tools = maal _toolset.get_tools(actions=['GOOGLECALENDAR_FIND_EVENT'])

        agent = create_openai_functions_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        task = f"give me max_results=5 next events timeMin={formatted_date}"

        result = agent_executor.invoke({"input": task})
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get-maildb', methods=['GET'])
def get_maildb():
    try:
        if db is None:  # Changed from 'if not db' to 'if db is None'
            return jsonify({
                "status": "error",
                "message": "Database connection not available"
            }), 500

        print(db)
        # Get the collection
        collection = db.emails
        
        # Fetch all documents from the collection
        documents = list(collection.find({}, {'_id': 0}))
        
        return jsonify({
            "status": "success",
            "count": len(documents),
            "data": documents
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
