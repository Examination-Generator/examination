// src/components/StatsTab.jsx
import React, { useState, useEffect, useCallback, memo } from 'react';
import StatsCards from './StatsCards';
import * as questionService from '../services/questionService';
import * as authService from '../services/authService';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// ── Marks Breakdown 
const MarksBreakdown = memo(function MarksBreakdown({ byMarks }) {
    if (!byMarks) return null;

    // Handle both object { "2": 5 } and array [{ marks: 2, count: 5 }] formats
    let entries = [];
    if (Array.isArray(byMarks)) {
        entries = byMarks
            .map(item => [
                item.marks ?? item.mark ?? item.value ?? '?',
                item.count ?? item.total ?? 0,
            ])
            .filter(([, count]) => count > 0);
    } else if (typeof byMarks === 'object') {
        entries = Object.entries(byMarks)
            .map(([k, v]) => [k, typeof v === 'object' ? (v.count ?? v.total ?? 0) : v])
            .filter(([, count]) => Number(count) > 0);
    }

    if (entries.length === 0) return null;

    const sorted = [...entries].sort(([a], [b]) => Number(a) - Number(b));

    return (
        <div className="mt-3 pt-3 border-t border-gray-200">
            <p className="text-xs font-semibold text-gray-600 mb-2">Marks Breakdown:</p>
            <div className="flex flex-wrap gap-1">
                {sorted.map(([marks, count]) => (
                    <span
                        key={marks}
                        className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs font-medium whitespace-nowrap"
                    >
                        {marks}m: {count}
                    </span>
                ))}
            </div>
        </div>
    );
});

const normalizeMarksDistribution = (distribution) => {
    if (!distribution) return [];

    if (Array.isArray(distribution)) {
        return distribution
            .map(item => ({
                marks: item.marks ?? item.mark ?? item.value ?? '?',
                count: item.count ?? item.total ?? 0,
            }))
            .filter(item => Number(item.count) > 0);
    }

    if (typeof distribution === 'object') {
        return Object.entries(distribution)
            .map(([marks, value]) => ({
                marks,
                count: typeof value === 'object' ? (value.count ?? value.total ?? 0) : value,
            }))
            .filter(item => Number(item.count) > 0);
    }

    return [];
};

// ── Creator Card 
const CreatorCard = memo(function CreatorCard({ creator, subjectBreakdown }) {
    const details = subjectBreakdown?.find(
        c => c.creatorName === creator.creatorName
    );

    return (
        <div className="bg-white rounded-lg p-4 shadow-md border border-gray-200 hover:shadow-lg transition">
            {/* Top row */}
            <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-purple-400 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
                        #{creator.rank}
                    </div>
                    <div>
                        <p className="font-bold text-gray-800">{creator.creatorName}</p>
                        {creator.phoneNumber && (
                            <p className="text-xs text-gray-500 flex items-center gap-1 mt-0.5">
                                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                        d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                                </svg>
                                {creator.phoneNumber}
                            </p>
                        )}
                    </div>
                </div>
                <div className="text-right ml-3">
                    <p className="text-2xl font-bold text-purple-600">{creator.totalQuestions}</p>
                    <p className="text-xs text-gray-500">{creator.percentage}%</p>
                </div>
            </div>

            {/* Progress bar */}
            <div className="w-full bg-gray-200 rounded-full h-2 mb-3">
                <div
                    className="bg-purple-500 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${Math.min(Number(creator.percentage) || 0, 100)}%` }}
                />
            </div>

            {/* Subject breakdown */}
            {details?.subjects?.length > 0 && (
                <div className="pt-2 border-t border-gray-100">
                    <p className="text-xs font-semibold text-gray-600 mb-2">By Subject:</p>
                    <div className="flex flex-wrap gap-1">
                        {[...details.subjects]
                            .sort((a, b) => b.count - a.count)
                            .map((s, i) => (
                                <span
                                    key={i}
                                    className="bg-purple-100 text-purple-800 px-2 py-1 rounded-full text-xs font-medium"
                                >
                                    {s.subjectName}: {s.count}
                                </span>
                            ))}
                    </div>
                </div>
            )}
        </div>
    );
});

