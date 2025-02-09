from flask import Flask, jsonify, request
import json
import speech_recognition as sr
from pydub import AudioSegment
from pathlib import Path
import os
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pymongo import MongoClient
import numpy as np
from datetime import datetime
from collections import Counter
from textblob import TextBlob
import spacy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import CountVectorizer
import re
from keybert import KeyBERT
import logging
from werkzeug.serving import WSGIRequestHandler
from dotenv import load_dotenv
import time
import contextlib
import wave
from flask.json.provider import DefaultJSONProvider

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('audio_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CustomJSONProvider(DefaultJSONProvider):
    """Custom JSON provider to handle NumPy and datetime types"""
    def default(self, obj):
        try:
            # Handle all numpy numeric types
            if hasattr(obj, 'dtype'):
                if np.issubdtype(obj.dtype, np.integer):
                    return int(obj)
                elif np.issubdtype(obj.dtype, np.floating):
                    return float(obj)
            # Handle numpy arrays
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            # Handle datetime objects
            elif isinstance(obj, datetime):
                return obj.isoformat()
            return super().default(obj)
        except Exception as e:
            # Fallback for any other types that can't be serialized
            return str(obj)

app = Flask(__name__)
app.json = CustomJSONProvider(app)
app.config['TIMEOUT'] = 600  # 10 minutes in seconds

# MongoDB setup
client = MongoClient(os.getenv('MONGODB_URI'))
db = client['SPIT_HACK']
meets_collection = db['meet_details']
print(meets_collection)
analysis_collection = db['meet_analysis']

# Initialize models and tools
nlp = spacy.load('en_core_web_sm')
sentiment_analyzer = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")
emotion_analyzer = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base")
key_phrase_model = KeyBERT()
vader_analyzer = SentimentIntensityAnalyzer()

# Initialize Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    logger.error("GOOGLE_API_KEY not found in environment variables")
    raise ValueError("GOOGLE_API_KEY is required. Please set it in your .env file")

try:
    genai.configure(api_key=GOOGLE_API_KEY)
    llm = GoogleGenerativeAI(model="gemini-pro", google_api_key=GOOGLE_API_KEY)
    logger.info("Successfully configured Gemini API")
except Exception as e:
    logger.error(f"Failed to configure Gemini API: {str(e)}")
    raise


import os
import speech_recognition as sr
from pydub import AudioSegment
from pathlib import Path
import subprocess
import logging
from datetime import datetime

def check_ffmpeg():
    """Check if FFmpeg is installed and accessible"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        logger.info("✓ FFmpeg is installed and accessible")
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        logger.error("✗ FFmpeg is not installed or not accessible")
        logger.info("\nPlease install FFmpeg using one of these methods:")
        logger.info("1. Using Chocolatey (recommended):")
        logger.info("   choco install ffmpeg")
        logger.info("\n2. Manual installation:")
        logger.info("   a. Download from: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-full.7z")
        logger.info("   b. Extract to C:\\ffmpeg")
        logger.info("   c. Add C:\\ffmpeg\\bin to your system PATH")
        return False

def convert_mp3_to_wav(mp3_path):
    """Convert MP3 file to WAV format"""
    try:
        wav_path = mp3_path.with_suffix('.wav')
        logger.info(f"Converting: {mp3_path}")
        logger.info(f"Output to: {wav_path}")
        
        audio = AudioSegment.from_mp3(str(mp3_path))
        audio.export(str(wav_path), format="wav")
        logger.info("✓ Conversion successful")
        return wav_path
    except Exception as e:
        logger.error(f"Error during conversion: {str(e)}")
        raise

def transcribe_audio(audio_path):
    """
    Transcribe audio file to text using Google Speech Recognition.
    
    Args:
        audio_path (str): Path to the audio file
        
    Returns:
        str: Transcribed text or None if transcription fails
    """
    try:
        logger.info(f"Starting transcription for: {audio_path}")
        
        # Check FFmpeg installation first
        if not check_ffmpeg():
            logger.error("FFmpeg check failed - cannot proceed with transcription")
            return None

        # Initialize recognizer with increased timeout
        recognizer = sr.Recognizer()
        recognizer.operation_timeout = 600  # 10 minutes timeout
        
        # Convert path to Path object
        audio_file = Path(audio_path)
        if not audio_file.exists():
            logger.error(f"Audio file not found: {audio_path}")
            return None
            
        # Handle MP3 files by converting to WAV first
        if audio_file.suffix.lower() == '.mp3':
            try:
                wav_file = convert_mp3_to_wav(audio_file)
                audio_file = wav_file
            except Exception as e:
                logger.error(f"Error converting MP3 to WAV: {str(e)}")
                return None
        
        # Read and transcribe the audio file
        logger.info("Starting transcription...")
        start_time = datetime.now()
        
        with sr.AudioFile(str(audio_file)) as source:
            logger.info("Reading audio file...")
            audio_data = recognizer.record(source)
            
            logger.info("Sending to Google Speech Recognition...")
            text = recognizer.recognize_google(audio_data)
            
            # Calculate transcription time
            duration = datetime.now() - start_time
            logger.info(f"Transcription completed in {duration.total_seconds():.2f} seconds")
            
            # Save transcription to a text file with same name as audio file
            output_file = audio_file.with_suffix('.txt')
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(text)
            
            logger.info(f"Transcription saved to: {output_file}")
            logger.info("Preview:")
            logger.info(f"{text[:200]}..." if len(text) > 200 else text)
        
        # Clean up temporary WAV file if it was converted from MP3
        if audio_file.suffix.lower() == '.wav' and audio_file != Path(audio_path):
            audio_file.unlink()
            logger.info("Temporary WAV file cleaned up")
            
        return text
        
    except sr.RequestError as e:
        logger.error(f"Google Speech Recognition request failed: {e}")
        return None
    except sr.UnknownValueError:
        logger.error(f"Could not understand audio in file: {audio_path}")
        return None
    except Exception as e:
        logger.error(f"Error processing {audio_path}: {e}", exc_info=True)
        return None

def generate_meeting_summary(transcript):
    """Generate meeting summary using Gemini"""
    try:
        summary_prompt = f"""
        Based on this meeting transcript, provide a structured analysis in the following format:
        
        1. Executive Summary (2-3 paragraphs)
        2. Key Points Discussed (bullet points)
        3. Action Items:
           - Who is responsible
           - What needs to be done
           - Timeline if mentioned
        4. Decisions Made
        5. Next Steps
        
        Transcript: {transcript}
        """
        
        summary = llm.invoke(summary_prompt)
        return summary
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        raise

def generate_meeting_minutes(transcript, meeting_details):
    """Generate formal meeting minutes using Gemini with meeting details"""
    try:
        # Format meeting details
        start_time = datetime.strptime(meeting_details.get('start_time', ''), "%Y-%m-%dT%H:%M:%SZ")
        end_time = datetime.strptime(meeting_details.get('end_time', ''), "%Y-%m-%dT%H:%M:%SZ")
        duration = (end_time - start_time).total_seconds() / 60  # in minutes
        
        participants = meeting_details.get('participants', [])
        attendee_list = "\n".join([
            f"- {p['name']} (Joined: {p['join_time']}, Left: {p['leave_time']})"
            for p in participants
        ])

        minutes_prompt = f"""
        Create formal meeting minutes using the following details:
        
        Meeting Date: {start_time.strftime('%B %d, %Y')}
        Start Time: {start_time.strftime('%I:%M %p')}
        End Time: {end_time.strftime('%I:%M %p')}
        Duration: {duration:.0f} minutes
        
        Attendees:
        {attendee_list}
        
        Please include:
        1. Meeting Overview
        2. Agenda Items Covered
        3. Discussion Points
        4. Action Items and Owners
        5. Next Steps
        6. Next Meeting (if mentioned)
        
        Use this transcript to generate the minutes:
        {transcript}
        """
        
        minutes = llm.invoke(minutes_prompt)
        return {
            'formatted_minutes': minutes,
            'metadata': {
                'date': start_time.strftime('%Y-%m-%d'),
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'duration_minutes': duration,
                'participant_count': len(participants),
                'participants': participants
            }
        }
    except Exception as e:
        logger.error(f"Error generating minutes: {str(e)}")
        raise

def analyze_sentiment(transcript):
    """Perform sentiment analysis on the transcript"""
    try:
        # Overall sentiment analysis
        overall_sentiment = vader_analyzer.polarity_scores(transcript)
        
        # Break transcript into segments for detailed analysis
        segments = [s.strip() for s in transcript.split('.') if s.strip()]
        segment_analysis = []
        
        for segment in segments:
            scores = vader_analyzer.polarity_scores(segment)
            segment_analysis.append({
                'text': segment,
                'sentiment': scores
            })
        
        return {
            'overall_sentiment': overall_sentiment,
            'detailed_analysis': segment_analysis,
            'summary': {
                'positive_segments': len([s for s in segment_analysis if s['sentiment']['compound'] > 0.05]),
                'negative_segments': len([s for s in segment_analysis if s['sentiment']['compound'] < -0.05]),
                'neutral_segments': len([s for s in segment_analysis if abs(s['sentiment']['compound']) <= 0.05])
            }
        }
    except Exception as e:
        logger.error(f"Error in sentiment analysis: {str(e)}")
        raise

@app.route('/analyze/<meet_id>', methods=['POST'])
def analyze_meeting(meet_id):
    try:
        logger.info(f"Starting analysis for meet_id: {meet_id}")
        
        # Get meeting details from database
        meeting = meets_collection.find_one({'meet_id': meet_id})
        if not meeting:
            return jsonify({'error': 'Meeting not found'}), 404
        
        # Handle transcription if needed
        transcript = meeting.get('transcript')
        if not transcript:
            logger.info(f"No transcript found, attempting transcription for meet_id: {meet_id}")
            audio_path = meeting.get('audio_path')
            
            if not audio_path:
                return jsonify({'error': 'No audio path found'}), 400
                
            transcript = transcribe_audio(audio_path)
            if not transcript:
                return jsonify({'error': 'Transcription failed'}), 500
                
            # Update meeting document with transcript
            meets_collection.update_one(
                {'meet_id': meet_id},
                {'$set': {'transcript': transcript}}
            )
            logger.info(f"Transcription completed and saved for meet_id: {meet_id}")
        
        # Store participants in separate collection
        participants_collection = db['meeting_participants']
        participant_doc = {
            'meet_id': meet_id,
            'timestamp': datetime.utcnow(),
            'participants': meeting.get('participants', []),
            'total_participants': len(meeting.get('participants', [])),
            'duration_minutes': meeting.get('duration_minutes', 0)
        }
        participants_collection.insert_one(participant_doc)
        
        # Generate analysis with complete meeting details
        summary = generate_meeting_summary(transcript)
        minutes = generate_meeting_minutes(transcript, meeting)
        sentiment = analyze_sentiment(transcript)
        
        # Create comprehensive analysis document
        analysis = {
            'meet_id': meet_id,
            'timestamp': datetime.utcnow(),
            'meeting_details': {
                'start_time': meeting.get('start_time'),
                'end_time': meeting.get('end_time'),
                'duration_minutes': meeting.get('duration_minutes'),
                'host': meeting.get('host'),
                'title': meeting.get('title'),
                'participant_count': len(meeting.get('participants', []))
            },
            'transcript': transcript,
            'summary': summary,
            'minutes': minutes,
            'sentiment_analysis': sentiment,
            'participants': participant_doc
        }
        
        # Store analysis
        analysis_collection.insert_one(analysis)
        logger.info(f"Analysis completed and stored for meet_id: {meet_id}")
        
        return jsonify({
            'message': 'Analysis completed successfully',
            'meet_id': meet_id,
            'transcript_preview': transcript[:200] + '...' if len(transcript) > 200 else transcript,
            'participant_count': len(meeting.get('participants', [])),
            'duration_minutes': meeting.get('duration_minutes', 0)
        })
        
    except Exception as e:
        logger.error(f"Error analyzing meeting {meet_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/getAnalysis/<meet_id>', methods=['GET'])
def get_analysis(meet_id):
    try:
        analysis = analysis_collection.find_one({'meet_id': meet_id})
        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404
            
        analysis['_id'] = str(analysis['_id'])
        return jsonify(analysis)
        
    except Exception as e:
        logger.error(f"Error fetching analysis for meet_id {meet_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info("Starting Meeting Analysis Server...")
    app.run(debug=True, port=5050)