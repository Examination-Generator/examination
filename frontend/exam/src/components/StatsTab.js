// src/components/StatsTab.jsx
import React, { useState, useEffect, useRef, useCallback, memo } from 'react';
import StatsCards from './StatsCards';
import * as questionService from '../services/questionService';

const StatsTab = memo(function StatsTab({
    existingSubjects,
    onOpenPrintableByPaper,
    onOpenPrintableByTopic,
}) {
    const [stats, setStats] = useState({ totalQuestions: 0, activeQuestions: 0, inactiveQuestions: 0, unknownTopics: 0, bySubject: {}, byPaper: {}, byTopic: {} });
    const [isLoading, setIsLoading] = useState(false);
    const [filterSubject, setFilterSubject] = useState('');
    const [filterPaper, setFilterPaper] = useState('');
    const [filterStatus, setFilterStatus] = useState('all');
    const [availablePapers, setAvailablePapers] = useState([]);

    const fetchStats = useCallback(async (filters = {}) => {
        setIsLoading(true);
        try {
            const raw = await questionService.getQuestionStats(filters);
            const transformed = {
                totalQuestions: raw.total || 0,
                activeQuestions: raw.active || 0,
                inactiveQuestions: raw.inactive || 0,
                unknownTopics: raw.unknownTopics || 0,
                bySubject: {},
                byPaper: {},
                byTopic: {},
            };
            (raw.bySubject || []).forEach(item => {
                transformed.bySubject[item.subjectName || 'Unknown'] = {
                    total: item.total || 0, active: item.active || 0, inactive: item.inactive || 0,
                    subjectId: item.subjectId,
                };
            });
            (raw.byPaper || []).forEach(item => {
                const key = `${item.subject || 'Unknown'} - ${item.paper || 'Unknown'}`;
                transformed.byPaper[key] = {
                    total: item.total || 0, active: item.active || 0, inactive: item.inactive || 0,
                    subject: item.subject, paper: item.paper,
                    subjectId: item.subjectId, paperId: item.paperId,
                };
            });
            (raw.byTopic || []).forEach(item => {
                transformed.byTopic[item.topicName || 'Unknown'] = {
                    total: item.total || 0, active: item.active || 0, inactive: item.inactive || 0,
                    byMarks: {}, topicId: item.topicId, subjectId: item.subjectId,
                    subject: item.subject, paper: item.paper,
                };
            });
            setStats(transformed);
        } catch (err) {
            console.error('Stats error:', err);
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => { fetchStats(); }, [fetchStats]);

    useEffect(() => {
        if (filterSubject && existingSubjects.length > 0) {
            const s = existingSubjects.find(s => s.name === filterSubject);
            setAvailablePapers(s?.papers || []);
            setFilterPaper('');
        } else {
            setAvailablePapers([]);
        }
    }, [filterSubject, existingSubjects]);

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold text-gray-800">Question Statistics</h2>
                <button onClick={() => fetchStats()} disabled={isLoading}
                    className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition disabled:opacity-50">
                    <svg className={`w-5 h-5 ${isLoading ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    {isLoading ? 'Loading...' : 'Refresh'}
                </button>
            </div>

            <StatsCards stats={stats} />

            {/* Filters */}
            <div className="bg-white rounded-xl shadow-lg p-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <select value={filterSubject} onChange={e => setFilterSubject(e.target.value)}
                        className="px-4 py-2 border rounded-lg outline-none focus:ring-2 focus:ring-blue-500">
                        <option value="">All Subjects</option>
                        {existingSubjects.map(s => <option key={s.id} value={s.name}>{s.name}</option>)}
                    </select>
                    <select value={filterPaper} onChange={e => setFilterPaper(e.target.value)}
                        disabled={!filterSubject}
                        className="px-4 py-2 border rounded-lg outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100">
                        <option value="">All Papers</option>
                        {availablePapers.map(p => <option key={p.id} value={p.name}>{p.name}</option>)}
                    </select>
                    <select value={filterStatus} onChange={e => setFilterStatus(e.target.value)}
                        className="px-4 py-2 border rounded-lg outline-none focus:ring-2 focus:ring-blue-500">
                        <option value="all">All Status</option>
                        <option value="active">Active Only</option>
                        <option value="inactive">Inactive Only</option>
                    </select>
                </div>
            </div>

            {/* By Subject */}
            <div className="bg-white rounded-xl shadow-lg p-6">
                <h3 className="text-lg font-bold mb-4">By Subject</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-h-80 overflow-y-auto">
                    {Object.entries(stats.bySubject).map(([subject, counts]) => (
                        <div key={subject} className="border-2 border-gray-200 rounded-lg p-4 bg-blue-50">
                            <div className="flex justify-between items-center mb-2">
                                <h4 className="text-sm font-bold text-gray-700 truncate">{subject}</h4>
                                <span className="text-2xl font-bold text-blue-600">{counts.total}</span>
                            </div>
                            <div className="flex gap-3 text-xs">
                                <span className="text-green-700">Active: {counts.active}</span>
                                <span className="text-red-700">Inactive: {counts.inactive}</span>
                            </div>
                        </div>
                    ))}
                    {Object.keys(stats.bySubject).length === 0 && (
                        <p className="col-span-3 text-center text-gray-500 py-8">No subjects found</p>
                    )}
                </div>
            </div>

            {/* By Paper */}
            <div className="bg-white rounded-xl shadow-lg p-6">
                <h3 className="text-lg font-bold mb-4">By Paper (click to print)</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-h-80 overflow-y-auto">
                    {Object.entries(stats.byPaper).map(([key, counts]) => (
                        <div key={key}
                            className="border-2 border-gray-200 rounded-lg p-4 bg-purple-50 cursor-pointer hover:shadow-md transition"
                            onClick={() => onOpenPrintableByPaper?.(counts)}>
                            <p className="text-xs text-gray-500">{counts.subject}</p>
                            <h4 className="text-sm font-bold text-gray-700">{counts.paper}</h4>
                            <div className="flex justify-between mt-2">
                                <span className="text-xs text-gray-600">Total: {counts.total}</span>
                                <span className="text-xl font-bold text-purple-600">{counts.total}</span>
                            </div>
                        </div>
                    ))}
                    {Object.keys(stats.byPaper).length === 0 && (
                        <p className="col-span-3 text-center text-gray-500 py-8">No papers found</p>
                    )}
                </div>
            </div>

            {/* By Topic */}
            <div className="bg-white rounded-xl shadow-lg p-6">
                <h3 className="text-lg font-bold mb-4">By Topic (click to print)</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-h-80 overflow-y-auto">
                    {Object.entries(stats.byTopic).map(([topic, counts]) => (
                        <div key={topic}
                            className="border-2 border-gray-200 rounded-lg p-4 bg-green-50 cursor-pointer hover:shadow-md transition"
                            onClick={() => counts.topicId && onOpenPrintableByTopic?.({ ...counts, topic })}>
                            <h4 className="text-sm font-bold text-gray-700 truncate">{topic}</h4>
                            <div className="flex justify-between mt-2">
                                <div className="text-xs space-y-1">
                                    <p className="text-green-700">Active: {counts.active}</p>
                                    <p className="text-red-700">Inactive: {counts.inactive}</p>
                                </div>
                                <span className="text-xl font-bold text-green-600">{counts.total}</span>
                            </div>
                        </div>
                    ))}
                    {Object.keys(stats.byTopic).length === 0 && (
                        <p className="col-span-3 text-center text-gray-500 py-8">No topics found</p>
                    )}
                </div>
            </div>
        </div>
    );
});

export default StatsTab;