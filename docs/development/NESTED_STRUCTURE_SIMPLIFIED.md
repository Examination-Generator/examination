# Nested Question Structure - Simplified Implementation

## Summary of Changes

The nested question structure has been **simplified** based on your requirement that users only need to identify if a question is nested and provide the total marks.

## What Changed

### 1. Database Model (api/models.py)
- **`is_nested`** field: Boolean flag (True for nested, False for standalone)
- **`nested_parts`** field: Now **optional** (nullable) - not required for paper generation
- **`marks`** field: Total marks for the question (same for both nested and standalone)

### 2. Migration Applied
- **Migration 0005**: Made `nested_parts` nullable and updated help text
- Old questions deleted and replaced with simplified structure

### 3. New Management Command
- Created `add_simple_questions.py` command
- Generates 100 nested + 150 standalone = 250 questions
- **No parts breakdown** - only `is_nested=True` and total marks

## Current Database Status

### Nested Questions (100 total)
- **4 marks**: 15 questions
- **5 marks**: 36 questions  
- **6 marks**: 35 questions
- **7 marks**: 14 questions

**Distribution by Topic:**
- Cell Biology: 18 questions
- Ecology: 16 questions
- Nutrition: 16 questions
- Reproduction: 13 questions
- Respiration: 21 questions
- Transport: 16 questions

### Standalone Questions (150 total)
- **1 mark**: 33 questions
- **2 marks**: 62 questions (preferred)
- **3 marks**: 38 questions (preferred)
- **4 marks**: 17 questions

## How Users Should Create Questions

When creating a question in the database, users only need to:

1. **Set `is_nested`**: 
   - `True` if the question has multiple parts (a, b, c, d)
   - `False` if it's a standalone single question

2. **Set `marks`**: 
   - Enter the **total marks** only
   - For nested: typically 4-7 marks
   - For standalone: typically 1-4 marks

3. **`nested_parts` field**: 
   - Can be left **NULL** or empty
   - Not used by the paper generation algorithm
   - Optional - can store part details if needed for other purposes

## Paper Generation Algorithm

The algorithm uses:
- ✅ `is_nested` flag to distinguish question types
- ✅ `marks` field for mark calculations
- ❌ `nested_parts` - **NOT USED** (algorithm only cares about total marks)

### Generation Strategy:
1. **Phase 1**: Select 10-18 nested questions (50-65 marks total)
   - Strategic selection: queries for exact marks when close to target
2. **Phase 2**: Fill remaining marks with standalone (prefer 2-3 marks)
3. **Result**: 22-30 questions, exactly 80 marks

## Files Modified

1. **api/models.py** - Made `nested_parts` optional
2. **api/migrations/0005_make_nested_parts_optional.py** - New migration
3. **api/management/commands/add_simple_questions.py** - New command
4. **Database** - 250 questions with simplified structure

## Testing Next

Run paper generation tests to verify:
- Papers generate with 22-30 questions
- Exactly 80 marks total
- Nested: 10-18 questions, 50-65 marks
- Standalone fills remaining marks
- Success rate is high with 100 nested questions available
