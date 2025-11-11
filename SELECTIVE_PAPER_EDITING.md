# Selective Paper Editing Feature

## Overview
The selective paper editing feature allows teachers to choose which specific papers they want to update when editing a subject, rather than being forced to update all papers at once. This provides more control and prevents accidental changes to papers that don't need modification.

## Key Features

### 1. **Paper Selection Checkboxes**
- Each existing paper displays a checkbox for selection
- Only selected papers will be updated when you save
- New papers are automatically selected and will always be saved

### 2. **View Topics Button**
- Click the "View Topics" button (eye icon) next to any existing paper
- Opens a modal showing all current topics and sections for that paper
- Helps avoid duplicate topics when editing
- Read-only view - no accidental edits

### 3. **Visual Indicators**

#### Paper Status Badges:
- **"New" Badge** (Green): Indicates a newly added paper
- **"Selected" Badge** (Purple): Indicates an existing paper selected for editing

#### Paper Border Colors:
- **Purple Border**: Selected paper or new paper (will be saved)
- **Gray Border (faded)**: Unselected existing paper (will not be saved)

#### Input Field States:
- **Enabled**: Paper is selected - you can edit it
- **Disabled (grayed out)**: Paper is unselected - name field is read-only

## How to Use

### Scenario 1: Update Only Specific Papers

**Example**: You have a subject "Computer Science" with 3 papers (Paper 1, Paper 2, Paper 3). You only want to add topics to Paper 2.

**Steps**:
1. Click the purple "plus" icon to open full edit mode
2. Review the "Current Subject Information" to see existing papers
3. Check the checkbox next to "Paper 2" only
4. Add new topics to Paper 2 (use "View Topics" first to avoid duplicates)
5. Click "Save Changes"
6. Result: Only Paper 2 is updated. Paper 1 and Paper 3 remain unchanged.

### Scenario 2: View Topics Before Editing

**Example**: You want to add topics to "Paper 1" but don't remember what topics already exist.

**Steps**:
1. Open full edit mode for the subject
2. Click the "View Topics" button (eye icon) next to Paper 1
3. Review the existing topics in the modal:
   - Topics are displayed with blue badges
   - Sections are displayed with green badges
4. Note which topics already exist
5. Close the modal
6. Check the Paper 1 checkbox to select it
7. Add new topics that don't duplicate existing ones
8. Save changes

### Scenario 3: Add New Paper Without Touching Existing Papers

**Example**: You want to add "Paper 4" to a subject without modifying Paper 1, 2, or 3.

**Steps**:
1. Open full edit mode
2. Don't check any existing paper checkboxes
3. Click "Add Paper" button
4. Fill in the new paper's name, topics, and sections
5. The new paper is automatically marked with a "New" badge
6. Click "Save Changes"
7. Result: Paper 4 is added. Papers 1, 2, and 3 remain unchanged.

### Scenario 4: Mix of Updates and New Papers

**Example**: Update Paper 1, leave Paper 2 unchanged, and add Paper 4.

**Steps**:
1. Open full edit mode
2. Check the checkbox for Paper 1
3. Edit Paper 1 (add/modify topics)
4. Leave Paper 2 unchecked
5. Click "Add Paper" to create Paper 4
6. Fill in Paper 4 details
7. Click "Save Changes"
8. Success message shows:
   - "Updated 1 existing paper"
   - "Added 1 new paper"

## Important Notes

### ⚠️ Selection Requirements
- You must select at least one existing paper OR add at least one new paper
- If you click "Save" with no papers selected and no new papers, you'll get an error
- This prevents accidentally saving empty subjects

### 🎯 Auto-Selection for New Papers
- When you click "Add Paper", the new paper is automatically considered "selected"
- You don't need to manually select new papers
- New papers always get saved when you click "Save Changes"

### 🔒 Unselected Papers Are Protected
- Unselected existing papers cannot be edited (fields are disabled)
- These papers remain completely unchanged in the database
- This prevents accidental modifications

### 📊 Success Messages
When you save, the system tells you exactly what was updated:
```
Subject updated successfully!
• Updated 2 existing papers
• Added 1 new paper
```

## Benefits

1. **Precision**: Only update exactly what needs to be changed
2. **Safety**: Unselected papers are protected from accidental edits
3. **Efficiency**: No need to re-enter data for unchanged papers
4. **Clarity**: Visual indicators show exactly what will be saved
5. **Duplicate Prevention**: View existing topics before adding new ones

## Technical Details

### States Used
```javascript
- selectedPaperIndices: [] // Array of indices of selected papers
- showTopicsModal: false // Controls topic viewing modal
- viewingPaperTopics: null // Data for the paper being viewed
```

### Paper Classification Logic
```javascript
const isExistingPaper = paperIndex < originalPaperCount;
const isNewPaper = paperIndex >= originalPaperCount;
const isSelected = selectedPaperIndices.includes(paperIndex);
```

### Save Logic
- Papers saved = (Selected existing papers) + (All new papers)
- Papers ignored = (Unselected existing papers)

## FAQ

**Q: What happens if I don't select any papers?**
A: You'll get an error asking you to select at least one paper or add a new one.

**Q: Can I view topics for new papers I just added?**
A: No, the "View Topics" button only appears for existing papers. New papers don't have existing data to view.

**Q: What if I select a paper but don't make any changes?**
A: The paper will still be saved with its current data. No harm done.

**Q: Can I uncheck all papers and just add new ones?**
A: Yes! You can leave all existing papers unchecked and only add new papers.

**Q: How do I know which papers are selected?**
A: Look for:
- Purple border around the paper card
- "Selected" badge next to the paper name
- Checkbox is checked
- Input fields are enabled (not grayed out)

**Q: Can I change my mind about which papers to select?**
A: Yes, you can check and uncheck papers as many times as you want before clicking "Save Changes".

## Related Features

- **Duplicate Detection**: Works with selective editing to prevent duplicates in selected papers
- **Section Optionality**: Sections remain optional for both selected and new papers
- **Current Info Display**: Shows all papers (helps decide which to select)

---

**Last Updated**: January 2025
