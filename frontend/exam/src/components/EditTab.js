// src/components/EditTab.jsx
import React, { useState, useEffect, useCallback, useRef } from 'react';
import EditFilters from './EditFilters';
import EditForm from './EditForm';
import QuestionListItem from './QuestionListItem';
import { useEditForm } from '../hooks/useEditForm';
import { usePagination } from '../hooks/usePagination';
import { useDebounce } from '../hooks/useDebounce';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

export default function EditTab({ existingSubjects }) {
    const editState = useEditForm();
    const { selectedQuestion, loadQuestion, clearEdit } = editState;
    const pagination = usePagination();

    // FIX: Keep a ref to the latest pagination object so callbacks can call
    // pagination.reset() / pagination.fetchPage() without adding `pagination`
    // itself to their dependency arrays. Adding the pagination object to deps
    // caused an infinite loop because the object is recreated every render.
    const paginationRef = useRef(pagination);
    useEffect(() => {
        paginationRef.current = pagination;
    }); // no dep array — runs after every render to stay current

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
    const listRef = useRef(null);
    const pendingScrollRestoreRef = useRef(null);
    const scrollTimerRef = useRef(null); 
    const suppressScrollRef = useRef(false);
    const lastScrollTopRef = useRef(0);
    
    // Build API filters — stable as long as its own deps don't change
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

    
    useEffect(() => {
        paginationRef.current.reset(buildFilters());
    }, [debouncedSearch, filterSubject, filterPaper, filterTopic, filterStatus, filterType, buildFilters]);

    // Subject -> papers cascade
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

    // Paper -> topics cascade
    useEffect(() => {
        if (filterPaper && availablePapers.length > 0) {
            const p = availablePapers.find(p => p.name === filterPaper);
            setAvailableTopics(p?.topics || []);
            setFilterTopic('');
        } else {
            setAvailableTopics([]);
        }
    }, [filterPaper, availablePapers]);

    
    useEffect(() => {
        if (!selectedQuestion?.paper) return;

        const controller = new AbortController();
        const { signal } = controller;

        const fetchTopics = async () => {
            try {
                const token = localStorage.getItem('token');
                const res = await fetch(`${API_URL}/subjects`, {
                    headers: { 'Authorization': `Bearer ${token}` },
                    signal,
                });
                if (signal.aborted) return;

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
                if (err.name !== 'AbortError') console.error('Failed to load topics:', err);
            }
        };

        fetchTopics();
        return () => controller.abort();
    }, [selectedQuestion?.paper]); 
    const handleListScroll = useCallback(() => {
        if (scrollTimerRef.current) return;
        if (suppressScrollRef.current) return;

        scrollTimerRef.current = setTimeout(() => {
            scrollTimerRef.current = null;
            const container = listRef.current;
            const pg = paginationRef.current;
            if (!container || pg.isLoadingMore) return;

            const currentScrollTop = container.scrollTop;
            const scrollingDown = currentScrollTop > lastScrollTopRef.current;
            const scrollingUp = currentScrollTop < lastScrollTopRef.current;
            lastScrollTopRef.current = currentScrollTop;

            const nearTop = container.scrollTop <= 80;
            const nearBottom = container.scrollTop + container.clientHeight >= container.scrollHeight - 80;

            if (nearBottom && scrollingDown && pg.hasMore) {
                pendingScrollRestoreRef.current = 'top';
                pg.fetchPage(pg.currentPage + 1, buildFilters());
                return;
            }

            if (nearTop && scrollingUp && pg.currentPage > 1) {
                pendingScrollRestoreRef.current = 'bottom';
                pg.fetchPage(pg.currentPage - 1, buildFilters());
            }
        }, 150);
    }, [buildFilters]); 

    
    useEffect(() => {
        const container = listRef.current;
        const pending = pendingScrollRestoreRef.current;
        if (!container || !pending) return;

        suppressScrollRef.current = true;
        if (scrollTimerRef.current) {
            clearTimeout(scrollTimerRef.current);
            scrollTimerRef.current = null;
        }

        if (pending === 'top') {
            container.scrollTop = 0;
        } else if (pending === 'bottom') {
            container.scrollTop = container.scrollHeight;
        }
        lastScrollTopRef.current = container.scrollTop;
        pendingScrollRestoreRef.current = null;

        const release = window.requestAnimationFrame(() => {
            suppressScrollRef.current = false;
        });

        return () => window.cancelAnimationFrame(release);
    }, [pagination.currentPage, pagination.paginatedQuestions.length]);

    
    useEffect(() => {
        return () => {
            if (scrollTimerRef.current) clearTimeout(scrollTimerRef.current);
        };
    }, []);

    const handleSelectQuestion = useCallback((q) => {
        loadQuestion(q);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }, [loadQuestion]);

    
    const handleSaved = useCallback((updatedQuestion) => {
        if (updatedQuestion?.id && paginationRef.current.replaceQuestionInPage) {
            paginationRef.current.replaceQuestionInPage(updatedQuestion);
            return;
        }
        paginationRef.current.reset(buildFilters());
    }, [buildFilters]);

    const handleDeleted = useCallback((deletedId) => {
        clearEdit();
        if (deletedId && paginationRef.current.removeQuestionFromPage) {
            paginationRef.current.removeQuestionFromPage(deletedId);
            return;
        }
        paginationRef.current.reset(buildFilters());
    }, [clearEdit, buildFilters]);

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

                <div
                    ref={listRef}
                    onScroll={handleListScroll}
                    className="space-y-3 max-h-[60vh] overflow-y-auto"
                >
                    {pagination.paginatedQuestions.map(q => (
                        <QuestionListItem
                            key={q.id}
                            question={q}
                            isSelected={selectedQuestion?.id === q.id}
                            onClick={handleSelectQuestion}
                        />
                    ))}

                    {pagination.isLoadingMore && (
                        <div className="py-4 text-center">
                            <div className="flex justify-center items-center gap-2">
                                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600" />
                                <span className="text-gray-600 text-sm">Loading page...</span>
                            </div>
                        </div>
                    )}
                    {pagination.paginatedQuestions.length === 0 && !pagination.isLoadingMore && (
                        <div className="py-4 text-center">
                            <p className="text-gray-500 text-sm">No questions found. Try adjusting filters.</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}