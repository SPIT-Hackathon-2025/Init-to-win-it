import { motion, useScroll, useSpring } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import {
  FiTrendingUp,
  FiMessageCircle,
  FiCheckSquare,
  FiCalendar,
  FiGitMerge,
  FiTwitter,
  FiBarChart2
} from 'react-icons/fi'
import { RiRobot2Line } from 'react-icons/ri'

const DiagonalSection = ({ children, reverse }) => (
  <div className={`relative py-20 ${reverse ? 'bg-[#111]' : 'bg-yellow-400'}`}>
    <div className="absolute inset-0 overflow-hidden">
      {[...Array(20)].map((_, i) => (
        <motion.div
          key={i}
          className={`absolute h-[2px] ${reverse ? 'bg-yellow-400/20' : 'bg-black/10'}`}
          style={{
            width: Math.random() * 300 + 100,
            top: `${(i * 5) + Math.random() * 5}%`,
            left: `${Math.random() * 100}%`,
          }}
          animate={{
            x: [0, 100, 0],
            opacity: [0.5, 1, 0.5],
          }}
          transition={{
            duration: Math.random() * 5 + 5,
            repeat: Infinity,
            ease: "linear",
          }}
        />
      ))}
    </div>
    <div className="relative container mx-auto px-6">{children}</div>
  </div>
)

const FeatureStrip = ({ feature, index }) => (
  <motion.div
    initial={{ x: index % 2 === 0 ? -100 : 100, opacity: 0 }}
    whileInView={{ x: 0, opacity: 1 }}
    transition={{ duration: 0.8, ease: "easeOut" }}
    className={`flex items-center gap-8 ${index % 2 === 0 ? 'flex-row' : 'flex-row-reverse'} 
      py-12 border-b border-yellow-400/20`}
  >
    <div className="w-24 h-24 flex-shrink-0 rounded-full bg-yellow-400 flex items-center justify-center">
      <feature.icon className="w-12 h-12 text-black" />
    </div>
    <div>
      <h3 className="text-2xl font-bold mb-2 text-white">{feature.title}</h3>
      <p className="text-gray-300">{feature.description}</p>
    </div>
  </motion.div>
)

const StaggeredGrid = ({ items }) => (
  <div className="grid md:grid-cols-2 gap-8">
    {items.map((item, i) => (
      <motion.div
        key={i}
        initial={{ y: 50, opacity: 0 }}
        whileInView={{ y: 0, opacity: 1 }}
        transition={{ delay: i * 0.1 }}
        className="bg-black/50 backdrop-blur-lg rounded-lg p-8 border border-yellow-400/20
          hover:border-yellow-400 transition-colors"
      >
        <item.icon className="w-12 h-12 text-yellow-400 mb-4" />
        <h3 className="text-xl font-bold mb-3 text-white">{item.title}</h3>
        <p className="text-gray-300">{item.description}</p>
      </motion.div>
    ))}
  </div>
)

export default function LandingPage() {
  const navigate = useNavigate()
  const { scrollYProgress } = useScroll()
  const scaleX = useSpring(scrollYProgress, {
    stiffness: 100,
    damping: 30,
    restDelta: 0.001
  })

  const handleStartTrial = () => {
    navigate('/login')
  }

  const mainFeatures = [
    {
      icon: FiTrendingUp,
      title: "Smart Content Creation",
      description: "AI-powered content generation tailored to your brand voice and audience.",
      color: "border-purple-100"
    },
    {
      icon: RiRobot2Line,
      title: "AI Support Assistant",
      description: "Intelligent bot that learns from your business context to assist customers.",
      color: "border-blue-100"
    },
    {
      icon: FiCheckSquare,
      title: "Smart Ticketing",
      description: "Automated ticket management with smart prioritization.",
      color: "border-pink-100"
    },
    {
      icon: FiTwitter,
      title: "Social Automation",
      description: "Schedule and manage social media posts with ease.",
      color: "border-indigo-100"
    }
  ]

  const workflowFeatures = [
    {
      icon: FiGitMerge,
      title: "Campaign Dashboard",
      description: "Centralized dashboard to manage all Marketing campaigns, toggle campaign status, and monitor performance metrics.",
      color: "border-green-100"
    },
    {
      icon: FiBarChart2,
      title: "Performance Analytics",
      description: "Comprehensive analytics showing bot performance, customer sentiment, and campaign effectiveness.",
      color: "border-orange-100"
    },
    {
      icon: FiCalendar,
      title: "Content Calendar",
      description: "Visual calendar interface for scheduling posts, managing content pipeline, and coordinating campaigns.",
      color: "border-teal-100"
    },
    {
      icon: FiMessageCircle,
      title: "Interaction Monitor",
      description: "Track and analyze all customer interactions with sentiment analysis and automated response suggestions.",
      color: "border-cyan-100"
    }
  ]

  return (
    <div className="min-h-screen bg-[#111]">
      <motion.div
        className="fixed top-0 left-0 right-0 h-1 bg-yellow-400 z-50"
        style={{ scaleX }}
      />

      <section className="min-h-screen relative flex items-center overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] 
          from-yellow-400/20 via-transparent to-transparent" />
        <div className="container mx-auto px-6 relative">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-4xl mx-auto text-center"
          >
            <motion.span
              className="inline-block px-6 py-2 bg-yellow-400 rounded-full text-black text-sm 
                font-medium mb-6"
              whileHover={{ scale: 1.05 }}
            >
              The Future of Marketing is Here
            </motion.span>
            <h1 className="text-5xl md:text-7xl font-bold mb-6 text-white">
              Upgrade Your Marketing Agency with{' '}
              <span className="text-yellow-400">AI</span>
            </h1>
            <p className="text-xl text-gray-300 mb-8">
              Enhance your entire Marketing workflow with AI-powered solutions
            </p>
          </motion.div>
        </div>
      </section>

      <DiagonalSection reverse>
        <div className="space-y-4">
          {mainFeatures.map((feature, index) => (
            <FeatureStrip key={index} feature={feature} index={index} />
          ))}
        </div>
      </DiagonalSection>

      <DiagonalSection>
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl font-bold mb-4 text-black">Workflow Management</h2>
          <p className="text-xl text-black/70">Everything you need to manage your Marketing automation</p>
        </motion.div>
        <StaggeredGrid items={workflowFeatures} />
      </DiagonalSection>

      <section className="py-20 relative overflow-hidden">
        <div className="container mx-auto px-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            className="max-w-3xl mx-auto text-center"
          >
            <h2 className="text-4xl font-bold mb-6 text-white">
              Ready to Transform Your Marketing?
            </h2>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="px-8 py-4 bg-yellow-400 text-black font-bold rounded-lg 
                hover:bg-yellow-300 transition-colors"
              onClick={handleStartTrial}
            >
              Get Started Now
            </motion.button>
          </motion.div>
        </div>
      </section>
    </div>
  )
}