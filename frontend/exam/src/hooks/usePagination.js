
import { useState, useRef, useCallback, useEffect } from 'react';
import * as questionService from '../services/questionService';

export function usePagination() {
    const [paginatedQuestions, setPaginatedQuestions] = useState([]);
    const [currentPage, setCurrentPage] = useState(1);
    const [isLoadingMore, setIsLoadingMore] = useState(false);
    const [hasMore, setHasMore] = useState(true);
    const [totalCount, setTotalCount] = useState(0);

    const inFlightRef = useRef(false);
    const currentPageRef = useRef(1);
    const paginatedRef = useRef([]);
    const hasNextRef = useRef(false);
    const lastReturnedRef = useRef(0);
    const dbTotalRef = useRef(0);

    useEffect(() => {
        paginatedRef.current = paginatedQuestions;
    }, [paginatedQuestions]);

    const fetchPage = useCallback(async (pageNum = 1, filters = {}) => {
        const targetPage = Math.max(1, Number(pageNum) || 1);

        if (inFlightRef.current) return [];
        if (targetPage === currentPageRef.current && paginatedRef.current.length > 0) {
            return paginatedRef.current;
        }

        try {
            inFlightRef.current = true;
            setIsLoadingMore(true);

            const params = {
                page: targetPage,
                limit: 50,
                ...filters,
            };
            Object.keys(params).forEach(k => params[k] === undefined && delete params[k]);

            const result = await questionService.getPaginatedQuestions(params);
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
            console.error('Pagination error:', err);
            if (targetPage === 1) setPaginatedQuestions([]);
            return [];
        } finally {
            setIsLoadingMore(false);
            inFlightRef.current = false;
        }
    }, []);

    const reset = useCallback((filters = {}) => {
        setPaginatedQuestions([]);
        setCurrentPage(1);
        setHasMore(true);
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