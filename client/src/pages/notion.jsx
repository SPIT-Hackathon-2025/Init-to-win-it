import React, { useState } from 'react';
import { Terminal, BarChart3, Brain, ArrowRight } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const NotionAIDashboard = () => {
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [analysisData, setAnalysisData] = useState(null);
  const [loadingText, setLoadingText] = useState('');

  const loadingPhrases = [
    "🤖 Parsing natural language...",
    "🧠 Analyzing workflow patterns...",
    "📊 Crunching the numbers...",
    "🔄 Optimizing task sequences...",
    "🎯 Identifying priorities...",
    "🌟 Generating insights...",
    "🔍 Deep diving into metrics...",
    "📈 Calculating efficiency scores...",
    "🎨 Creating visualizations...",
    "🚀 Preparing recommendations..."
  ];

  const cycleLoadingText = () => {
    let currentIndex = 0;
    return setInterval(() => {
      setLoadingText(loadingPhrases[currentIndex]);
      currentIndex = (currentIndex + 1) % loadingPhrases.length;
    }, 2000);
  };

  const handleSubmit = async () => {
    setLoading(true);
    const intervalId = cycleLoadingText();

    try {
      const response = await fetch('/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email_body: prompt })
      });
      
      if (!response.ok) throw new Error('Failed to process task');
      
      const data = await response.json();
      setAnalysisData(data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      clearInterval(intervalId);
      setLoading(false);
    }
  };

  const fetchAnalysis = async () => {
    try {
      const response = await fetch('/api/analysis');
      const data = await response.json();
      setAnalysisData(data);
    } catch (error) {
      console.error('Error fetching analysis:', error);
    }
  };

  const redirectToGraphs = () => {
    window.location.href = 'http://127.0.0.1:8080/graphs';
  };

  return (
    <div className="min-h-screen bg-black p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div className="bg-gray-900 rounded-lg p-6 shadow-lg border border-yellow-400">
          <h1 className="text-3xl font-bold flex items-center gap-2 text-yellow-400">
            <Terminal className="text-yellow-400" />
            Notion AI Task Assistant
          </h1>
        </div>

        {/* Chat Input */}
        <div className="bg-gray-900 rounded-lg p-6 shadow-lg border border-yellow-400">
          <div className="flex gap-4">
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              className="flex-1 p-4 rounded-lg min-h-[100px] bg-gray-800 text-yellow-400 border border-yellow-400 placeholder-yellow-600"
              placeholder="Describe your task here..."
            />
            <button
              onClick={handleSubmit}
              disabled={loading}
              className="bg-yellow-400 text-black px-6 py-2 rounded-lg hover:bg-yellow-300 transition-colors font-bold"
            >
              Process Task
            </button>
          </div>
        </div>

        {/* Loading Animation */}
        {loading && (
          <div className="bg-gray-900 rounded-lg p-8 shadow-lg text-center border border-yellow-400">
            <div className="animate-spin w-16 h-16 border-4 border-yellow-400 border-t-transparent rounded-full mx-auto mb-4" />
            <p className="text-xl font-semibold text-yellow-400 animate-pulse">
              {loadingText}
            </p>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-4">
          <button
            onClick={fetchAnalysis}
            className="flex items-center gap-2 bg-yellow-400 text-black px-6 py-3 rounded-lg hover:bg-yellow-300 transition-colors font-bold"
          >
            <BarChart3 /> View Analysis
          </button>
          <button
            onClick={redirectToGraphs}
            className="flex items-center gap-2 bg-yellow-400 text-black px-6 py-3 rounded-lg hover:bg-yellow-300 transition-colors font-bold"
          >
            <Brain /> Advanced AI Analysis
          </button>
        </div>

        {/* Analysis Results */}
        {analysisData && (
          <div className="bg-gray-900 rounded-lg p-6 shadow-lg space-y-6 border border-yellow-400">
            <h2 className="text-2xl font-bold mb-4 text-yellow-400">Analysis Results</h2>
            
            {/* Task Distribution Chart */}
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart
                  data={[
                    { name: 'High', value: analysisData.tasks_by_priority?.High || 0 },
                    { name: 'Medium', value: analysisData.tasks_by_priority?.Medium || 0 },
                    { name: 'Low', value: analysisData.tasks_by_priority?.Low || 0 }
                  ]}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#4B5563" />
                  <XAxis dataKey="name" stroke="#FCD34D" />
                  <YAxis stroke="#FCD34D" />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#111827', 
                      border: '1px solid #FCD34D',
                      color: '#FCD34D'
                    }}
                  />
                  <Line type="monotone" dataKey="value" stroke="#FCD34D" />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Statistics Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gray-800 p-4 rounded-lg border border-yellow-400">
                <h3 className="font-semibold text-yellow-400">Total Tasks</h3>
                <p className="text-2xl text-yellow-400">{analysisData.total_tasks}</p>
              </div>
              <div className="bg-gray-800 p-4 rounded-lg border border-yellow-400">
                <h3 className="font-semibold text-yellow-400">Urgent Tasks</h3>
                <p className="text-2xl text-yellow-400">{analysisData.urgent_tasks}</p>
              </div>
              <div className="bg-gray-800 p-4 rounded-lg border border-yellow-400">
                <h3 className="font-semibold text-yellow-400">Overdue Tasks</h3>
                <p className="text-2xl text-yellow-400">{analysisData.overdue_tasks}</p>
              </div>
            </div>

            {/* AI Insights */}
            <div className="prose max-w-none">
              <h3 className="text-xl font-bold mb-4 text-yellow-400">AI Insights</h3>
              <div 
                className="text-yellow-400"
                dangerouslySetInnerHTML={{ __html: analysisData.ai_insights }} 
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default NotionAIDashboard;