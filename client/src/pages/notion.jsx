import React, { useState, useEffect } from 'react';
import { Terminal, BarChart3, Brain, AlertCircle, Download } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import AdvancedAnalytics from '@/components/analytics';
import html2pdf from 'html2pdf.js';

const API_BASE_URL = 'http://127.0.0.1:8080';

const loadingEmojis = ["🎯", "⚡", "🔄", "✨"];
const loadingPhrases = [
  {
    emoji: "🎯",
    text: "Targeting your task objectives...",
    rotation: -15
  },
  {
    emoji: "⚡",
    text: "Powering up the task engine...",
    rotation: 15
  },
  {
    emoji: "🔄",
    text: "Synchronizing with Notion...",
    rotation: -10
  },
  {
    emoji: "✨",
    text: "Sprinkling some AI magic...",
    rotation: 10
  }
];

const schedulingPhrases = [
  { text: "🎯 Analyzing task requirements...", duration: 2000 },
  { text: "⚡ Processing task details...", duration: 2000 },
  { text: "🔄 Organizing schedule...", duration: 2000 },
  { text: "✨ Finalizing task entry...", duration: 2000 }
];

const analysisPhrases = [
  { text: "🔍 Initializing data analysis...", duration: 2000 },
  { text: "📊 Crunching numbers...", duration: 2000 },
  { text: "🧮 Calculating metrics...", duration: 2000 },
  { text: "📈 Generating insights...", duration: 2000 },
  { text: "🎨 Creating visualizations...", duration: 2000 },
  { text: "🤖 Applying AI analysis...", duration: 2000 },
  { text: "📝 Compiling report...", duration: 2000 },
  { text: "✨ Finalizing results...", duration: 2000 }
];

const colors = {
  yellow: {
    primary: '#FCD34D',
    secondary: '#FBBF24',
    hover: '#F59E0B',
    muted: '#FEF3C7'
  },
  black: {
    pure: '#000000',
    primary: '#111827',
    secondary: '#1F2937'
  }
};

