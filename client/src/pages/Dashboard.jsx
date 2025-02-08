import { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import LoadingAnimation from '@/components/LoadingAnimation';
import {
  PieChart, Pie, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend, Cell, AreaChart, Area
} from 'recharts';
import { ResponsiveSunburst } from '@nivo/sunburst'
import { ResponsiveSwarmPlot } from '@nivo/swarmplot'
import { ResponsiveTreeMap } from '@nivo/treemap'
import { ResponsiveSankey } from '@nivo/sankey'
import { ResponsiveNetwork } from '@nivo/network'
import { ResponsiveRadar } from '@nivo/radar'

const SERVER_URL = 'http://127.0.0.1:8001';

const Dashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Check for cached data
        const cachedData = localStorage.getItem('dashboardData');
        const cachedTimestamp = localStorage.getItem('dashboardDataTimestamp');
        
        // Check if cache is valid (less than 5 min)
        if (cachedData && cachedTimestamp) {
          const now = new Date().getTime();
          const cacheAge = now - parseInt(cachedTimestamp);
          if (cacheAge < 5 * 60 * 1000) { // 5 min
            setData(JSON.parse(cachedData));
            setLoading(false);
            return;
          }
        }

        // Fetch fresh data if cache is invalid or missing
        const response = await fetch(`${SERVER_URL}/analyze`);
        const result = await response.json();
        
        // Cache the new data
        try {
          localStorage.setItem('dashboardData', JSON.stringify(result));
          localStorage.setItem('dashboardDataTimestamp', new Date().getTime().toString());
        } catch (error) {
          console.warn('Failed to cache dashboard data:', error);
        }

        setData(result);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching data:', error);
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const formatNumber = (num) => {
    if (typeof num === 'number') {
      return num.toFixed(2);
    }
    return num;
  };

  if (loading) return <LoadingAnimation />;
  if (!data) return <div className="p-6">No data available</div>;

  const COLORS = ['#FFD700', '#FFA500', '#FF6B6B', '#4CAF50'];

  const emailData = {
    labels: ['Subscribed', 'Not Subscribed'],
    values: [
      data.email_marketing.metrics.subscription_status.Subscribed,
      data.email_marketing.metrics.subscription_status['Not Subscribed']
    ]
  };

  const sessionData = Object.entries(data.content_strategy.metrics.session_duration)
    .map(([type, duration]) => ({ type, duration }));

  const supportSunburstData = {
    name: 'support',
    children: Object.entries(data.customer_support.metrics.response_patterns)
      .map(([tier, score]) => ({
        name: tier,
        value: score,
        satisfactionScore: score * 33.33,
        color: COLORS[['Bronze', 'Silver', 'Gold', 'Platinum'].indexOf(tier)]
      }))
  };

  const devicePerformanceData = Object.entries(data.seo_optimization.metrics.bounce_rates)
    .map(([device, rate]) => ({
      id: device,
      group: device,
      value: rate * 100,
      performance: data.integration.metrics.cross_channel_performance[`('${device}', 'Video')`]
    }));

  const adMetricsNetwork = {
    nodes: Object.entries(data.ab_testing.metrics.ad_performance.ad_relevance_score)
      .map(([type]) => ({
        id: type,
        radius: Math.max(5, data.ab_testing.metrics.ad_performance.clicks[type] || 0),
        color: COLORS[['Banner', 'Video', 'Carousel', 'Popup'].indexOf(type)],
        data: {
          score: data.ab_testing.metrics.ad_performance.ad_relevance_score[type],
          conversions: data.ab_testing.metrics.ad_performance.conversions[type],
          clicks: data.ab_testing.metrics.ad_performance.clicks[type]
        }
      })),
    links: [
      { source: 'Banner', target: 'Video', value: 2 },
      { source: 'Video', target: 'Carousel', value: 2 },
      { source: 'Carousel', target: 'Popup', value: 2 },
      { source: 'Popup', target: 'Banner', value: 2 }
    ]
  };

  const marketTreeMap = {
    name: 'market',
    children: Object.entries(data.competitive_analysis.metrics.relative_performance)
      .map(([category, value]) => ({
        name: category,
        value: value * 1000
      }))
  };

  const customerFlowData = {
    nodes: [
      { id: 'total', color: COLORS[0] },
      { id: 'satisfied', color: COLORS[1] },
      { id: 'loyal', color: COLORS[2] },
      { id: 'retained', color: COLORS[3] },
    ],
    links: [
      {
        source: 'total',
        target: 'satisfied',
        value: data.customer_relationship.metrics.customer_satisfaction * 30
      },
      {
        source: 'satisfied',
        target: 'loyal',
        value: Object.values(data.customer_relationship.metrics.loyalty_scores).reduce((a, b) => a + b, 0) / 4
      },
      {
        source: 'loyal',
        target: 'retained',
        value: data.customer_relationship.metrics.retention_rate * 50
      }
    ]
  };

  const channelPerformanceData = Object.entries(data.ab_testing.metrics.ad_performance.ad_relevance_score)
    .map(([type, score]) => ({
      type,
      relevance: score,
      clicks: data.ab_testing.metrics.ad_performance.clicks[type] / 10,
      conversions: data.ab_testing.metrics.ad_performance.conversions[type] * 2,
      roi: data.budget_optimization.metrics.roi_by_channel[type]
    }));

  return (
    <div className="p-6 max-w-[1400px] mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-transparent bg-gradient-to-r from-yellow-300 to-yellow-500 bg-clip-text mb-6">
          Marketing Analytics Dashboard
        </h1>

        {/* Quick Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          {[
            {
              title: 'Conversion Rate',
              value: `${(data.conversion_optimization.metrics.funnel_metrics.conversion_rate * 100).toFixed(1)}%`,
              change: '+2.3%',
              color: 'yellow'
            },
            {
              title: 'Customer Satisfaction',
              value: data.customer_relationship.metrics.customer_satisfaction.toFixed(2),
              change: '+0.5',
              color: 'green'
            },
            {
              title: 'Email Open Rate',
              value: `${(data.email_marketing.metrics.open_rate * 100).toFixed(1)}%`,
              change: '+5.2%',
              color: 'blue'
            },
            {
              title: 'Retention Rate',
              value: `${(data.customer_relationship.metrics.retention_rate * 100).toFixed(1)}%`,
              change: '+1.2%',
              color: 'purple'
            }
          ].map((stat, idx) => (
            <Card key={idx} className="bg-zinc-800/50 border-zinc-700/50">
              <CardContent className="p-4">
                <p className="text-sm text-zinc-400">{stat.title}</p>
                <div className="flex justify-between items-baseline mt-1">
                  <p className="text-2xl font-semibold text-zinc-100">{stat.value}</p>
                  <span className={`text-sm text-${stat.color}-400`}>
                    {stat.change}
                  </span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Market Position TreeMap */}
          <Card className="bg-zinc-800/50 border-zinc-700/50 hover:shadow-lg hover:shadow-yellow-500/10 transition-all">
            <CardContent className="p-4">
              <h3 className="text-white text-lg font-semibold mb-4">Market Position TreeMap</h3>
              <div style={{ height: 400 }}>
                <ResponsiveTreeMap
                  data={marketTreeMap}
                  identity="name"
                  value="value"
                  valueFormat=".2f"
                  margin={{ top: 10, right: 10, bottom: 10, left: 10 }}
                  labelSkipSize={12}
                  labelTextColor={{ from: 'color', modifiers: [['darker', 1.2]] }}
                  parentLabelPosition="left"
                  parentLabelTextColor={{ from: 'color', modifiers: [['darker', 2]] }}
                  borderColor={{ from: 'color', modifiers: [['darker', 0.1]] }}
                />
              </div>
            </CardContent>
          </Card>

          {/* Ad Performance Network */}
          <Card className="bg-zinc-800/50 border-zinc-700/50 hover:shadow-lg hover:shadow-yellow-500/10 transition-all">
            <CardContent className="p-4">
              <h3 className="text-white text-lg font-semibold mb-4">Ad Performance Network</h3>
              <div style={{ height: 400 }}>
                <ResponsiveNetwork
                  data={adMetricsNetwork}
                  margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
                  linkDistance={e => 150}
                  centeringStrength={0.5}
                  repulsivity={8}
                  nodeSize={n => n.radius}
                  activeNodeSize={n => n.radius * 1.5}
                  nodeColor={n => n.color}
                  nodeBorderWidth={2}
                  nodeBorderColor={{
                    from: 'color',
                    modifiers: [['darker', 0.8]]
                  }}
                  linkThickness={2}
                  linkBlendMode="multiply"
                  motionConfig="gentle"
                  nodeTooltip={node => {
                    if (!node?.data) return null;
                    return (
                      <div style={{
                        background: '#333',
                        padding: '8px',
                        borderRadius: '4px',
                        color: '#fff'
                      }}>
                        <strong>{node.id}</strong>
                        <div>Relevance: {node.data.score?.toFixed(2) || 'N/A'}</div>
                        <div>Conversions: {node.data.conversions?.toFixed(2) || 'N/A'}</div>
                        <div>Clicks: {node.data.clicks?.toFixed(2) || 'N/A'}</div>
                      </div>
                    );
                  }}
                />
              </div>
            </CardContent>
          </Card>

          {/* Customer Journey Flow */}
          <Card className="bg-zinc-800/50 border-zinc-700/50 hover:shadow-lg hover:shadow-yellow-500/10 transition-all">
            <CardContent className="p-4">
              <h3 className="text-white text-lg font-semibold mb-4">Customer Journey Flow</h3>
              <div style={{ height: 400 }}>
                <ResponsiveSankey
                  data={customerFlowData}
                  margin={{ top: 40, right: 160, bottom: 40, left: 50 }}
                  align="justify"
                  colors={{ scheme: 'category10' }}
                  nodeOpacity={1}
                  nodeThickness={18}
                  nodeInnerPadding={3}
                  nodeSpacing={24}
                  nodeBorderWidth={0}
                  nodeBorderColor={{ from: 'color', modifiers: [['darker', 0.8]] }}
                  linkOpacity={0.5}
                  linkHoverOthersOpacity={0.1}
                  enableLinkGradient={true}
                  labelPosition="outside"
                  labelOrientation="vertical"
                  labelPadding={16}
                  labelTextColor={{ from: 'color', modifiers: [['darker', 1]] }}
                  animate={true}
                  motionConfig="gentle"
                />
              </div>
            </CardContent>
          </Card>

          {/* Channel Performance Radar */}
          <Card className="bg-zinc-800/50 border-zinc-700/50 hover:shadow-lg hover:shadow-yellow-500/10 transition-all">
            <CardContent className="p-4">
              <h3 className="text-white text-lg font-semibold mb-4">Channel Performance Radar</h3>
              <div style={{ height: 400 }}>
                <ResponsiveRadar
                  data={channelPerformanceData}
                  keys={['relevance', 'clicks', 'conversions', 'roi']}
                  indexBy="type"
                  maxValue="auto"
                  margin={{ top: 70, right: 80, bottom: 40, left: 80 }}
                  curve="cardinalClosed"
                  borderWidth={2}
                  borderColor={{ from: 'color' }}
                  gridLevels={5}
                  gridShape="circular"
                  gridLabelOffset={36}
                  enableDots={true}
                  dotSize={8}
                  dotColor={{ theme: 'background' }}
                  dotBorderWidth={2}
                  dotBorderColor={{ from: 'color' }}
                  enableDotLabel={false}
                  colors={COLORS}
                  fillOpacity={0.35}
                  blendMode="multiply"
                  animate={true}
                  motionConfig="gentle"
                  theme={{
                    textColor: '#fff',
                    fontSize: 11,
                    tooltip: {
                      container: {
                        background: '#333',
                        color: '#fff',
                        fontSize: '12px'
                      }
                    }
                  }}
                />
              </div>
            </CardContent>
          </Card>

          {/* Email Marketing */}
          <Card className="bg-zinc-800/50 border-zinc-700/50 hover:shadow-lg hover:shadow-yellow-500/10 transition-all">
            <CardContent className="p-4">
              <h3 className="text-white text-lg font-semibold mb-4">Email Subscription Status</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={emailData.labels.map((label, index) => ({
                      name: label,
                      value: emailData.values[index]
                    }))}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    label
                  >
                    {emailData.labels.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={['#FFD700', '#FF6B6B'][index]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Session Duration */}
          <Card className="bg-zinc-800/50 border-zinc-700/50 hover:shadow-lg hover:shadow-yellow-500/10 transition-all">
            <CardContent className="p-4">
              <h3 className="text-white text-lg font-semibold mb-4">Session Duration by Ad Type</h3>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={sessionData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="type" />
                  <YAxis
                    domain={[0, 'auto']}
                    tickFormatter={val => val.toFixed(2)}
                  />
                  <Tooltip formatter={val => val.toFixed(2)} />
                  <Area type="monotone" dataKey="duration" fill="#4CAF50" stroke="#4CAF50" />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Spiral Chart for Customer Support */}
          <Card className="bg-zinc-800/50 border-zinc-700/50 hover:shadow-lg hover:shadow-yellow-500/10 transition-all">
            <CardContent className="p-4">
              <h3 className="text-white text-lg font-semibold mb-4">Customer Support Matrix</h3>
              <div style={{ height: 300 }}>
                <ResponsiveSunburst
                  data={supportSunburstData}
                  margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
                  id="name"
                  value="value"
                  cornerRadius={2}
                  borderWidth={1}
                  borderColor="white"
                  colors={{ datum: 'data.color' }}
                  childColor={{ from: 'color' }}
                  animate={true}
                  motionConfig="gentle"
                  enableArcLabels={true}
                  arcLabelsSkipAngle={10}
                  arcLabelsTextColor={{ from: 'color', modifiers: [['darker', 3]] }}
                />
              </div>
            </CardContent>
          </Card>

          {/* 3D-like Bounce Rate Visualization */}
          <Card className="bg-zinc-800/50 border-zinc-700/50 hover:shadow-lg hover:shadow-yellow-500/10 transition-all">
            <CardContent className="p-4">
              <h3 className="text-white text-lg font-semibold mb-4">Device Performance Matrix</h3>
              <div style={{ height: 300 }}>
                <ResponsiveSwarmPlot
                  data={devicePerformanceData}
                  groups={['Desktop', 'Mobile', 'Tablet']}
                  value="value"
                  valueFormat=">.2f"
                  size={15}
                  forceStrength={4}
                  simulationIterations={100}
                  borderColor={{
                    from: 'color',
                    modifiers: [['darker', 0.6]]
                  }}
                  margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
                  axisTop={null}
                  axisRight={null}
                  axisBottom={{
                    tickSize: 10,
                    tickPadding: 5,
                    tickRotation: 0,
                    legend: 'Device Type',
                    legendPosition: 'middle',
                    legendOffset: 46
                  }}
                  axisLeft={{
                    tickSize: 10,
                    tickPadding: 5,
                    tickRotation: 0,
                    legend: 'Bounce Rate (%)',
                    legendPosition: 'middle',
                    legendOffset: -46
                  }}
                  motionConfig="gentle"
                />
              </div>
            </CardContent>
          </Card>

          {/* Conversion Metrics */}
          <Card className="bg-zinc-800/50 border-zinc-700/50 hover:shadow-lg hover:shadow-yellow-500/10 transition-all">
            <CardContent className="p-6">
              <h3 className="text-white text-lg font-semibold mb-6">Key Metrics</h3>
              <div className="space-y-4 text-zinc-300">
                <div className="flex justify-between items-center">
                  <span>Conversion Rate</span>
                  <span className="text-yellow-400">
                    {formatNumber(data.conversion_optimization.metrics.funnel_metrics.conversion_rate * 100)}%
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span>Cart Abandonment</span>
                  <span className="text-red-400">
                    {formatNumber(data.conversion_optimization.metrics.funnel_metrics.cart_abandonment * 100)}%
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span>Avg Order Value</span>
                  <span className="text-green-400">
                    ${data.conversion_optimization.metrics.funnel_metrics.avg_order_value.toFixed(2)}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Recommendations */}
          <Card className="bg-zinc-800/50 border-zinc-700/50 hover:shadow-lg hover:shadow-yellow-500/10 transition-all">
            <CardContent className="p-4">
              <h3 className="text-white text-lg font-semibold mb-4">Key Recommendations</h3>
              <div className="space-y-3">
                {[
                  ...data.ab_testing.recommendations,
                  ...data.budget_optimization.recommendations,
                  ...data.content_strategy.recommendations
                ].map((rec, idx) => (
                  <div key={idx} className="flex items-start gap-2">
                    <span className="text-yellow-500">→</span>
                    <p className="text-sm text-zinc-300">{rec}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* New Insights Grid with Animation */}
        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          {Object.entries(data).flatMap(([category, content]) =>
            content.insights?.map((insight, idx) => (
              <Card
                key={`${category}-${idx}`}
                className="bg-zinc-800/50 border-zinc-700/50 hover:scale-105 transition-all duration-300 hover:shadow-lg hover:shadow-yellow-500/10"
              >
                <CardContent className="p-4">
                  <div className="flex items-start gap-2">
                    <span className="text-2xl">
                      {['✨', '📊', '🎯', '📈', '🔄', '⚡'][idx % 6]}
                    </span>
                    <div>
                      <p className="text-sm text-zinc-300">{insight}</p>
                      <span className="text-xs text-yellow-500/70 mt-2 block">
                        {category.split('_').map(word =>
                          word.charAt(0).toUpperCase() + word.slice(1)
                        ).join(' ')}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
