# Paper Generation Architecture

## Overview
This document explains the organization of KCSE Biology Paper 1 generation code.

## File Structure

```
api/
├── paper_generator.py              # CORE LOGIC - Production generator class
├── paper_generation_views.py       # VIEWS - API endpoints
├── biology_paper_generation.py     # DEPRECATED - Old implementation (kept for reference)
└── models.py                       # Data models (Paper, Question, GeneratedPaper, etc.)
```

## Production Implementation

### 1. Core Logic: `paper_generator.py`
**Class:** `BiologyPaper1Generator`

**Purpose:** Intelligent 3-phase paper generation algorithm

**Algorithm:**
```
Phase 1: Nested Question Selection (Flexible)
├── Target: 50-65 marks (flexible count: 10-18 questions)
├── Strategic exact-mark targeting for completion
└── If 1-2 marks remain, use standalone to complete

Phase 2: Dynamic Recalculation
├── Calculate actual nested marks achieved
└── Compute exact standalone distribution needed

Phase 3: Standalone Selection
├── Fill exact remaining marks to reach 80 total
├── Priority: 2m > 3m > 1m (only if needed)
└── Topic and question type balancing
```

**Key Features:**
- Flexible nested completion (can use standalone in nested phase)
- Early success detection (if target achieved)
- Comprehensive validation (14 checks)
- Detailed logging for debugging
- Automatic backtracking on failure

**Usage:**
```python
from .paper_generator import BiologyPaper1Generator

generator = BiologyPaper1Generator(
    paper_id="uuid-string",
    selected_topic_ids=["topic1-uuid", "topic2-uuid"],
    user=request.user
)
generated_paper = generator.generate()  # Returns GeneratedPaper object
```

### 2. API Views: `paper_generation_views.py`
**Purpose:** REST API endpoints for paper generation

**Endpoints:**

| Method | URL | Description |
|--------|-----|-------------|
| POST | `/api/papers/generate` | Generate and save a paper |
| GET | `/api/papers/generated` | List all generated papers |
| GET | `/api/papers/generated/{id}` | Get specific generated paper |
| GET | `/api/papers/{id}/configuration` | Get paper configuration |
| PATCH | `/api/papers/{id}/configuration` | Update paper configuration |
| GET | `/api/papers/{id}/topics/statistics` | Get topic question statistics |

**Frontend Input (POST /api/papers/generate):**
```json
{
  "paper_id": "uuid-string",
  "selected_topics": ["topic-uuid-1", "topic-uuid-2", ...]
}
```

**Backend Response:**
```json
{
  "success": true,
  "message": "Paper generated successfully",
  "generated_paper": {
    "id": "generated-paper-uuid",
    "unique_code": "BIO-P1-2024-001",
    "status": "validated",
    "total_marks": 80,
    "total_questions": 25,
    "mark_distribution": {"1": 0, "2": 8, "3": 5, "4": 2, ...},
    "validation_passed": true,
    "generation_time_seconds": 1.2
  }
}
```

### 3. Deprecated: `biology_paper_generation.py`
**Status:** DEPRECATED - Do not use in production

**Why deprecated:**
- Uses older, simpler algorithm
- No flexible nested completion
- No comprehensive validation
- Less robust error handling

**Kept for:** Historical reference only

All views in this file return HTTP 410 Gone with message to use new endpoints.

## Data Models

### Question Model
```python
class Question(models.Model):
    # Basic fields
    question_text = TextField()
    answer_text = TextField()
    marks = IntegerField()
    
    # Nested question support (SIMPLIFIED)
    is_nested = BooleanField(default=False)  # Just a flag
    nested_parts = JSONField(null=True, blank=True)  # Optional, not required
    
    # Relations
    paper = ForeignKey(Paper)
    topic = ForeignKey(Topic)
    section = ForeignKey(Section, null=True)
```

**Nested Question Simplified Structure:**
- Only need `is_nested=True` and `marks` (total marks)
- No need to break down into parts
- Algorithm handles it as a single unit

