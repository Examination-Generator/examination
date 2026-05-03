// src/hooks/usePagination.js
import { useState, useRef, useCallback } from 'react';
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

    useRef(() => {
        paginatedRef.current = paginatedQuestions;
    }, [paginatedQuestions]);

    const mergeUnique = (base, incoming) => {
        const map = new Map();
        [...base, ...incoming].forEach((q, i) => {
            const key = q?.id ? String(q.id) : `idx-${i}`;
            map.set(key, q);
        });
        return Array.from(map.values());
    };

    const fetchPage = useCallback(async (pageNum = 1, filters = {}) => {
        if (inFlightRef.current) return [];
        if (pageNum > 1 && pageNum <= currentPageRef.current) return [];

        try {
            inFlightRef.current = true;
            setIsLoadingMore(true);

            const params = {
                page: pageNum,
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

            const previous = pageNum === 1 ? [] : paginatedRef.current;
            const merged = mergeUnique(previous, questions);

            const derivedHasMore =
                pagination.has_next === true ||
                (serverTotal > 0 && merged.length < serverTotal);

            setPaginatedQuestions(merged);
            setHasMore(derivedHasMore);
            setCurrentPage(pageNum);
            currentPageRef.current = pageNum;
            paginatedRef.current = merged;

            return questions;
        } catch (err) {
            console.error('Pagination error:', err);
            if (pageNum === 1) setPaginatedQuestions([]);
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