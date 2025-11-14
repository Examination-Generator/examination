# KCSE Biology Paper 1 Generation System

## Overview

This system implements a complete database-driven algorithm for generating KCSE Biology Paper 1 examination papers. The implementation follows the detailed specification provided and ensures all constraints and validation rules are met.

## Features

### ✅ Complete Database-Driven Architecture
- **No hardcoded values** - All configuration retrieved from database
- **Flexible topic management** - Topics can be added/modified without code changes
- **Configurable constraints** - Mark distributions, question types, and ranges all database-controlled
- **Extensible** - Easy to add new subjects, papers, and question types

### ✅ Intelligent Question Selection
- **Weighted random selection** - Balances randomness with constraint satisfaction
- **Proportional adjustment** - Automatically adjusts topic ranges when subset selected
- **Backtracking algorithm** - Attempts to fix constraint violations by replacing questions
- **Multiple generation attempts** - Retries until valid paper generated

### ✅ Comprehensive Validation
- Total marks validation (must equal exactly 80)
- Mark distribution validation (1-mark, 2-mark, 3-mark, 4-mark percentages)
- Topic coverage validation (min/max marks per topic)
- Question count validation (25-30 questions)
- Duplicate detection
- Answer completeness check

### ✅ Pedagogical Question Arrangement
- **Early section (40%)**: Mostly 1-mark questions to build confidence
- **Middle section (40%)**: Mix of 1, 2, and 3-mark questions
- **Final section (20%)**: Complex 3 and 4-mark questions

## Database Models

### New Models Added

#### 1. **PaperConfiguration**
Stores all generation constraints and rules for a paper:

```python
class PaperConfiguration(models.Model):
    paper = OneToOneField(Paper)
    
    # Mark distribution constraints (percentages)
    one_mark_min_percent = 30.0
    one_mark_max_percent = 40.0
    two_mark_min_percent = 35.0
    two_mark_max_percent = 45.0
    three_mark_min_percent = 15.0
    three_mark_max_percent = 25.0
    four_mark_min_percent = 0.0
    four_mark_max_percent = 5.0
    
    # Question type distribution (percentages)
    name_identify_min_percent = 20.0
    name_identify_max_percent = 30.0
    # ... (state_reasons, distinguish, explain, describe, calculate)
    
    # Question count constraints
    min_questions = 25
    max_questions = 30
    
    # Generation parameters
    max_backtracking_attempts = 100
    max_generation_attempts = 5
    
    instructions = "Answer all questions..."
```

#### 2. **GeneratedPaper**
Stores generated examination papers with full metadata:

```python
class GeneratedPaper(models.Model):
    paper = ForeignKey(Paper)
    unique_code = CharField()  # e.g., "KCSE-BIO-P1-20251111120000"
    status = CharField()  # draft, validated, published, archived
    
    # Selected questions (ordered)
    question_ids = JSONField()  # Array of UUIDs
    
    # Topic selection and adjustments
    selected_topics = JSONField()
    topic_adjustments = JSONField()
    
    # Statistics
    total_marks = IntegerField()
    total_questions = IntegerField()
    mark_distribution = JSONField()
    topic_distribution = JSONField()
    question_type_distribution = JSONField()
    
    # Validation
    validation_passed = BooleanField()
    validation_report = JSONField()
    
    # Generation metrics
    generation_attempts = IntegerField()
    backtracking_count = IntegerField()
    generation_time_seconds = FloatField()
    
    generated_by = ForeignKey(User)
    created_at = DateTimeField()
```

### Enhanced Existing Models

#### **Paper Model**
Added configuration fields:
```python
total_marks = IntegerField(default=80)
time_allocation = IntegerField(default=120)  # minutes
```

#### **Topic Model**
Added mark constraint fields:
```python
min_marks = IntegerField(default=4)
max_marks = IntegerField(default=10)
```

#### **Question Model**
Added KCSE question type field:
```python
KCSE_QUESTION_TYPE_CHOICES = [
    ('name_identify', 'Name/Identify'),
    ('state_give_reasons', 'State/Give Reasons'),
    ('distinguish', 'Distinguish/Differentiate'),
    ('explain_account', 'Explain/Account For'),
    ('describe', 'Describe'),
    ('calculate', 'Calculate'),
]

kcse_question_type = CharField(
    max_length=30,
    choices=KCSE_QUESTION_TYPE_CHOICES,
    null=True,
    blank=True
)
```

