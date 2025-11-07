# Quick Reference Card - Subject CRUD

## 🚀 Quick Start (3 Steps)

1. **Start Backend**: `cd backend && npm run dev`
2. **Start Frontend**: `cd frontend/exam && npm start`
3. **Go to**: Subjects tab in EditorDashboard

---

## 📋 Main Actions

| Action | How To | Icon |
|--------|--------|------|
| **View Subjects** | Click arrow next to subject name | ▶/▼ |
| **Refresh List** | Click green refresh button | 🔄 |
| **Edit Name** | Click blue pencil icon | ✏️ |
| **Delete Item** | Click red trash icon | 🗑️ |
| **Add Subject** | Fill form at bottom, click "Add Subject" | ➕ |

---

## 🎨 Visual Guide

### Hierarchy
```
Subject (green)
  └── Paper (blue)
      ├── Topics (list)
      └── Sections (list)
```

### Icons
- **▶** = Click to expand
- **▼** = Click to collapse
- **✏️** = Edit
- **🗑️** = Delete
- **❌** = Remove (in forms)
- **🔄** = Refresh

### Badges
- 🟢 **Green** = Paper count
- 🔵 **Blue** = Topic count  
- 🟣 **Purple** = Section count

---

## 🔧 CRUD Operations

### CREATE
```
1. Scroll to "Add New Subject" section
2. Enter subject name
3. Add papers with topics and sections
4. Click "Add Subject"
✅ Success: Subject appears in list above
```

### READ
```
1. View "Manage Subjects" section
2. Click arrow to expand subject
3. Click arrow to expand paper
4. See topics and sections
```

### UPDATE
```
1. Click blue edit icon (✏️)
2. Change name in modal
3. Click "Save Changes"
✅ Success: Name updates immediately
```

### DELETE
```
1. Click red delete icon (🗑️)
2. Read warning in modal
3. Click "Delete" to confirm
✅ Success: Item removed from list
```

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| No subjects showing | Click refresh button or create a new subject |
| Edit/Delete not working | Check backend is running on port 5000 |
| "Failed to load" error | Verify MongoDB is running and connected |
| Changes don't persist | Check backend console for database errors |

---

## 📞 API Endpoints (for testing)

```bash
# Get all subjects
GET http://localhost:5000/api/subjects

# Create subject
POST http://localhost:5000/api/subjects
Body: { name: "...", papers: [...] }

# Update subject
PUT http://localhost:5000/api/subjects/:id
Body: { name: "..." }

# Delete subject
DELETE http://localhost:5000/api/subjects/:id
```

⚠️ **Requires JWT token in Authorization header**

---

## 📚 Files to Know

| File | Purpose |
|------|---------|
| `backend/routes/subjects.js` | API endpoints (10 endpoints) |
| `frontend/src/services/subjectService.js` | API calls (13 functions) |
| `frontend/src/components/EditorDashboard.js` | UI components & logic |
| `backend/models/schema.js` | Database schemas |

---

## 🎯 Key Features

✅ View all subjects from database  
✅ Expandable tree structure  
✅ Edit subjects, papers, topics, sections  
✅ Delete with confirmation  
✅ Create new subjects with nested structure  
✅ Real-time updates  
✅ Loading indicators  
✅ Error handling  
✅ Mobile responsive  

---

## 💡 Pro Tips

1. **Refresh button**: Use after making changes from another browser/device
2. **Expand/Collapse**: Click arrow, not the name
3. **Delete cascade**: Deleting a subject affects all papers/topics/sections
4. **Sections "None"**: Papers without sections show as "None"
5. **Tokens**: JWT token auto-included from localStorage
6. **Network tab**: Use browser DevTools to debug API issues

---

## 🔐 Authentication

Login as:
- **Editor**: +254700000001 / editor123
- **Admin**: +254700000000 / admin123

Token stored in: `localStorage.getItem('token')`

---

## 📖 Full Documentation

- **SUBJECT_CRUD_GUIDE.md** - Complete feature guide
- **TESTING_GUIDE.md** - Step-by-step testing
- **IMPLEMENTATION_SUMMARY.md** - Technical details
- **UI_LAYOUT.md** - Visual mockups
- **QUICK_REFERENCE.md** - This file

---

## 🎓 Common Workflows

### Workflow 1: Add New Subject
```
Login → Subjects Tab → Add New Subject → 
Fill Form → Add Subject → See in List Above
```

### Workflow 2: Edit Existing
```
Login → Subjects Tab → Expand Subject → 
Click Edit Icon → Change Name → Save → Updated!
```

