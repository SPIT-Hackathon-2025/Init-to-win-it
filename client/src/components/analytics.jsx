import React, { useState } from 'react';
import { LineChart, BarChart, PieChart, RadarChart, Pie, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ComposedChart, Bar, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, Legend } from 'recharts';
import { Terminal, Brain, ChevronRight } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import ReactMarkdown from 'react-markdown';

const EnhancedAnalytics = ({ data }) => {
  const [showInsights, setShowInsights] = useState(false);

  // Update color scheme to only use yellow and black
  const colors = {
    yellow: {
      primary: '#FCD34D',
      secondary: '#FBBF24',
      tertiary: '#F59E0B',
      light: '#FEF3C7'
    },
    black: {
      pure: '#000000',
      primary: '#111827',
      secondary: '#1F2937'
    }
  };

  // Update chart colors
  const chartColors = [
    colors.yellow.primary,
    colors.yellow.secondary,
    colors.yellow.tertiary,
    colors.yellow.light
  ];

  if (!data) {
    return (
      <div className="flex items-center justify-center h-64 bg-black rounded-lg border-2 border-yellow-400 text-yellow-400">
        <div className="animate-spin mr-2">
          <Terminal size={24} />
        </div>
        Loading analytics data...
      </div>
    );
  }

  // Priority distribution data
  const priorityData = Object.entries(data.tasks_by_priority).map(([priority, count]) => ({
    name: priority,
    value: count,
    percentage: ((count / data.total_tasks) * 100).toFixed(1)
  }));

  // Category data
  const categoryData = Object.entries(data.tasks_by_category).map(([category, count]) => ({
    category,
    tasks: count,
    percentage: ((count / data.total_tasks) * 100).toFixed(1)
  })).sort((a, b) => b.tasks - a.tasks);

  // Status progress data
  const statusData = Object.entries(data.tasks_by_status).map(([status, count]) => ({
    name: status,
    value: count,
    percentage: ((count / data.total_tasks) * 100).toFixed(1)
  }));

  // Radar chart data for task distribution
  const radarData = categoryData.map(item => ({
    category: item.category,
    tasks: item.tasks,
    percentage: parseFloat(item.percentage)
  }));

  return (
    <div className="space-y-8 bg-black text-yellow-400 p-6">
      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-black border-2 border-yellow-400">
          <CardHeader className="p-4">
            <CardTitle className="text-sm font-medium text-yellow-400">Total Tasks</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-400">{data.total_tasks}</div>
          </CardContent>
        </Card>
        <Card className="bg-black border-2 border-yellow-400">
          <CardHeader className="p-4">
            <CardTitle className="text-sm font-medium text-yellow-400">Completion Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-400">
              {((data.tasks_by_status?.Completed || 0) / data.total_tasks * 100).toFixed(1)}%
            </div>
          </CardContent>
        </Card>
        <Card className="bg-black border-2 border-yellow-400">
          <CardHeader className="p-4">
            <CardTitle className="text-sm font-medium text-yellow-400">High Priority Tasks</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-400">{data.tasks_by_priority.High}</div>
          </CardContent>
        </Card>
        <Card className="bg-black border-2 border-yellow-400">
          <CardHeader className="p-4">
            <CardTitle className="text-sm font-medium text-yellow-400">Urgent Tasks</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-400">{data.urgent_tasks}</div>
          </CardContent>
        </Card>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Priority Distribution Pie Chart */}
        <Card className="bg-black border-2 border-yellow-400">
          <CardHeader className="p-4">
            <CardTitle className="text-xl font-bold text-yellow-400">Priority Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer>
                <PieChart>
                  <Pie
                    data={priorityData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    label={({ name, percentage }) => `${name}: ${percentage}%`}
                  >
                    {priorityData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={chartColors[index % chartColors.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: colors.black.pure,
                      border: `1px solid ${colors.yellow.primary}`,
                      color: colors.yellow.primary
                    }}
                  />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Category Distribution Bar Chart */}
        <Card className="bg-black border-2 border-yellow-400">
          <CardHeader className="p-4">
            <CardTitle className="text-xl font-bold text-yellow-400">Category Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer>
                <BarChart data={categoryData}>
                  <CartesianGrid strokeDasharray="3 3" stroke={colors.yellow.primary} opacity={0.2} />
                  <XAxis dataKey="category" stroke={colors.yellow.primary} />
                  <YAxis stroke={colors.yellow.primary} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: colors.black.pure,
                      border: `1px solid ${colors.yellow.primary}`,
                      color: colors.yellow.primary
                    }}
                  />
                  <Bar dataKey="tasks" fill={colors.yellow.primary}>
                    {categoryData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={chartColors[index % chartColors.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Status Distribution Radar Chart */}
        <Card className="bg-black border-2 border-yellow-400">
          <CardHeader className="p-4">
            <CardTitle className="text-xl font-bold text-yellow-400">Task Distribution Radar</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer>
                <RadarChart data={radarData}>
                  <PolarGrid stroke={colors.yellow.primary} />
                  <PolarAngleAxis dataKey="category" stroke={colors.yellow.primary} />
                  <PolarRadiusAxis stroke={colors.yellow.primary} />
                  <Radar
                    name="Tasks"
                    dataKey="tasks"
                    stroke={colors.yellow.secondary}
                    fill={colors.yellow.primary}
                    fillOpacity={0.6}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: colors.black.pure,
                      border: `1px solid ${colors.yellow.primary}`,
                      color: colors.yellow.primary
                    }}
                  />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Status Progress Line Chart */}
        <Card className="bg-black border-2 border-yellow-400">
          <CardHeader className="p-4">
            <CardTitle className="text-xl font-bold text-yellow-400">Task Status Progress</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer>
                <LineChart data={statusData}>
                  <CartesianGrid strokeDasharray="3 3" stroke={colors.yellow.primary} opacity={0.2} />
                  <XAxis dataKey="name" stroke={colors.yellow.primary} />
                  <YAxis stroke={colors.yellow.primary} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: colors.black.pure,
                      border: `1px solid ${colors.yellow.primary}`,
                      color: colors.yellow.primary
                    }}
                  />
                  <Line
                    type="monotone"
                    dataKey="value"
                    stroke={colors.yellow.primary}
                    strokeWidth={2}
                    dot={{ fill: colors.yellow.secondary }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* AI Insights Button */}
      <div className="flex justify-center">
        <button
          onClick={() => setShowInsights(true)}
          className="flex items-center gap-2 bg-yellow-400 text-black px-8 py-4 rounded-lg hover:bg-yellow-300 transition-colors font-bold text-lg"
        >
          <Brain /> View AI Analysis
        </button>
      </div>

      {/* AI Insights Dialog */}
      <Dialog open={showInsights} onOpenChange={setShowInsights}>
        <DialogContent className="bg-black text-yellow-400 border-2 border-yellow-400 max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="text-2xl font-bold flex items-center gap-2">
              <Brain className="w-6 h-6" />
              AI Task Analysis Insights
            </DialogTitle>
          </DialogHeader>
          
          <div className="prose prose-invert prose-yellow max-w-none">
            <ReactMarkdown>{data.ai_insights}</ReactMarkdown>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default EnhancedAnalytics;