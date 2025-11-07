# Vercel Deployment Notes

## Important Configuration Details

### Python Runtime
- Vercel uses Python 3.9 by default
- Compatible with Django 5.0

### Static Files
- Handled by WhiteNoise middleware
- Automatically collected during build

### Database
- Uses Vercel Postgres in production
- Environment variables auto-injected

### Serverless Functions
- Each API endpoint runs as a serverless function
- Cold start time: ~1 second
- Maximum execution time: 10 seconds (Hobby), 60 seconds (Pro)

### File Size Limits
- Maximum function size: 50 MB
- Maximum request body: 4.5 MB (Hobby), 5 MB (Pro)

### Environment Variables
All environment variables must be set in Vercel dashboard under:
Project Settings → Environment Variables

### Build Process
1. Install dependencies from requirements.txt
2. Collect static files
3. Run migrations (manually via CLI)
4. Deploy serverless functions

### Known Limitations
- No background workers (use external services like Celery with Redis)
- No cron jobs (use Vercel Cron or external scheduler)
- No file system persistence (use external storage like S3)

### Recommendations
1. Keep function execution time under 5 seconds
2. Use database connection pooling
3. Enable caching where possible
4. Monitor function logs regularly
5. Set up error tracking (e.g., Sentry)

### Troubleshooting
- Check Vercel function logs for errors
- Verify all environment variables are set
- Ensure database connection is active
- Check CORS settings if frontend can't connect
