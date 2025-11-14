# Quick Start Guide - Testing Paper Generation# Quick Start Guide: Testing Subject CRUD Features



## Prerequisites Check## Prerequisites



Before starting, ensure you have:1. **Backend server must be running**

- ✅ Python installed (3.8+)2. **Frontend development server must be running**

- ✅ Node.js installed (14+)3. **MongoDB must be running** (Atlas local or regular MongoDB)

- ✅ Database populated with sample questions (run `python create_sample_questions.py` if not done)4. **Must be logged in** as an editor user



## Step 1: Start Backend Server## Step-by-Step Testing Guide



### Windows PowerShell### Step 1: Start Backend (if not running)

```powershell```powershell

# Navigate to Django backendcd c:\Users\pc\Desktop\exam\backend

cd django_backendnpm run dev

```

# Activate virtual environment (if you have one)

# .\venv\Scripts\Activate.ps1Expected output:

```

# Start Django serverServer running on port 5000

python manage.py runserverConnected to MongoDB: test

``````



You should see:### Step 2: Start Frontend (if not running)

```Open a new PowerShell window:

Starting development server at http://127.0.0.1:8000/```powershell

```cd c:\Users\pc\Desktop\exam\frontend\exam

npm start

## Step 2: Start Frontend Server```



### Open a NEW PowerShell windowBrowser should automatically open to `http://localhost:3000`

```powershell

# Navigate to frontend### Step 3: Login

cd frontend\examUse one of the test users:

- **Editor**: 

# Install dependencies (first time only)  - Phone: `+254700000001`

npm install  - Password: `editor123`



# Start React development server### Step 4: Navigate to Subjects Tab

npm start1. Click on "Add New Subject" tab in the dashboard

```2. You should see two sections:

   - **Manage Subjects** (top)

Browser should automatically open to `http://localhost:3000`   - **Add New Subject** (bottom)



## Step 3: Test the Application### Step 5: View Existing Subjects

The "Manage Subjects" section should show:

### Login- Existing subjects from the database

1. Use your existing user credentials- If empty, you'll see "No subjects found"

2. Or create a new account through the signup page- If loading, you'll see a spinner

- Click the **Refresh** button to reload subjects

### Access Paper Generation

1. After login, you'll be on the **User Dashboard**### Step 6: Test Creating a New Subject

2. Click on **"KCSE Paper Generation"** button (should be selected by default)1. Scroll down to "Add New Subject" section

3. You should see the **Biology Paper 1 Generator** interface2. Enter a subject name (e.g., "Biology")

3. Add a paper:

### Generate Your First Paper   - Enter paper name (e.g., "Paper 1")

   - Add topics (e.g., "Cells", "Genetics", "Evolution")

1. **Select Topics:**   - Add sections (optional, e.g., "Section A", "Section B")

   - You'll see 6 Biology topics with checkboxes4. Click "Add Paper" to add more papers if needed

   - Each shows available questions (e.g., "Cell Biology: 12 questions")5. Click "Add Subject" button

   - Select 3-4 topics (e.g., Cell Biology, Nutrition, Ecology)6. You should see a success alert

7. The subject should appear in the "Manage Subjects" section above

