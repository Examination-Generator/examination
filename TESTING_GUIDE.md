# Quick Start Guide: Testing Subject CRUD Features

## Prerequisites

1. **Backend server must be running**
2. **Frontend development server must be running**
3. **MongoDB must be running** (Atlas local or regular MongoDB)
4. **Must be logged in** as an editor user

## Step-by-Step Testing Guide

### Step 1: Start Backend (if not running)
```powershell
cd c:\Users\pc\Desktop\exam\backend
npm run dev
```

Expected output:
```
Server running on port 5000
Connected to MongoDB: test
```

### Step 2: Start Frontend (if not running)
Open a new PowerShell window:
```powershell
cd c:\Users\pc\Desktop\exam\frontend\exam
npm start
```

Browser should automatically open to `http://localhost:3000`

### Step 3: Login
Use one of the test users:
- **Editor**: 
  - Phone: `+254700000001`
  - Password: `editor123`

### Step 4: Navigate to Subjects Tab
1. Click on "Add New Subject" tab in the dashboard
2. You should see two sections:
   - **Manage Subjects** (top)
   - **Add New Subject** (bottom)

### Step 5: View Existing Subjects
The "Manage Subjects" section should show:
- Existing subjects from the database
- If empty, you'll see "No subjects found"
- If loading, you'll see a spinner
- Click the **Refresh** button to reload subjects

### Step 6: Test Creating a New Subject
1. Scroll down to "Add New Subject" section
2. Enter a subject name (e.g., "Biology")
3. Add a paper:
   - Enter paper name (e.g., "Paper 1")
   - Add topics (e.g., "Cells", "Genetics", "Evolution")
   - Add sections (optional, e.g., "Section A", "Section B")
4. Click "Add Paper" to add more papers if needed
5. Click "Add Subject" button
6. You should see a success alert
7. The subject should appear in the "Manage Subjects" section above

### Step 7: Test Viewing Subject Hierarchy
1. In "Manage Subjects" section, find your newly created subject
2. Click the **arrow** icon next to the subject name
3. The subject should expand showing all papers
4. Click the **arrow** next to a paper name
5. The paper should expand showing topics and sections

### Step 8: Test Edit Subject Name
1. Click the **blue edit icon** (pencil) next to a subject name
2. A modal should appear with the current name
3. Change the name (e.g., "Biology" → "Advanced Biology")
4. Click "Save Changes"
5. You should see a success alert
6. The subject name should update in the list

### Step 9: Test Edit Paper Name
1. Expand a subject to see its papers
2. Click the **blue edit icon** next to a paper name
3. Change the paper name (e.g., "Paper 1" → "Paper 1A")
4. Click "Save Changes"
5. Verify the paper name updates

### Step 10: Test Edit Topic Name
1. Expand a paper to see its topics
2. Click the **blue edit icon** next to a topic
3. Change the topic name
4. Click "Save Changes"
5. Verify the topic name updates

### Step 11: Test Edit Section Name
1. Expand a paper to see its sections
2. Click the **blue edit icon** next to a section
3. Change the section name
4. Click "Save Changes"
5. Verify the section name updates

### Step 12: Test Delete Topic
1. Expand a paper to see its topics
2. Click the **red delete icon** (trash) next to a topic
3. A confirmation modal should appear
4. Read the warning message
5. Click "Delete" to confirm
6. You should see a success alert
7. The topic should be removed from the list

### Step 13: Test Delete Section
1. Expand a paper to see its sections
2. Click the **red delete icon** next to a section
3. Confirm deletion
4. Verify the section is removed

### Step 14: Test Delete Paper
1. Expand a subject to see its papers
2. Click the **red delete icon** next to a paper
3. Read the warning (all topics and sections will be affected)
4. Confirm deletion
5. Verify the paper is removed

### Step 15: Test Delete Subject
1. Click the **red delete icon** next to a subject
2. Read the warning (all papers, topics, sections will be affected)
3. Confirm deletion
4. Verify the subject is removed (soft delete)

### Step 16: Test Persistence
1. Create a new subject
2. Refresh the browser page (F5)
3. Login again
4. Navigate to Subjects tab
5. Verify your subject is still there (data persisted to database)

## Expected Behavior Checklist

- ✅ Subjects load automatically when switching to Subjects tab
- ✅ Loading spinner appears while fetching data
- ✅ Subjects display in a collapsible tree structure
- ✅ Paper counts, topic counts, section counts are shown
- ✅ Edit modals open when clicking edit icons
- ✅ Delete confirmation modals appear when clicking delete icons
- ✅ Success alerts show after successful operations
- ✅ Error alerts show if operations fail
- ✅ List refreshes automatically after create/edit/delete
- ✅ Changes persist after page reload
- ✅ Nested structure (subject → paper → topics/sections) works correctly
- ✅ "None" sections don't show edit/delete buttons

## Visual Indicators to Look For

### Icons:
- **Arrow Right** (→): Collapsed item
- **Arrow Down** (↓): Expanded item
- **Blue Pencil**: Edit button
- **Red Trash**: Delete button
- **Green Refresh**: Reload button

### Badges:
- **Green badge**: Paper count (e.g., "2 papers")
- **Blue badge**: Topic count (e.g., "5 topics")
- **Purple badge**: Section count (e.g., "3 sections")

### Colors:
- **Green**: Primary actions, subject headers
- **Blue**: Paper headers, edit actions
- **Red**: Delete actions, warnings
- **Gray**: Neutral states, disabled items

## Common Issues & Solutions

### Issue: "No subjects found"
**Possible Causes**:
- Database is empty
- Backend not running
- Authentication token expired

**Solution**:
1. Create a subject using "Add New Subject" form
2. Check backend console for errors
3. Try refreshing the page and logging in again

### Issue: Edit/Delete buttons don't work
**Possible Causes**:
- Backend not running
- Network error
- Authentication issue

**Solution**:
1. Check backend is running: `http://localhost:5000/api/subjects`
2. Open browser DevTools → Network tab
3. Check for failed API requests
4. Verify JWT token in localStorage

### Issue: Changes don't persist
**Possible Causes**:
- MongoDB not running
- Connection string incorrect
- Write permissions issue

**Solution**:
1. Check MongoDB status: `atlas deployments list`
2. Verify connection in backend console
3. Check backend/.env file has correct MONGODB_URI

## API Testing with PowerShell

You can also test the API directly:

### Get All Subjects:
```powershell
$token = "YOUR_JWT_TOKEN_HERE"
$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}
Invoke-RestMethod -Uri "http://localhost:5000/api/subjects" -Headers $headers -Method GET
```

### Create Subject:
```powershell
$body = @{
    name = "Chemistry"
    papers = @(
        @{
            name = "Paper 1"
            topics = @("Organic Chemistry", "Inorganic Chemistry")
            sections = @("Section A", "Section B")
        }
    )
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://localhost:5000/api/subjects" -Headers $headers -Method POST -Body $body
```

## Next Steps After Testing

Once you've verified all CRUD operations work:

1. ✅ Test with different user accounts
2. ✅ Test with larger datasets (100+ subjects)
3. ✅ Test network failures (stop backend mid-operation)
4. ✅ Test concurrent edits (multiple browser tabs)
5. ✅ Test mobile responsiveness
6. ✅ Add additional features (search, filter, sort)

## Support

If you encounter any issues:
1. Check the browser console (F12)
2. Check the backend console logs
3. Review `SUBJECT_CRUD_GUIDE.md` for detailed documentation
4. Check MongoDB connection status
5. Verify all dependencies are installed

---

Happy Testing! 🎉
