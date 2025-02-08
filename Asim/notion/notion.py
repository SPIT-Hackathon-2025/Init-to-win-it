from flask import Flask, request, jsonify, render_template
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from composio_langchain import ComposioToolSet
from langchain.prompts import PromptTemplate
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from apscheduler.schedulers.background import BackgroundScheduler
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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

# Define response schemas for task extraction
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

# Constants
CSV_FILE_PATH = 'notion_mock_tasks.csv'
TEMPLATES_DIR = Path('templates')
DASHBOARD_TEMPLATE = TEMPLATES_DIR / 'dashboard.html'
ANALYSIS_FILE = 'analysis_results.json'

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

    Email body:
    {email_body}

    {format_instructions}
    """,
    input_variables=["email_body", "current_date", "current_day", "current_time"],
    partial_variables={"format_instructions": output_parser.get_format_instructions()}
)

# Initialize Composio tools
composio_toolset = ComposioToolSet(api_key=os.getenv("COMPOSIO_API_KEY"))
tools = composio_toolset.get_tools(actions=[
    'NOTION_INSERT_ROW_DATABASE',
    'NOTION_QUERY_DATABASE',
])

agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

def initialize_csv():
    """Initialize CSV file with headers if it doesn't exist"""
    if not os.path.exists(CSV_FILE_PATH):
        headers = ['Name', 'Deadline', 'Status', 'Priority', 'Category']
        pd.DataFrame(columns=headers).to_csv(CSV_FILE_PATH, index=False)
        logger.info(f"Created new CSV file at {CSV_FILE_PATH}")

def save_to_csv(task_data):
    """Save task data to CSV file"""
    try:
        initialize_csv()
        df = pd.DataFrame([task_data])
        df.to_csv(CSV_FILE_PATH, mode='a', header=False, index=False)
        logger.info(f"Successfully saved task to CSV: {task_data['name']}")
    except Exception as e:
        logger.error(f"Error saving to CSV: {str(e)}")
        raise

def extract_task_info(email_body):
    """Extract task information from email body using Gemini"""
    try:
        context = get_current_context()
        extraction_input = extraction_prompt.format(
            email_body=email_body,
            current_date=context['current_date'],
            current_day=context['current_day'],
            current_time=context['current_time']
        )
        response = gemini.invoke(extraction_input)
        extracted_data = output_parser.parse(response.content)
        logger.info(f"Successfully extracted task info: {extracted_data['name']}")
        return extracted_data
    except Exception as e:
        logger.error(f"Error extracting task info: {str(e)}")
        raise

def generate_ai_insights(df):
    """Generate comprehensive AI insights using Gemini"""
    try:
        # Prepare data for analysis
        total_tasks = len(df)
        urgent_tasks = len(df[df['Days_to_Deadline'] <= 3])
        overdue_tasks = len(df[df['Days_to_Deadline'] < 0])
        category_counts = df['Category'].value_counts().to_dict()
        priority_counts = df['Priority'].value_counts().to_dict()
        
        analysis_prompt = f"""
        Analyze this task management data and provide comprehensive optimization advice:

        Task Overview:
        - Total Tasks: {total_tasks}
        - Urgent Tasks (≤3 days): {urgent_tasks}
        - Overdue Tasks: {overdue_tasks}

        Category Distribution:
        {json.dumps(category_counts, indent=2)}

        Priority Distribution:
        {json.dumps(priority_counts, indent=2)}

        Please provide detailed insights including:
        1. Workload Analysis
           - Current workload distribution
           - Bottlenecks and potential risks
           - Resource allocation recommendations

        2. Priority Management
           - High-priority task handling strategy
           - Risk mitigation for urgent tasks
           - Balancing urgent vs. important tasks

        3. Timeline Optimization
           - Deadline management recommendations
           - Task sequencing suggestions
           - Resource leveling strategies

        4. Category-specific Strategies
           - Recommendations for each task category
           - Cross-category dependencies
           - Resource optimization per category

        5. Efficiency Improvements
           - Process optimization suggestions
           - Team collaboration recommendations
           - Productivity enhancement strategies

        Format the response in HTML with proper headers and bullet points.
        """
        
        response = gemini.invoke(analysis_prompt)
        return response.content
    except Exception as e:
        logger.error(f"Error generating AI insights: {e}")
        return "Error generating AI insights"

