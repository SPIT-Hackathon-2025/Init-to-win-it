import React, { useEffect, useState } from 'react';
import { Card, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
// import { Skeleton } from '@/components/ui/skeleton';
import { AlertCircle, Clock, Mail, Shield } from 'lucide-react';

const fakeMails = [
    {
        id: 1,
        subject: 'Meeting Reminder',
        body: 'Don\'t forget our meeting at 3 PM.',
        category: 'read',
        timestamp: new Date().toISOString(),
        analysis: {
            action: 'Schedule a meet',
            confidence: 0.92,
            priority: 'high',
            entities: ['meeting', 'time'],
            sentiment: 'neutral',
            suggestedResponse: 'I\'ll attend the meeting at 3 PM.',
        }
    },
    {
        id: 2,
        subject: 'Spam Offer',
        body: 'You won a million dollars!',
        category: 'unread',
        timestamp: new Date().toISOString(),
        analysis: {
            action: 'Mark as spam',
            confidence: 0.98,
            priority: 'low',
            entities: ['money'],
            sentiment: 'suspicious',
            suggestedResponse: 'Delete and block sender',
        }
    },
    {
        id: 3,
        subject: 'Project Update',
        body: 'The project is on track.',
        category: 'read',
        timestamp: new Date().toISOString(),
        analysis: {
            action: 'Assign a task',
            confidence: 0.85,
            priority: 'medium',
            entities: ['project', 'status'],
            sentiment: 'positive',
            suggestedResponse: 'Acknowledge progress',
        }
    },
    {
        id: 4,
        subject: 'Unread Mail',
        body: 'Please review the attached document.',
        category: 'unread',
        timestamp: new Date().toISOString(),
        analysis: {
            action: 'Review document',
            confidence: 0.88,
            priority: 'high',
            entities: ['document', 'review'],
            sentiment: 'neutral',
            suggestedResponse: 'Will review and respond',
        }
    },
];

const fakeLogs = [
    {
        message: 'AI Agent started analyzing mails...',
        timestamp: new Date().toISOString(),
        level: 'info'
    },
    {
        message: 'Mail ID 1 classified as read and scheduled a meet.',
        timestamp: new Date().toISOString(),
        level: 'info'
    },
    {
        message: 'Mail ID 2 classified as unread and marked as spam.',
        timestamp: new Date().toISOString(),
        level: 'info'
    },
    {
        message: 'Mail ID 3 classified as read and assigned a task.',
        timestamp: new Date().toISOString(),
        level: 'info'
    },
    {
        message: 'Mail ID 4 classified as unread and assigned a task.',
        timestamp: new Date().toISOString(),
        level: 'info'
    },
];

const LiveTracker = () => {
    const [mails, setMails] = useState([]);
    const [logs, setLogs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all');

    useEffect(() => {
        // Use fake data instead of fetching from backend
        setMails(fakeMails);
        setLogs(fakeLogs);
        setLoading(false);
    }, []);

    const getPriorityColor = (priority) => ({
        high: 'text-red-400',
        medium: 'text-orange-400',
        low: 'text-green-400'
    }[priority]);

    const renderAnalysisBadge = (confidence) => (
        <Badge variant={confidence > 0.8 ? 'success' : 'warning'}>
            {`${(confidence * 100).toFixed(1)}% Confident`}
        </Badge>
    );

    const renderMailCard = (mail) => {
        // Add error handling for malformed mail objects
        const analysis = mail.analysis || {};
        const entities = analysis.entities || [];
        const confidence = analysis.confidence || 0;
        const priority = analysis.priority || 'medium';
        const sentiment = analysis.sentiment || 'unknown';
        const action = analysis.action || 'No action specified';
        const suggestedResponse = analysis.suggestedResponse || 'No suggested response';

        return (
            <Card key={mail.id} className="bg-gray-800 text-yellow-400 mb-4 hover:bg-gray-700 transition-colors">
                <CardHeader className="flex flex-row justify-between items-center">
                    <div>
                        <h3 className="text-lg font-bold flex items-center gap-2">
                            <Mail className="h-4 w-4" />
                            {mail.subject}
                        </h3>
                        <p className="text-sm text-gray-400 flex items-center gap-2">
                            <Clock className="h-4 w-4" />
                            {new Date(mail.timestamp || Date.now()).toLocaleString()}
                        </p>
                    </div>
                    {renderAnalysisBadge(confidence)}
                </CardHeader>
                <div className="p-4 border-t border-gray-700">
                    <p className="mb-4">{mail.body}</p>
                    <div className="bg-gray-900 p-4 rounded-lg">
                        <h4 className="font-semibold mb-2 flex items-center gap-2">
                            <Shield className="h-4 w-4" />
                            AI Analysis
                        </h4>
                        <div className="grid grid-cols-2 gap-4 text-sm">
                            <div>
                                <p className="text-gray-400">Action Required:</p>
                                <p className={getPriorityColor(priority)}>
                                    {action}
                                </p>
                            </div>
                            <div>
                                <p className="text-gray-400">Entities Detected:</p>
                                <p>{entities.join(', ') || 'None detected'}</p>
                            </div>
                            <div>
                                <p className="text-gray-400">Sentiment:</p>
                                <p>{sentiment}</p>
                            </div>
                            <div>
                                <p className="text-gray-400">Suggested Response:</p>
                                <p className="text-sm">{suggestedResponse}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </Card>
        );
    };

    const renderLogs = () => (
        <div className="space-y-2">
            {logs.map((log, index) => (
                <Card key={index} className="bg-gray-800 text-yellow-400">
                    <div className="p-4 flex items-center gap-2">
                        <AlertCircle className="h-4 w-4" />
                        <p className="flex-1">{log.message}</p>
                        <span className="text-sm text-gray-400">
                            {new Date(log.timestamp).toLocaleTimeString()}
                        </span>
                    </div>
                </Card>
            ))}
        </div>
    );

    if (loading) {
        // return <Skeleton className="w-full h-screen" />;
    }

    return (
        <div className="live-tracker bg-black text-yellow-400 p-4 min-h-screen">
            <h1 className="text-3xl font-bold mb-6 flex items-center gap-2">
                <Shield className="h-8 w-8" />
                Email Analysis Live Tracker
            </h1>
            <div className="mails mb-8">
                <h2 className="text-2xl font-semibold mb-4">Unread Mails</h2>
                {mails.filter(mail => mail.category === 'unread').map(renderMailCard)}
                <h2 className="text-2xl font-semibold mb-4">Read Mails</h2>
                {mails.filter(mail => mail.category === 'read').map(renderMailCard)}
            </div>
            <div className="logs">
                <h2 className="text-2xl font-semibold mb-4">AI Agent Logs</h2>
                {renderLogs()}
            </div>
        </div>
    );
};

export default LiveTracker;