## API Endpoints

### 1. Generate Paper
**POST** `/api/papers/generate`

Generate a new KCSE Biology Paper 1.

**Request:**
```json
{
  "paper_id": "uuid-of-biology-paper-1",
  "selected_topics": [
    "uuid-topic-1",
    "uuid-topic-2",
    "uuid-topic-3"
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Paper generated successfully",
  "generated_paper": {
    "id": "uuid",
    "unique_code": "KCSE-BIO-P1-20251111120000",
    "status": "validated",
    "total_marks": 80,
    "total_questions": 28,
    "mark_distribution": {
      "one_mark": 11,
      "two_mark": 12,
      "three_mark": 5,
      "four_mark": 0
    },
    "topic_distribution": {
      "Cell Biology": 8,
      "Nutrition": 10,
      "Respiration": 7,
      // ...
    },
    "question_type_distribution": {
      "name_identify": 7,
      "state_give_reasons": 9,
      "distinguish": 4,
      "explain_account": 6,
      "describe": 2,
      "calculate": 0
    },
    "validation_passed": true,
    "validation_report": {
      "all_passed": true,
      "passed_checks": [...],
      "failed_checks": [],
      "warnings": []
    },
    "generation_time_seconds": 2.34,
    "generation_attempts": 1,
    "backtracking_count": 3,
    "created_at": "2025-11-11T12:00:00Z"
  }
}
```

### 2. Get Generated Paper
**GET** `/api/papers/generated/{paper_id}`

Retrieve a generated paper with full question details.

**Response:**
```json
{
  "id": "uuid",
  "unique_code": "KCSE-BIO-P1-20251111120000",
  "status": "validated",
  "paper": {
    "id": "uuid",
    "name": "Paper 1",
    "subject_name": "Biology",
    "total_marks": 80,
    "time_allocation": 120
  },
  "total_marks": 80,
  "total_questions": 28,
  "mark_distribution": {...},
  "topic_distribution": {...},
  "question_type_distribution": {...},
  "validation_passed": true,
  "validation_report": {...},
  "generation_statistics": {
    "generation_time_seconds": 2.34,
    "generation_attempts": 1,
    "backtracking_count": 3
  },
  "questions": [
    {
      "id": "uuid",
      "question_text": "Name the organelle responsible for protein synthesis.",
      "question_inline_images": [],
      "answer_text": "Ribosome",
      "answer_inline_images": [],
      "marks": 1,
      "question_type": "structured",
      "kcse_question_type": "name_identify",
      "difficulty": "easy",
      "topic_name": "Cell Biology",
      "section_name": "Cell Organelles"
    },
    // ... more questions in order
  ],
  "created_at": "2025-11-11T12:00:00Z",
  "generated_by": {
    "id": "uuid",
    "full_name": "John Doe"
  }
}
```

### 3. List Generated Papers
**GET** `/api/papers/generated?paper_id=uuid&status=validated`

List all generated papers with optional filtering.

**Response:**
```json
{
  "count": 5,
  "papers": [
    {
      "id": "uuid",
      "unique_code": "KCSE-BIO-P1-20251111120000",
      "status": "validated",
      "paper_name": "Paper 1",
      "subject_name": "Biology",
      "total_marks": 80,
      "total_questions": 28,
      "validation_passed": true,
      "generated_by": "John Doe",
      "created_at": "2025-11-11T12:00:00Z"
    },
    // ... more papers
  ]
}
```

### 4. Get Paper Configuration
**GET** `/api/papers/{paper_id}/configuration`

Get or create configuration for a paper.