### GeneratedPaper Model
```python
class GeneratedPaper(models.Model):
    unique_code = CharField()  # "BIO-P1-2024-001"
    paper = ForeignKey(Paper)
    question_ids = JSONField()  # Ordered list of question UUIDs
    
    # Metadata
    total_marks = IntegerField()
    total_questions = IntegerField()
    mark_distribution = JSONField()
    topic_distribution = JSONField()
    
    # Generation stats
    generation_attempts = IntegerField()
    generation_time_seconds = FloatField()
    validation_passed = BooleanField()
    validation_report = JSONField()
    
    # Audit
    generated_by = ForeignKey(User)
    created_at = DateTimeField()
```

## KCSE Paper 1 Requirements

### Constraints
- **Total Marks:** Exactly 80
- **Total Questions:** 22-30 questions
- **Nested Questions:**
  - Count: 10-18 questions (flexible)
  - Marks: 50-65 marks total
  - Individual: 4-7 marks each
- **Standalone Questions:**
  - Fill to exactly 80 marks
  - Marks: 1-4 marks each
  - Priority: 2m > 3m > 1m (use 1m only if needed)

### Mark Distribution (Target)
- 1-mark: 30-40% of questions
- 2-mark: 35-45% of questions
- 3-mark: 15-25% of questions
- 4-mark: 0-5% of questions

### Topic Distribution
Each topic should have roughly equal representation (±20% of average).

### Question Type Distribution
Must include variety:
- Name/Identify: 30-40%
- State/Give reasons: 20-30%
- Distinguish: 5-10%
- Explain: 10-20%
- Describe: 5-15%
- Calculate: 0-10%

## Testing

### Current Status (as of Nov 2024)
⚠️ **Tests failing:** Standalone phase has issues

**Known Issues:**
1. Standalone selection gets stuck after 4-6 questions
2. Papers reach 68-79 marks instead of 80
3. Hitting max iterations (1000) without progress
4. Question starvation (constraint violations)

**Test Command:**
```bash
cd django_backend
python test_generation.py
```

### Next Steps
1. Fix standalone selection logic (question starvation)
2. Relax constraints for standalone phase
3. Ensure papers always reach exactly 80 marks
4. Pass all validation checks

## Development Workflow

### Adding New Features
1. **Logic changes:** Modify `paper_generator.py`
2. **API changes:** Modify `paper_generation_views.py`
3. **Data model changes:** Modify `models.py` + create migration

### Testing Changes
```bash
# Unit tests
python test_generation.py

# API test
curl -X POST http://localhost:8000/api/papers/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"paper_id": "uuid", "selected_topics": ["uuid1", "uuid2"]}'
```

### Debugging
Enable detailed logging in `paper_generator.py`:
- `[NESTED]` - Nested question selection
- `[STANDALONE]` - Standalone question selection
- `[SELECTION]` - Overall selection progress
- `[VALIDATION]` - Validation results
- `[ERROR]` - Error messages

## Migration History

### Nested Questions Evolution
1. **Migration 0004:** Added `is_nested` and `nested_parts` fields
2. **Migration 0005:** Made `nested_parts` optional (simplified structure)

**Current approach:** 
- Teachers mark `is_nested=True` and enter total marks only
- No need to break down into sub-parts
- Algorithm treats nested as single unit with higher marks

## Future Enhancements

### Planned
- [ ] Fix standalone selection bug
- [ ] Add difficulty balancing
- [ ] Improve topic distribution algorithm
- [ ] Support for custom constraints per paper
- [ ] Paper preview before saving
- [ ] Export to PDF/Word

### Under Consideration
- Multiple paper generation in batch
- AI-powered question selection
- Duplicate question detection
- Historical paper analysis

## Contact & Support

For questions about this architecture:
1. Check this document first
2. Review code comments in `paper_generator.py`
3. Check git history for context
4. Contact development team

---
**Last Updated:** November 13, 2024
**Version:** 2.0 (Simplified Nested + Flexible Algorithm)
