from flask import Flask, request, jsonify
from composio import Composio, ComposioToolSet
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

@app.route('/api-auth', methods=['POST'])
def api_auth():
    try:
        # Get API key from request parameters
        api_key = request.json.get('api_key')
        if not api_key:
            return jsonify({"error": "API key is required"}), 400

        # Initialize Composio client
        composio = Composio(api_key=api_key)
        gmail_app = composio.apps.get(name="gmail")

        # Create integration using environment variables
        integration = composio.integrations.create(
            app_id=gmail_app.appId,
            auth_config={
                "client_id": os.getenv('GOOGLE_CLIENT_ID'),
                "client_secret": os.getenv('GOOGLE_CLIENT_SECRET'),
                "oauth_redirect_uri": "https://backend.composio.dev/api/v1/auth-apps/add",
                "scopes": "https://www.googleapis.com/auth/gmail.modify,https://www.googleapis.com/auth/userinfo.profile"
            },
            auth_mode="OAUTH2",
            force_new_integration=True,
            name="gmail_1",
            use_composio_auth=False
        )

        # Initialize toolset and get connection URL
        toolset = ComposioToolSet(api_key=api_key)
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

if __name__ == '__main__':
    app.run(debug=True, port=5001)