### Workflow 3: Delete Item
```
Login → Subjects Tab → Expand Subject → 
Click Delete Icon → Confirm → Removed!
```

### Workflow 4: Browse Hierarchy
```
Login → Subjects Tab → Click Subject Arrow → 
Click Paper Arrow → View Topics & Sections
```

---

## ⌨️ Keyboard Shortcuts (Future)

Currently use mouse/touch. Future keyboard navigation:
- `Tab` - Navigate elements
- `Enter` - Activate button
- `Escape` - Close modal
- `Space` - Toggle expand/collapse

---

## 📊 Status Indicators

| State | What You See |
|-------|--------------|
| **Loading** | Spinning circle animation |
| **Empty** | "No subjects found" message |
| **Success** | Green alert box |
| **Error** | Red alert box |
| **Collapsed** | ▶ arrow icon |
| **Expanded** | ▼ arrow icon |

---

## 🎨 Color Meanings

| Color | Meaning |
|-------|---------|
| 🟢 **Green** | Primary actions, success, subjects |
| 🔵 **Blue** | Secondary actions, papers, edit |
| 🔴 **Red** | Danger, delete, warnings |
| 🟣 **Purple** | Sections, tertiary info |
| ⚫ **Gray** | Neutral, disabled, background |

---

## 🚦 HTTP Status Codes

| Code | Meaning | What To Do |
|------|---------|------------|
| 200 | Success | Nothing, it worked! |
| 201 | Created | New subject added |
| 400 | Bad Request | Check form input |
| 401 | Unauthorized | Login again |
| 404 | Not Found | Item doesn't exist |
| 500 | Server Error | Check backend logs |

---

## 🔍 Debugging Checklist

- [ ] Backend running? (`http://localhost:5000`)
- [ ] Frontend running? (`http://localhost:3000`)
- [ ] MongoDB running? (Atlas local or regular)
- [ ] Logged in? (Check localStorage for token)
- [ ] Network errors? (Check browser DevTools → Network tab)
- [ ] Backend errors? (Check backend console logs)
- [ ] CORS issues? (Backend should have CORS enabled)

---

## 📱 Browser Support

| Browser | Status |
|---------|--------|
| Chrome | ✅ Fully supported |
| Firefox | ✅ Fully supported |
| Edge | ✅ Fully supported |
| Safari | ⚠️ Needs testing |
| Mobile | ⚠️ Needs testing |

---

## 🔗 Related Backend Routes

```javascript
// In backend/routes/subjects.js

POST   /api/subjects              - Create
GET    /api/subjects              - Read all
GET    /api/subjects/:id          - Read one
PUT    /api/subjects/:id          - Update
DELETE /api/subjects/:id          - Delete
GET    /api/subjects/:sId/papers/:pId/topics - Filter topics
PUT    /api/subjects/topics/:id   - Update topic
DELETE /api/subjects/topics/:id   - Delete topic
PUT    /api/subjects/sections/:id - Update section
DELETE /api/subjects/sections/:id - Delete section
```

---

## 💾 Database Collections

```javascript
subjects   // Main subjects
papers     // Papers within subjects
topics     // Topics within papers
sections   // Sections within papers
questions  // Questions linked to all above
users      // Users (editors, admins)
otplogs    // OTP verification logs
sessions   // User sessions
```

---

## 🎯 Testing Scenarios

1. **Happy Path**: Create → View → Edit → Delete
2. **Error Path**: Invalid input, network failure
3. **Edge Cases**: Empty sections, many papers, long names
4. **Concurrency**: Multiple users editing same subject
5. **Performance**: 100+ subjects, slow network

---

## 📞 Need Help?

1. Check browser console (F12)
2. Check backend console logs
3. Review documentation files
4. Test API with PowerShell/Postman
5. Verify database connection

---

## ✨ Success Criteria

You'll know it's working when:
- ✅ Subjects appear in "Manage Subjects"
- ✅ Arrows expand/collapse correctly
- ✅ Edit modal opens and saves
- ✅ Delete modal confirms and removes
- ✅ New subjects appear after creation
- ✅ Changes persist after page reload

---

## 🎉 You're All Set!

Everything is ready to use. Just start the servers and navigate to the Subjects tab!

**Quick Command**:
```powershell
# Terminal 1
cd c:\Users\pc\Desktop\exam\backend
npm run dev

# Terminal 2  
cd c:\Users\pc\Desktop\exam\frontend\exam
npm start
```

Then login and go to "Add New Subject" tab! 🚀