// ── Creators Modal 
const CreatorsModal = memo(function CreatorsModal({
    isOpen,
    onClose,
    onRefresh,
    creatorStats,
    isLoading,
}) {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] flex flex-col overflow-hidden">

                {/* Header */}
                <div className="bg-gradient-to-r from-purple-600 to-purple-700 px-6 py-4 flex justify-between items-center flex-shrink-0">
                    <div className="flex items-center gap-3">
                        <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                        </svg>
                        <h3 className="text-xl font-bold text-white">Creator Contributions</h3>
                    </div>
                    <div className="flex items-center gap-2">
                        <button
                            onClick={onRefresh}
                            disabled={isLoading}
                            className="text-white hover:bg-purple-800 rounded-full p-2 transition disabled:opacity-50"
                            title="Refresh"
                        >
                            <svg
                                className={`w-5 h-5 ${isLoading ? 'animate-spin' : ''}`}
                                fill="none" stroke="currentColor" viewBox="0 0 24 24"
                            >
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                            </svg>
                        </button>
                        <button
                            onClick={onClose}
                            className="text-white hover:bg-purple-800 rounded-full p-2 transition"
                        >
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>
                </div>

                {/* Body */}
                <div className="flex-1 overflow-y-auto p-6 space-y-8">
                    {isLoading ? (
                        <div className="flex justify-center items-center py-16">
                            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600" />
                        </div>
                    ) : !creatorStats ? (
                        <div className="text-center py-16 text-gray-500">
                            <svg className="w-16 h-16 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                    d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            <p className="text-lg font-semibold">No creator data available</p>
                            <p className="text-sm mt-1">Try refreshing or check the API connection.</p>
                        </div>
                    ) : (
                        <>
                            {/* Overall summary cards */}
                            <section>
                                <h4 className="text-base font-bold text-gray-800 mb-3 flex items-center gap-2">
                                    <svg className="w-5 h-5 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                                        <path d="M2 10a8 8 0 018-8v8h8a8 8 0 11-16 0z" />
                                        <path d="M12 2.252A8.014 8.014 0 0117.748 8H12V2.252z" />
                                    </svg>
                                    Overall Summary
                                </h4>
                                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                                    {[
                                        {
                                            label: 'Total Creators',
                                            value: creatorStats.overallSummary?.totalCreators ?? 0,
                                            color: 'text-purple-600',
                                        },
                                        {
                                            label: 'Total Questions',
                                            value: creatorStats.overallSummary?.totalQuestions ?? 0,
                                            color: 'text-blue-600',
                                        },
                                        {
                                            label: 'Avg per Creator',
                                            value: creatorStats.overallSummary?.averagePerCreator ?? 0,
                                            color: 'text-green-600',
                                        },
                                    ].map(card => (
                                        <div
                                            key={card.label}
                                            className="bg-purple-50 rounded-lg p-4 border border-purple-100 text-center"
                                        >
                                            <p className="text-sm text-gray-600">{card.label}</p>
                                            <p className={`text-3xl font-bold mt-1 ${card.color}`}>
                                                {card.value}
                                            </p>
                                        </div>
                                    ))}
                                </div>
                            </section>

                            {/* Top contributors */}
                            {creatorStats.topContributors?.length > 0 && (
                                <section>
                                    <h4 className="text-base font-bold text-gray-800 mb-3 flex items-center gap-2">
                                        <svg className="w-5 h-5 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                                            <path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a5 5 0 015 5v1H1v-1a5 5 0 015-5z" />
                                        </svg>
                                        Top Contributors ({creatorStats.topContributors.length})
                                    </h4>
                                    <div className="space-y-3">
                                        {creatorStats.topContributors.map((creator, index) => (
                                            <CreatorCard
                                                key={creator.creatorId || index}
                                                creator={creator}
                                                subjectBreakdown={creatorStats.subjectBreakdownPerCreator}
                                            />
                                        ))}
                                    </div>
                                </section>
                            )}

                            {/* Questions by subject */}
                            {creatorStats.questionsBySubject?.length > 0 && (
                                <section>
                                    <h4 className="text-base font-bold text-gray-800 mb-3 flex items-center gap-2">
                                        <svg className="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                                            <path d="M9 4.804A7.968 7.968 0 005.5 4c-1.255 0-2.443.29-3.5.804v10A7.969 7.969 0 015.5 14c1.669 0 3.218.51 4.5 1.385A7.962 7.962 0 0114.5 14c1.255 0 2.443.29 3.5.804v-10A7.968 7.968 0 0014.5 4c-1.255 0-2.443.29-3.5.804V12a1 1 0 11-2 0V4.804z" />
                                        </svg>
                                        Questions by Subject
                                    </h4>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        {[...creatorStats.questionsBySubject]
                                            .sort((a, b) => b.totalQuestions - a.totalQuestions)
                                            .map((subject, i) => (
                                                <div
                                                    key={subject.subjectId || i}
                                                    className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4 border border-blue-200"
                                                >
                                                    <div className="flex justify-between items-start mb-2">
                                                        <div>
                                                            <h5 className="font-bold text-gray-800">
                                                                {subject.subjectName}
                                                            </h5>
                                                            <p className="text-xs text-gray-600 mt-0.5">
                                                                {subject.uniqueCreators}{' '}
                                                                {subject.uniqueCreators === 1 ? 'creator' : 'creators'}
                                                            </p>
                                                        </div>
                                                        <div className="text-right ml-3">
                                                            <p className="text-2xl font-bold text-blue-600">
                                                                {subject.totalQuestions}
                                                            </p>
                                                            <p className="text-xs text-blue-700">
                                                                {subject.percentage}%
                                                            </p>
                                                        </div>
                                                    </div>
                                                    <div className="w-full bg-gray-200 rounded-full h-2">
                                                        <div
                                                            className="bg-blue-600 h-2 rounded-full transition-all duration-500"
                                                            style={{
                                                                width: `${Math.min(
                                                                    Number(subject.percentage) || 0,
                                                                    100
                                                                )}%`,
                                                            }}
                                                        />
                                                    </div>
                                                </div>
                                            ))}
                                    </div>
                                </section>
                            )}
                        </>
                    )}
                </div>

                {/* Footer */}
                <div className="bg-gray-50 border-t border-gray-200 px-6 py-4 flex-shrink-0">
                    <button
                        onClick={onClose}
                        className="w-full bg-gray-600 hover:bg-gray-700 text-white font-semibold py-2 px-6 rounded-lg transition"
                    >
                        Close
                    </button>
                </div>
            </div>
        </div>
    );
});

