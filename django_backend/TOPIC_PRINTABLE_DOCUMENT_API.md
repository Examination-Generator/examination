# Topic & Paper Printable Document API

## Endpoint
```
GET /api/topics/printable-document
```

## Description
Generates a beautifully formatted, printable HTML document containing questions and answers for either:
- **A specific topic** (topic-level)
- **An entire paper with all its topics** (paper-level)

## Authentication
Requires authentication token in the Authorization header.

## Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `subject_id` | UUID | Yes | The ID of the subject |
| `topic_id` | UUID | Conditional | The ID of the topic to print (required if paper_id not provided) |
| `paper_id` | UUID | Conditional | The ID of the paper to print all topics (required if topic_id not provided) |

**Note:** You must provide either `topic_id` OR `paper_id`, but not both.

## Usage Scenarios

### Scenario 1: Print a Single Topic
Generate a document for one specific topic.

```
GET /api/topics/printable-document?subject_id={subjectId}&topic_id={topicId}
```

### Scenario 2: Print Entire Paper
Generate a document for all topics in a paper (questions grouped by topic).

```
GET /api/topics/printable-document?subject_id={subjectId}&paper_id={paperId}
```

## Example Requests

### Topic-Level Request
```javascript
// Print questions for a specific topic
const subjectId = "123e4567-e89b-12d3-a456-426614174000";
const topicId = "987fcdeb-51a2-43f7-8b9c-123456789abc";

fetch(`/api/topics/printable-document?subject_id=${subjectId}&topic_id=${topicId}`, {
  headers: {
    'Authorization': `Bearer ${authToken}`
  }
})
  .then(response => response.text())
  .then(html => {
    const printWindow = window.open('', '_blank');
    printWindow.document.write(html);
    printWindow.document.close();
  });
```

### Paper-Level Request
```javascript
// Print all questions for an entire paper
const subjectId = "123e4567-e89b-12d3-a456-426614174000";
const paperId = "456789ab-cdef-0123-4567-89abcdef0123";

fetch(`/api/topics/printable-document?subject_id=${subjectId}&paper_id=${paperId}`, {
  headers: {
    'Authorization': `Bearer ${authToken}`
  }
})
  .then(response => response.text())
  .then(html => {
    const printWindow = window.open('', '_blank');
    printWindow.document.write(html);
    printWindow.document.close();
  });
```

## Response

Returns an HTML document with:

### Features for Topic-Level Documents
1. **Topic Name as Title** - Prominently displayed at the top
2. **Subject Name** - Shows which subject the topic belongs to
3. **Sequential Numbering** - Questions numbered from 1 to N
4. **Paper Information** - Each question shows which paper it belongs to
5. **Marks Display** - Shows marks allocated for each question
6. **Question Text** - Full question with proper formatting
7. **Inline Images** - Diagrams and images displayed properly
8. **Answer Section** - Complete answer below each question
9. **Answer Images** - Diagrams in answers displayed correctly
10. **Print Button** - Built-in print button for easy printing
11. **Professional Styling** - Clean, readable format optimized for A4 printing

### Additional Features for Paper-Level Documents
1. **Questions Grouped by Topic** - Organized sections for each topic
2. **Topic Headers** - Beautiful gradient headers showing topic name and question count
3. **Topic Badges** - Each question shows its topic in addition to paper info
4. **Continuous Numbering** - Questions numbered 1 to N across all topics
5. **Topic Summary** - Shows how many questions per topic

### Document Structure (Topic-Level)
```
┌─────────────────────────────────┐
│ [SUBJECT NAME]                  │
│ TOPIC NAME                      │
│ Questions and Answers           │
├─────────────────────────────────┤
│ Total Questions: X              │
├─────────────────────────────────┤
│ Question 1     [Paper 1] [5 mk] │
│ ┌───────────────────────────┐   │
│ │ 📝 Question               │   │
│ │ Question text here...     │   │
│ │ [Image if present]        │   │
│ └───────────────────────────┘   │
│ ┌───────────────────────────┐   │
│ │ ✅ Answer                 │   │
│ │ Answer text here...       │   │
│ │ [Image if present]        │   │
│ └───────────────────────────┘   │
├─────────────────────────────────┤
│ Question 2     [Paper 2] [8 mk] │
│ ...                             │
└─────────────────────────────────┘
```

