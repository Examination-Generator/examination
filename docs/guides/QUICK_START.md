# Quick Start Guide - KCSE Paper Generation

## ✅ System Setup Complete!

The KCSE Biology Paper 1 generation system has been successfully implemented and the database has been migrated.

## 🚀 Getting Started

### Step 1: Create Biology Subject and Paper

Use the existing API or Django admin to create:

```python
# Via Django shell (python manage.py shell)
from api.models import Subject, Paper, Topic, User

# Get admin user
admin = User.objects.filter(role='admin').first()

# Create Biology subject
biology = Subject.objects.create(
    name="Biology",
    description="KCSE Biology examination",
    created_by=admin
)

# Create Paper 1
paper1 = Paper.objects.create(
    name="Paper 1",
    subject=biology,
    description="Biology Paper 1 - 2 hours, 80 marks",
    total_marks=80,
    time_allocation=120,  # minutes
    created_by=admin
)

print(f"✓ Created {paper1}")
```

### Step 2: Create Topics with Mark Constraints

```python
# Biology Paper 1 topics with KCSE standard mark allocations
topics_data = [
    ("Cell Biology", 6, 8),
    ("Classification", 4, 6),
    ("Nutrition", 8, 10),
    ("Respiration", 6, 8),
    ("Transport", 6, 8),
    ("Excretion and Homeostasis", 6, 8),
    ("Gaseous Exchange", 5, 7),
    ("Reproduction", 8, 10),
    ("Growth and Development", 4, 6),
    ("Evolution", 4, 6),
    ("Ecology", 8, 10),
    ("Genetics", 6, 8),
]

created_topics = []
for name, min_marks, max_marks in topics_data:
    topic = Topic.objects.create(
        name=name,
        paper=paper1,
        min_marks=min_marks,
        max_marks=max_marks,
        created_by=admin
    )
    created_topics.append(topic)
    print(f"✓ Created topic: {name} ({min_marks}-{max_marks} marks)")

print(f"\n✓ Created {len(created_topics)} topics")
```

### Step 3: Add Questions

Use the existing question creation endpoint or add via shell:

```python
from api.models import Question

# Example: Cell Biology questions
cell_bio_topic = Topic.objects.get(name="Cell Biology", paper=paper1)

questions = [
    {
        "question_text": "Name the organelle responsible for protein synthesis.",
        "answer_text": "Ribosome",
        "marks": 1,
        "kcse_question_type": "name_identify",
        "difficulty": "easy"
    },
    {
        "question_text": "State TWO functions of the cell membrane.",
        "answer_text": "1. Controls movement of substances in and out of the cell\n2. Provides shape and support to the cell",
        "marks": 2,
        "kcse_question_type": "state_give_reasons",
        "difficulty": "medium"
    },
    {
        "question_text": "Explain THREE ways in which mitochondria are adapted to their function.",
        "answer_text": "1. Have a large surface area due to cristae for attachment of respiratory enzymes\n2. Contain enzymes for cellular respiration\n3. Have their own DNA for synthesis of some proteins",
        "marks": 3,
        "kcse_question_type": "explain_account",
        "difficulty": "medium"
    },
    # Add more questions...
]

for q_data in questions:
    Question.objects.create(
        subject=biology,
        paper=paper1,
        topic=cell_bio_topic,
        question_type="structured",
        created_by=admin,
        **q_data
    )

print(f"✓ Created {len(questions)} questions for Cell Biology")
```

**IMPORTANT**: You need approximately **200-300 questions** across all topics for successful paper generation.

Recommended distribution per topic:
- 1-mark questions: 10-15
- 2-mark questions: 12-18
- 3-mark questions: 6-10
- 4-mark questions: 1-3

### Step 4: Check Topic Statistics

Before generating, check if you have enough questions:

```bash
GET /api/papers/{paper_id}/topics/statistics
```

Response will show:
```json
{
  "topics": [
    {
      "name": "Cell Biology",
      "min_marks": 6,
      "max_marks": 8,
      "total_questions": 35,
      "questions_by_mark": {
        "1": 12,
        "2": 15,
        "3": 7,
        "4": 1
      },
      "sufficient": true  ← Should be true
    }
  ]
}
```

### Step 5: Generate Your First Paper!

```bash
POST /api/papers/generate
{
  "paper_id": "your-biology-paper-1-uuid",
  "selected_topics": [
    "cell-biology-uuid",
    "nutrition-uuid",
    "respiration-uuid",
    "transport-uuid",
    "reproduction-uuid",
    "ecology-uuid"
  ]
}
```