**Response:**
```json
{
  "paper_id": "uuid",
  "paper_name": "Paper 1",
  "total_marks": 80,
  "time_allocation": 120,
  "configuration": {
    "mark_distribution": {
      "one_mark": {
        "min_percent": 30.0,
        "max_percent": 40.0
      },
      "two_mark": {
        "min_percent": 35.0,
        "max_percent": 45.0
      },
      "three_mark": {
        "min_percent": 15.0,
        "max_percent": 25.0
      },
      "four_mark": {
        "min_percent": 0.0,
        "max_percent": 5.0
      }
    },
    "question_type_distribution": {
      "name_identify": {
        "min_percent": 20.0,
        "max_percent": 30.0
      },
      "state_reasons": {
        "min_percent": 25.0,
        "max_percent": 35.0
      },
      "distinguish": {
        "min_percent": 10.0,
        "max_percent": 15.0
      },
      "explain": {
        "min_percent": 20.0,
        "max_percent": 30.0
      },
      "describe": {
        "min_percent": 10.0,
        "max_percent": 20.0
      },
      "calculate": {
        "min_percent": 0.0,
        "max_percent": 5.0
      }
    },
    "question_count": {
      "min": 25,
      "max": 30
    },
    "instructions": "Answer all questions in the spaces provided on this paper."
  },
  "created": false
}
```

### 5. Update Paper Configuration
**PATCH** `/api/papers/{paper_id}/configuration/update`

Update configuration for a paper (Editor/Admin only).

**Request:**
```json
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

### 6. Get Topic Statistics
**GET** `/api/papers/{paper_id}/topics/statistics`

Get statistics about available questions per topic.

**Response:**
```json
{
  "paper_id": "uuid",
  "paper_name": "Paper 1",
  "topics": [
    {
      "id": "uuid",
      "name": "Cell Biology",
      "min_marks": 6,
      "max_marks": 8,
      "total_questions": 45,
      "questions_by_mark": {
        "1": 15,
        "2": 18,
        "3": 10,
        "4": 2
      },
      "sufficient": true
    },
    // ... more topics
  ],
  "total_topics": 12
}
```

## Generation Algorithm Flow

### Step 1: Initialize from Database
1. Retrieve Paper record
2. Get or create PaperConfiguration
3. Load selected Topics with constraints
4. Initialize tracking variables

### Step 2: Proportional Adjustment
1. Calculate sum of max marks for selected topics
2. Compute scaling factor: `target_marks / sum_max_marks`
3. Apply scaling to each topic's min/max ranges
4. Validate that generation is mathematically possible

### Step 3: Iterative Question Selection
```
WHILE total_marks < target_marks:
  1. Determine next mark value (1, 2, 3, or 4)
     - Based on current distribution vs target percentages
     - Weighted random selection
  
  2. Determine next topic
     - Prioritize topics below minimum marks
     - Weighted random selection
  
  3. Query database for eligible questions
     - Match topic and mark value
     - Exclude already selected questions
  
  4. Randomly select from eligible questions
  
  5. Validate question addition
     - Won't exceed total marks
     - Won't exceed topic max marks
     - Won't violate distribution constraints
  
  6. If valid, add question and update tracking
  7. If invalid or no eligible questions, try different combination
```

### Step 4: Backtracking
If stuck (can't find valid questions):
1. Try replacing lower-mark questions with higher-mark ones
2. Stay within same topic to maintain topic distribution
3. Maximum backtracking attempts: 100 (configurable)
4. If backtracking fails, restart generation

### Step 5: Question Arrangement
1. Separate questions by mark value
2. Shuffle each group for topic variety
3. Create three sections:
   - **Early (40%)**: Mostly 1-mark questions
   - **Middle (40%)**: Mix of 1, 2, 3-mark questions
   - **Final (20%)**: Complex 3 and 4-mark questions
4. Assign sequential numbers 1, 2, 3, ...

### Step 6: Answer Retrieval
- All answers already in Question records
- Organized in parallel to question paper
- Includes marking schemes and alternatives

### Step 7: Comprehensive Validation
Validates:
- ✓ Total marks = 80
- ✓ Mark distribution within ranges
- ✓ Topic coverage within min/max
- ✓ Question count within 25-30
- ✓ No duplicate questions
- ✓ All questions have complete answers

### Step 8: Output Generation
1. Generate unique code (timestamp-based)
2. Create GeneratedPaper record
3. Store all metadata and statistics
4. Update question usage counters
5. Return complete paper with validation report

## Usage Examples

### Example 1: Generate Paper with All Topics

```python
# Via API
POST /api/papers/generate
{
  "paper_id": "biology-paper-1-uuid",
  "selected_topics": [
    "cell-biology-uuid",
    "classification-uuid",
    "nutrition-uuid",
    "respiration-uuid",
    "transport-uuid",
    "excretion-uuid",
    "gaseous-exchange-uuid",
    "reproduction-uuid",
    "growth-uuid",
    "evolution-uuid",
    "ecology-uuid",
    "genetics-uuid"
  ]
}

