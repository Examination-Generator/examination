import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import * as questionService from '../services/questionService';

// Hook for searching questions with filters
export function useSearchQuestions(searchQuery, filters, enabled = true) {
  return useQuery({
    queryKey: ['questions', 'search', searchQuery, filters],
    queryFn: async () => {
      if (!searchQuery || searchQuery.length < 2) return [];
      
      const allQuestions = await questionService.getAllQuestions({ limit: 10000 });
      
      // Apply filters
      let filtered = Array.isArray(allQuestions) ? [...allQuestions] : [];

      const searchTerm = searchQuery && searchQuery.trim().length >= 2 ? searchQuery.toLowerCase().trim() : null;
      if (searchTerm) {
        filtered = filtered.filter(q => {
          const searchableText = [
            q.question_text || '',
            q.answer_text || '',
            q.subject_name || '',
            q.topic_name || ''
          ].join(' ').toLowerCase();
          return searchableText.includes(searchTerm);
        });
      }

      // Subject filter
      if (filters?.editFilterSubject) {
        filtered = filtered.filter(q => q.subject_name === filters.editFilterSubject);
      }

      // Paper filter
      if (filters?.editFilterPaper) {
        filtered = filtered.filter(q => q.paper_name === filters.editFilterPaper);
      }

      // Topic filter
      if (filters?.editFilterTopic) {
        filtered = filtered.filter(q => q.topic_name === filters.editFilterTopic);
      }

      // Status filter
      if (filters?.editFilterStatus && filters.editFilterStatus !== 'all') {
        if (filters.editFilterStatus === 'active') {
          filtered = filtered.filter(q => q.is_active !== false);
        } else if (filters.editFilterStatus === 'inactive') {
          filtered = filtered.filter(q => q.is_active === false);
        }
      }

      // Type filter (nested/standalone/essay/graph etc.)
      if (filters?.editFilterType && filters.editFilterType !== 'all') {
        if (filters.editFilterType === 'nested') filtered = filtered.filter(q => q.is_nested === true);
        if (filters.editFilterType === 'standalone') filtered = filtered.filter(q => q.is_nested !== true);
        if (filters.editFilterType === 'essay') filtered = filtered.filter(q => q.is_essay_question === true || q.is_essay === true);
        if (filters.editFilterType === 'graph') filtered = filtered.filter(q => q.is_graph_question === true || q.is_graph === true);
      }

      return filtered;
    },
    enabled: enabled && searchQuery.length >= 2,
    staleTime: 5 * 60 * 1000,
  });
}

// Hook for getting single question details
export function useQuestionDetails(questionId) {
  return useQuery({
    queryKey: ['questions', questionId],
    queryFn: () => questionService.getQuestionById(questionId),
    enabled: !!questionId,
  });
}

// Hook for updating a question
export function useUpdateQuestion() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }) => questionService.updateQuestion(id, data),
    onSuccess: () => {
      // Invalidate and refetch
      queryClient.invalidateQueries(['questions']);
    },
  });
}