2. **Generate:**

   - Click the **"Generate Paper"** button### Step 7: Test Viewing Subject Hierarchy

   - Wait 2-5 seconds (you'll see a loading spinner)1. In "Manage Subjects" section, find your newly created subject

   - Success message will appear with paper code (e.g., "BP1-ABC123")2. Click the **arrow** icon next to the subject name

3. The subject should expand showing all papers

3. **View Paper:**4. Click the **arrow** next to a paper name

   - Click **"View Full Paper"** button5. The paper should expand showing topics and sections

   - You'll see:

     - Paper information (marks, questions, status)### Step 8: Test Edit Subject Name

     - Mark distribution chart1. Click the **blue edit icon** (pencil) next to a subject name

     - All questions with answers2. A modal should appear with the current name

3. Change the name (e.g., "Biology" → "Advanced Biology")

4. **Go Back:**4. Click "Save Changes"

   - Click **"← Back"** to return to dashboard5. You should see a success alert

   - Generate another paper with different topics6. The subject name should update in the list



### View Paper History### Step 9: Test Edit Paper Name

1. Expand a subject to see its papers

1. Click the **"Generated Papers"** tab2. Click the **blue edit icon** next to a paper name

2. See all your previously generated papers3. Change the paper name (e.g., "Paper 1" → "Paper 1A")

3. Click **"View Paper"** on any entry to see details4. Click "Save Changes"

5. Verify the paper name updates

## Expected Results

### Step 10: Test Edit Topic Name

### Sample Generation Result1. Expand a paper to see its topics

```2. Click the **blue edit icon** next to a topic

✅ Paper Generated Successfully!3. Change the topic name

   Unique Code: BP1-ABC1234. Click "Save Changes"

   Total Marks: 805. Verify the topic name updates

   Questions: 28

   Status: VALID### Step 11: Test Edit Section Name

```1. Expand a paper to see its sections

2. Click the **blue edit icon** next to a section

### Sample Paper Structure3. Change the section name

- **Questions:** 25-30 questions4. Click "Save Changes"

- **Marks:** Exactly 80 marks total5. Verify the section name updates

- **Distribution:**

  - 1-mark: 30-40% (around 10-12 questions)### Step 12: Test Delete Topic

  - 2-mark: 35-45% (around 14-18 questions)1. Expand a paper to see its topics

  - 3-mark: 15-25% (around 4-7 questions)2. Click the **red delete icon** (trash) next to a topic

  - 4-mark: 0-5% (0-1 questions)3. A confirmation modal should appear

4. Read the warning message

## Troubleshooting5. Click "Delete" to confirm

6. You should see a success alert

### Backend Not Starting7. The topic should be removed from the list

```powershell

# Check Python version### Step 13: Test Delete Section

python --version1. Expand a paper to see its sections

2. Click the **red delete icon** next to a section

# Try with python33. Confirm deletion

python3 manage.py runserver4. Verify the section is removed



# Check migrations### Step 14: Test Delete Paper

python manage.py migrate1. Expand a subject to see its papers

```2. Click the **red delete icon** next to a paper

3. Read the warning (all topics and sections will be affected)

### Frontend Not Starting4. Confirm deletion

```powershell5. Verify the paper is removed

# Clear node_modules and reinstall

Remove-Item -Recurse -Force node_modules### Step 15: Test Delete Subject

npm install1. Click the **red delete icon** next to a subject

2. Read the warning (all papers, topics, sections will be affected)

# Try different port if 3000 is busy3. Confirm deletion

$env:PORT=3001; npm start4. Verify the subject is removed (soft delete)

```

### Step 16: Test Persistence

### "Failed to load topics" Error1. Create a new subject

- Ensure backend server is running on port 80002. Refresh the browser page (F5)

- Check REACT_APP_API_URL in `.env` file3. Login again

- Check browser console for CORS errors4. Navigate to Subjects tab

5. Verify your subject is still there (data persisted to database)

### "Failed to generate paper" Error

- Ensure sample questions were created successfully## Expected Behavior Checklist

- Try selecting more topics (4-6 topics recommended)

- Check backend console for error messages- ✅ Subjects load automatically when switching to Subjects tab

- ✅ Loading spinner appears while fetching data

### Database Issues- ✅ Subjects display in a collapsible tree structure

```powershell- ✅ Paper counts, topic counts, section counts are shown

# Re-run sample questions script- ✅ Edit modals open when clicking edit icons

cd django_backend- ✅ Delete confirmation modals appear when clicking delete icons

python create_sample_questions.py- ✅ Success alerts show after successful operations

```- ✅ Error alerts show if operations fail

- ✅ List refreshes automatically after create/edit/delete

## Testing Checklist- ✅ Changes persist after page reload

- ✅ Nested structure (subject → paper → topics/sections) works correctly

### ✅ Basic Functionality- ✅ "None" sections don't show edit/delete buttons

- [ ] Backend server starts successfully

- [ ] Frontend loads without errors## Visual Indicators to Look For

- [ ] Can login to application

- [ ] Paper Generation dashboard loads### Icons:

- [ ] See 6 Biology topics with statistics- **Arrow Right** (→): Collapsed item

- [ ] Can select/deselect topics- **Arrow Down** (↓): Expanded item

- [ ] Generate button works- **Blue Pencil**: Edit button

- [ ] Paper generates successfully- **Red Trash**: Delete button

- [ ] Can view generated paper details- **Green Refresh**: Reload button

- [ ] Paper history tab shows papers

- [ ] Can view papers from history### Badges:

- **Green badge**: Paper count (e.g., "2 papers")

### ✅ Edge Cases- **Blue badge**: Topic count (e.g., "5 topics")

- [ ] Try generating with only 1 topic- **Purple badge**: Section count (e.g., "3 sections")

- [ ] Try generating with all 6 topics

- [ ] Generate multiple papers in succession### Colors:

- [ ] Check different mark distributions- **Green**: Primary actions, subject headers

- [ ] Verify questions are different each time- **Blue**: Paper headers, edit actions

- **Red**: Delete actions, warnings

### ✅ UI/UX- **Gray**: Neutral states, disabled items

- [ ] Interface is responsive

- [ ] Loading spinners appear during operations## Common Issues & Solutions

- [ ] Error messages are clear

- [ ] Success messages display correctly### Issue: "No subjects found"

- [ ] Can navigate between tabs smoothly**Possible Causes**:

- [ ] Back button works in viewer- Database is empty

- Backend not running

## Sample Test Scenarios- Authentication token expired



### Scenario 1: Single Topic Paper**Solution**:

```1. Create a subject using "Add New Subject" form

1. Select only "Cell Biology"2. Check backend console for errors

2. Click Generate3. Try refreshing the page and logging in again

3. Expected: Paper with 12 questions from Cell Biology

4. Total marks should be close to 80### Issue: Edit/Delete buttons don't work

```**Possible Causes**:

- Backend not running

### Scenario 2: All Topics Paper- Network error

```- Authentication issue

1. Click "Select All"

2. Click Generate**Solution**:

3. Expected: Questions distributed across all 6 topics1. Check backend is running: `http://localhost:5000/api/subjects`

4. Each topic should have questions within its mark range2. Open browser DevTools → Network tab

```3. Check for failed API requests

4. Verify JWT token in localStorage

### Scenario 3: Subset of Topics

```### Issue: Changes don't persist

1. Select: Cell Biology, Nutrition, Ecology (3 topics)**Possible Causes**:

2. Click Generate- MongoDB not running

3. Expected: Balanced distribution across selected topics- Connection string incorrect

4. Proportional mark adjustment should work- Write permissions issue

```

**Solution**:

## API Endpoints to Test1. Check MongoDB status: `atlas deployments list`

2. Verify connection in backend console

You can also test backend directly:3. Check backend/.env file has correct MONGODB_URI



### Get Topics Statistics## API Testing with PowerShell

```bash

# PowerShellYou can also test the API directly:

$headers = @{"Authorization"="Bearer YOUR_TOKEN"}

Invoke-RestMethod -Uri "http://localhost:8000/api/papers/efa6d535-6a6b-45ac-931a-d20b9ccf15aa/topics/statistics" -Headers $headers### Get All Subjects:

``````powershell

$token = "YOUR_JWT_TOKEN_HERE"

### Generate Paper$headers = @{

```bash    "Authorization" = "Bearer $token"

# PowerShell    "Content-Type" = "application/json"

$headers = @{}

    "Authorization"="Bearer YOUR_TOKEN"Invoke-RestMethod -Uri "http://localhost:5000/api/subjects" -Headers $headers -Method GET

    "Content-Type"="application/json"```

}

