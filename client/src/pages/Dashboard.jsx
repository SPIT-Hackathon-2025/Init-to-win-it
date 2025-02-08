import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FiCalendar, FiSend } from 'react-icons/fi';
import { SiNotion } from 'react-icons/si';

const Dashboard = () => {
  const [greeting, setGreeting] = useState('');
  const [inputMessage, setInputMessage] = useState('');

  useEffect(() => {
    const hour = new Date().getHours();
    if (hour < 12) setGreeting('Good Morning');
    else if (hour < 18) setGreeting('Good Afternoon');
    else setGreeting('Good Evening');
  }, []);

  const mockSchedule = [
    { time: '09:00 AM', title: 'Team Standup', duration: '30min' },
    { time: '10:30 AM', title: 'Client Meeting', duration: '1h' },
    { time: '02:00 PM', title: 'Product Review', duration: '45min' },
    { time: '04:00 PM', title: 'Marketing Sync', duration: '1h' }
  ];

  const mockTasks = [
    { title: 'Review Q4 Marketing Strategy', status: 'In Progress', priority: 'High' },
    { title: 'Prepare Client Presentation', status: 'Todo', priority: 'Medium' },
    { title: 'Update Content Calendar', status: 'In Progress', priority: 'High' },
    { title: 'Social Media Analytics Report', status: 'Todo', priority: 'Low' }
  ];

  return (
    <div className="min-h-screen  p-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-7xl mx-auto"
      >
        {/* Greeting Section */}
        <h1 className="text-4xl font-bold text-yellow-400 mb-8">{greeting}</h1>

        {/* Chat Interface */}
        <div className="mb-12">
          <div className="relative">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="How can I assist you today?"
              className="w-full p-4 pr-12 rounded-lg bg-[##18181B] border border-yellow-400/20 
                text-yellow-100 placeholder-yellow-600/30 focus:outline-none focus:border-yellow-400 
                transition-colors backdrop-blur-lg"
            />
            <button
              className="absolute right-4 top-1/2 transform -translate-y-1/2 text-yellow-400 
                hover:text-yellow-300 transition-colors"
            >
              <FiSend size={20} />
            </button>
          </div>
        </div>

        {/* Two Column Layout */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Schedule Column */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-black/50 backdrop-blur-lg rounded-lg p-6 border border-yellow-400/20"
          >
            <div className="flex items-center gap-3 mb-6">
              <FiCalendar className="text-yellow-400 w-6 h-6" />
              <h2 className="text-2xl font-semibold text-yellow-400">Your Schedule</h2>
            </div>
            <div className="space-y-4">
              {mockSchedule.map((event, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 rounded-lg 
                    bg-yellow-400/5 border border-yellow-400/10 hover:border-yellow-400/30 
                    transition-colors"
                >
                  <div>
                    <p className="text-yellow-100 font-medium">{event.title}</p>
                    <p className="text-yellow-400/60 text-sm">{event.time}</p>
                  </div>
                  <span className="text-yellow-400/80 text-sm">{event.duration}</span>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Tasks Column */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-black/50 backdrop-blur-lg rounded-lg p-6 border border-yellow-400/20"
          >
            <div className="flex items-center gap-3 mb-6">
              <SiNotion className="text-yellow-400 w-6 h-6" />
              <h2 className="text-2xl font-semibold text-yellow-400">Your Tasks</h2>
            </div>
            <div className="space-y-4">
              {mockTasks.map((task, index) => (
                <div
                  key={index}
                  className="p-3 rounded-lg bg-yellow-400/5 border border-yellow-400/10 
                    hover:border-yellow-400/30 transition-colors"
                >
                  <div className="flex justify-between items-start mb-2">
                    <p className="text-yellow-100 font-medium">{task.title}</p>
                    <span
                      className={`text-xs px-2 py-1 rounded ${
                        task.priority === 'High'
                          ? 'bg-red-400/20 text-red-400'
                          : task.priority === 'Medium'
                          ? 'bg-yellow-400/20 text-yellow-400'
                          : 'bg-green-400/20 text-green-400'
                      }`}
                    >
                      {task.priority}
                    </span>
                  </div>
                  <p className="text-yellow-400/60 text-sm">{task.status}</p>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </motion.div>
    </div>
  );
};

export default Dashboard;