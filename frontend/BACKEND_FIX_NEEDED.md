# Backend Fix Required for Biology Paper 2 Generation

## Error
```
null value in column "selected_topics" of relation "generated_papers" violates not-null constraint
```

## Issue
The `BiologyPaper2Generator.save_generated_paper()` method is not setting the `selected_topics` field when creating the `GeneratedPaper` object.

## Fix Required in `biology_paper2_generation.py`

### Current Code (around line 280):
```python
# Create GeneratedPaper
generated_paper = GeneratedPaper.objects.create(
    paper=self.paper,
    total_marks=self.TOTAL_MARKS,
    total_questions=self.TOTAL_QUESTIONS,
    question_ids=list(self.used_question_ids),
    metadata={
        'paper_type': 'Biology Paper 2',
        # ... rest of metadata
    }
)
```

### Fixed Code:
```python
# Create GeneratedPaper
generated_paper = GeneratedPaper.objects.create(
    paper=self.paper,
    total_marks=self.TOTAL_MARKS,
    total_questions=self.TOTAL_QUESTIONS,
    question_ids=list(self.used_question_ids),
    selected_topics=self.selected_topic_ids,  # ADD THIS LINE
    metadata={
        'paper_type': 'Biology Paper 2',
        'generation_algorithm': 'BiologyPaper2Generator',
        'section_a_questions': self.SECTION_A_QUESTIONS,
        'section_a_marks_per_question': self.SECTION_A_MARKS_PER_QUESTION,
        'section_b_questions': self.SECTION_B_QUESTIONS,
        'section_b_marks_per_question': self.SECTION_B_MARKS_PER_QUESTION,
        'question_6_type': question_6_type,
        'topic_distribution': dict(self.topic_distribution),
        'selected_topics': [str(t.id) for t in self.topics],
        'question_order': [
            {
                'question_number': idx + 1,
                'question_id': str(q.id),
                'section': 'A' if idx < 5 else 'B',
                'type': question_6_type if idx == 5 else ('essay' if idx > 5 else 'structured'),
                'marks': q.marks,
                'topic': q.topic.name
            }
            for idx, q in enumerate(all_questions)
        ]
    }
)
```

## Summary
Add `selected_topics=self.selected_topic_ids` to the `GeneratedPaper.objects.create()` call in the `save_generated_paper()` method.

The `selected_topic_ids` is already available as `self.selected_topic_ids` in the class from the constructor.
