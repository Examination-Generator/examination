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

    useEffect(() => {
        paginatedRef.current = paginatedQuestions;
    }, [paginatedQuestions]);

    const fetchPage = useCallback(async (pageNum = 1, filters = {}) => {
        const targetPage = Math.max(1, Number(pageNum) || 1);

        
        if (abortControllerRef.current) {
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

            setPaginatedQuestions(questions);
            setHasMore(derivedHasMore);
            setCurrentPage(targetPage);
            currentPageRef.current = targetPage;
            paginatedRef.current = questions;

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

    const reset = useCallback((filters = {}) => {
        
        if (abortControllerRef.current) {
            abortControllerRef.current.abort();
        }

        setPaginatedQuestions([]);
        setCurrentPage(1);
        setHasMore(true);
        setIsLoadingMore(false);
        currentPageRef.current = 0;
        inFlightRef.current = false;
        paginatedRef.current = [];

        fetchPage(1, filters);
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
        reset,
        paginatedRef,
        inFlightRef,
        currentPageRef,
    };
}