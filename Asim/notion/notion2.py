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

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize components (previous initializations remain the same)
llm = ChatOpenAI()
prompt = hub.pull("hwchase17/openai-functions-agent")
gemini = ChatGoogleGenerativeAI(
    model="gemini-pro",
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# Previous schema and prompt definitions remain the same
response_schemas = [
    # ... (previous schema definitions)
]

output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
extraction_prompt = PromptTemplate(
    # ... (previous prompt template)
)

# CSV file path
CSV_FILE_PATH = 'notion_mock_tasks.csv'

def save_to_csv(task_data):
    """Save task data to CSV file"""
    df = pd.DataFrame([task_data])
    if not os.path.exists(CSV_FILE_PATH):
        df.to_csv(CSV_FILE_PATH, index=False)
    else:
        df.to_csv(CSV_FILE_PATH, mode='a', header=False, index=False)

def generate_task_analysis():
    """Generate comprehensive task analysis and visualizations"""
    df = pd.read_csv(CSV_FILE_PATH)
    
    # Convert deadline to datetime
    df['Deadline'] = pd.to_datetime(df['Deadline'], format='%d - %m - %Y')
    
    # Basic statistics
    total_tasks = len(df)
    tasks_by_status = df['Status'].value_counts()
    tasks_by_priority = df['Priority'].value_counts()
    tasks_by_category = df['Category'].value_counts()
    
    # Deadline analysis
    today = datetime.now()
    df['Days_to_Deadline'] = (df['Deadline'] - pd.Timestamp(today)).dt.days
    urgent_tasks = df[df['Days_to_Deadline'] <= 3]
    overdue_tasks = df[df['Days_to_Deadline'] < 0]
    
    # Create visualizations
    
    # 1. Status Distribution Pie Chart
    fig1 = px.pie(df, names='Status', title='Task Status Distribution',
                  color_discrete_sequence=px.colors.qualitative.Set3)
    
    # 2. Priority vs Category Heatmap
    priority_category = pd.crosstab(df['Priority'], df['Category'])
    fig2 = go.Figure(data=go.Heatmap(
        z=priority_category.values,
        x=priority_category.columns,
        y=priority_category.index,
        colorscale='Viridis'))
    fig2.update_layout(title='Priority vs Category Distribution')
    
    # 3. Timeline of Tasks
    fig3 = px.timeline(df, x_start='Deadline', y='Category',
                      color='Priority', title='Task Timeline')
    
    # 4. Days to Deadline Distribution
    fig4 = px.histogram(df, x='Days_to_Deadline',
                       title='Days to Deadline Distribution',
                       nbins=20)
    
    # Generate AI insights using Gemini
    analysis_prompt = f"""
    Analyze the following task data and provide strategic insights:
    
    Total Tasks: {total_tasks}
    Urgent Tasks (<=3 days): {len(urgent_tasks)}
    Overdue Tasks: {len(overdue_tasks)}
    
    Status Distribution:
    {tasks_by_status.to_string()}
    
    Priority Distribution:
    {tasks_by_priority.to_string()}
    
    Category Distribution:
    {tasks_by_category.to_string()}
    
    Provide:
    1. Key insights about task distribution and management
    2. Recommendations for better task management
    3. Risk assessment and mitigation strategies
    4. Productivity optimization suggestions
    """
    
    ai_insights = gemini.invoke(analysis_prompt).content
    
    # Save visualizations to HTML
    graphs_html = f"""
    <html>
    <head>
        <title>Task Analysis Dashboard</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    </head>
    <body class="bg-gray-100 p-8">
        <div class="max-w-7xl mx-auto">
            <h1 class="text-3xl font-bold mb-8">Task Analysis Dashboard</h1>
            
            <div class="grid grid-cols-2 gap-8 mb-8">
                <div class="bg-white p-6 rounded-lg shadow-lg">
                    {fig1.to_html(full_html=False)}
                </div>
                <div class="bg-white p-6 rounded-lg shadow-lg">
                    {fig2.to_html(full_html=False)}
                </div>
            </div>
            
            <div class="grid grid-cols-2 gap-8 mb-8">
                <div class="bg-white p-6 rounded-lg shadow-lg">
                    {fig3.to_html(full_html=False)}
                </div>
                <div class="bg-white p-6 rounded-lg shadow-lg">
                    {fig4.to_html(full_html=False)}
                </div>
            </div>
            
            <div class="bg-white p-6 rounded-lg shadow-lg mb-8">
                <h2 class="text-2xl font-bold mb-4">AI Insights</h2>
                <div class="prose">
                    {ai_insights}
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    with open('templates/dashboard.html', 'w') as f:
        f.write(graphs_html)
    
    return {
        'basic_stats': {
            'total_tasks': total_tasks,
            'urgent_tasks': len(urgent_tasks),
            'overdue_tasks': len(overdue_tasks)
        },
        'ai_insights': ai_insights
    }

# Modified POST route
@app.route('/tasks', methods=['POST'])
def create_task():
    try:
        data = request.json
        
        if 'email_body' not in data:
            return jsonify({'error': 'Missing email_body in request'}), 400
        
        # Extract task information
        extracted_info = extract_task_info(data['email_body'])
        
        # Save to CSV
        save_to_csv(extracted_info)
        
        # Create task in Notion (previous Notion logic remains the same)
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
        
        return jsonify({
            'message': 'Task created successfully',
            'extracted_info': extracted_info,
            'result': result
        }), 201
    
    except Exception as e:
        return jsonify({
            'error': f'Failed to create task: {str(e)}'
        }), 500

# New route for dashboard
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=generate_task_analysis, 
                 trigger="interval", 
                 hours=6,
                 id='task_analysis_job')
scheduler.start()

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Generate initial analysis
    generate_task_analysis()
    
    app.run(debug=True, port=8080)