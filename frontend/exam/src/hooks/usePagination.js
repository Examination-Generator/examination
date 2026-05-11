import { useState, useRef, useCallback, useEffect } from 'react';
import * as questionService from '../services/questionService';

export function usePagination() {
    const [paginatedQuestions, setPaginatedQuestions] = useState([]);
    const [currentPage, setCurrentPage] = useState(1);
    const [isLoadingMore, setIsLoadingMore] = useState(false);
    const [hasMore, setHasMore] = useState(true);
    const [totalCount, setTotalCount] = useState(0);

    // Internal refs — never cause re-renders
    const inFlightRef = useRef(false);
    const currentPageRef = useRef(1);
    const paginatedRef = useRef([]);
    const hasNextRef = useRef(false);
    const lastReturnedRef = useRef(0);
    const dbTotalRef = useRef(0);


    const abortControllerRef = useRef(null);
    // Track if current fetch is scroll-initiated (pagination navigation)
    // vs filter-initiated (reset). Prevents filter resets from aborting scrolls.
    const isScrollInitiatedRef = useRef(false);

    useEffect(() => {
        paginatedRef.current = paginatedQuestions;
    }, [paginatedQuestions]);

    const fetchPage = useCallback(async (pageNum = 1, filters = {}, isScrollFetch = false) => {
        const targetPage = Math.max(1, Number(pageNum) || 1);

        // Mark whether this is a scroll-initiated fetch
        isScrollInitiatedRef.current = isScrollFetch;

        // Only abort previous request if this is NOT a scroll fetch
        // (scroll fetches should complete to maintain bidirectional pagination)
        if (!isScrollFetch && abortControllerRef.current) {
            abortControllerRef.current.abort();
        }
        const controller = new AbortController();
        abortControllerRef.current = controller;
        const { signal } = controller;

        try {
            inFlightRef.current = true;
            setIsLoadingMore(true);

            const params = {
                page: targetPage,
                limit: 50,
                ...filters,
            };
            Object.keys(params).forEach(k => params[k] === undefined && delete params[k]);

            const result = await questionService.getPaginatedQuestions(params, signal);

            
            if (signal.aborted) return [];

            const questions = Array.isArray(result?.questions) ? result.questions : [];
            const pagination = result?.pagination || {};

            hasNextRef.current = !!pagination.has_next;
            lastReturnedRef.current = questions.length;

            const serverTotal = Number(pagination.total || 0);
            if (serverTotal > 0) {
                dbTotalRef.current = serverTotal;
                setTotalCount(serverTotal);
            }

            const derivedHasMore =
                pagination.has_next === true ||
                (serverTotal > 0 && targetPage * 50 < serverTotal);

            // Update refs first (no render)
            currentPageRef.current = targetPage;
            paginatedRef.current = questions;

            // Batch state updates - React will batch these into single render
            setPaginatedQuestions(questions);
            setHasMore(derivedHasMore);
            setCurrentPage(targetPage);
            if (serverTotal > 0) {
                setTotalCount(serverTotal);
            }

            return questions;
        } catch (err) {
            
            if (err.name === 'AbortError') return [];
            console.error('Pagination error:', err);
            if (targetPage === 1) setPaginatedQuestions([]);
            return [];
        } finally {
            
            if (!signal.aborted) {
                setIsLoadingMore(false);
                inFlightRef.current = false;
            }
        }
    }, []);

    const replaceQuestionInPage = useCallback((updatedQuestion) => {
        if (!updatedQuestion?.id) return;

        setPaginatedQuestions(prev => {
            const next = prev.map(question => (
                question?.id === updatedQuestion.id ? updatedQuestion : question
            ));
            paginatedRef.current = next;
            return next;
        });
    }, []);

    const removeQuestionFromPage = useCallback((questionId) => {
        if (!questionId) return;

        setPaginatedQuestions(prev => {
            const next = prev.filter(question => question?.id !== questionId);
            paginatedRef.current = next;
            return next;
        });
    }, []);

    const reset = useCallback((filters = {}) => {
        // Don't abort scroll-initiated fetches - let them complete naturally
        // This prevents filter changes from interrupting pagination navigation
        if (!isScrollInitiatedRef.current && abortControllerRef.current) {
            abortControllerRef.current.abort();
        }

        setPaginatedQuestions([]);
        setCurrentPage(1);
        setHasMore(true);
        setIsLoadingMore(false);
        currentPageRef.current = 0;
        inFlightRef.current = false;
        paginatedRef.current = [];

        fetchPage(1, filters, false); // false = not a scroll fetch
    }, [fetchPage]);

    return {
        paginatedQuestions,
        currentPage,
        isLoadingMore,
        hasMore,
        totalCount,
        dbTotal: dbTotalRef.current,
        hasNextRef,
        lastReturnedRef,
        fetchPage,
        replaceQuestionInPage,
        removeQuestionFromPage,
        reset,
        paginatedRef,
        inFlightRef,
        currentPageRef,
    };
}