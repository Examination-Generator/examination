# Backend Fix Required - Biology Paper 2 Generation

## Error Found
```
'ascii' codec can't encode character '\u2713' in position 1: ordinal not in range(128)
```

## Problem
The backend Python file `biology_paper2_generation.py` contains Unicode characters (✓, ⚠, etc.) in print statements that cannot be encoded in ASCII.

## Solution Options

### Option 1: Add UTF-8 Encoding Support (RECOMMENDED)
Add this at the **very top** of `biology_paper2_generation.py`:

```python
# -*- coding: utf-8 -*-
import sys
import io

# Force UTF-8 encoding for stdout
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
```

### Option 2: Replace Unicode Characters with ASCII
Replace all Unicode characters in print statements:

**Find and Replace:**
- `✓` → `OK` or `[SUCCESS]`
- `⚠` → `WARNING` or `[WARN]`
- `🧬` → `[BIO]`
- `#` repeated (like `#####`) → `-` repeated (like `-----`)
- `=` repeated → `-` repeated

**Example changes in biology_paper2_generation.py:**

```python
# BEFORE
print(f"✓ Data loaded successfully")
print(f"\n{'#'*70}")
print(f"⚠ Warning: No graph questions found")

# AFTER
print(f"OK Data loaded successfully")
print(f"\n{'-'*70}")
print(f"WARNING: No graph questions found")
```

### Option 3: Remove All Print Statements (QUICK FIX)
Comment out or remove all `print()` statements in the file if they're only for debugging.

## Files to Fix
1. `api/biology_paper2_generation.py` - Main file with the error

## Testing After Fix
1. Generate a Biology Paper 2 with multiple topics
2. Check that generation completes successfully
3. Verify console output doesn't have encoding errors

## Current Status
- ✅ Frontend: Correctly detects Biology Paper 2
- ✅ Frontend: Sends correct request to `/api/papers/biology-paper2/generate`
- ✅ Backend: Validation endpoint works (returns 200 OK)
- ❌ Backend: Generation endpoint fails with encoding error (returns 400)

## Request Details
The frontend is sending the correct data:
```json
{
  "paper_id": "09bad953-0b64-423a-9ee7-953a217531f5",
  "selected_topics": [...17 topic IDs...]
}
```

Endpoint being called: `https://speedstarexams.co.ke/api/papers/biology-paper2/generate`