def generate_enhanced_graphs(df):
    """Generate comprehensive set of graphs"""
    graphs = {}
    
    # 1. Status Distribution with details
    fig_status = px.pie(df, names='Status', title='Task Status Distribution',
                       color_discrete_sequence=px.colors.qualitative.Set3,
                       hover_data=['Category', 'Priority'])
    
    # 2. Priority Distribution with timeline
    fig_priority = px.sunburst(df, path=['Priority', 'Category'], 
                              color='Days_to_Deadline',
                              title='Priority and Category Distribution')
    
    # 3. Enhanced Timeline
    fig_timeline = px.timeline(df, x_start='Deadline', x_end='Deadline_End',
                             y='Category', color='Priority',
                             hover_data=['Status', 'Days_to_Deadline'])
    
    # 4. Category Distribution
    fig_category = px.treemap(df, path=['Category', 'Priority', 'Status'],
                             title='Task Category Hierarchy')
    
    # 5. Priority-Category Matrix
    matrix_data = pd.crosstab(df['Priority'], df['Category'])
    fig_matrix = px.imshow(matrix_data, title='Priority-Category Matrix',
                          color_continuous_scale='Viridis')
    
    # 6. Deadline Distribution
    fig_deadline = px.histogram(df, x='Days_to_Deadline',
                               color='Priority', nbins=20,
                               title='Days to Deadline Distribution')
    
    # 7. Weekly Workload
    df['Week'] = df['Deadline'].dt.isocalendar().week
    workload = df.groupby(['Week', 'Category']).size().unstack(fill_value=0)
    fig_workload = px.bar(workload, title='Weekly Workload by Category',
                         barmode='stack')
    
    # 8. Completion Trend
    completion = df[df['Status'] == 'Completed'].groupby('Week').size()
    fig_completion = px.line(x=completion.index, y=completion.values,
                            title='Task Completion Trend',
                            labels={'x': 'Week', 'y': 'Completed Tasks'})
    
    # 9. Category Relationships
    category_matrix = pd.crosstab(df['Category'], df['Status'])
    fig_relationships = px.scatter_matrix(df, dimensions=['Days_to_Deadline', 'Priority'],
                                        color='Category', title='Task Relationships')
    
    # Convert all figures to HTML
    graphs = {
        'status_distribution': fig_status.to_html(
            full_html=False,
            include_plotlyjs=False,
            config={'responsive': True}
        ),
        'priority_distribution': fig_priority.to_html(
            full_html=False,
            include_plotlyjs=False,
            config={'responsive': True}
        ),
        'timeline': fig_timeline.to_html(
            full_html=False,
            include_plotlyjs=False,
            config={'responsive': True}
        ),
        'category_distribution': fig_category.to_html(
            full_html=False,
            include_plotlyjs=False,
            config={'responsive': True}
        ),
        'priority_category_matrix': fig_matrix.to_html(
            full_html=False,
            include_plotlyjs=False,
            config={'responsive': True}
        ),
        'deadline_distribution': fig_deadline.to_html(
            full_html=False,
            include_plotlyjs=False,
            config={'responsive': True}
        ),
        'workload_distribution': fig_workload.to_html(
            full_html=False,
            include_plotlyjs=False,
            config={'responsive': True}
        ),
        'category_relationships': fig_relationships.to_html(
            full_html=False,
            include_plotlyjs=False,
            config={'responsive': True}
        )
    }
    
    return graphs

def generate_task_analysis():
    try:
        if not os.path.exists(CSV_FILE_PATH):
            logger.warning("No tasks found in CSV file")
            return None

        df = pd.read_csv(CSV_FILE_PATH)
        df['Deadline'] = pd.to_datetime(df['Deadline'], format='%d - %m - %Y')
        df['Deadline_End'] = df['Deadline'] + pd.Timedelta(days=1)
        df['Days_to_Deadline'] = (df['Deadline'] - pd.Timestamp(datetime.now())).dt.days

        # Generate enhanced graphs
        graphs = generate_enhanced_graphs(df)
        
        # Generate AI insights
        ai_insights = generate_ai_insights(df)
        
        # Basic statistics for API
        insights = {
            'total_tasks': len(df),
            'urgent_tasks': len(df[df['Days_to_Deadline'] <= 3]),
            'overdue_tasks': len(df[df['Days_to_Deadline'] < 0]),
            'tasks_by_status': df['Status'].value_counts().to_dict(),
            'tasks_by_priority': df['Priority'].value_counts().to_dict(),
            'tasks_by_category': df['Category'].value_counts().to_dict(),
            'ai_insights': ai_insights
        }
        
        return {'graphs_html': graphs, 'insights_json': insights}
    except Exception as e:
        logger.error(f"Error generating task analysis: {str(e)}")
        raise

