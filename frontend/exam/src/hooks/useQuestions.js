import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import * as questionService from '../services/questionService';

// Hook for searching questions with filters
export function useSearchQuestions(searchQuery, filters, enabled = true) {
  return useQuery({
    queryKey: ['questions', 'search', searchQuery, filters],
    queryFn: async () => {
      if (!searchQuery || searchQuery.length < 2) return [];
      
      const allQuestions = await questionService.getAllQuestions({ limit: 10000 });
      
      // Apply filters (your existing logic)
      let filtered = [...allQuestions];
      
      // Text search
      if (searchQuery.trim().length >= 2) {
        const searchTerm = searchQuery.toLowerCase().trim();
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
      if (filters.editFilterSubject) {
        filtered = filtered.filter(q => q.subject_name === filters.editFilterSubject);
      }
      
      // Add other filters...
      
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