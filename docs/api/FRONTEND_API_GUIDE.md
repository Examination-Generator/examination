# Frontend API Guide - Paper Generation

Quick reference for frontend developers working with the KCSE Paper Generation API.

## Base URL
```
http://localhost:8000/api
```

## Authentication
All endpoints require authentication. Include JWT token in headers:
```javascript
headers: {
  'Authorization': 'Bearer <your-jwt-token>',
  'Content-Type': 'application/json'
}
```

---

## 1. Generate Paper

**Generate a new KCSE Biology Paper 1**

### Request
```http
POST /api/papers/generate
Content-Type: application/json
Authorization: Bearer <token>

{
  "paper_id": "efa6d535-6a6b-45ac-931a-d20b9ccf15aa",
  "selected_topics": [
    "topic-uuid-1",
    "topic-uuid-2",
    "topic-uuid-3"
  ]
}
```

### Response (Success)
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
    "mark_distribution": {
      "1": 0,
      "2": 10,
      "3": 8,
      "4": 2,
      "5": 3,
      "6": 2,
      "7": 0
    },
    "topic_distribution": {
      "topic-uuid-1": 28,
      "topic-uuid-2": 26,
      "topic-uuid-3": 26
    },
    "question_type_distribution": {
      "name_identify": 8,
      "state_reasons": 6,
      "explain": 5,
      "describe": 4,
      "distinguish": 2
    },
    "validation_passed": true,
    "validation_report": {
      "passed": 14,
      "failed": 0,
      "errors": []
    },
    "generation_time_seconds": 1.25,
    "generation_attempts": 1,
    "backtracking_count": 0,
    "created_at": "2024-11-13T10:30:00Z"
  }
}
```

### Response (Error)
```json
{
  "error": "Paper generation failed",
  "details": "Failed to generate valid paper after 5 attempts"
}
```

### Frontend Usage Example
```javascript
async function generatePaper(paperId, topicIds) {
  try {
    const response = await fetch('http://localhost:8000/api/papers/generate', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${getToken()}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        paper_id: paperId,
        selected_topics: topicIds
      })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.details || error.error);
    }
    
    const data = await response.json();
    console.log('Paper generated:', data.generated_paper.unique_code);
    return data;
    
  } catch (error) {
    console.error('Generation failed:', error.message);
    throw error;
  }
}
```

---

## 2. Get Generated Paper

**Retrieve a specific generated paper with all questions**

### Request
```http
GET /api/papers/generated/{paper_id}
Authorization: Bearer <token>
```

### Response
```json
{
  "success": true,
  "id": "generated-paper-uuid",
  "unique_code": "BIO-P1-2024-001",
  "status": "validated",
  "paper": {
    "id": "paper-uuid",
    "name": "Paper 1",
    "subject_name": "Biology",
    "total_marks": 80,
    "time_allocation": 120
  },
  "total_marks": 80,
  "total_questions": 25,
  "mark_distribution": {...},
  "topic_distribution": {...},
  "question_type_distribution": {...},
  "validation_passed": true,
  "validation_report": {...},
  "generation_statistics": {
    "generation_time_seconds": 1.25,
    "generation_attempts": 1,
    "backtracking_count": 0
  },
  "questions": [
    {
      "id": "question-uuid-1",
      "question_text": "Name the process by which...",
      "answer_text": "Photosynthesis",
      "marks": 2,
      "question_type": "name_identify",
      "kcse_question_type": "name_identify",
      "difficulty": "easy",
      "topic_name": "Cell Biology",
      "section_name": "Introduction",
      "question_inline_images": [],
      "answer_inline_images": []
    },
    // ... more questions
  ],
  "created_at": "2024-11-13T10:30:00Z",
  "generated_by": {
    "id": "user-uuid",
    "full_name": "John Doe"
  }
}
```

### Frontend Usage Example
```javascript
async function getGeneratedPaper(paperId) {
  const response = await fetch(
    `http://localhost:8000/api/papers/generated/${paperId}`,
    {
      headers: {
        'Authorization': `Bearer ${getToken()}`
      }
    }
  );
  
  const data = await response.json();
  return data;
}
```

---

## 3. List Generated Papers

**Get list of all generated papers with filters**

### Request
```http
GET /api/papers/generated?paper_id=uuid&status=validated
Authorization: Bearer <token>
```

### Query Parameters
- `paper_id` (optional): Filter by paper template ID
- `status` (optional): Filter by status (draft, validated, published)

### Response
```json
{
  "count": 2,
  "papers": [
    {
      "id": "generated-paper-uuid-1",
      "unique_code": "BIO-P1-2024-001",
      "status": "validated",
      "paper_name": "Paper 1",
      "subject_name": "Biology",
      "total_marks": 80,
      "total_questions": 25,
      "validation_passed": true,
      "generated_by": "John Doe",
      "created_at": "2024-11-13T10:30:00Z"
    },
    {
      "id": "generated-paper-uuid-2",
      "unique_code": "BIO-P1-2024-002",
      "status": "draft",
      "paper_name": "Paper 1",
      "subject_name": "Biology",
      "total_marks": 80,
      "total_questions": 24,
      "validation_passed": false,
      "generated_by": "Jane Smith",
      "created_at": "2024-11-13T11:00:00Z"
    }
  ]
}
```

### Frontend Usage Example
```javascript
async function listGeneratedPapers(filters = {}) {
  const params = new URLSearchParams(filters);
  const response = await fetch(
    `http://localhost:8000/api/papers/generated?${params}`,
    {
      headers: {
        'Authorization': `Bearer ${getToken()}`
      }
    }
  );
  
  const data = await response.json();
  return data.papers;
}
```

---

## 4. Get Paper Configuration

**Get configuration settings for a paper template**

### Request
```http
GET /api/papers/{paper_id}/configuration
Authorization: Bearer <token>
```

### Response
```json
{
  "paper_id": "paper-uuid",
  "paper_name": "Paper 1",
  "total_marks": 80,
  "time_allocation": 120,
  "configuration": {
    "mark_distribution": {
      "one_mark": {"min_percent": 30, "max_percent": 40},
      "two_mark": {"min_percent": 35, "max_percent": 45},
      "three_mark": {"min_percent": 15, "max_percent": 25},
      "four_mark": {"min_percent": 0, "max_percent": 5}
    },
    "question_type_distribution": {
      "name_identify": {"min_percent": 30, "max_percent": 40},
      "state_reasons": {"min_percent": 20, "max_percent": 30},
      "explain": {"min_percent": 10, "max_percent": 20},
      "describe": {"min_percent": 5, "max_percent": 15},
      "distinguish": {"min_percent": 5, "max_percent": 10},
      "calculate": {"min_percent": 0, "max_percent": 10}
    },
    "question_count": {
      "min": 22,
      "max": 30
    },
    "instructions": "Answer all questions in the spaces provided..."
  },
  "created": false
}
```

---

## 5. Get Topic Statistics

**Get question availability statistics for topics**

### Request
```http
GET /api/papers/{paper_id}/topics/statistics
Authorization: Bearer <token>
```

### Response
```json
{
  "paper_id": "paper-uuid",
  "paper_name": "Paper 1",
  "topics": [
    {
      "id": "topic-uuid-1",
      "name": "Cell Biology",
      "min_marks": 6,
      "max_marks": 8,
      "total_questions": 45,
      "questions_by_mark": {
        "1": 8,
        "2": 15,
        "3": 12,
        "4": 10
      },
      "sufficient": true
    },
    {
      "id": "topic-uuid-2",
      "name": "Ecology",
      "min_marks": 8,
      "max_marks": 10,
      "total_questions": 38,
      "questions_by_mark": {
        "1": 6,
        "2": 12,
        "3": 10,
        "4": 10
      },
      "sufficient": true
    }
  ],
  "total_topics": 6
}
```

### Frontend Usage Example
```javascript
async function getTopicStatistics(paperId) {
  const response = await fetch(
    `http://localhost:8000/api/papers/${paperId}/topics/statistics`,
    {
      headers: {
        'Authorization': `Bearer ${getToken()}`
      }
    }
  );
  
  const data = await response.json();
  
  // Check if all topics have sufficient questions
  const allSufficient = data.topics.every(t => t.sufficient);
  
  if (!allSufficient) {
    console.warn('Some topics have insufficient questions!');
  }
  
  return data;
}
```

---

## Error Handling

### Common Error Codes

| Status Code | Meaning | Action |
|-------------|---------|--------|
| 400 | Bad Request | Check input validation |
| 401 | Unauthorized | Check authentication token |
| 403 | Forbidden | Check user permissions |
| 404 | Not Found | Check resource IDs |
| 410 | Gone | Endpoint deprecated, use new one |
| 500 | Server Error | Contact backend team |

### Error Response Format
```json
{
  "error": "Error type",
  "details": "Detailed error message"
}
```

### Frontend Error Handling Pattern
```javascript
async function apiCall(url, options) {
  try {
    const response = await fetch(url, options);
    
    // Handle specific status codes
    if (response.status === 401) {
      // Redirect to login
      window.location.href = '/login';
      return;
    }
    
    if (response.status === 410) {
      const error = await response.json();
      alert(error.message); // Show deprecation message
      return;
    }
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.details || error.error || 'Unknown error');
    }
    
    return await response.json();
    
  } catch (error) {
    console.error('API Error:', error.message);
    // Show user-friendly error message
    showNotification('Error', error.message, 'error');
    throw error;
  }
}
```

---

## Complete Frontend Example

### React Component
```javascript
import { useState } from 'react';

