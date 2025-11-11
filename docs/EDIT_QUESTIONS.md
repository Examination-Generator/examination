# Edit Questions Feature Guide

## Overview
The Edit Questions tab provides a comprehensive interface for searching, viewing, editing, and managing existing questions in the examination system. This feature enables full CRUD (Create, Read, Update, Delete) operations on questions with an intuitive search and edit workflow.

## Access

### Navigation
1. Open the EditorDashboard
2. Click on the **"Edit Questions"** tab in the main navigation
3. The tab is located between "Add New Subject" and other tabs

### Tab Icon
🖊️ Edit icon with "Edit Questions" label

## Features

### 1. Question Search

#### Search Functionality
- **Search Fields**: Questions can be found by searching:
  - Question text content
  - Answer text content
  - Subject name
  - Topic name
  - Paper name

#### Search Interface
- **Search Bar**: Large, prominent search input field
- **Search Button**: Click to execute search
- **Real-time Search**: Automatically searches as you type (minimum 2 characters)
- **Clear Results**: Results clear when search query is removed

#### Search Behavior
- **Minimum Characters**: 2 characters required
- **Case Insensitive**: Searches ignore letter case
- **Partial Matches**: Finds questions containing the search term
- **Live Results**: Updates as you type

### 2. Search Results Display

#### Result Cards
Each search result shows:
- **Question Preview**: First 150 characters of question text
- **Marks**: Points assigned to the question
- **Subject Badge**: Subject name with 📚 icon
- **Paper Badge**: Paper name with 📄 icon (if available)
- **Topic Badge**: Topic name with 📖 icon (if available)

#### Visual Indicators
- **Hover Effect**: Cards highlight on mouse over
- **Selected State**: Selected question has blue border and background
- **Click to Select**: Click any result card to load it for editing

#### Result Count
- Displays "Found X question(s)" above results
- Scrollable list for many results
- Maximum height with scroll for better UX

### 3. Question Editing

#### Edit Form Components

**Question Content Editor:**
- **Dual-Area Display**:
  - Top 60%: Formatted preview of question
  - Bottom 40%: Editable textarea with markdown
- **Text Formatting Buttons**: B (Bold), I (Italic), U (Underline)
- **Real-time Preview**: See formatting as you edit
- **Monospace Font**: Easy to see markdown syntax

**Answer Content Editor:**
- **Same Dual-Area Layout**: 60% preview, 40% edit
- **Independent Formatting**: Format answer separately from question
- **Preview Section**: Shows formatted answer in real-time

**Marks Input:**
- Number field for question marks/points
- Decimal support (e.g., 0.5, 2.5)
- Minimum value: 0
- Step increment: 0.5

**Question Information Display:**
- Read-only metadata shown in gray box:
  - Subject name
  - Paper name (if available)
  - Topic name (if available)

### 4. Edit Actions

#### Save Changes
- **Button**: Green "Save Changes" button with checkmark icon
- **Action**: Updates question in database
- **Validation**: Requires question text and answer text
- **Feedback**: Success message on completion
- **Auto-refresh**: Updates search results after save

#### Delete Question
- **Button**: Red "Delete" button with trash icon
- **Confirmation**: "Are you sure?" dialog before deletion
- **Warning**: States that action cannot be undone
- **Feedback**: Success message after deletion
- **Auto-refresh**: Removes from search results

#### Cancel Editing
- **Button**: Gray "Cancel" button
- **Action**: Clears selection and closes edit form
- **No Save**: Changes are discarded
- **Return**: Goes back to search results

## Workflow

### Complete Edit Process

#### Step 1: Search for Question
1. Click "Edit Questions" tab
2. Type search term (minimum 2 characters)
3. Press Enter or click "Search" button
4. View search results

#### Step 2: Select Question
1. Review search results
2. Click on the question card you want to edit
3. Edit form loads with question data
4. Question and answer appear in editors

#### Step 3: Edit Content
1. Modify question text in bottom textarea
2. Use B, I, U buttons to format text
3. View changes in preview area (top section)
4. Edit answer text similarly
5. Update marks if needed