### Document Structure (Paper-Level)
```
┌─────────────────────────────────┐
│ [SUBJECT NAME]                  │
│ PAPER NAME                      │
│ Questions and Answers           │
├─────────────────────────────────┤
│ Total Questions: X              │
├─────────────────────────────────┤
│ 📚 Topic 1                      │
│    5 question(s)                │
├─────────────────────────────────┤
│ Question 1  [Paper][Topic][5mk] │
│ ┌───────────────────────────┐   │
│ │ 📝 Question               │   │
│ │ ...                       │   │
│ └───────────────────────────┘   │
│ ┌───────────────────────────┐   │
│ │ ✅ Answer                 │   │
│ │ ...                       │   │
│ └───────────────────────────┘   │
├─────────────────────────────────┤
│ Question 2  [Paper][Topic][8mk] │
│ ...                             │
├─────────────────────────────────┤
│ 📚 Topic 2                      │
│    3 question(s)                │
├─────────────────────────────────┤
│ Question 6  [Paper][Topic][4mk] │
│ ...                             │
└─────────────────────────────────┘
```

## Frontend Implementation Guide

### 1. User selects subject, then either topic or paper
```javascript
// Fetch subjects
const subjects = await fetch('/api/subjects', {
  headers: { 'Authorization': `Bearer ${token}` }
}).then(r => r.json());

// When subject is selected, show its papers
const selectedSubject = subjects.data.find(s => s.id === selectedSubjectId);
const papers = selectedSubject.papers;

// Each paper has topics
papers.forEach(paper => {
  console.log(`${paper.name}:`, paper.topics);
});
```

### 2. Generate printable document - Topic Level
```javascript
function generateTopicDocument(subjectId, topicId) {
  const url = `/api/topics/printable-document?subject_id=${subjectId}&topic_id=${topicId}`;
  
  fetch(url, {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  })
    .then(response => {
      if (!response.ok) {
        throw new Error('Failed to generate document');
      }
      return response.text();
    })
    .then(html => {
      // Open in new window
      const printWindow = window.open('', '_blank');
      printWindow.document.write(html);
      printWindow.document.close();
    })
    .catch(error => {
      console.error('Error:', error);
      alert('Failed to generate printable document');
    });
}
```

### 3. Generate printable document - Paper Level
```javascript
function generatePaperDocument(subjectId, paperId) {
  const url = `/api/topics/printable-document?subject_id=${subjectId}&paper_id=${paperId}`;
  
  fetch(url, {
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    }
  })
    .then(response => {
      if (!response.ok) {
        throw new Error('Failed to generate document');
      }
      return response.text();
    })
    .then(html => {
      // Open in new window
      const printWindow = window.open('', '_blank');
      printWindow.document.write(html);
      printWindow.document.close();
    })
    .catch(error => {
      console.error('Error:', error);
      alert('Failed to generate printable document');
    });
}
```

### 4. Example React Component with Both Options
```jsx
function PrintSelector() {
  const [subjects, setSubjects] = useState([]);
  const [selectedSubject, setSelectedSubject] = useState(null);
  const [selectedPaper, setSelectedPaper] = useState(null);
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [printMode, setPrintMode] = useState('topic'); // 'topic' or 'paper'
  
  const subjectData = subjects.find(s => s.id === selectedSubject);
  const paperData = subjectData?.papers.find(p => p.id === selectedPaper);
  
  const handlePrint = async () => {
    if (!selectedSubject) {
      alert('Please select a subject');
      return;
    }
    
    let url;
    if (printMode === 'paper' && selectedPaper) {
      url = `/api/topics/printable-document?subject_id=${selectedSubject}&paper_id=${selectedPaper}`;
    } else if (printMode === 'topic' && selectedTopic) {
      url = `/api/topics/printable-document?subject_id=${selectedSubject}&topic_id=${selectedTopic}`;
    } else {
      alert('Please select what to print');
      return;
    }
    
    try {
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      const html = await response.text();
      const printWindow = window.open('', '_blank');
      printWindow.document.write(html);
      printWindow.document.close();
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to generate document');
    }
  };
  
  return (
    <div>
      {/* Subject Selection */}
      <select onChange={(e) => setSelectedSubject(e.target.value)}>
        <option value="">Select Subject</option>
        {subjects.map(subject => (
          <option key={subject.id} value={subject.id}>
            {subject.name}
          </option>
        ))}
      </select>
      
      {/* Print Mode Selection */}
      {selectedSubject && (
        <div>
          <label>
            <input 
              type="radio" 
              value="paper" 
              checked={printMode === 'paper'} 
              onChange={(e) => setPrintMode(e.target.value)} 
            />
            Print Entire Paper
          </label>
          <label>
            <input 
              type="radio" 
              value="topic" 
              checked={printMode === 'topic'} 
              onChange={(e) => setPrintMode(e.target.value)} 
            />
            Print Single Topic
          </label>
        </div>
      )}
      
      {/* Paper Selection (for paper mode) */}
      {selectedSubject && printMode === 'paper' && (
        <select onChange={(e) => setSelectedPaper(e.target.value)}>
          <option value="">Select Paper</option>
          {subjectData?.papers.map(paper => (
            <option key={paper.id} value={paper.id}>
              {paper.name}
            </option>
          ))}
        </select>
      )}
      
      {/* Topic Selection (for topic mode) */}
      {selectedSubject && printMode === 'topic' && (
        <>
          <select onChange={(e) => setSelectedPaper(e.target.value)}>
            <option value="">Select Paper First</option>
            {subjectData?.papers.map(paper => (
              <option key={paper.id} value={paper.id}>
                {paper.name}
              </option>
            ))}
          </select>
          
          {selectedPaper && (
            <select onChange={(e) => setSelectedTopic(e.target.value)}>
              <option value="">Select Topic</option>
              {paperData?.topics.map(topic => (
                <option key={topic.id} value={topic.id}>
                  {topic.name}
                </option>
              ))}
            </select>
          )}
        </>
      )}
      
      <button onClick={handlePrint}>
        {printMode === 'paper' ? '🖨️ Print Entire Paper' : '🖨️ Print Topic'}
      </button>
    </div>
  );
}
```