$body = @{### Create Subject:

    paper_id = "efa6d535-6a6b-45ac-931a-d20b9ccf15aa"```powershell

    selected_topics = @("TOPIC_ID_1", "TOPIC_ID_2")$body = @{

} | ConvertTo-Json    name = "Chemistry"

    papers = @(

Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/papers/generate" -Headers $headers -Body $body        @{

```            name = "Paper 1"

            topics = @("Organic Chemistry", "Inorganic Chemistry")

## Performance Expectations            sections = @("Section A", "Section B")

        }

### Generation Time    )

- **Normal:** 2-5 seconds} | ConvertTo-Json -Depth 10

- **With backtracking:** 5-10 seconds

- **Maximum:** 15 seconds (if retrying multiple times)Invoke-RestMethod -Uri "http://localhost:5000/api/subjects" -Headers $headers -Method POST -Body $body

```

### Frontend Load Time

- **Initial load:** 1-2 seconds## Next Steps After Testing

- **Topic loading:** 0.5-1 second

- **Paper viewing:** 0.3-0.5 secondsOnce you've verified all CRUD operations work:



## Success Indicators1. ✅ Test with different user accounts

2. ✅ Test with larger datasets (100+ subjects)

You'll know everything is working when:3. ✅ Test network failures (stop backend mid-operation)

1. ✅ No console errors in browser4. ✅ Test concurrent edits (multiple browser tabs)

2. ✅ Topics load and display correctly5. ✅ Test mobile responsiveness

3. ✅ Paper generates with status "VALID"6. ✅ Add additional features (search, filter, sort)

4. ✅ Total marks = 80

5. ✅ Question count between 25-30## Support

6. ✅ All questions have answers

7. ✅ Mark distribution looks reasonableIf you encounter any issues:

8. ✅ Papers appear in history tab1. Check the browser console (F12)

2. Check the backend console logs

## Next Steps After Testing3. Review `SUBJECT_CRUD_GUIDE.md` for detailed documentation

4. Check MongoDB connection status

### If Everything Works5. Verify all dependencies are installed

1. Test with different users

2. Generate multiple papers---

3. Verify question randomization

4. Check validation edge casesHappy Testing! 🎉

5. Test error scenarios

### If Issues Found
1. Check browser console for errors
2. Check backend console for errors
3. Verify database has sample questions
4. Ensure migrations are up to date
5. Check CORS configuration

## Development URLs

- **Frontend:** http://localhost:3000
- **Backend:** http://localhost:8000
- **API Docs:** http://localhost:8000/api/ (if available)
- **Admin:** http://localhost:8000/admin (if enabled)

## Sample Question Distribution

Currently available in database:
```
Cell Biology:    12 questions (4×1m, 5×2m, 3×3m, 0×4m)
Nutrition:       10 questions (3×1m, 5×2m, 2×3m, 0×4m)
Respiration:      9 questions (3×1m, 4×2m, 2×3m, 0×4m)
Transport:        9 questions (3×1m, 4×2m, 2×3m, 0×4m)
Reproduction:    10 questions (3×1m, 5×2m, 2×3m, 0×4m)
Ecology:          9 questions (3×1m, 4×2m, 2×3m, 0×4m)
───────────────────────────────────────────────────────
TOTAL:           59 questions (19×1m, 27×2m, 13×3m, 0×4m)
```

## Happy Testing! 🎉

If you encounter any issues not covered here, please document:
1. What you were trying to do
2. What happened instead
3. Any error messages
4. Browser and OS information

---

**Last Updated:** January 2024  
**System:** KCSE Examination System - Paper Generation Module  
**Version:** 1.0
