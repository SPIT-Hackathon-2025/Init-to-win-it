from flask import Flask, jsonify, request
from pymongo import MongoClient
import google.generativeai as genai
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize MongoDB connection
client = MongoClient(os.getenv('MONGODB_URI'))
db = client['SPIT_HACK']
user_actions_collection = db['user_data']

# Initialize Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.0-flash')

def format_user_history(actions):
    """Format user history into a structured prompt for Gemini."""
    formatted_history = "\nUser Action History:\n"
    for action in actions:
        formatted_history += f"- Timestamp: {action['timestamp']}\n"
        formatted_history += f"  Agent: {action['agent_used']}\n"
        formatted_history += f"  Task: {action['task_type']}\n"
        formatted_history += f"  Status: {action['completion_status']}\n"
        formatted_history += f"  Priority: {action['priority_level']}\n"
        formatted_history += f"  Feedback: {action['feedback_score']}\n"
        formatted_history += "---\n"
    return formatted_history

def generate_prompt(user_history):
    """Create a detailed prompt for Gemini."""
    prompt = """You are an AI assistant helping to analyze user behavior patterns and suggest next actions on our platform. 
    Based on the following user history, suggest the next 3 most likely actions or tasks the user might want to perform.
    Consider patterns in:
    - Preferred time of day for different tasks
    - Common task sequences
    - Priority patterns
    - Agent preferences
    - Task completion rates
    - User feedback patterns
    
    For each suggestion, provide:
    1. The recommended action/task
    2. Which agent should handle it
    3. Suggested priority level
    4. Brief explanation of why this suggestion is relevant
    
    Here's the user's recent history:"""
    
    prompt += user_history
    
    prompt += "\nPlease provide your suggestions in a clear, structured format."
    return prompt

@app.route('/api/user-suggestions/<user_id>', methods=['GET'])
def get_user_suggestions(user_id):
    try:
        print(f"Received user_id: {user_id}")
        
        # Get user's recent actions from MongoDB (last 30 days)
        from datetime import timezone
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)

        query = {
            'user_id': str(user_id),  # Ensure user_id is treated as a string
            # 'timestamp': {'$gte': thirty_days_ago}
        }
        print(f"Database query: {query}")
        
        user_actions = list(user_actions_collection.find(query).sort('timestamp', -1))
        print("User actions:", user_actions)
        
        if not user_actions:
            return jsonify({
                'error': 'No recent user history found'
            }), 404

        prompt=f"""You are an AI assistant helping to analyze user behavior patterns and suggest next actions on our platform. 
    Based on the following user history, suggest the next 3 most likely actions or tasks the user might want to perform.
    Consider patterns in:
    - Preferred time of day for different tasks
    - Common task sequences
    - Priority patterns
    - Agent preferences
    - Task completion rates
    - User feedback patterns
    
    For each suggestion, provide:
    1. The recommended action/task
    2. Which agent should handle it
    3. Suggested priority level
    4. Brief explanation of why this suggestion is relevant
    
    Here's the user's recent history:{user_actions}.Remember the format of the answer should be such that it shouldnt look ai has generated it.Do not include these kind of words in response Okay, based on the user's recent activity, here are three suggested next actions:1. """
        # Generate prompt based on user history
       
        print("prompt:", prompt)
        # Get suggestions from Gemini
        response = model.generate_content(prompt)
        print("response:", response)
        # Parse and structure Gemini's response
        suggestions = {
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'recent_actions_analyzed': len(user_actions),
            'suggestions': response.text,
            'user_patterns': {
                'most_used_agent': max(set(a['agent_used'] for a in user_actions), 
                                     key=lambda x: sum(1 for a in user_actions if a['agent_used'] == x)),
                'average_feedback': sum(a['feedback_score'] for a in user_actions) / len(user_actions),
                'common_priority': max(set(a['priority_level'] for a in user_actions), 
                                    key=lambda x: sum(1 for a in user_actions if a['priority_level'] == x))
            }
        }

        return jsonify(suggestions)

    except Exception as e:
        return jsonify({
            'error': f'Error generating suggestions: {str(e)}'
        }), 500
    
@app.route('/update/agent', methods=['POST'])
def health_check():
    try:
        # Check if MongoDB is connected
        db_status = client.admin.command('ping')  # MongoDB health check
        
        return jsonify({
            'status': 'ai agent has been successfully updated and retrained with new rewards',
            'message': 'Updation Sucessful',
            'db_status': db_status
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010)