def store_analysis_results(analysis_data):
    """Store analysis results in a JSON file"""
    try:
        with open(ANALYSIS_FILE, 'w') as f:
            json.dump(analysis_data, f, indent=2)
        logger.info("Analysis results stored successfully")
    except Exception as e:
        logger.error(f"Error storing analysis results: {str(e)}")
        raise

def load_analysis_results():
    """Load analysis results from JSON file"""
    try:
        if not os.path.exists(ANALYSIS_FILE):
            return None
        with open(ANALYSIS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading analysis results: {str(e)}")
        return None

@app.route('/tasks', methods=['POST'])
def create_task():
    """Create a new task from email body"""
    try:
        data = request.json
        
        if 'email_body' not in data:
            return jsonify({'error': 'Missing email_body in request'}), 400
        
        # Extract task information
        extracted_info = extract_task_info(data['email_body'])
        
        # Save to CSV
        save_to_csv(extracted_info)
        
        # Create task in Notion
        task_prompt = f"""
        Insert a new row into the Notion database with the following properties:
        
        - **Name** (Type: Title): {extracted_info['name']}
        - **Deadline** (Type: Rich Text): {extracted_info['deadline']}
        - **Status** (Type: Rich Text): {extracted_info['status']}
        - **Priority** (Type: Rich Text): {extracted_info['priority']}
        - **Category** (Type: Rich Text): {extracted_info['category']}
        
        Use the database ID: {os.getenv('NOTION_DATABASE_ID')}
        """
        
        result = agent_executor.invoke({"input": task_prompt})
        
        # Trigger analysis update
        generate_task_analysis()
        
        return jsonify({
            'message': 'Task created successfully',
            'extracted_info': extracted_info,
            'result': result
        }), 201
    
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        return jsonify({
            'error': f'Failed to create task: {str(e)}'
        }), 500

@app.route('/dashboard')
def dashboard():
    """Render the task graphs dashboard"""
    try:
        analysis = generate_task_analysis()
        graphs = analysis.get('graphs_html')
        if not graphs:
            return "No graphs available", 404
        dashboard_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Task Graphs Dashboard</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
        </head>
        <body class="bg-gray-100">
            <div class="container mx-auto px-4 py-8">
                <header class="mb-8">
                    <h1 class="text-4xl font-bold">Task Graphs Dashboard</h1>
                    <p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </header>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>{graphs['graph_status']}</div>
                    <div>{graphs['graph_priority_category']}</div>
                    <div>{graphs['graph_timeline']}</div>
                    <div>{graphs['graph_deadline_histogram']}</div>
                    <div class="md:col-span-2">{graphs['graph_completion_trend']}</div>
                </div>
            </div>
        </body>
        </html>
        """
        return dashboard_html
    except Exception as e:
        logger.error(f"Error rendering dashboard: {str(e)}")
        return jsonify({'error': f'Failed to render dashboard: {str(e)}'}), 500

@app.route('/api/analysis')
def get_analysis():
    """Get the latest task analysis insights from stored results"""
    try:
        analysis = load_analysis_results()
        if not analysis:
            # If stored analysis doesn't exist, generate new one
            analysis = generate_task_analysis()
            store_analysis_results(analysis)
        return jsonify(analysis.get('insights_json', {})), 200
    except Exception as e:
        logger.error(f"Error getting analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/graphs')
def show_graphs():
    """Render the comprehensive graphs dashboard"""
    try:
        analysis = generate_task_analysis()
        if not analysis or not analysis.get('graphs_html'):
            return "No data available", 404
        
        # Add plot.js configuration for better rendering
        return render_template(
            'graphs.html',
            graphs=analysis['graphs_html'],
            ai_insights=analysis['insights_json'].get('ai_insights', ''),
            last_updated=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
    except Exception as e:
        logger.error(f"Error rendering graphs: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(
    func=lambda: store_analysis_results(generate_task_analysis()),
    trigger="interval",
    hours=6,
    id='task_analysis_job',
    max_instances=1,
    coalesce=True
)

def initialize_app():
    """Initialize application components"""
    try:
        # Create necessary directories
        TEMPLATES_DIR.mkdir(exist_ok=True)
        
        # Initialize CSV file
        initialize_csv()
        
        # Generate and store initial analysis
        logger.info("Generating initial analysis...")
        initial_analysis = generate_task_analysis()
        store_analysis_results(initial_analysis)
        logger.info("Initial analysis completed and stored")
        
        # Start the scheduler
        scheduler.start()
        
        logger.info("Application initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing application: {str(e)}")
        raise

if __name__ == '__main__':
    initialize_app()
    app.run(debug=True, port=8080)