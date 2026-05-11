// src/components/EditTab.jsx
import React, { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { unstable_batchedUpdates } from 'react-dom';
import EditFilters from './EditFilters';
import EditForm from './EditForm';
import QuestionListItem from './QuestionListItem';
import { useEditForm } from '../hooks/useEditForm';
import { usePagination } from '../hooks/usePagination';
import { useDebounce } from '../hooks/useDebounce';

export default function EditTab({ existingSubjects }) {
    const editState = useEditForm();
    const { selectedQuestion, loadQuestion, clearEdit } = editState;
    const pagination = usePagination();

    // Keep a ref to the latest pagination object so scroll/save callbacks
    // can reach it without listing `pagination` in their dep arrays
    // (which caused infinite loops because the object recreates every render).
    const paginationRef = useRef(pagination);
    useEffect(() => {
        paginationRef.current = pagination;
    }); // intentionally no dep array — must stay current after every render

    // -------------------------------------------------------------------------
    // Filter state
    // -------------------------------------------------------------------------
    const [searchQuery, setSearchQuery]     = useState('');
    const [filterSubject, setFilterSubject] = useState('');
    const [filterPaper, setFilterPaper]     = useState('');
    const [filterTopic, setFilterTopic]     = useState('');
    const [filterStatus, setFilterStatus]   = useState('all');
    const [filterType, setFilterType]       = useState('all');
    const [availablePapers, setAvailablePapers] = useState([]);
    const [availableTopics, setAvailableTopics] = useState([]);

    const debouncedSearch = useDebounce(searchQuery, 400);

    // -------------------------------------------------------------------------
    // FIX A — Stabilise existingSubjects reference.
    //
    // The parent re-renders for its own reasons and passes a new array instance
    // each time even when subjects haven't changed. Without this, buildFilters
    // gets a new identity on every parent render which caused the memoizedFilters
    // ref to fall out of sync — reset() would then be called with stale (empty)
    // filters, fetching ALL questions unfiltered and freezing the browser while
    // React rendered thousands of list items.
    // -------------------------------------------------------------------------
    const stableExistingSubjects = useMemo(
        () => existingSubjects,
        // eslint-disable-next-line react-hooks/exhaustive-deps
        [existingSubjects?.map(s => s.id).join(',')]
    );

    // -------------------------------------------------------------------------
    // buildFilters — computes the API params object from current filter state.
    // Stable as long as the filter primitive values don't change.
    // -------------------------------------------------------------------------
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

    // -------------------------------------------------------------------------
    // FIX B — Store buildFilters in a ref so it is always called at point-of-use.
    //
    // The previous version stored buildFilters() RESULT in a ref, initialised at
    // mount when no filters were set (= {}). If the update effect hadn't fired
    // before handleSaved ran the fallback reset(), it called reset({}) which
    // fetched ALL questions — potentially thousands of rows — freezing the
    // browser while React tried to render them all.
    //
    // Storing the FUNCTION instead means every call always uses the current
    // closure with no async-effect lag between filter state and what gets fetched.
    // -------------------------------------------------------------------------
    const buildFiltersRef = useRef(buildFilters);
    useEffect(() => {
        buildFiltersRef.current = buildFilters;
    }); // intentionally no dep array — mirrors paginationRef pattern

    // Always returns current filter params at call time — safe to use anywhere.
    const getCurrentFilters = useCallback(() => buildFiltersRef.current(), []);

    // -------------------------------------------------------------------------
    // FIX C — Pagination reset only fires when filter VALUES change, never when
    // buildFilters' function identity changes due to parent re-renders.
    //
    // The original code listed `buildFilters` in this effect's dep array. That
    // caused a full list reset every time the parent re-rendered (even with no
    // filter change), because existingSubjects got a new array reference which
    // flowed through to buildFilters' identity. Removing it and using the
    // primitive filter state vars as the true deps fixes this.
    // -------------------------------------------------------------------------
    useEffect(() => {
        paginationRef.current.reset(buildFiltersRef.current());
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [debouncedSearch, filterSubject, filterPaper, filterTopic, filterStatus, filterType]);

    // -------------------------------------------------------------------------
    // Subject → papers cascade
    // -------------------------------------------------------------------------
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

    // -------------------------------------------------------------------------
    // FIX D — Topics/sections for the selected question: use cached data.
    //
    // The original code made a fresh GET /api/subjects network request on every
    // question selection. This had two serious problems:
    //
    //   1. Race condition: selecting Q1, then quickly selecting Q2 before the
    //      Q1 fetch resolved caused the Q1 response to call setEditQuestionTopics
    //      with Q1's topics after Q2 had already loaded — silently populating the
    //      topic dropdown with the wrong question's topics.
    //
    //   2. The fetch was completely unnecessary. existingSubjects (passed as a
    //      prop from EditorDashboard) already contains the full subject/paper/
    //      topic tree. There is no reason to re-fetch it on every question click.
    //
    // Fix: look up topics synchronously from stableExistingSubjects. Instant,
    // no network, no race condition possible.
    // -------------------------------------------------------------------------
    useEffect(() => {
        if (!selectedQuestion?.paper) {
            editState.setEditQuestionTopics([]);
            editState.setEditQuestionSections([]);
            return;
        }

        for (const subject of stableExistingSubjects) {
            const paper = subject.papers?.find(p => p.id === selectedQuestion.paper);
            if (paper) {
                editState.setEditQuestionTopics(paper.topics || []);
                editState.setEditQuestionSections(paper.sections || []);
                return;
            }
        }

        // Paper not found in cached data — clear dropdowns to avoid stale values
        editState.setEditQuestionTopics([]);
        editState.setEditQuestionSections([]);

    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [selectedQuestion?.paper, stableExistingSubjects]);

    // -------------------------------------------------------------------------
    // Scroll handling
    // -------------------------------------------------------------------------
    const listRef                    = useRef(null);
    const pendingScrollRestoreRef    = useRef(null);
    const scrollTimerRef             = useRef(null);
    const suppressScrollRef          = useRef(false);
    const lastScrollTopRef           = useRef(0);
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
                pg.fetchPage(pg.currentPage + 1, getCurrentFilters(), true); // true = scroll-initiated
                return;
            }

            if (nearTop && scrollingUp && pg.currentPage > 1) {
                pendingScrollRestoreRef.current = 'bottom';
                pg.fetchPage(pg.currentPage - 1, getCurrentFilters(), true); // true = scroll-initiated
            }
        }, 150);
    }, [getCurrentFilters]);

    // -------------------------------------------------------------------------
    // Scroll handling: CRITICAL - only restore scroll when ACTUAL page flip occurs
    //
    // Previous version had dependency on [pagination.currentPage, pagination.paginatedQuestions.length]
    // which caused the effect to fire on EVERY list update (e.g., replaceQuestionInPage).
    // This triggered unnecessary DOM writes even when the page number didn't change,
    // blocking the main thread and causing the freeze.
    //
    // Fix: Track the previous page number. Only run scroll restoration when it actually changes.
    // -------------------------------------------------------------------------
    const prevPageRef = useRef(pagination.currentPage);
    
    useEffect(() => {
        const hasPageChanged = pagination.currentPage !== prevPageRef.current;
        prevPageRef.current = pagination.currentPage;

        if (!hasPageChanged) return;

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
            lastScrollTopRef.current = container.scrollTop;
            pendingScrollRestoreRef.current = null;

            requestAnimationFrame(() => {
                suppressScrollRef.current = false;
            });
        });
    }, [pagination.currentPage]);

    useEffect(() => {
        return () => {
            if (scrollTimerRef.current) clearTimeout(scrollTimerRef.current);
        };
    }, []);

    // -------------------------------------------------------------------------
    // FIX E — Select a question: batch all state updates into one render.
    // -------------------------------------------------------------------------
    const handleSelectQuestion = useCallback((q) => {
        unstable_batchedUpdates(() => {
            loadQuestion(q);
        });
        window.scrollTo({ top: 0, behavior: 'auto' });
    }, [loadQuestion]);

    // -------------------------------------------------------------------------
    // After save: patch the item in the list in-place, then clear the form.
    //
    // reset() is intentionally NOT called here. Calling reset() risked fetching
    // all questions when getCurrentFilters() could still be stale. Patching
    // in-place is faster, correct, and requires no network round-trip.
    // If the API didn't return the updated question, we still clear the form —
    // a momentarily stale list item is far preferable to a browser freeze.
    // -------------------------------------------------------------------------
    const handleSaved = useCallback((updatedQuestion) => {
        formOperationInProgressRef.current = true;
        unstable_batchedUpdates(() => {
            if (updatedQuestion?.id) {
                paginationRef.current.replaceQuestionInPage(updatedQuestion);
            }
            clearEdit();
        });
        requestAnimationFrame(() => {
            formOperationInProgressRef.current = false;
        });
    }, [clearEdit]);

    const handleDeleted = useCallback((deletedId) => {
        formOperationInProgressRef.current = true;
        unstable_batchedUpdates(() => {
            if (deletedId) {
                paginationRef.current.removeQuestionFromPage(deletedId);
            }
            clearEdit();
        });
        requestAnimationFrame(() => {
            formOperationInProgressRef.current = false;
        });
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

    // -------------------------------------------------------------------------
    // Render
    // -------------------------------------------------------------------------
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