# Via Python
from api.paper_generator import BiologyPaper1Generator

generator = BiologyPaper1Generator(
    paper_id="biology-paper-1-uuid",
    selected_topic_ids=all_topic_ids,
    user=request.user
)

generated_paper = generator.generate()
```

### Example 2: Generate Paper with Subset of Topics

```python
# Select only 6 topics
POST /api/papers/generate
{
  "paper_id": "biology-paper-1-uuid",
  "selected_topics": [
    "cell-biology-uuid",
    "nutrition-uuid",
    "respiration-uuid",
    "transport-uuid",
    "reproduction-uuid",
    "ecology-uuid"
  ]
}

# Algorithm automatically applies proportional adjustment
# If original ranges were:
#   Cell Biology: 6-8 marks
#   Nutrition: 8-10 marks
#   ... (sum of max = 48 marks)
#
# Scaling factor = 80 / 48 = 1.67
# Adjusted ranges become:
#   Cell Biology: 10-13 marks
#   Nutrition: 13-17 marks
#   ...
```

### Example 3: Check Topic Statistics Before Generation

```python
# Check if sufficient questions exist
GET /api/papers/{paper_id}/topics/statistics

# Response shows which topics have enough questions
{
  "topics": [
    {
      "name": "Cell Biology",
      "total_questions": 45,
      "questions_by_mark": {
        "1": 15,
        "2": 18,
        "3": 10,
        "4": 2
      },
      "sufficient": true  // ✓ Good to go
    },
    {
      "name": "Evolution",
      "total_questions": 8,
      "questions_by_mark": {
        "1": 3,
        "2": 4,
        "3": 1,
        "4": 0
      },
      "sufficient": false  // ⚠️ Need more questions
    }
  ]
}
```

## Configuration Management

### Setting Up a New Paper

```python
# 1. Create subject and paper
subject = Subject.objects.create(name="Biology", created_by=admin)
paper = Paper.objects.create(
    name="Paper 1",
    subject=subject,
    total_marks=80,
    time_allocation=120,
    created_by=admin
)

# 2. Create topics with mark constraints
topics = [
    ("Cell Biology", 6, 8),
    ("Nutrition", 8, 10),
    ("Respiration", 6, 8),
    # ... more topics
]

for name, min_marks, max_marks in topics:
    Topic.objects.create(
        name=name,
        paper=paper,
        min_marks=min_marks,
        max_marks=max_marks,
        created_by=admin
    )

# 3. Configuration is auto-created with defaults
# Modify if needed:
config = PaperConfiguration.objects.get(paper=paper)
config.one_mark_min_percent = 35.0  # Adjust if needed
config.save()
```

### Updating Configuration via API

```python
PATCH /api/papers/{paper_id}/configuration/update
{
  "mark_distribution": {
    "one_mark": {
      "min_percent": 35.0,  // Increase 1-mark questions
      "max_percent": 45.0
    }
  },
  "question_count": {
    "min": 27,  // Require more questions
    "max": 32
  }
}
```

## Error Handling

### Common Errors and Solutions

#### 1. "Insufficient questions in database"
**Cause**: Not enough questions for selected topics

**Solution**:
- Add more questions via `/api/questions`
- Check `/api/papers/{id}/topics/statistics`
- Need at least 25 questions total, well distributed

#### 2. "Failed to generate valid paper after N attempts"
**Cause**: Constraints too strict or question distribution poor

**Solutions**:
- Relax mark distribution percentages
- Add more questions to database
- Check topic min/max ranges aren't too restrictive
- Ensure variety of mark values (1, 2, 3, 4) available

#### 3. "Cannot generate paper: minimum marks exceeds target"
**Cause**: Selected topics' minimum marks sum > 80

**Solution**:
- Reduce some topics' min_marks
- Select fewer topics
- Algorithm will warn before attempting generation

#### 4. "Backtracking failed, cannot reach target marks"
**Cause**: Got stuck during question selection

**Solution**:
- System automatically retries (up to 5 attempts)
- If persistent, add more questions to database
- Check that questions exist for all mark values

## Performance Considerations

### Generation Time
- **Typical**: 1-3 seconds for well-stocked database
- **Maximum**: 10-15 seconds with backtracking
- **Factors**: Number of questions, constraint tightness

### Database Optimization
```python
# Indexes automatically created:
- Question: (subject, paper, topic)
- Question: (is_active)
- Question: (question_type, difficulty)
- GeneratedPaper: (paper, status)
- GeneratedPaper: (unique_code)
```

### Caching Recommendations
```python
# Cache configuration for frequently accessed papers
from django.core.cache import cache

