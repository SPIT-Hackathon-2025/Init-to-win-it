
# Init-to-win-it

A comprehensive productivity suite with AI-powered services for email analysis, meeting transcription, audio processing, and task management.

## Table of Contents
- [Project Overview](#project-overview)
- [Setup Instructions](#setup-instructions)
- [Architecture Overview](#architecture-overview)
- [Services](#services)
  - [Email Analyzer](#email-analyzer)
  - [Auth Service](#auth-service)
  - [User Services](#user-services)
  - [RL Agent](#rl-agent)
  - [Email Daemon](#email-daemon)
  - [Client](#client)

## Project Overview

Init-to-win-it is an integrated AI-powered productivity platform designed to streamline workflows across multiple communication channels. The system leverages advanced AI technologies including Google's Gemini models, OpenAI, and custom reinforcement learning algorithms to create a comprehensive solution for managing emails, meetings, audio transcriptions, and task planning.

### Core Capabilities

The platform provides several key capabilities:

1. **Intelligent Email Processing** - Automatically analyzes emails to extract key information, prioritize messages, identify action items, and detect meeting invitations.

2. **Meeting Management** - Monitors Google Meet sessions, captures and distributes transcripts, and provides smart summaries of meeting content.

3. **Audio Processing** - Transcribes and analyzes audio recordings with sentiment analysis, key topic extraction, and meeting minute generation.

4. **Smart Task Suggestions** - Uses reinforcement learning to analyze user behavior patterns and suggest optimal next actions based on historical interactions.

5. **Document Generation** - Creates and distributes documents based on analyzed content from various sources.

6. **Authentication & Integration** - Provides secure authentication and seamless integration with Google services (Gmail, Google Docs, Google Meet).

### System Architecture

The platform uses a microservices architecture where each service focuses on a specific functionality:

mermaid
flowchart TD
    %% Main components
    Client[Client Web App]
    
    %% Core Services
    Auth[Auth Service\n5001, 5002]
    Email[Email Analyzer\n5009]
    Daemon[Email Daemon\n5000]
    RL[RL Agent\n5010]
    
    %% User Services
    Meet[Meet Service\n5004]
    Audio[Audio Service\n5050]
    Notion[Notion\n8080]
    
    %% External Systems
    DB[(MongoDB)]
    Google[Google Services]
    AI[AI Models]
    
    %% Connections
    Client --> Auth
    Client --> Email
    Client --> Meet
    Client --> Audio
    Client --> RL
    
    Daemon --> Email
    
    Auth --> DB
    Email --> DB
    RL --> DB
    Meet --> DB
    Audio --> DB
    
    Auth --> Google
    Meet --> Google
    
    Email --> AI
    Audio --> AI
    RL --> AI


### Data Flow

The system processes information through several interconnected workflows:

1. **Email Workflow**:
   - Email Daemon monitors Gmail accounts
   - New emails are sent to Email Analyzer for processing
   - Analysis results are stored in MongoDB
   - UI displays prioritized emails and extracted tasks

2. **Meeting Workflow**:
   - Meet Service monitors Google Meet sessions
   - Meeting transcripts are captured and distributed
   - Audio recordings can be processed by the Audio Service
   - Meeting summaries and action items are extracted

3. **Task Management Workflow**:
   - Tasks extracted from emails and meetings
   - RL Agent analyzes user behavior and suggests optimal tasks
   - Tasks can be integrated with external systems via Notion

4. **Document Workflow**:
   - Content from various sources can generate documents
   - Auth Service manages document creation and sharing
   - Documents can be distributed via email

## Setup Instructions

### Prerequisites
- Python
- Node.js
- MongoDB instance
- Google Cloud account with required APIs enabled

### Quick Setup

1. Clone the repository and navigate to the project folder.

2. Configure environment variables:
   - Each service folder contains configuration settings
   - Create `.env` files in each service folder as needed with appropriate API keys
   - Required API keys include:
     - `MONGODB_URI`: MongoDB connection string
     - `GOOGLE_API_KEY`: Google API key for Gemini AI
     - `OPENAI_API_KEY`: OpenAI API key for certain services
     - `COMPOSIO_API_KEY`: Composio API key for Google integration

3. Starting all services:
bash
bash start_all_servers.sh


4. To stop all services:
bash
bash stop_all_servers.sh


## Architecture Overview

mermaid
graph TB
    Client[Client React App] --> APIServer[API Server]
    Client --> AuthService[Auth Service]
    
    APIServer --> EmailAnalyzer[Email Analyzer]
    APIServer --> UserServices[User Services]
    APIServer --> RLAgent[RL Agent]
    
    EmailDaemon[Email Daemon] --> EmailAnalyzer
    EmailDaemon --> MongoDB[(MongoDB)]
    
    UserServices --> MeetService[Meet Service]
    UserServices --> NotionService[Notion Integration]
    UserServices --> AudioService[Audio Processing]
    UserServices --> ReminderService[Reminder Service]
    
    MeetService --> GoogleMeet[Google Meet API]
    NotionService --> NotionAPI[Notion API]
    AudioService --> SpeechRecognition[Speech Recognition]
    
    EmailAnalyzer --> GeminiAI[Google Gemini AI]
    RLAgent --> MachineLearning[Machine Learning Models]
    
    AuthService --> GoogleAuth[Google Auth]
    AuthService --> JWT[JWT Authentication]


## Services

### Email Analyzer
**Port: 5009**

The Email Analyzer service provides intelligent email analysis using Google's Gemini AI model to prioritize, categorize, and extract key information from emails.

mermaid
sequenceDiagram
    participant EmailDaemon
    participant EmailAnalyzer
    participant GeminiAI
    participant MongoDB
    
    EmailDaemon->>EmailAnalyzer: POST /analyze_email (email_content)
    EmailAnalyzer->>GeminiAI: Process email for key topics, entities, tasks
    GeminiAI-->>EmailAnalyzer: Return structured analysis
    EmailAnalyzer->>EmailAnalyzer: Calculate final priority score
    EmailAnalyzer-->>EmailDaemon: Return comprehensive analysis
    EmailDaemon->>MongoDB: Store email with analysis


#### Features
- Comprehensive email content analysis
- Priority scoring based on content and sender
- Task and meeting extraction
- Calendar event detection
- Spam detection
- Internal/external sender verification
- Authority level assessment

### Auth Service
**Ports: 5001, 5002**

The Auth Service provides authentication and integration with Google services including document creation and email functionalities.

mermaid
flowchart TD
    A[Client] -->|Authentication Request| B[Auth Service]
    B -->|Validate Credentials| C[Google Auth API]
    C -->|Token| B
    B -->|Create Agent| D[LangChain Agent]
    D -->|Access Tools| E[Composio Tools]
    E -->|Gmail Tools| F[Gmail API]
    E -->|Google Docs Tools| G[Google Docs API]
    B -->|Store User Data| H[(MongoDB)]
    A -->|Document Creation Request| B
    B -->|Execute Agent| D
    D -->|Create Document| G
    D -->|Send Email| F


#### Features
- Google authentication
- Document creation with AI
- Email distribution
- Database integration for user records
- OpenAI function-calling integration

### User Services

#### Meet Service
**Port: 5004**

Integrates with Google Meet to monitor meetings, capture transcripts, and distribute them to participants.

mermaid
sequenceDiagram
    participant User
    participant MeetMonitor
    participant GoogleMeet
    participant EmailService
    
    MeetMonitor->>GoogleMeet: Check for new meetings
    GoogleMeet-->>MeetMonitor: Return recent meetings
    MeetMonitor->>GoogleMeet: Get conference record
    GoogleMeet-->>MeetMonitor: Return conference details
    MeetMonitor->>GoogleMeet: Get recordings and transcript
    GoogleMeet-->>MeetMonitor: Return transcript
    MeetMonitor->>MeetMonitor: Process transcript
    MeetMonitor->>EmailService: Send transcript to participants
    EmailService-->>User: Email with meeting transcript


#### Audio Summary Service
**Port: 5050**

Transcribes and analyzes audio recordings from meetings, providing sentiment analysis, key topics, and summaries.

mermaid
flowchart LR
    A[Audio File] -->|Upload| B[Audio Processing Service]
    B -->|Convert| C[WAV Format]
    C -->|Transcribe| D[Speech Recognition]
    D -->|Raw Text| E[Text Processing]
    E -->|Analyze| F{Analysis Pipeline}
    F -->|Sentiment| G[Sentiment Analysis]
    F -->|Topics| H[Key Topic Extraction]
    F -->|Summary| I[Meeting Summary]
    F -->|Minutes| J[Meeting Minutes]
    G -->|Store| K[(MongoDB)]
    H -->|Store| K
    I -->|Store| K
    J -->|Store| K
    K -->|Retrieve| L[Client Application]


#### Features
- Speech-to-text conversion
- Sentiment analysis
- Key topic extraction
- Meeting summary generation
- Meeting minutes creation
- Integration with Notion for documentation

### RL Agent
**Port: 5010**

An AI agent using reinforcement learning to suggest personalized next actions based on user behavior patterns.

mermaid
flowchart TD
    UserData[(User Data)] -->|Historical Actions| RLAgent[RL Agent]
    RLAgent -->|Feature Engineering| FeatureExtraction[Feature Extraction]
    FeatureExtraction -->|Processed Data| ModelPipeline[AI Model Pipeline]
    
    ModelPipeline -->|Evaluate| MAB[Multi-Armed Bandit]
    ModelPipeline -->|Estimate| MCS[Monte Carlo Simulation]
    ModelPipeline -->|Analyze| PGR[Policy Gradient Ranking]
    ModelPipeline -->|Assess| BI[Bayesian Inference]
    ModelPipeline -->|Cluster| KMeans[K-Means Clustering]
    ModelPipeline -->|Learn| DQL[Deep Q-Learning]
    
    MAB -->|Ranked Actions| Aggregator[Result Aggregator]
    MCS -->|Simulated Outcomes| Aggregator
    PGR -->|Policy Scores| Aggregator
    BI -->|Bayesian Scores| Aggregator
    KMeans -->|Cluster Assignment| Aggregator
    DQL -->|Q-Values| Aggregator
    
    Aggregator -->|Final Recommendations| API[API Response]
    API -->|Suggestions| Client[Client Application]


#### Features
- User behavior analysis
- Task prediction using advanced ML algorithms
- Multi-armed bandit approach for optimal action selection
- Monte Carlo simulations for action rewards
- Bayesian inference for uncertainty modeling
- Policy gradient methods for action ranking
- K-means clustering for user behavior patterns
- Deep Q-learning for action optimization

### Email Daemon
**Port: 5000**

Background service that monitors Gmail accounts, fetches new emails, and sends them for analysis.

mermaid
sequenceDiagram
    participant GmailAPI
    participant EmailDaemon
    participant AnalysisService
    participant MongoDB
    
    loop Every 2 minutes
        EmailDaemon->>GmailAPI: Fetch new emails since last check
        GmailAPI-->>EmailDaemon: Return new messages
        
        loop Each email
            EmailDaemon->>EmailDaemon: Extract email body
            EmailDaemon->>AnalysisService: Send for analysis
            AnalysisService-->>EmailDaemon: Return analysis results
            EmailDaemon->>MongoDB: Store email with analysis
        end
        
        EmailDaemon->>MongoDB: Update last check timestamp
    end


#### Features
- Gmail API integration
- Periodic email fetching
- Email content extraction
- Integration with analysis service
- MongoDB storage for emails and metadata

### Client
A React-based web application that provides a unified interface to interact with all services.

mermaid
flowchart TD
    A[Client App] -->|Routes| B[React Router]
    B -->|Dashboard| C[Dashboard Page]
    B -->|Email| D[Email Management]
    B -->|Meetings| E[Meeting Analytics]
    B -->|Tasks| F[Task Management]
    
    C -->|Components| G[Dashboard Components]
    D -->|Components| H[Email Components]
    E -->|Components| I[Meeting Components]
    F -->|Components| J[Task Components]
    
    G -->|API Calls| K[API Services]
    H -->|API Calls| K
    I -->|API Calls| K
    J -->|API Calls| K
    
    K -->|Auth Requests| L[Auth Service]
    K -->|Email Requests| M[Email API]
    K -->|Meeting Requests| N[Meeting API]
    K -->|Task Requests| O[Task API]
    
    L -->|Response| A
    M -->|Response| A
    N -->|Response| A
    O -->|Response| A


#### Features
- Modern React architecture
- Responsive UI with Tailwind CSS
- State management
- API integration with all backend services
- Real-time updates

## Service Ports
- Meet API: 5004 (in user_services/meet)
- Authentication: 5001, 5002 (in auth_service)
- Notion Integration: 8080 (in user_services/notion)
- Audio Processing: 5050 (in user_services/audio_summary)
- RL Agent Model: 5010 (in rl_agent)
- Email Daemon: 5000 (in services/email_deamon)
- Email Analysis: 5009 (in email_analyzer)