## Error Responses

### Missing subject_id (400)
```json
{
  "success": false,
  "message": "Missing required parameters",
  "data": {
    "error": "subject_id is required"
  }
}
```

### Missing both topic_id and paper_id (400)
```json
{
  "success": false,
  "message": "Missing required parameters",
  "data": {
    "error": "Either topic_id or paper_id is required"
  }
}
```

### Invalid Relationship - Paper (400)
```json
{
  "success": false,
  "message": "Invalid relationship",
  "data": {
    "error": "Paper does not belong to the specified subject"
  }
}
```

### Invalid Relationship - Topic (400)
```json
{
  "success": false,
  "message": "Invalid relationship",
  "data": {
    "error": "Topic does not belong to the specified subject"
  }
}
```

### No Questions Found - Topic (404)
```json
{
  "success": false,
  "message": "No questions found",
  "data": {
    "error": "No active questions found for this topic"
  }
}
```

### No Questions Found - Paper (404)
```json
{
  "success": false,
  "message": "No questions found",
  "data": {
    "error": "No active questions found for this paper"
  }
}
```

### No Topics Found (404)
```json
{
  "success": false,
  "message": "No topics found",
  "data": {
    "error": "No active topics found for this paper"
  }
}
```

### Subject/Topic/Paper Not Found (404)
```json
{
  "success": false,
  "message": "Subject not found",
  "data": {
    "error": "Subject with the specified ID does not exist"
  }
}
```

## Styling Features

The generated HTML includes:
- **Responsive design** - Adapts to different screen sizes
- **Print optimization** - A4 page formatting with proper margins
- **Color coding** - Blue for papers, green for answers
- **Professional typography** - Times New Roman for readability
- **Image handling** - Automatic sizing and centering
- **Section separation** - Clear visual boundaries between questions
- **Badges** - Visual indicators for paper and marks
- **Print-specific CSS** - Optimized layout when printing

## Notes

1. Only **active questions** are included in the document
2. Questions are ordered by **topic name** (for paper-level) then **creation date** (oldest first)
3. Images are displayed as **base64-encoded** inline images
4. The document can be **printed directly** or saved as PDF using browser print-to-PDF
5. For **paper-level** documents:
   - Questions are grouped by topic with beautiful topic headers
   - Each question shows both paper AND topic badges
   - Topics are shown in alphabetical order
   - Continuous numbering across all topics
6. For **topic-level** documents:
   - Questions show only the paper badge (not topic since it's the same for all)
   - Simple, focused layout
7. The document is **self-contained** (no external dependencies)
8. **Paper cards functionality**: The paper-level endpoint solves the issue where "Questions by Paper" cards can now generate complete documents for entire papers

## Comparison: Topic-Level vs Paper-Level

| Feature | Topic-Level | Paper-Level |
|---------|-------------|-------------|
| **Scope** | Single topic | All topics in a paper |
| **Parameters** | `topic_id` | `paper_id` |
| **Grouping** | None (all questions from one topic) | Grouped by topic |
| **Topic Headers** | Not shown | Beautiful gradient headers |
| **Topic Badges** | Not shown | Shown on each question |
| **Use Case** | Focused practice on one topic | Complete paper overview |
| **Numbering** | 1 to N | 1 to N (continuous across topics) |

## Best Practices

1. **For Topic-Level**: Use when students need focused practice on a specific concept
2. **For Paper-Level**: Use when teachers need a complete question bank for a paper
3. **Performance**: Both endpoints are optimized with `select_related()` for fast query execution
4. **User Experience**: Open in new window allows users to keep browsing while document loads
5. **Printing**: Documents are pre-styled for A4 paper with proper margins