const NotionAIApp = () => {
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [analysisData, setAnalysisData] = useState(null);
  const [loadingText, setLoadingText] = useState('');
  const [showAnalysis, setShowAnalysis] = useState(false);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [currentPhrase, setCurrentPhrase] = useState('');

  useEffect(() => {
    // Fetch initial analysis data when component mounts
    fetchAnalysis();
  }, []);

  const cycleLoadingText = () => {
    let currentIndex = 0;
    return setInterval(() => {
      setLoadingText(loadingPhrases[currentIndex]);
      currentIndex = (currentIndex + 1) % loadingPhrases.length;
    }, 2000);
  };

  const runLoadingSequence = async (phrases) => {
    for (const phrase of phrases) {
      setCurrentPhrase(phrase.text);
      await new Promise(resolve => setTimeout(resolve, phrase.duration));
    }
  };

  const handleDownloadPDF = () => {
    const element = document.getElementById('analysis-report');
    const opt = {
      margin: 1,
      filename: 'task-analysis-report.pdf',
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: { scale: 2 },
      jsPDF: { unit: 'in', format: 'a4', orientation: 'portrait' }
    };
    html2pdf().set(opt).from(element).save();
  };

  const handleGenerateReport = async () => {
    setAnalysisLoading(true);
    try {
      await runLoadingSequence(analysisPhrases);
      await fetchAnalysis();
      setShowAnalysis(true);
    } finally {
      setAnalysisLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!prompt.trim()) {
      setError('Please enter a task description');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      await runLoadingSequence(schedulingPhrases);
      
      const response = await fetch(`${API_BASE_URL}/tasks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email_body: prompt }),
      });

      if (!response.ok) throw new Error(`Server responded with ${response.status}`);

      const data = await response.json();
      console.log('Task processed:', data);
      setPrompt('');
    } catch (err) {
      setError(`Failed to process task: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const fetchAnalysis = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/analysis`);
      if (!response.ok) {
        throw new Error(`Server responded with ${response.status}`);
      }
      const data = await response.json();
      setAnalysisData(data);
    } catch (err) {
      setError(`Failed to fetch analysis: ${err.message}`);
    }
  };

  return (
    <div className="min-h-screen bg-black p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div className="bg-black rounded-lg p-6 shadow-lg border-2 border-yellow-400">
          <h1 className="text-3xl font-bold flex items-center gap-2 text-yellow-400">
            <Terminal className="text-yellow-400" />
            Schedule Task
          </h1>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-black rounded-lg p-4 border-2 border-yellow-400 flex items-center gap-2 text-yellow-400">
            <AlertCircle size={20} />
            <p>{error}</p>
          </div>
        )}

        {/* Chat Input */}
        <div className="bg-black rounded-lg p-6 shadow-lg border-2 border-yellow-400">
          <div className="flex gap-4">
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              className="flex-1 p-4 rounded-lg min-h-[100px] bg-black text-yellow-400 border-2 border-yellow-400 placeholder-yellow-600 focus:outline-none focus:ring-2 focus:ring-yellow-400"
              placeholder="Describe your task here..."
            />
            <button
              onClick={handleSubmit}
              disabled={loading}
              className="bg-yellow-400 text-black px-6 py-2 rounded-lg hover:bg-yellow-300 transition-colors font-bold disabled:opacity-50 disabled:hover:bg-yellow-400"
            >
              Schedule Task
            </button>
          </div>
        </div>

        {/* Loading Screens */}
        {(loading || analysisLoading) && (
          <div className="fixed inset-0 bg-black bg-opacity-95 z-50 flex items-center justify-center">
            <div className="text-center space-y-8">
              <div className="text-6xl animate-bounce mb-8">
                {loading ? "📋" : "📊"}
              </div>
              <p className="text-yellow-400 text-2xl font-bold animate-pulse">
                {currentPhrase}
              </p>
            </div>
          </div>
        )}

        {/* Analysis Results */}
        {analysisData && (
          <div className="bg-black rounded-lg p-6 shadow-lg space-y-6 border border-yellow-400">
            <h2 className="text-2xl font-bold mb-4 text-yellow-400">Analysis Results</h2>
            <AdvancedAnalytics data={analysisData} />
          </div>
        )}

        {/* Advanced Analysis Button */}
        <div className="flex justify-center">
          <button
            onClick={() => window.location.href = `${API_BASE_URL}/graphs`}
            className="flex items-center gap-2 bg-yellow-400 text-black px-8 py-4 rounded-lg hover:bg-yellow-300 transition-colors font-bold text-lg"
          >
            <Brain /> View Advanced Analysis
          </button>
        </div>

        {/* Analysis Section */}
        <div className="space-y-6">
          {!showAnalysis ? (
            <button
              onClick={handleGenerateReport}
              disabled={analysisLoading}
              className="w-full bg-black rounded-lg p-6 border-2 border-yellow-400 text-yellow-400 hover:bg-yellow-400 hover:text-black transition-colors disabled:opacity-50 disabled:hover:bg-black disabled:hover:text-yellow-400"
            >
              Generate Analysis Report
            </button>
          ) : (
            <div className="bg-black rounded-lg p-6 border-2 border-yellow-400">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-yellow-400">Analysis Report</h2>
                <button
                  onClick={handleDownloadPDF}
                  className="flex items-center gap-2 bg-yellow-400 text-black px-4 py-2 rounded-lg hover:bg-yellow-300 transition-colors"
                >
                  <Download size={20} />
                  Download PDF
                </button>
              </div>
              <div id="analysis-report" className="bg-black text-yellow-400">
                <AdvancedAnalytics data={analysisData} />
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Add keyframe animations */}
      <style jsx global>{`
        @keyframes pulse {
          0% { opacity: 0.4; }
          50% { opacity: 1; }
          100% { opacity: 0.4; }
        }
        
        @keyframes spin {
          from { transform: translate(-50%, -50%) rotate(0deg); }
          to { transform: translate(-50%, -50%) rotate(360deg); }
        }

        /* Override any non-black/yellow colors */
        * {
          scrollbar-color: #FCD34D #000000;
        }

        ::-webkit-scrollbar {
          width: 12px;
        }

        ::-webkit-scrollbar-track {
          background: #000000;
        }

        ::-webkit-scrollbar-thumb {
          background-color: #FCD34D;
          border: 3px solid #000000;
          border-radius: 6px;
        }
      `}</style>
    </div>
  );
};

export default NotionAIApp;