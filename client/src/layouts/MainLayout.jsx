import { useState } from 'react';
import { Link, useLocation, Outlet } from 'react-router-dom';
import { 
  FaUsers, 
  FaChartBar, 
  FaMagic, 
  FaBars, 
  FaTimes,
} from 'react-icons/fa';
import { MessageSquare } from 'lucide-react';

const MainLayout = () => {
  const [isSidebarOpen, setSidebarOpen] = useState(true);
  const location = useLocation();

  const navItems = [
    { 
      path: '/dashboard', 
      icon: FaChartBar, 
      label: 'Dashboard',
      emoji: '📊',
      description: 'Overview and analytics'
    },
    { 
      path: '/agents', 
      icon: FaUsers, 
      label: 'Specialized Agents',
      emoji: '🤖',
      description: 'Access specialized AI agents'
    },
    { 
      path: '/market-trends', 
      icon: FaChartBar, 
      label: 'Market Trends',
      emoji: '📊',
      description: 'Real-time market analysis'
    },
    { 
      path: '/ad-generator', 
      icon: FaMagic, 
      label: 'Ad Generator',
      emoji: '✨',
      description: 'Create engaging ad campaigns'
    },
    { 
      path: '/post-generate', 
      icon: MessageSquare, 
      label: 'Post Generator',
      emoji: '📝',
      description: 'Generate social media posts'
    },
    { 
      path: '/ab-testing', 
      icon: FaChartBar, 
      label: 'A/B Testing',
      emoji: '🔬',
      description: 'Test campaign performance'
    },
    // { 
    //   path: '/chat', 
    //   icon: MessageSquare, 
    //   label: 'AI Assistant',
    //   emoji: '💬',
    //   description: 'Chat with AI Assistant'
    // },
    { 
      path: '/ai-strategist', 
      icon: FaMagic, 
      label: 'AI Strategist',
      emoji: '🧠',
      description: 'Strategic campaign planning'
    },
    { 
      path: '/specialized-agents', 
      icon: FaUsers, 
      label: 'Agent Hub',
      emoji: '🌟',
      description: 'Specialized agent interface'
    }
  ];

  return (
    <div className="flex h-screen bg-zinc-900">
      {/* Reduced height by adding pb-14 to account for footer and adjusted spacing */}
      <div className={`fixed inset-y-0 left-0 z-50 w-64 bg-gradient-to-br from-zinc-800 via-zinc-900 to-black shadow-xl transform transition-all duration-300 ease-in-out overflow-hidden flex flex-col ${
        isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
      }`}>
        <div className="flex items-center justify-between h-14 px-4 border-b border-zinc-700/50 backdrop-blur-md bg-zinc-800/30">
          <h1 className="text-xl font-bold text-transparent bg-gradient-to-r from-yellow-300 to-yellow-500 bg-clip-text">
            Prachaar
          </h1>
          <button
            onClick={() => setSidebarOpen(false)}
            className="p-1.5 rounded-full hover:bg-white/50 transition-all lg:hidden"
          >
            <FaTimes className="w-5 h-5" />
          </button>
        </div>

        {/* Added max-height and overflow-auto to nav */}
        <nav className="flex-1 mt-2 px-2 overflow-auto">
          <div className="space-y-0.5 pb-14"> {/* Reduced gap between items and added bottom padding */}
            {navItems.map(({ path, icon: Icon, label, emoji, description }) => (
              <Link
                key={path}
                to={path}
                className={`group flex flex-col px-3 py-1.5 rounded-lg transition-all duration-200 ${
                  location.pathname === path
                    ? 'bg-gradient-to-r from-yellow-500 to-yellow-600 text-zinc-900 shadow-lg shadow-yellow-500/20 scale-[1.02]'
                    : 'text-zinc-400 hover:bg-zinc-800/50 hover:shadow-md hover:scale-[1.02]'
                }`}
              >
                <div className="flex items-center">
                  <span className="text-lg mr-2">{emoji}</span>
                  <span className="font-medium text-sm">{label}</span>
                </div>
                <span className={`text-[11px] mt-0.5 ml-8 ${
                  location.pathname === path ? 'text-blue-100' : 'text-gray-500'
                }`}>
                  {description}
                </span>
              </Link>
            ))}
          </div>
        </nav>

        {/* Fixed footer positioning */}
        <div className="flex-shrink-0 p-2 border-t border-zinc-700/50">
          <div className="flex items-center justify-center space-x-1 text-xs text-zinc-400">
            <span>Made with</span>
            <span className="text-red-500">❤️</span>
            <span>by Team Init.io</span>
          </div>
        </div>
      </div>

      {/* Adjusted margin to match new sidebar width */}
      <div className="flex-1 ml-0 lg:ml-64">
        <header className="h-16 bg-zinc-800/50 backdrop-blur-md border-b border-zinc-700/50 shadow-sm flex items-center px-6 sticky top-0 z-40">
          <button
            onClick={() => setSidebarOpen(true)}
            className="p-2 rounded-full hover:bg-zinc-700/50 transition-all lg:hidden"
          >
            <FaBars className="w-6 h-6 text-zinc-400" />
          </button>
          <div className="ml-4 text-zinc-300 font-medium">
            {navItems.find(item => item.path === location.pathname)?.label || 'Dashboard'}
          </div>
        </header>
        <main className="p-6 bg-zinc-900">
          <Outlet />
        </main>
      </div>

      {isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 backdrop-blur-sm lg:hidden z-40"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  );
};

export default MainLayout;
