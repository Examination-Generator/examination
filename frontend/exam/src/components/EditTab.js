// src/components/EditTab.jsx
import React, { useState, useEffect, useCallback, useRef } from 'react';
import EditFilters from './EditFilters';
import EditForm from './EditForm';
import QuestionListItem from './QuestionListItem';
import { useEditForm } from '../hooks/useEditForm';
import { usePagination } from '../hooks/usePagination';
import { useDebounce } from '../hooks/useDebounce';
import * as subjectService from '../services/subjectService';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

export default function EditTab({ existingSubjects }) {
    const editState = useEditForm();
    const { selectedQuestion, loadQuestion, clearEdit } = editState;
    const pagination = usePagination();

    // Filters
    const [searchQuery, setSearchQuery] = useState('');
    const [filterSubject, setFilterSubject] = useState('');
    const [filterPaper, setFilterPaper] = useState('');
    const [filterTopic, setFilterTopic] = useState('');
    const [filterStatus, setFilterStatus] = useState('all');
    const [filterType, setFilterType] = useState('all');
    const [availablePapers, setAvailablePapers] = useState([]);
    const [availableTopics, setAvailableTopics] = useState([]);

    const debouncedSearch = useDebounce(searchQuery, 400);
    const endRef = useRef(null);

    // Build API filters
    const buildFilters = useCallback(() => {
        const params = {};
        if (filterSubject) {
            const s = existingSubjects.find(s => s.name === filterSubject);
            if (s?.id) params.subject = s.id;
        }
        if (filterPaper) {
            const p = availablePapers.find(p => p.name === filterPaper);
            if (p?.id) params.paper = p.id;
        }
        if (filterTopic) {
            const t = availableTopics.find(t => t.name === filterTopic);
            if (t?.id) params.topic = t.id;
        }
        if (filterStatus !== 'all') params.isActive = filterStatus === 'active' ? 'true' : 'false';
        if (filterType === 'nested') params.isNested = 'true';
        if (filterType === 'standalone') params.isNested = 'false';
        if (debouncedSearch.length >= 2) params.search = debouncedSearch.trim();
        return params;
    }, [filterSubject, filterPaper, filterTopic, filterStatus, filterType, debouncedSearch, existingSubjects, availablePapers, availableTopics]);

    // Reload when filters change
    useEffect(() => {
        pagination.reset(buildFilters());
    }, [debouncedSearch, filterSubject, filterPaper, filterTopic, filterStatus, filterType]);

    // Subject -> papers
    useEffect(() => {
        if (filterSubject && existingSubjects.length > 0) {
            const s = existingSubjects.find(s => s.name === filterSubject);
            setAvailablePapers(s?.papers || []);
            setFilterPaper('');
            setFilterTopic('');
            setAvailableTopics([]);
        } else {
            setAvailablePapers([]);
            setAvailableTopics([]);
        }
    }, [filterSubject, existingSubjects]);

    // Paper -> topics
    useEffect(() => {
        if (filterPaper && availablePapers.length > 0) {
            const p = availablePapers.find(p => p.name === filterPaper);
            setAvailableTopics(p?.topics || []);
            setFilterTopic('');
        } else {
            setAvailableTopics([]);
        }
    }, [filterPaper, availablePapers]);

    // Fetch topics/sections when a question is selected
    useEffect(() => {
        if (!selectedQuestion?.paper) return;
        const fetchTopics = async () => {
            try {
                const token = localStorage.getItem('token');
                const res = await fetch(`${API_URL}/subjects`, {
                    headers: { 'Authorization': `Bearer ${token}` },
                });
                const data = await res.json();
                const subjects = data.data || [];
                for (const subject of subjects) {
                    const paper = subject.papers?.find(p => p.id === selectedQuestion.paper);
                    if (paper) {
                        editState.setEditQuestionTopics(paper.topics || []);
                        editState.setEditQuestionSections(paper.sections || []);
                        return;
                    }
                }
            } catch (err) {
                console.error('Failed to load topics:', err);
            }
        };
        fetchTopics();
    }, [selectedQuestion?.paper]);

    // Infinite scroll observer
    useEffect(() => {
        const observer = new IntersectionObserver(entries => {
            if (entries[0].isIntersecting && !pagination.isLoadingMore && pagination.hasMore) {
                pagination.fetchPage(pagination.currentPage + 1, buildFilters());
            }
        }, { threshold: 0.1 });
        if (endRef.current) observer.observe(endRef.current);
        return () => { if (endRef.current) observer.unobserve(endRef.current); };
    }, [pagination.isLoadingMore, pagination.currentPage, pagination.hasMore, buildFilters]);

    const handleSelectQuestion = useCallback((q) => {
        loadQuestion(q);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }, [loadQuestion]);

    const handleSaved = useCallback(() => {
        pagination.reset(buildFilters());
    }, [pagination, buildFilters]);

    const handleDeleted = useCallback(() => {
        clearEdit();
        pagination.reset(buildFilters());
    }, [clearEdit, pagination, buildFilters]);

    return (
        <div className="space-y-6">
            {/* Edit form (shown when a question is selected) */}
            {selectedQuestion && (
                <EditForm
                    editState={editState}
                    onSaved={handleSaved}
                    onDeleted={handleDeleted}
                    onCancel={clearEdit}
                />
            )}

            {/* Search and filters */}
            <div className="bg-white rounded-xl shadow-lg p-6">
                <h2 className="text-xl font-bold text-gray-800 mb-4">Search & Edit Questions</h2>
                <EditFilters
                    searchQuery={searchQuery} onSearchChange={setSearchQuery}
                    filterSubject={filterSubject} onSubjectChange={setFilterSubject}
                    filterPaper={filterPaper} onPaperChange={setFilterPaper}
                    filterTopic={filterTopic} onTopicChange={setFilterTopic}
                    filterStatus={filterStatus} onStatusChange={setFilterStatus}
                    filterType={filterType} onTypeChange={setFilterType}
                    existingSubjects={existingSubjects}
                    availablePapers={availablePapers}
                    availableTopics={availableTopics}
                    onClearAll={() => {
                        setSearchQuery('');
                        setFilterSubject('');
                        setFilterPaper('');
                        setFilterTopic('');
                        setFilterStatus('all');
                        setFilterType('all');
                    }}
                />
            </div>

            {/* Question list */}
            <div className="bg-white rounded-xl shadow-lg p-6">
                <p className="text-sm text-gray-600 mb-4">
                    Showing {pagination.paginatedQuestions.length} / {pagination.totalCount} questions
                </p>

                <div className="space-y-3 max-h-[60vh] overflow-y-auto">
                    {pagination.paginatedQuestions.map(q => (
                        <QuestionListItem
                            key={q.id}
                            question={q}
                            isSelected={selectedQuestion?.id === q.id}
                            onClick={handleSelectQuestion}
                        />
                    ))}

                    <div ref={endRef} className="py-4 text-center">
                        {pagination.isLoadingMore && (
                            <div className="flex justify-center items-center gap-2">
                                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600" />
                                <span className="text-gray-600 text-sm">Loading more...</span>
                            </div>
                        )}
                        {!pagination.hasMore && pagination.paginatedQuestions.length > 0 && (
                            <p className="text-sm text-gray-500">All {pagination.paginatedQuestions.length} questions loaded</p>
                        )}
                        {pagination.paginatedQuestions.length === 0 && !pagination.isLoadingMore && (
                            <p className="text-gray-500 text-sm">No questions found. Try adjusting filters.</p>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}