function PaperGenerator({ paperId }) {
  const [loading, setLoading] = useState(false);
  const [selectedTopics, setSelectedTopics] = useState([]);
  const [generatedPaper, setGeneratedPaper] = useState(null);
  const [error, setError] = useState(null);
  
  const handleGenerate = async () => {
    if (selectedTopics.length === 0) {
      setError('Please select at least one topic');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8000/api/papers/generate', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          paper_id: paperId,
          selected_topics: selectedTopics
        })
      });
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.details || error.error);
      }
      
      const data = await response.json();
      setGeneratedPaper(data.generated_paper);
      
      // Show success message
      alert(`Paper ${data.generated_paper.unique_code} generated successfully!`);
      
    } catch (err) {
      setError(err.message);
      console.error('Generation failed:', err);
      
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="paper-generator">
      <h2>Generate KCSE Biology Paper 1</h2>
      
      {/* Topic selection UI */}
      <TopicSelector 
        onChange={setSelectedTopics}
        selected={selectedTopics}
      />
      
      {/* Generate button */}
      <button 
        onClick={handleGenerate}
        disabled={loading || selectedTopics.length === 0}
      >
        {loading ? 'Generating...' : 'Generate Paper'}
      </button>
      
      {/* Error display */}
      {error && (
        <div className="error-message">{error}</div>
      )}
      
      {/* Success display */}
      {generatedPaper && (
        <div className="success-panel">
          <h3>Paper Generated Successfully!</h3>
          <p>Unique Code: {generatedPaper.unique_code}</p>
          <p>Total Questions: {generatedPaper.total_questions}</p>
          <p>Total Marks: {generatedPaper.total_marks}</p>
          <p>Status: {generatedPaper.status}</p>
          
          <button onClick={() => viewPaper(generatedPaper.id)}>
            View Paper
          </button>
        </div>
      )}
    </div>
  );
}
```

---

## Tips for Frontend Developers

### 1. Always Validate Input
```javascript
function validatePaperRequest(paperId, topicIds) {
  if (!paperId || typeof paperId !== 'string') {
    throw new Error('Valid paper_id is required');
  }
  
  if (!Array.isArray(topicIds) || topicIds.length === 0) {
    throw new Error('At least one topic must be selected');
  }
  
  return true;
}
```

### 2. Show Loading State
Paper generation can take 1-3 seconds. Always show loading indicator:
```javascript
setLoading(true);
// ... API call
setLoading(false);
```

### 3. Handle Validation Failures
Generated papers might not pass validation. Show appropriate message:
```javascript
if (!data.generated_paper.validation_passed) {
  showWarning(
    'Paper generated but has validation issues',
    data.generated_paper.validation_report.errors
  );
}
```

### 4. Store Generated Paper ID
Always store the generated paper ID for future reference:
```javascript
localStorage.setItem('lastGeneratedPaperId', data.generated_paper.id);
```

### 5. Use Question Statistics
Before generating, check if enough questions are available:
```javascript
const stats = await getTopicStatistics(paperId);
const insufficientTopics = stats.topics.filter(t => !t.sufficient);

if (insufficientTopics.length > 0) {
  alert(`Warning: ${insufficientTopics.map(t => t.name).join(', ')} have insufficient questions`);
}
```

---

## Questions?

For API issues or questions:
1. Check this guide
2. Check console logs for detailed errors
3. Contact backend team with error details

**Last Updated:** November 13, 2024
