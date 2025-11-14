"""
Management command to clean up generated papers older than 30 days

Run this command daily via cron job or task scheduler:
python manage.py cleanup_old_papers
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from api.models import GeneratedPaper
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Archive or delete generated papers older than 30 days'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Permanently delete old papers instead of archiving',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to retain papers (default: 30)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        days = options['days']
        delete = options['delete']
        dry_run = options['dry_run']
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(f"Cleaning up papers older than {days} days")
        self.stdout.write(f"Cutoff date: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')}")
        self.stdout.write(f"Mode: {'DRY RUN' if dry_run else 'DELETE' if delete else 'ARCHIVE'}")
        self.stdout.write(f"{'='*60}\n")
        
        # Find old papers
        old_papers = GeneratedPaper.objects.filter(
            created_at__lt=cutoff_date
        ).exclude(
            status='archived'  # Don't re-archive already archived papers
        )
        
        count = old_papers.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS(
                "✓ No papers found older than {} days".format(days)
            ))
            return
        
        self.stdout.write(f"Found {count} papers to process:\n")
        
        # Show sample of papers
        for paper in old_papers[:10]:
            age_days = (timezone.now() - paper.created_at).days
            self.stdout.write(
                f"  - {paper.unique_code} ({paper.paper.subject.name} - {paper.paper.name}) "
                f"- {age_days} days old - Status: {paper.status}"
            )
        
        if count > 10:
            self.stdout.write(f"  ... and {count - 10} more\n")
        
        if dry_run:
            self.stdout.write(self.style.WARNING(
                f"\n[DRY RUN] Would process {count} papers"
            ))
            return
        
        # Process papers
        if delete:
            # Permanently delete
            deleted_count, _ = old_papers.delete()
            self.stdout.write(self.style.SUCCESS(
                f"\n✓ Permanently deleted {deleted_count} papers"
            ))
            logger.info(f"Deleted {deleted_count} papers older than {days} days")
        else:
            # Archive papers
            updated = old_papers.update(status='archived')
            self.stdout.write(self.style.SUCCESS(
                f"\n✓ Archived {updated} papers"
            ))
            logger.info(f"Archived {updated} papers older than {days} days")
        
        self.stdout.write(self.style.SUCCESS("\n✓ Cleanup completed successfully\n"))