Response:
```json
{
  "success": true,
  "message": "Paper generated successfully",
  "generated_paper": {
    "unique_code": "KCSE-BIO-P1-20251111120000",
    "total_marks": 80,
    "total_questions": 28,
    "validation_passed": true,
    "mark_distribution": {
      "one_mark": 11,
      "two_mark": 12,
      "three_mark": 5,
      "four_mark": 0
    },
    "generation_time_seconds": 2.34
  }
}
```

### Step 6: Retrieve Generated Paper

```bash
GET /api/papers/generated/{generated_paper_id}
```

This returns the complete paper with all questions in order, ready for use!

## 📊 Configuration (Optional)

The system uses sensible defaults, but you can customize:

```bash
# View configuration
GET /api/papers/{paper_id}/configuration

# Update configuration (admin only)
PATCH /api/papers/{paper_id}/configuration/update
{
  "mark_distribution": {
    "one_mark": {
      "min_percent": 35.0,
      "max_percent": 45.0
    }
  },
  "question_count": {
    "min": 27,
    "max": 32
  }
}
```

## 🎯 Quick Test

Here's a minimal test to verify the system works:

```python
# python manage.py shell

from api.models import *
from api.paper_generator import BiologyPaper1Generator

# Get your paper and topics
paper = Paper.objects.get(name="Paper 1", subject__name="Biology")
topics = Topic.objects.filter(paper=paper)[:6]  # Use 6 topics
topic_ids = [str(t.id) for t in topics]

# Get admin user
admin = User.objects.filter(role='admin').first()

# Generate!
generator = BiologyPaper1Generator(
    paper_id=str(paper.id),
    selected_topic_ids=topic_ids,
    user=admin
)

try:
    generated_paper = generator.generate()
    print(f"✓ SUCCESS! Generated paper: {generated_paper.unique_code}")
    print(f"  Total marks: {generated_paper.total_marks}")
    print(f"  Total questions: {generated_paper.total_questions}")
    print(f"  Validation: {'PASSED' if generated_paper.validation_passed else 'FAILED'}")
except Exception as e:
    print(f"✗ ERROR: {e}")
```

## 📝 Adding Questions in Bulk

Use the existing bulk create endpoint:

```bash
POST /api/questions/bulk
{
  "questions": [
    {
      "subject": "biology-uuid",
      "paper": "paper1-uuid",
      "topic": "cell-biology-uuid",
      "question_text": "Name the process by which...",
      "answer_text": "Osmosis",
      "marks": 1,
      "question_type": "structured",
      "kcse_question_type": "name_identify",
      "difficulty": "easy"
    },
    // ... more questions
  ]
}
```

## 🔍 Monitoring

List all generated papers:
```bash
GET /api/papers/generated?status=validated
```

Check specific paper:
```bash
GET /api/papers/generated/{id}
```

## ⚠️ Common Issues

### "Insufficient questions in database"
- **Solution**: Add more questions using `/api/questions` or bulk create
- **Minimum**: 150+ questions across selected topics
- **Recommended**: 300+ questions for variety

### "Failed to generate valid paper after 5 attempts"
- **Cause**: Constraints too tight or poor question distribution
- **Solution**: 
  1. Check topic statistics
  2. Add more questions with diverse mark values
  3. Adjust configuration if needed

### "Cannot generate paper: minimum marks exceeds target"
- **Cause**: Too many topics selected with high minimums
- **Solution**: Select fewer topics or reduce topic min_marks

## 📚 Full Documentation

See `PAPER_GENERATION_README.md` for complete documentation including:
- Detailed API reference
- Algorithm explanation
- Advanced configuration
- Error handling
- Performance optimization
- Extension to other subjects

## 🎓 Next Steps

1. **Populate Database**: Add 200-300 questions across all topics
2. **Test Generation**: Try generating papers with different topic combinations
3. **Review Outputs**: Check generated papers meet KCSE standards
4. **Fine-tune Configuration**: Adjust percentages if needed
5. **Production Use**: Start generating exam papers!

## 💡 Tips

- **Start small**: Test with 3-4 topics first
- **Balance questions**: Ensure good distribution across mark values
- **Use statistics endpoint**: Always check before generating
- **Review validation**: Check validation_report in response
- **Monitor performance**: Check generation_time_seconds

## ✨ You're All Set!

The KCSE Biology Paper 1 generation system is ready to use. Start by adding questions and then generate your first paper!

For help or questions, refer to the comprehensive documentation in `PAPER_GENERATION_README.md`.
