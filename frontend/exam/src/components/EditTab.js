// src/components/EditTab.jsx
import React, { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { unstable_batchedUpdates } from 'react-dom';
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
    const paginationRef = useRef(pagination);

    useEffect(() => {
        paginationRef.current = pagination;
    }); 
    
    const [searchQuery, setSearchQuery]     = useState('');
    const [filterSubject, setFilterSubject] = useState('');
    const [filterPaper, setFilterPaper]     = useState('');
    const [filterTopic, setFilterTopic]     = useState('');
    const [filterStatus, setFilterStatus]   = useState('all');
    const [filterType, setFilterType]       = useState('all');
    const [availablePapers, setAvailablePapers]   = useState([]);
    const [availableTopics, setAvailableTopics]   = useState([]);

    const debouncedSearch = useDebounce(searchQuery, 400);

    
    const stableExistingSubjects = useMemo(
        () => existingSubjects,
        // eslint-disable-next-line react-hooks/exhaustive-deps
        [existingSubjects?.map(s => s.id).join(',')]
    );

    
    const buildFilters = useCallback(() => {
        const params = {};
        if (filterSubject) {
            const s = stableExistingSubjects.find(s => s.name === filterSubject);
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
        if (filterType === 'nested')     params.isNested = 'true';
        if (filterType === 'standalone') params.isNested = 'false';
        if (debouncedSearch.length >= 2) params.search = debouncedSearch.trim();
        return params;
    }, [
        filterSubject, filterPaper, filterTopic,
        filterStatus, filterType, debouncedSearch,
        stableExistingSubjects, availablePapers, availableTopics,
    ]);

    
    useEffect(() => {
        paginationRef.current.reset(buildFilters());
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [debouncedSearch, filterSubject, filterPaper, filterTopic, filterStatus, filterType]);

    
    useEffect(() => {
        if (filterSubject && stableExistingSubjects.length > 0) {
            const s = stableExistingSubjects.find(s => s.name === filterSubject);
            setAvailablePapers(s?.papers || []);
            setFilterPaper('');
            setFilterTopic('');
            setAvailableTopics([]);
        } else {
            setAvailablePapers([]);
            setAvailableTopics([]);
        }
    }, [filterSubject, stableExistingSubjects]);

    // Paper → topics cascade
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
    }, [selectedQuestion?.paper]); // eslint-disable-line react-hooks/exhaustive-deps

    
    const memoizedFilters = useRef(buildFilters());
    useEffect(() => {
        memoizedFilters.current = buildFilters();
    }, [buildFilters]);

    
    const listRef                   = useRef(null);
    const pendingScrollRestoreRef   = useRef(null);
    const scrollTimerRef            = useRef(null);
    const suppressScrollRef         = useRef(false);
    const lastScrollTopRef          = useRef(0);
    // Guard: skip scroll-triggered page loads while a form save/delete is running
    const formOperationInProgressRef = useRef(false);

    const handleListScroll = useCallback(() => {
        if (scrollTimerRef.current) return;
        if (suppressScrollRef.current) return;
        if (formOperationInProgressRef.current) return;

        scrollTimerRef.current = setTimeout(() => {
            scrollTimerRef.current = null;
            const container = listRef.current;
            const pg = paginationRef.current;
            if (!container || pg.isLoadingMore) return;

            // Batch DOM reads to prevent layout thrashing
            const currentScrollTop = container.scrollTop;
            const clientHeight     = container.clientHeight;
            const scrollHeight     = container.scrollHeight;

            const scrollingDown = currentScrollTop > lastScrollTopRef.current;
            const scrollingUp   = currentScrollTop < lastScrollTopRef.current;
            lastScrollTopRef.current = currentScrollTop;

            const nearTop    = currentScrollTop <= 80;
            const nearBottom = currentScrollTop + clientHeight >= scrollHeight - 80;

            if (nearBottom && scrollingDown && pg.hasMore) {
                pendingScrollRestoreRef.current = 'top';
                pg.fetchPage(pg.currentPage + 1, memoizedFilters.current);
                return;
            }

            if (nearTop && scrollingUp && pg.currentPage > 1) {
                pendingScrollRestoreRef.current = 'bottom';
                pg.fetchPage(pg.currentPage - 1, memoizedFilters.current);
            }
        }, 150);
    }, []); // no deps — reads everything through stable refs

    // Restore scroll position after a page flip
    useEffect(() => {
        const container = listRef.current;
        const pending   = pendingScrollRestoreRef.current;
        if (!container || !pending) return;

        suppressScrollRef.current = true;
        if (scrollTimerRef.current) {
            clearTimeout(scrollTimerRef.current);
            scrollTimerRef.current = null;
        }

        requestAnimationFrame(() => {
            if (pending === 'top') {
                container.scrollTop = 0;
            } else if (pending === 'bottom') {
                container.scrollTop = container.scrollHeight;
            }
            lastScrollTopRef.current = pendingScrollRestoreRef.current = null;

            requestAnimationFrame(() => {
                suppressScrollRef.current = false;
            });
        });
    }, [pagination.currentPage, pagination.paginatedQuestions.length]);

    // Cleanup scroll timer on unmount
    useEffect(() => {
        return () => {
            if (scrollTimerRef.current) clearTimeout(scrollTimerRef.current);
        };
    }, []);

   
    const handleSelectQuestion = useCallback((q) => {
        unstable_batchedUpdates(() => {
            loadQuestion(q);
        });
        // Instant scroll (no smooth) to avoid additional main-thread work
        window.scrollTo({ top: 0, behavior: 'auto' });
    }, [loadQuestion]);

    // After a successful save: patch the item in-place rather than resetting
    // the whole list, then clear the edit form.
    const handleSaved = useCallback((updatedQuestion) => {
        formOperationInProgressRef.current = true;
        try {
            if (updatedQuestion?.id && paginationRef.current.replaceQuestionInPage) {
                paginationRef.current.replaceQuestionInPage(updatedQuestion);
                clearEdit();
                return;
            }
            // Fallback: full reset (e.g. server didn't return the updated object)
            paginationRef.current.reset(memoizedFilters.current);
            clearEdit();
        } finally {
            requestAnimationFrame(() => {
                formOperationInProgressRef.current = false;
            });
        }
    }, [clearEdit]);

    const handleDeleted = useCallback((deletedId) => {
        formOperationInProgressRef.current = true;
        try {
            if (deletedId && paginationRef.current.removeQuestionFromPage) {
                paginationRef.current.removeQuestionFromPage(deletedId);
                clearEdit();
                return;
            }
            clearEdit();
            paginationRef.current.reset(memoizedFilters.current);
        } finally {
            requestAnimationFrame(() => {
                formOperationInProgressRef.current = false;
            });
        }
    }, [clearEdit]);

    const handleClearAllFilters = useCallback(() => {
        unstable_batchedUpdates(() => {
            setSearchQuery('');
            setFilterSubject('');
            setFilterPaper('');
            setFilterTopic('');
            setFilterStatus('all');
            setFilterType('all');
        });
    }, []);

    return (
        <div className="space-y-6">
            {/* Edit form — only mounted while a question is selected */}
            {selectedQuestion && (
                <EditForm
                    editState={editState}
                    onSaved={handleSaved}
                    onDeleted={handleDeleted}
                    onCancel={clearEdit}
                />
            )}

            {/* Filters */}
            <div className="bg-white rounded-xl shadow-lg p-6">
                <h2 className="text-xl font-bold text-gray-800 mb-4">Search & Edit Questions</h2>
                <EditFilters
                    searchQuery={searchQuery}       onSearchChange={setSearchQuery}
                    filterSubject={filterSubject}   onSubjectChange={setFilterSubject}
                    filterPaper={filterPaper}       onPaperChange={setFilterPaper}
                    filterTopic={filterTopic}       onTopicChange={setFilterTopic}
                    filterStatus={filterStatus}     onStatusChange={setFilterStatus}
                    filterType={filterType}         onTypeChange={setFilterType}
                    existingSubjects={stableExistingSubjects}
                    availablePapers={availablePapers}
                    availableTopics={availableTopics}
                    onClearAll={handleClearAllFilters}
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
                                <span className="text-gray-600 text-sm">Loading page…</span>
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