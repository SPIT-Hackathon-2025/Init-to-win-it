import os
import time
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from pymongo import MongoClient
import pickle
import datetime
import base64  # added import

# Load environment variables
load_dotenv()

# Environment variables
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
GMAIL_CREDENTIALS = os.getenv('GMAIL_CREDENTIALS', 'credentials.json')
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', 120))  # 2 minutes in seconds

class GmailMonitor:
    def __init__(self):
        # MongoDB setup
        self.client = MongoClient(MONGODB_URI)
        self.db = self.client['email_db']
        self.emails = self.db['emails']
        self.metadata = self.db['metadata']
        
        # Gmail API setup
        self.SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
        
        # Initialize last check timestamp
        self.initialize_timestamp()

    def initialize_timestamp(self):
        """Initialize or get the last check timestamp from MongoDB"""
        timestamp_doc = self.metadata.find_one({'_id': 'last_check'})
        if not timestamp_doc:
            # Start from 24 hours ago if no timestamp exists
            initial_timestamp = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)
            self.metadata.insert_one({
                '_id': 'last_check',
                'timestamp': initial_timestamp
            })
            self.last_check_time = initial_timestamp
        else:
            self.last_check_time = timestamp_doc['timestamp']

    def update_timestamp(self):
        """Update the last check timestamp in MongoDB"""
        current_time = datetime.datetime.now(datetime.timezone.utc)
        self.metadata.update_one(
            {'_id': 'last_check'},
            {'$set': {'timestamp': current_time}},
            upsert=True
        )
        self.last_check_time = current_time

    def get_gmail_service(self):
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    GMAIL_CREDENTIALS, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        return build('gmail', 'v1', credentials=creds)

    def fetch_new_emails(self):
        try:
            service = self.get_gmail_service()
            
            # Convert timestamp to Gmail's query format
            # Gmail API uses seconds since epoch for comparison
            after_timestamp = int(self.last_check_time.timestamp())
            query = f'after:{after_timestamp}'
            
            results = service.users().messages().list(
                userId='me',
                q=query
            ).execute()
            
            messages = results.get('messages', [])
            
            for message in messages:
                msg = service.users().messages().get(
                    userId='me',
                    id=message['id'],
                    format='full'
                ).execute()
                
                # Extract email details
                headers = msg['payload']['headers']
                subject = next(
                    (header['value'] for header in headers if header['name'].lower() == 'subject'),
                    'No Subject'
                )
                sender = next(
                    (header['value'] for header in headers if header['name'].lower() == 'from'),
                    'No Sender'
                )
                
                # Get internal date from the email (in milliseconds since epoch)
                received_date = datetime.datetime.fromtimestamp(
                    int(msg['internalDate']) / 1000,
                    tz=datetime.timezone.utc
                )
                
                # Extract full email content from payload
                payload = msg.get('payload', {})
                full_body = ""
                if 'parts' in payload:
                    for part in payload['parts']:
                        if part.get('mimeType', '').startswith('text/'):
                            data = part.get('body', {}).get('data', '')
                            if data:
                                full_body += base64.urlsafe_b64decode(data.encode('UTF-8')).decode('utf-8', errors='replace')
                else:
                    data = payload.get('body', {}).get('data', '')
                    if data:
                        full_body = base64.urlsafe_b64decode(data.encode('UTF-8')).decode('utf-8', errors='replace')
                
                # Store only if not already in database
                if not self.emails.find_one({'message_id': message['id']}):
                    email_doc = {
                        'message_id': message['id'],
                        'subject': subject,
                        'sender': sender,
                        'received_at': received_date,
                        'stored_at': datetime.datetime.now(datetime.timezone.utc),
                        'snippet': msg.get('snippet', ''),
                        'labels': msg.get('labelIds', []),
                        'body': full_body  # added full email content
                    }
                    self.emails.insert_one(email_doc)
                    print(f"New email stored: {subject} (received at {received_date})")
            
            # Update the timestamp after successful fetch
            self.update_timestamp()
            
        except Exception as e:
            print(f"Error fetching emails: {str(e)}")

    def run(self):
        print("Gmail monitor started. Press Ctrl+C to stop.")
        try:
            while True:
                current_time = datetime.datetime.now(datetime.timezone.utc)
                print(f"\nChecking for new emails at {current_time}")
                print(f"Fetching emails since: {self.last_check_time}")
                self.fetch_new_emails()
                time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            print("\nStopping Gmail monitor...")
            self.client.close()

if __name__ == "__main__":
    monitor = GmailMonitor()
    monitor.run()