#### Step 4: Save or Delete
1. Review changes in preview areas
2. Click "Save Changes" to update
   - OR -
3. Click "Delete" to remove question
4. Confirm any prompts
5. Success message appears

#### Step 5: Continue or Exit
1. Search for another question to edit
   - OR -
2. Switch to different tab
3. Changes are saved permanently

## Text Formatting

### Formatting Tools
Same as in Add Questions tab:
- **Bold**: `**text**` → **text**
- **Italic**: `*text*` → *text*
- **Underline**: `__text__` → <u>text</u>

### How to Format
1. Type or paste text
2. Select the text to format
3. Click B, I, or U button
4. Markdown syntax added automatically
5. Preview shows formatted result

### Scientific Names
Use italic (I) button for proper scientific notation:
```
*Homo sapiens*
*E. coli*
*Canis lupus*
```

## Use Cases

### 1. Fix Typos
**Scenario**: Question has spelling errors
**Steps**:
1. Search for question by subject or content
2. Select the question
3. Correct typos in question/answer text
4. Click "Save Changes"

### 2. Update Answers
**Scenario**: Answer needs clarification
**Steps**:
1. Search for question
2. Select it
3. Edit answer text to add more detail
4. Use formatting to emphasize key points
5. Save changes

### 3. Adjust Marks
**Scenario**: Question difficulty changed
**Steps**:
1. Find and select question
2. Update marks value
3. Save changes

### 4. Remove Duplicate
**Scenario**: Same question entered twice
**Steps**:
1. Search for duplicate
2. Select the duplicate entry
3. Click "Delete"
4. Confirm deletion

### 5. Format Scientific Names
**Scenario**: Question has unformatted species names
**Steps**:
1. Search and select question
2. Select species name in text
3. Click I (italic) button
4. Repeat for all scientific names
5. Save changes

## Search Tips

### Effective Searching

**By Subject**:
```
Search: "Mathematics"
Finds: All math questions
```

**By Topic**:
```
Search: "Algebra"
Finds: Algebra questions across subjects
```

**By Content**:
```
Search: "photosynthesis"
Finds: Questions mentioning photosynthesis
```

**By Marks**:
Search doesn't support marks directly, but you can:
1. Search by subject/topic
2. Browse results
3. Marks shown on each card

### Multiple Word Search
```
Search: "cell division"
Finds: Questions containing both "cell" AND "division"
```

### Partial Words
```
Search: "photo"
Finds: photosynthesis, photograph, photon, etc.
```

## Best Practices

### 1. Search Before Adding
- Search before creating new questions
- Avoid duplicates
- Check for similar questions

### 2. Review Before Saving
- Check preview areas
- Verify formatting looks correct
- Ensure marks are appropriate
- Confirm all required fields filled

### 3. Use Formatting Consistently
- Format scientific names in italics
- Bold key terms uniformly
- Underline only critical warnings

### 4. Backup Before Major Changes
- For bulk edits, note original content
- Consider exporting data periodically
- Test changes on one question first

### 5. Delete Carefully
- Deletion is permanent
- No undo feature
- Confirm you have the right question
- Consider deactivating instead (if feature exists)

## Keyboard Shortcuts

### Navigation
- **Tab**: Move between fields
- **Enter**: Submit search (in search box)
- **Escape**: Clear selection (when editing)

### Text Editing
- **Ctrl+A**: Select all text
- **Ctrl+C**: Copy selected text
- **Ctrl+V**: Paste text
- **Ctrl+Z**: Undo typing

## Validation Rules

### Required Fields
- ✅ Question text (cannot be empty)
- ✅ Answer text (cannot be empty)
- ⚠️ Marks (optional, keeps original if not changed)

### Field Limits
- Question text: No maximum
- Answer text: No maximum
- Marks: Must be non-negative number

## Error Handling

### Common Errors

**"No question selected"**
- **Cause**: Tried to save/delete without selecting question
- **Solution**: Click a search result first

**"Failed to search questions"**
- **Cause**: Database connection issue
- **Solution**: Check internet, refresh page, try again

**"Failed to update question"**
- **Cause**: Permission issue or network error
- **Solution**: Verify login, check connection, retry