// ── Main StatsTab 
const StatsTab = memo(function StatsTab({
    existingSubjects,
    onOpenPrintableByPaper,
    onOpenPrintableByTopic,
}) {
    const [stats, setStats] = useState({
        totalQuestions: 0,
        activeQuestions: 0,
        inactiveQuestions: 0,
        unknownTopics: 0,
        bySubject: {},
        byPaper: {},
        byTopic: {},
    });
    const [isLoading, setIsLoading] = useState(false);

    // Filters
    const [filterSubject, setFilterSubject] = useState('');
    const [filterPaper, setFilterPaper] = useState('');
    const [filterStatus, setFilterStatus] = useState('all');
    const [availablePapers, setAvailablePapers] = useState([]);

    // Creators
    const [showCreators, setShowCreators] = useState(false);
    const [creatorStats, setCreatorStats] = useState(null);
    const [isLoadingCreators, setIsLoadingCreators] = useState(false);

    // ── Transform raw API stats 
    const transformStats = useCallback((raw) => {
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
                total: item.total || 0,
                active: item.active || 0,
                inactive: item.inactive || 0,
                subjectId: item.subjectId,
            };
        });

        (raw.byPaper || []).forEach(item => {
            const key = `${item.subject || 'Unknown'} - ${item.paper || 'Unknown'}`;
            const marksDistribution = normalizeMarksDistribution(
                item.marksDistribution || item.byMarks || item.marks_breakdown || item.markBreakdown
            );
            transformed.byPaper[key] = {
                total: item.total || 0,
                active: item.active || 0,
                inactive: item.inactive || 0,
                subject: item.subject || 'Unknown',
                paper: item.paper || 'Unknown',
                subjectId: item.subjectId,
                paperId: item.paperId,
                marksDistribution,
                byMarks: marksDistribution,
            };
        });

        (raw.byTopic || []).forEach(item => {
            const marksDistribution = normalizeMarksDistribution(
                item.marksDistribution || item.byMarks || item.marks_breakdown || item.markBreakdown
            );

            transformed.byTopic[item.topicName || 'Unknown'] = {
                total: item.total || 0,
                active: item.active || 0,
                inactive: item.inactive || 0,
                marksDistribution,
                byMarks: marksDistribution,
                topicId: item.topicId,
                subjectId: item.subjectId,
                subject: item.subject || 'Unknown',
                paper: item.paper || 'Unknown',
            };
        });

        return transformed;
    }, []);

    // ── Fetch stats ────────────────────────────────────────────────────
    const fetchStats = useCallback(async (filters = {}) => {
        setIsLoading(true);
        try {
            const raw = await questionService.getQuestionStats(filters);
            setStats(transformStats(raw));
        } catch (err) {
            console.error('Stats fetch error:', err);
        } finally {
            setIsLoading(false);
        }
    }, [transformStats]);

    // ── Fetch creator stats ────────────────────────────────────────────
    const fetchCreatorStats = useCallback(async () => {
        setIsLoadingCreators(true);
        try {
            const token = authService.getAuthToken();
            const res = await fetch(`${API_URL}/questions/creator-statistics/`, {
                headers: {
                    Authorization: `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
            });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();
            setCreatorStats(data.data || data);
        } catch (err) {
            console.error('Creator stats error:', err);
        } finally {
            setIsLoadingCreators(false);
        }
    }, []);

    // Initial load
    useEffect(() => {
        fetchStats();
    }, [fetchStats]);

    // Re-fetch when filters change
    useEffect(() => {
        const params = {};
        if (filterSubject) {
            const s = existingSubjects.find(s => s.name === filterSubject);
            if (s?.id) params.subject = s.id;
        }
        if (filterPaper) {
            const p = availablePapers.find(p => p.name === filterPaper);
            if (p?.id) params.paper = p.id;
        }
        if (filterStatus !== 'all') {
            params.isActive = filterStatus === 'active' ? 'true' : 'false';
        }
        fetchStats(params);
    }, [filterSubject, filterPaper, filterStatus, fetchStats, existingSubjects, availablePapers]);

    // Subject → papers cascade
    useEffect(() => {
        if (filterSubject) {
            const s = existingSubjects.find(s => s.name === filterSubject);
            setAvailablePapers(s?.papers || []);
            setFilterPaper('');
        } else {
            setAvailablePapers([]);
            setFilterPaper('');
        }
    }, [filterSubject, existingSubjects]);

    const handleOpenCreators = useCallback(() => {
        setShowCreators(true);
        fetchCreatorStats();
    }, [fetchCreatorStats]);

    const clearFilters = useCallback(() => {
        setFilterSubject('');
        setFilterPaper('');
        setFilterStatus('all');
    }, []);

    const hasFilters = filterSubject || filterPaper || filterStatus !== 'all';

    // ── Render 
    return (
        <div className="space-y-6">

            {/* ── Header  */}
            <div className="flex flex-wrap justify-between items-center gap-3">
                <h2 className="text-2xl font-bold text-gray-800">Question Statistics</h2>
                <div className="flex gap-3">
                    {/* Creators button */}
                    <button
                        onClick={handleOpenCreators}
                        className="flex items-center gap-2 bg-purple-600 hover:bg-purple-700 text-white font-semibold py-2 px-4 rounded-lg transition shadow-sm"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                        </svg>
                        Creators
                    </button>

                    {/* Refresh button */}
                    <button
                        onClick={() => fetchStats()}
                        disabled={isLoading}
                        className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition shadow-sm disabled:opacity-50"
                    >
                        <svg
                            className={`w-5 h-5 ${isLoading ? 'animate-spin' : ''}`}
                            fill="none" stroke="currentColor" viewBox="0 0 24 24"
                        >
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                        {isLoading ? 'Refreshing...' : 'Refresh'}
                    </button>
                </div>
            </div>

            {/* ── Stats cards  */}
            <StatsCards stats={stats} />

            {/* ── Filters ─────────────────────────────────────────────── */}
            <div className="bg-white rounded-xl shadow-lg p-6">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-bold text-gray-800">Filters</h3>
                    {hasFilters && (
                        <button
                            onClick={clearFilters}
                            className="text-sm text-blue-600 hover:text-blue-800 font-semibold"
                        >
                            Clear Filters
                        </button>
                    )}
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <select
                        value={filterSubject}
                        onChange={e => setFilterSubject(e.target.value)}
                        className="px-4 py-2 border border-gray-300 rounded-lg outline-none focus:ring-2 focus:ring-blue-500"
                    >
                        <option value="">All Subjects</option>
                        {existingSubjects.map(s => (
                            <option key={s.id} value={s.name}>{s.name}</option>
                        ))}
                    </select>

                    <select
                        value={filterPaper}
                        onChange={e => setFilterPaper(e.target.value)}
                        disabled={!filterSubject}
                        className="px-4 py-2 border border-gray-300 rounded-lg outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                    >
                        <option value="">All Papers</option>
                        {availablePapers.map(p => (
                            <option key={p.id} value={p.name}>{p.name}</option>
                        ))}
                    </select>

                    <select
                        value={filterStatus}
                        onChange={e => setFilterStatus(e.target.value)}
                        className="px-4 py-2 border border-gray-300 rounded-lg outline-none focus:ring-2 focus:ring-blue-500"
                    >
                        <option value="all">All Status</option>
                        <option value="active">Active Only</option>
                        <option value="inactive">Inactive Only</option>
                    </select>
                </div>
            </div>

            {/* ── By Subject */}
            <div className="bg-white rounded-xl shadow-lg p-6">
                <h3 className="text-lg font-bold text-gray-800 mb-4">Questions by Subject</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-h-80 overflow-y-auto pr-1">
                    {Object.entries(stats.bySubject).length === 0 ? (
                        <p className="col-span-3 text-center text-gray-500 py-8">No subjects found</p>
                    ) : (
                        Object.entries(stats.bySubject).map(([subject, counts]) => (
                            <div
                                key={subject}
                                className="border-2 border-gray-200 rounded-lg p-4 bg-gradient-to-br from-blue-50 to-white hover:border-blue-400 transition"
                            >
                                <div className="flex items-center justify-between mb-2">
                                    <h4 className="text-sm font-bold text-gray-700 truncate flex-1">
                                        {subject}
                                    </h4>
                                    <span className="text-2xl font-bold text-blue-600 ml-2">
                                        {counts.total}
                                    </span>
                                </div>
                                <div className="flex gap-4 text-xs">
                                    <span className="flex items-center gap-1">
                                        <span className="w-2 h-2 bg-green-500 rounded-full inline-block" />
                                        Active: <strong>{counts.active}</strong>
                                    </span>
                                    <span className="flex items-center gap-1">
                                        <span className="w-2 h-2 bg-red-500 rounded-full inline-block" />
                                        Inactive: <strong>{counts.inactive}</strong>
                                    </span>
                                </div>

                                <MarksBreakdown byMarks={counts.marksDistribution || counts.byMarks} />
                            </div>
                        ))
                    )}
                </div>
            </div>

            {/* ── By Paper */}
            <div className="bg-white rounded-xl shadow-lg p-6">
                <h3 className="text-lg font-bold text-gray-800 mb-1">Questions by Paper</h3>
                <p className="text-xs text-gray-500 mb-4">Click a card to generate a printable document</p>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-h-80 overflow-y-auto pr-1">
                    {Object.entries(stats.byPaper).length === 0 ? (
                        <p className="col-span-3 text-center text-gray-500 py-8">No papers found</p>
                    ) : (
                        Object.entries(stats.byPaper).map(([key, counts]) => (
                            <div
                                key={key}
                                onClick={() => onOpenPrintableByPaper?.(counts)}
                                className="border-2 border-gray-200 rounded-lg p-4 bg-gradient-to-br from-purple-50 to-white cursor-pointer hover:border-purple-400 hover:shadow-md transition"
                            >
                                <p className="text-xs text-gray-500 font-medium mb-0.5">
                                    {counts.subject}
                                </p>
                                <h4 className="text-sm font-bold text-gray-700 mb-2">
                                    {counts.paper}
                                </h4>
                                <div className="flex items-center justify-between mb-2">
                                    <span className="text-xs text-gray-600">Total</span>
                                    <span className="text-xl font-bold text-purple-600">
                                        {counts.total}
                                    </span>
                                </div>
                                <div className="flex gap-4 text-xs">
                                    <span className="flex items-center gap-1">
                                        <span className="w-2 h-2 bg-green-500 rounded-full inline-block" />
                                        Active: <strong>{counts.active}</strong>
                                    </span>
                                    <span className="flex items-center gap-1">
                                        <span className="w-2 h-2 bg-red-500 rounded-full inline-block" />
                                        Inactive: <strong>{counts.inactive}</strong>
                                    </span>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>

            {/* ── By Topic — with marks breakdown */}
            <div className="bg-white rounded-xl shadow-lg p-6">
                <h3 className="text-lg font-bold text-gray-800 mb-1">Questions by Topic</h3>
                <p className="text-xs text-gray-500 mb-4">Click a card to generate a printable document</p>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-h-[520px] overflow-y-auto pr-1">
                    {Object.entries(stats.byTopic).length === 0 ? (
                        <p className="col-span-3 text-center text-gray-500 py-8">No topics found</p>
                    ) : (
                        Object.entries(stats.byTopic).map(([topic, counts]) => (
                            <div
                                key={topic}
                                onClick={() =>
                                    counts.topicId &&
                                    onOpenPrintableByTopic?.({ ...counts, topic })
                                }
                                className={`border-2 border-gray-200 rounded-lg p-4 bg-gradient-to-br from-green-50 to-white transition
                                    ${counts.topicId
                                        ? 'cursor-pointer hover:border-green-400 hover:shadow-md'
                                        : 'opacity-80'
                                    }`}
                            >
                                <h4 className="text-sm font-bold text-gray-700 truncate mb-2">
                                    {topic}
                                </h4>

                                <div className="flex items-center justify-between mb-2">
                                    <span className="text-xs text-gray-600">Total Questions</span>
                                    <span className="text-xl font-bold text-green-600">
                                        {counts.total}
                                    </span>
                                </div>

                                <div className="flex gap-4 text-xs">
                                    <span className="flex items-center gap-1">
                                        <span className="w-2 h-2 bg-green-500 rounded-full inline-block" />
                                        Active: <strong>{counts.active}</strong>
                                    </span>
                                    <span className="flex items-center gap-1">
                                        <span className="w-2 h-2 bg-red-500 rounded-full inline-block" />
                                        Inactive: <strong>{counts.inactive}</strong>
                                    </span>
                                </div>

                                {/* Marks breakdown */}
                                <MarksBreakdown byMarks={counts.marksDistribution || counts.byMarks} />
                            </div>
                        ))
                    )}
                </div>
            </div>

            {/* Creators Modal  */}
            <CreatorsModal
                isOpen={showCreators}
                onClose={() => setShowCreators(false)}
                onRefresh={fetchCreatorStats}
                creatorStats={creatorStats}
                isLoading={isLoadingCreators}
            />
        </div>
    );
});

export default StatsTab;