config = cache.get(f'paper_config_{paper_id}')
if not config:
    config = PaperConfiguration.objects.get(paper_id=paper_id)
    cache.set(f'paper_config_{paper_id}', config, 3600)
```

## Testing

### Unit Tests
```python
# Test proportional adjustment
def test_proportional_adjustment():
    generator = BiologyPaper1Generator(...)
    generator._apply_proportional_adjustment()
    
    total_min = sum(c['min_marks'] for c in generator.topic_constraints.values())
    total_max = sum(c['max_marks'] for c in generator.topic_constraints.values())
    
    assert total_min <= generator.paper.total_marks
    assert total_max >= generator.paper.total_marks

# Test validation
def test_validation_exact_marks():
    generator = BiologyPaper1Generator(...)
    generator.total_marks = 79  # Wrong!
    
    report = generator._validate_paper()
    assert not report['all_passed']
    assert 'Total marks mismatch' in str(report['failed_checks'])
```

### Integration Tests
```python
# Test full generation
def test_full_generation():
    response = client.post('/api/papers/generate', {
        'paper_id': str(paper.id),
        'selected_topics': [str(t.id) for t in topics]
    })
    
    assert response.status_code == 201
    assert response.data['generated_paper']['validation_passed']
    assert response.data['generated_paper']['total_marks'] == 80
```

## Logging

The system provides comprehensive logging:

```python
logger.info(f"[STEP 1] Initializing paper generation for paper {paper_id}")
logger.info(f"[STEP 2] Applying proportional adjustments for {n} topics")
logger.info(f"[SELECTION] Selected {n} questions totaling {m} marks in {i} iterations")
logger.info(f"[ARRANGE] Arranged into sections: Early={e}, Middle={m}, Final={f}")
logger.info(f"[VALIDATION] Passed: {p}, Failed: {f}")
logger.info(f"[SUCCESS] Paper generated in {t:.2f}s after {a} attempt(s)")

logger.warning(f"[BACKTRACK] Maximum backtracking attempts reached")
logger.error(f"[ERROR] Paper generation failed: {error}")
```

## Future Enhancements

### Planned Features
1. **PDF Export**: Generate formatted PDF papers and marking schemes
2. **Difficulty Balancing**: Ensure even distribution of easy/medium/hard questions
3. **Cognitive Level Distribution**: Track and balance Bloom's taxonomy levels
4. **Multi-language Support**: Generate papers in different languages
5. **Template Customization**: Allow custom paper templates and formatting
6. **Analytics Dashboard**: Track generation statistics and patterns
7. **Question Bank Health**: Monitoring and recommendations for database gaps

### Extension to Other Subjects
```python
# The algorithm is generic and can be used for:
- Chemistry Paper 1, 2, 3
- Physics Paper 1, 2, 3
- Mathematics Paper 1, 2
- Any subject with similar structure

# Just configure:
1. Create Subject and Papers
2. Define Topics with min/max marks
3. Set PaperConfiguration constraints
4. Add questions with proper metadata
```

## Support and Contribution

For issues, questions, or contributions, please contact the development team.

## License

This examination generation system is proprietary software developed for KCSE examination management.
