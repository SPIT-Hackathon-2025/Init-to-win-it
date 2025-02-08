from flask import Flask, request, jsonify
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain import hub
from langchain_openai import ChatOpenAI
from composio_langchain import ComposioToolSet
import os
from datetime import datetime
import pytz
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

class MeetingScheduler:
    def __init__(self, openai_api_key, composio_api_key, timezone="Asia/Kolkata"):
        os.environ["OPENAI_API_KEY"] = openai_api_key
        self.timezone = pytz.timezone(timezone)
        self.llm = ChatOpenAI()
        self.prompt = hub.pull("hwchase17/openai-functions-agent")
        
        self.composio_toolset = ComposioToolSet(api_key=composio_api_key)
        self.tools = self.composio_toolset.get_tools(actions=[
            'GOOGLEMEET_CREATE_MEET',
            'GOOGLEMEET_GET_RECORDINGS_BY_CONFERENCE_RECORD_ID',
            'GOOGLEMEET_GET_CONFERENCE_RECORD_FOR_MEET',
            'GOOGLEMEET_GET_MEET',
            'GOOGLECALENDAR_CREATE_EVENT',
            'GOOGLECALENDAR_FIND_FREE_SLOTS',
            'GMAIL_SEND_EMAIL'
        ])
        
        self.agent = create_openai_functions_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True)

    def get_current_time_context(self):
        current_time = datetime.now(self.timezone)
        return current_time.strftime("""
Current Context:
- Date: %A, %B %d, %Y
- Time: %I:%M %p %Z
- Timezone: {}""".format(self.timezone.zone))

    def process_meeting_request(self, user_prompt):
        time_context = self.get_current_time_context()
        
        enhanced_prompt = f"""
{time_context}

I am your AI Meeting Assistant with access to Google Meet, Google Calendar, and Gmail. I will help you with: {user_prompt}

I understand these types of requests:

A. CALENDAR AND FREE SLOT ANALYSIS:
   Command: "CHECK_FREE_SLOTS"
   - I will use GOOGLECALENDAR_FIND_FREE_SLOTS to check availability
   - View all available time slots for specified participants
   - Get optimal meeting times across multiple calendars
   - See conflicts and alternative suggestions
   Example: "Show me free slots for next week with john@email.com and mary@email.com"

B. TRANSCRIPT RETRIEVAL AND MANAGEMENT:
   Command: "GET_TRANSCRIPT"
   - Use GOOGLEMEET_GET_RECORDINGS_BY_CONFERENCE_RECORD_ID to fetch recordings
   - Use GOOGLEMEET_GET_CONFERENCE_RECORD_FOR_MEET to get meeting details
   - Retrieve and format meeting transcripts
   - Send transcripts via email to specified recipients
   Example: "Get me the transcript for meeting ID: abc-123-xyz"

C. MEETING SCHEDULING AND MANAGEMENT:
   Command: "SCHEDULE_MEETING"
   Follow these steps:

1. CALENDAR AVAILABILITY CHECK (CRITICAL):
   - Use GOOGLECALENDAR_FIND_FREE_SLOTS to check participant availability
   - If no slots available: Stop and report
   - If conflicts: Provide alternatives
   - Send availability confirmation emails using GMAIL_SEND_EMAIL

2. MEETING SETUP:
   - Use GOOGLEMEET_CREATE_MEET to generate meeting link
   - Enable recording automatically
   - Use GOOGLECALENDAR_CREATE_EVENT for calendar invite
   - Set up proper meeting metadata

3. CALENDAR AND EMAIL INTEGRATION:
   - Schedule with ICS formatting
   - Include Meet link in description
   - Add participants and roles
   - Use GMAIL_SEND_EMAIL to distribute invites with:
     * Calendar attachment
     * Agenda
     * Joining instructions
     * Role information
     * Required materials

4. AUTOMATED COMMUNICATIONS:
   - Send calendar invites
   - Configure reminder emails
   - Track responses
   - Use GMAIL_SEND_EMAIL for all notifications

5. POST-MEETING WORKFLOW:
   - Use GOOGLEMEET_GET_RECORDINGS_BY_CONFERENCE_RECORD_ID for recordings
   - Use GOOGLEMEET_GET_CONFERENCE_RECORD_FOR_MEET for meeting data
   - Send within 1 hour via GMAIL_SEND_EMAIL:
     * Recording link
     * Transcript
     * Action items
     * Shared resources

6. ERROR HANDLING:
   - Send immediate notifications for failures
   - Provide error details and solutions
   - Keep participants updated
   - Log all communications

7. FOLLOW-UP ACTIONS:
   - Send modification confirmations
   - Distribute post-meeting materials
   - Schedule follow-ups as needed
   - Archive meeting content

VALID COMMANDS:
1. "CHECK_FREE_SLOTS [participants] [timeframe]"
2. "GET_TRANSCRIPT [meeting_id]"
3. "SCHEDULE_MEETING [details]"
4. "SHOW_CALENDAR [timeframe]"
5. "FETCH_RECORDING [meeting_id]"

Available Tools:
- GOOGLEMEET_CREATE_MEET
- GOOGLEMEET_GET_RECORDINGS_BY_CONFERENCE_RECORD_ID
- GOOGLEMEET_GET_CONFERENCE_RECORD_FOR_MEET
- GOOGLEMEET_GET_MEET
- GOOGLECALENDAR_CREATE_EVENT
- GOOGLECALENDAR_FIND_FREE_SLOTS
- GMAIL_SEND_EMAIL

Email Rules:
- All communications via GMAIL_SEND_EMAIL
- Clear subject lines
- Proper email formatting
- Include necessary attachments
- Track delivery status

Required Email Confirmations:
1. Meeting creation
2. Calendar invites
3. Reminders
4. Post-meeting materials
5. Follow-ups

I will handle your request using the available tools and ensure all communications are properly sent and confirmed. Please specify your request using one of the valid commands or in natural language.
"""
        
        try:
            result = self.agent_executor.invoke({"input": enhanced_prompt})
            return {
                "status": "success",
                "result": result,
                "time_context": time_context
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "time_context": time_context
            }

# Initialize the scheduler
scheduler = MeetingScheduler(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    composio_api_key=os.getenv("COMPOSIO_API_KEY")
)

@app.route('/meet', methods=['POST'])
def schedule_meeting():
    try:
        data = request.json
        if not data or 'prompt' not in data:
            return jsonify({
                "status": "error",
                "message": "No prompt provided in request body"
            }), 400
        
        result = scheduler.process_meeting_request(data['prompt'])
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Server error: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)