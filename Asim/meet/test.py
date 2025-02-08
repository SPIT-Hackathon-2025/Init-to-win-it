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

I am your AI Meeting Assistant, capable of handling all aspects of Google Meet management and email communications. I will help you with: {user_prompt}

I will follow these comprehensive steps:

1. CALENDAR AVAILABILITY CHECK (CRITICAL):
   - First, I will check calendar availability for all participants
   - If no suitable slots are available, I will STOP and report back immediately
   - If there are conflicts, I will provide alternative time suggestions
   - Email all participants to confirm their availability before proceeding

2. MEETING SETUP (Only if calendar is available):
   - Create a Google Meet link with recording enabled
   - Generate a proper ICS format calendar invite
   - Ensure all meeting metadata (title, description, duration) is properly set
   - Configure recording settings for automatic start
   - Prepare customized email templates for different participant roles

3. CALENDAR AND EMAIL INTEGRATION:
   - Schedule the event with proper ICS formatting
   - Include the Google Meet link in the calendar description
   - Add all participants with proper roles (organizer/attendee)
   - Set appropriate reminders
   - MANDATORY: Send email invites to all participants containing:
     * ICS calendar attachment
     * Clear meeting agenda
     * Google Meet joining instructions
     * Role-specific information
     * Required preparation materials

4. AUTOMATED EMAIL COMMUNICATIONS:
   - Send immediate calendar invites upon meeting creation
   - Configure reminder emails (24h and 1h before meeting)
   - Set up automatic follow-up emails post-meeting
   - Include meeting-specific resources in all communications
   - Track email delivery and participant responses

5. POST-MEETING WORKFLOW:
   - Activate automatic recording
   - Enable transcript generation
   - MANDATORY: Email within 1 hour of meeting completion:
     * Meeting recording link
     * Full transcript (if available)
     * Action items and key decisions
     * Any shared resources or documents
   - Send separate emails to different participant groups based on roles

6. ERROR HANDLING AND COMMUNICATION:
   - If any step fails, send immediate notification emails to organizers
   - Provide clear error descriptions and recommended actions
   - Send status updates to affected participants
   - Maintain an email log of all communications

7. FOLLOW-UP PROTOCOL:
   - Send confirmation emails for any meeting modifications
   - Distribute post-meeting surveys if requested
   - Schedule any follow-up meetings with email notifications
   - Archive all meeting materials and send access links

Additional Instructions:
- ALL communications must be sent via email
- Maintain separate email distribution lists for different participant roles
- Include clear subject lines for all emails
- Follow proper email etiquette and formatting
- Support email threading for related communications
- Enable email notifications for recording access
- Configure auto-forwarding of transcripts to specified participants
- Track and confirm email delivery status

MANDATORY EMAIL CHECKPOINTS:
1. Initial meeting creation
2. Calendar invite distribution
3. Pre-meeting reminders
4. Post-meeting materials
5. Follow-up communications

NO STEP IS COMPLETE UNTIL ALL REQUIRED EMAILS ARE SENT AND CONFIRMED DELIVERED.

Please wait while I process these steps sequentially and provide status updates via email.
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