# Paper Retention Policy - 30 Days

## Overview
Generated exam papers are automatically retained for **30 days** from their creation date. After 30 days, papers are either archived or permanently deleted to maintain database efficiency.

## Features

### 1. Automatic Filtering
- The `/api/papers/generated` endpoint automatically filters papers to show only those created within the last 30 days
- Papers older than 30 days are hidden from the user interface
- Each paper displays "days remaining" countdown in the UI

### 2. User-Specific History
- Users can only see papers they generated themselves
- Use `user_only=true` parameter to filter by current user
- Papers are sorted by creation date (newest first)

### 3. Retention Indicators
The UI shows visual indicators for paper retention:
- **Green badge**: More than 7 days remaining
- **Yellow badge**: 1-7 days remaining (expiring soon)
- **Red badge**: Expired (0 days or less)

## Management Command

### Manual Cleanup
You can manually clean up old papers using the Django management command:

```bash
# Activate virtual environment
venv\Scripts\activate

# Archive papers older than 30 days (default)
python manage.py cleanup_old_papers

# Permanently delete instead of archiving
python manage.py cleanup_old_papers --delete

# Use custom retention period (e.g., 60 days)
python manage.py cleanup_old_papers --days 60

# Dry run (preview what would be deleted)
python manage.py cleanup_old_papers --dry-run
```

### Command Options

| Option | Description | Default |
|--------|-------------|---------|
| `--delete` | Permanently delete papers instead of archiving | Archive |
| `--days N` | Set retention period to N days | 30 |
| `--dry-run` | Show what would be deleted without actually deleting | False |

### Examples

```bash
# See what papers would be archived (dry run)
python manage.py cleanup_old_papers --dry-run

# Archive papers older than 30 days
python manage.py cleanup_old_papers

# Permanently delete papers older than 60 days
python manage.py cleanup_old_papers --days 60 --delete

# Archive papers older than 14 days
python manage.py cleanup_old_papers --days 14
```

## Automated Cleanup (Optional)

### Windows Task Scheduler
To run cleanup automatically on Windows:

1. Open Task Scheduler
2. Create New Task
3. Set trigger to run daily at 2:00 AM
4. Set action to run:
   ```
   C:\Users\pc\Desktop\exam\django_backend\venv\Scripts\python.exe
   ```
   With arguments:
   ```
   C:\Users\pc\Desktop\exam\django_backend\manage.py cleanup_old_papers
   ```

### Linux Cron Job
Add to crontab (`crontab -e`):

```bash
# Run cleanup daily at 2:00 AM
0 2 * * * cd /path/to/exam/django_backend && ./venv/bin/python manage.py cleanup_old_papers
```

## API Endpoint Details

### List Generated Papers
```
GET /api/papers/generated
```

**Query Parameters:**
- `paper_id` - Filter by specific paper UUID
- `status` - Filter by status (draft, validated, published, archived)
- `user_only` - Set to `true` to show only current user's papers

**Response:**
```json
{
  "count": 15,
  "retention_days": 30,
  "oldest_date": "2025-10-14T12:00:00Z",
  "generated_papers": [
    {
      "id": "uuid",
      "unique_code": "BIOL1-ABC123",
      "subject_name": "Biology",
      "paper_name": "Paper 1",
      "total_marks": 80,
      "total_questions": 27,
      "validation_passed": true,
      "generated_by": "John Doe",
      "created_at": "2025-11-10T14:30:00Z",
      "days_remaining": 25
    }
  ]
}
```

## Database Model

Papers are stored in the `generated_papers` table with:
- `created_at` - Timestamp of generation
- `status` - One of: draft, validated, published, archived
- `generated_by` - Foreign key to user who generated it

### Status Lifecycle
1. **draft** - Newly generated paper
2. **validated** - Paper passed validation
3. **published** - Paper is ready for use
4. **archived** - Paper older than 30 days (hidden from UI)

## Best Practices

1. **Regular Cleanup**: Run cleanup command weekly or set up automated task
2. **Dry Run First**: Always test with `--dry-run` before actual deletion
3. **Archive vs Delete**: Use archiving for audit trails, deletion for space savings
4. **Monitor Storage**: Check database size regularly if storing many papers
5. **User Notification**: Inform users about 30-day retention policy

## Troubleshooting

### Papers not showing in history
- Check if papers are older than 30 days
- Verify `user_only` filter is working correctly
- Check if papers were archived manually

### Cleanup command errors
- Ensure virtual environment is activated
- Check database connection
- Verify user has permission to delete records

### Performance issues
- If you have millions of papers, run cleanup during off-peak hours
- Consider adding database indexes on `created_at` field
- Use `--days` parameter to reduce batch size

## Future Enhancements

Potential improvements to consider:
- Email notifications when papers are about to expire
- User-configurable retention periods
- Bulk export before deletion
- Soft delete with recovery option
- Admin dashboard for retention management