**"Failed to delete question"**
- **Cause**: Question may be referenced elsewhere
- **Solution**: Contact administrator

### No Results Found
**Display**: Gray icon with "No questions found" message
**Possible Reasons**:
1. No questions match search term
2. Misspelled search term
3. Wrong subject/topic name
4. Database is empty

**Solutions**:
1. Try different search terms
2. Check spelling
3. Use broader terms
4. Search by subject instead of content

## Visual States

### Search Results
- **Unselected**: White background, gray border
- **Hover**: Light gray background, blue border
- **Selected**: Blue background, thick blue border

### Edit Form
- **Hidden**: No question selected
- **Visible**: Question selected, full edit interface
- **Saving**: Loading indicator (if implemented)

### Buttons
- **Enabled**: Full color, clickable
- **Disabled**: Faded, not clickable (e.g., Search with < 2 chars)
- **Hover**: Darker shade

## Technical Details

### Data Flow
1. User types in search box
2. After 2+ characters, search executes
3. Results fetched from database
4. Results displayed as cards
5. Click card → data loads into form
6. Edit → Update state
7. Save → PUT request to API
8. Success → Refresh results

### State Management
- `searchQuery`: Current search text
- `searchResults`: Array of found questions
- `selectedQuestion`: Currently editing question
- `editQuestionText`: Question editor content
- `editAnswerText`: Answer editor content
- `editMarks`: Marks field value

### API Endpoints Used
- `GET /api/questions/`: Fetch all questions for search
- `PUT /api/questions/{id}/`: Update question
- `DELETE /api/questions/{id}/`: Delete question

## Comparison with Add Questions

### Similarities
- Same text formatting tools (B, I, U)
- Same dual-area editor (60/40 split)
- Same markdown syntax
- Same preview rendering

### Differences
| Feature | Add Questions | Edit Questions |
|---------|--------------|----------------|
| Purpose | Create new | Modify existing |
| Search | No | Yes |
| Selection | N/A | Required |
| Subject/Topic | Dropdowns | Read-only display |
| Delete | No | Yes |
| Bulk Entry | Yes | No |
| Images | Upload new | View existing* |
| Voice Input | Yes | No* |

*Not currently implemented in Edit mode

## Future Enhancements

### Potential Features
1. **Image Editing**: Upload new images to existing questions
2. **Voice Input**: Add voice transcription to edit mode
3. **Bulk Edit**: Select multiple questions to edit at once
4. **Version History**: See previous versions of questions
5. **Duplicate Question**: Copy to create similar question
6. **Advanced Search**: Filter by marks, date, status
7. **Export**: Download selected questions
8. **Preview Mode**: See how question appears in exam

## Troubleshooting

### Search Not Working
**Check**:
1. Is search term at least 2 characters?
2. Is internet connection active?
3. Are there questions in database?
4. Is search button enabled?

### Can't Edit Question
**Check**:
1. Did you click a search result card?
2. Is edit form visible below?
3. Are textareas editable?
4. Is there an error message?

### Changes Not Saving
**Check**:
1. Is question text filled?
2. Is answer text filled?
3. Is internet connected?
4. Did you click "Save Changes"?
5. Do you have permission to edit?

### Formatting Not Showing
**Check**:
1. Is syntax correct? (`**bold**`, `*italic*`, `__underline__`)
2. Are you looking at preview area (top 60%)?
3. Is there a closing marker?
4. Try re-selecting and reformatting

## Support

### Getting Help
1. Check this documentation
2. Review error messages
3. Try the operation again
4. Check internet connection
5. Verify login status
6. Contact system administrator

### Reporting Issues
When reporting problems, include:
- What you were trying to do
- What you expected to happen
- What actually happened
- Any error messages
- Steps to reproduce

## Summary

The Edit Questions feature provides:
- ✅ Powerful search across all question content
- ✅ Easy selection from results
- ✅ Full editing with formatting support
- ✅ Real-time preview
- ✅ Safe deletion with confirmation
- ✅ Immediate feedback on actions
- ✅ Seamless integration with existing system

Use this tab to maintain and improve your question database by fixing errors, updating content, adjusting difficulty, and removing duplicates.
