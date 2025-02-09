import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiMail, FiClock, FiTag, FiCalendar, FiRefreshCw, FiCheck, FiX } from 'react-icons/fi';
import { BiAnalyse } from 'react-icons/bi';
import ReactMarkdown from 'react-markdown';
import rehypeRaw from 'rehype-raw';

const LiveTracker = () => {
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(true);
  const [processingEmail, setProcessingEmail] = useState(null);

  useEffect(() => {
    fetchEmails();
  }, []);

  const fetchEmails = async () => {
    setLoading(true); // Add this line to show loading state
    try {
      const response = await fetch('http://127.0.0.1:5001/get-maildb');
      const data = await response.json();
      
      if (data.status === 'success') {
        const sortedEmails = (data.data || []).sort((a, b) => 
          new Date(b.received_at) - new Date(a.received_at)
        );
        setEmails(sortedEmails);
      } else {
        console.error('Error fetching emails:', data.message);
      }
    } catch (error) {
      console.error('Error fetching emails:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAIAction = async (emailId, action) => {
    setProcessingEmail(emailId);
    try {
      const response = await fetch('http://127.0.0.1:5001/process-email', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email_id: emailId,
          action: action // 'accept' or 'reject'
        }),
      });
      const data = await response.json();
      // Handle response if needed
    } catch (error) {
      console.error('Error processing email:', error);
    } finally {
      setProcessingEmail(null);
    }
  };

  const getPriorityColor = (score) => {
    if (score > 0.7) return 'text-red-400';
    if (score > 0.4) return 'text-yellow-400';
    return 'text-green-400';
  };

  const formatDate = (dateString) => {
    try {
      return new Date(dateString).toLocaleString();
    } catch {
      return 'Invalid Date';
    }
  };

  const renderEmailCard = (email) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="group bg-gradient-to-br from-[#1a1a1a] to-[#0d0d0d] rounded-xl 
        border border-yellow-400/10 mb-6 hover:border-yellow-400/30 
        transition-all duration-300 overflow-hidden shadow-lg hover:shadow-yellow-400/5 relative" // Added relative positioning
    >
      <div className="flex flex-col lg:flex-row">
        {/* Email Content Section - Updated width */}
        <div className="lg:w-2/3 p-6 border-r border-yellow-400/20 bg-black/40">
          <div className="flex flex-col space-y-4">
            <div className="flex items-start justify-between">
              <h3 className="text-xl font-semibold text-yellow-400 group-hover:text-yellow-300 
                transition-colors">
                {email.subject || 'No Subject'}
              </h3>
              <div className="flex gap-2 flex-wrap">
                {email.labels?.map((label, index) => (
                  <motion.span
                    key={index}
                    whileHover={{ scale: 1.05 }}
                    className="text-xs px-2 py-1 rounded-full bg-yellow-400/20 text-yellow-300 
                      border border-yellow-400/30 flex items-center gap-1 font-medium"
                  >
                    <FiTag className="w-3 h-3" />
                    {label}
                  </motion.span>
                ))}
              </div>
            </div>
            
            <div className="flex items-center gap-4 text-sm text-yellow-300/90">
              <span className="flex items-center gap-2">
                <FiMail className="w-4 h-4" />
                {email.sender || 'Unknown Sender'}
              </span>
              <span className="flex items-center gap-2">
                <FiClock className="w-4 h-4" />
                {formatDate(email.received_at)}
              </span>
            </div>

            {/* Updated Email Body with Markdown */}
            <div className="prose prose-invert prose-yellow max-w-none mt-4 
              bg-black/20 rounded-lg p-4 border border-yellow-400/10">
              <ReactMarkdown
                rehypePlugins={[rehypeRaw]}
                className="text-yellow-100 leading-relaxed markdown-content"
                components={{
                  p: ({node, ...props}) => <p className="mb-2 text-yellow-100" {...props} />,
                  a: ({node, ...props}) => (
                    <a 
                      className="text-yellow-400 hover:text-yellow-300 underline" 
                      target="_blank"
                      rel="noopener noreferrer"
                      {...props}
                    />
                  ),
                  ul: ({node, ...props}) => <ul className="list-disc pl-4 mb-2" {...props} />,
                  ol: ({node, ...props}) => <ol className="list-decimal pl-4 mb-2" {...props} />,
                  li: ({node, ...props}) => <li className="mb-1 text-yellow-100" {...props} />,
                  h1: ({node, ...props}) => (
                    <h1 className="text-2xl font-bold text-yellow-400 mb-4" {...props} />
                  ),
                  h2: ({node, ...props}) => (
                    <h2 className="text-xl font-bold text-yellow-400 mb-3" {...props} />
                  ),
                  code: ({node, ...props}) => (
                    <code className="bg-black/40 px-1 rounded text-yellow-300" {...props} />
                  ),
                  pre: ({node, ...props}) => (
                    <pre className="bg-black/40 p-4 rounded-lg overflow-x-auto mb-4" {...props} />
                  ),
                }}
              >
                {email.body?.replace(/<div[^>]*>.*?<\/div>/g, '') || // Remove duplicate div content
                 email.snippet || 
                 'No content available'}
              </ReactMarkdown>
            </div>
          </div>
        </div>

        {/* Analysis Section - Updated width */}
        <div className="lg:w-1/3 p-6 pb-16 bg-black/60 backdrop-blur-sm"> {/* Added pb-16 for button space */}
          <div className="flex items-center gap-2 mb-6">
            <BiAnalyse className="w-5 h-5 text-yellow-400" />
            <h4 className="text-lg font-semibold text-yellow-400">Analysis</h4>
          </div>

          {email.analysis?.analysis ? (
            <div className="space-y-4">
              {/* Priority Score - More Prominent */}
              <div className="bg-yellow-400/5 p-4 rounded-lg backdrop-blur-sm">
                <div className="flex items-center justify-between">
                  <h5 className="text-yellow-400 font-medium">Priority Score</h5>
                  <motion.div
                    animate={{ scale: [1, 1.1, 1] }}
                    transition={{ duration: 2, repeat: Infinity }}
                    className={`px-3 py-1 rounded-full ${
                      getPriorityColor(email.analysis.analysis.final_priority_score)
                    }`}
                  >
                    {(email.analysis.analysis.final_priority_score * 10).toFixed(1)}
                  </motion.div>
                </div>
              </div>

              {/* Compact Content Analysis */}
              <div className="bg-yellow-400/5 p-4 rounded-lg space-y-3">
                <h5 className="text-yellow-400 font-medium mb-2">Quick Overview</h5>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <span className="text-yellow-400/60">Authority:</span>
                    <p className="font-medium text-white">
                      {email.analysis.analysis.authority_analysis?.authority_level || 'N/A'}
                    </p>
                  </div>
                  <div>
                    <span className="text-yellow-400/60">Tone:</span>
                    <p className="font-medium text-white">
                      {email.analysis.analysis.nlp_analysis?.tone || 'N/A'}
                    </p>
                  </div>
                </div>
              </div>

              {/* Calendar & Dates */}
              {(email.analysis.analysis.content_segments?.calendar?.length > 0 ||
                email.analysis.analysis.nlp_analysis?.important_dates?.length > 0) && (
                <div className="bg-yellow-400/5 p-4 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <FiCalendar className="w-4 h-4 text-yellow-400" />
                    <h5 className="text-yellow-400 font-medium">Time Sensitive</h5>
                  </div>
                  <div className="space-y-2 text-sm text-yellow-400/80">
                    {/* ...existing calendar content... */}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <p className="text-yellow-400/60 text-sm">No analysis available</p>
          )}

          {/* Action Buttons - Moved inside analysis section */}
          <div className="absolute bottom-4 right-4 flex items-center gap-2">
            <div className="text-sm text-yellow-400/60 mr-2 bg-black/40 px-2 py-1 rounded-lg backdrop-blur-sm">
              Let AI agent take action:
            </div>
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => handleAIAction(email.message_id, 'accept')}
              disabled={processingEmail === email.message_id}
              className="p-2 bg-green-400/10 hover:bg-green-400/20 
                text-green-400 rounded-lg transition-all duration-200 
                border border-green-400/20 hover:border-green-400/40
                disabled:opacity-50 disabled:cursor-not-allowed
                backdrop-blur-sm"
            >
              {processingEmail === email.message_id ? (
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  className="w-5 h-5 border-2 border-green-400 border-t-transparent rounded-full"
                />
              ) : (
                <FiCheck className="w-5 h-5" />
              )}
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => handleAIAction(email.message_id, 'reject')}
              disabled={processingEmail === email.message_id}
              className="p-2 bg-red-400/10 hover:bg-red-400/20 
                text-red-400 rounded-lg transition-all duration-200 
                border border-red-400/20 hover:border-red-400/40
                disabled:opacity-50 disabled:cursor-not-allowed
                backdrop-blur-sm"
            >
              {processingEmail === email.message_id ? (
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  className="w-5 h-5 border-2 border-red-400 border-t-transparent rounded-full"
                />
              ) : (
                <FiX className="w-5 h-5" />
              )}
            </motion.button>
          </div>
        </div>
      </div>
    </motion.div>
  );

  return (
    <div className="min-h-screen">
      <div className="p-8 max-w-7xl mx-auto">
        {/* Header Section - Updated with better contrast */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-black/40 backdrop-blur-sm rounded-xl border border-yellow-400/20 p-6 mb-8"
        >
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between 
            space-y-4 md:space-y-0">
            <div>
              <h1 className="text-4xl font-bold text-yellow-300 mb-2">Email Analytics</h1>
              <p className="text-yellow-200/90">
                Analyzing {emails.length} emails with AI-powered insights
              </p>
            </div>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => fetchEmails()} // Ensure we're calling the function
              disabled={loading} // Disable button while loading
              className={`px-4 py-2 bg-yellow-400/20 hover:bg-yellow-400/30 
                text-yellow-300 rounded-lg transition-colors flex items-center gap-2
                border border-yellow-400/30 shadow-lg hover:shadow-yellow-400/20
                ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              <FiRefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              {loading ? 'Refreshing...' : 'Refresh'}
            </motion.button>
          </div>
        </motion.div>

        {/* Email List */}
        {loading ? (
          <div className="flex justify-center py-12">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
              className="w-8 h-8 border-2 border-yellow-400 border-t-transparent rounded-full"
            />
          </div>
        ) : (
          <AnimatePresence>
            <div className="space-y-6">
              {emails.length > 0 ? (
                emails.map((email, index) => (
                  <motion.div
                    key={email.message_id || index}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }} // Reduced delay for smoother animation
                  >
                    {renderEmailCard(email)}
                  </motion.div>
                ))
              ) : (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="text-center py-12 bg-yellow-400/5 rounded-lg border 
                    border-yellow-400/10"
                >
                  <p className="text-yellow-400/60">No emails found</p>
                </motion.div>
              )}
            </div>
          </AnimatePresence>
        )}
      </div>
    </div>
  );
};

// Add these styles to your global CSS or component
const styles = `
  .markdown-content {
    color: rgb(253 224 71 / 0.9);
  }
  .markdown-content strong {
    color: rgb(253 224 71);
    font-weight: 600;
  }
  .markdown-content blockquote {
    border-left: 3px solid rgb(253 224 71 / 0.4);
    padding-left: 1rem;
    margin-left: 0;
    color: rgb(253 224 71 / 0.7);
  }
  .markdown-content img {
    max-width: 100%;
    border-radius: 0.5rem;
    margin: 1rem 0;
  }
`;

export default LiveTracker;
