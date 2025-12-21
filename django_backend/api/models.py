"""
Django Models for Examination System
Equivalent to the PostgreSQL schema with UUID primary keys
"""

import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
import bcrypt


# ==================== USER MODEL ====================

class UserManager(BaseUserManager):
    """Custom user manager for phone number authentication"""
    
    def create_user(self, phone_number, full_name, password=None, **extra_fields):
        """Create and return a regular user"""
        if not phone_number:
            raise ValueError('Phone number is required')
        if not full_name:
            raise ValueError('Full name is required')
        
        user = self.model(
            phone_number=phone_number,
            full_name=full_name,
            **extra_fields
        )
        
        if password:
            user.set_password(password)
        
        user.save(using=self._db)
        return user
    
    def create_superuser(self, phone_number, full_name, password=None, **extra_fields):
        """Create and return a superuser"""
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('otp_verified', True)
        
        return self.create_user(phone_number, full_name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User model with phone number authentication"""
    
    ROLE_CHOICES = [
        ('user', 'User'),
        ('editor', 'Editor'),
        ('admin', 'Admin'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=20, unique=True, db_index=True)
    full_name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    otp_verified = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['full_name']
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.full_name} ({self.phone_number})"
    
    def set_password(self, raw_password):
        """Hash password using bcrypt"""
        if raw_password:
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(raw_password.encode('utf-8'), salt)
            self.password = hashed.decode('utf-8')
    
    def check_password(self, raw_password):
        """Verify password using bcrypt"""
        if not raw_password or not self.password:
            return False
        return bcrypt.checkpw(
            raw_password.encode('utf-8'),
            self.password.encode('utf-8')
        )


# ==================== OTP LOG MODEL ====================

class OTPLog(models.Model):
    """OTP verification logs"""
    
    PURPOSE_CHOICES = [
        ('registration', 'Registration'),
        ('login', 'Login'),
        ('password_reset', 'Password Reset'),
    ]
    
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('verified', 'Verified'),
        ('expired', 'Expired'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=20, db_index=True)
    otp = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='sent')
    expires_at = models.DateTimeField()
    verified_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    attempts = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'otp_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['phone_number', 'status']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"OTP for {self.phone_number} - {self.purpose}"


# ==================== SUBJECT MODEL ====================

class Subject(models.Model):
    """Academic subjects"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_subjects'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'subjects'
        ordering = ['name']
    
    def __str__(self):
        return self.name


# ==================== PAPER MODEL ====================

class Paper(models.Model):
    """Exam papers within subjects"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='papers'
    )
    description = models.TextField(blank=True, null=True)
    
    # Paper configuration
    total_marks = models.IntegerField(
        default=80,
        help_text='Total marks for this paper'
    )
    time_allocation = models.IntegerField(
        default=120,
        help_text='Time allocation in minutes'
    )
    
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_papers'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'papers'
        ordering = ['name']
        unique_together = [['subject', 'name']]
        indexes = [
            models.Index(fields=['subject', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.subject.name} - {self.name}"


# ==================== TOPIC MODEL ====================

class Topic(models.Model):
    """Topics within papers"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    paper = models.ForeignKey(
        Paper,
        on_delete=models.CASCADE,
        related_name='topics'
    )
    description = models.TextField(blank=True, null=True)
    
    # Mark allocation constraints for paper generation
    min_marks = models.IntegerField(
        default=4,
        help_text='Minimum marks this topic should have in a generated paper'
    )
    max_marks = models.IntegerField(
        default=10,
        help_text='Maximum marks this topic should have in a generated paper'
    )
    
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_topics'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'topics'
        ordering = ['name']
        unique_together = [['paper', 'name']]
        indexes = [
            models.Index(fields=['paper', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.paper.name} - {self.name}"


# ==================== SECTION MODEL ====================

class Section(models.Model):
    """Sections within papers"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    paper = models.ForeignKey(
        Paper,
        on_delete=models.CASCADE,
        related_name='sections'
    )
    description = models.TextField(blank=True, null=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_sections'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'sections'
        ordering = ['order', 'name']
        unique_together = [['paper', 'name']]
        indexes = [
            models.Index(fields=['paper', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.paper.name} - {self.name}"


# ==================== QUESTION MODEL ====================

class Question(models.Model):
        
    """Question bank"""
    
    QUESTION_TYPE_CHOICES = [
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('short_answer', 'Short Answer'),
        ('essay', 'Essay'),
        ('structured', 'Structured'),
    ]
    
    # KCSE-specific question types for Biology Paper 1
    KCSE_QUESTION_TYPE_CHOICES = [
        ('name_identify', 'Name/Identify'),
        ('state_give_reasons', 'State/Give Reasons'),
        ('distinguish', 'Distinguish/Differentiate'),
        ('explain_account', 'Explain/Account For'),
        ('describe', 'Describe'),
        ('calculate', 'Calculate'),
    ]
    
    # Paper 2 question categories (for Section B)
    PAPER2_CATEGORY_CHOICES = [
        ('graph', 'Graph Question'),
        ('essay', 'Essay Question'),
        ('structured', 'Structured Question'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    paper = models.ForeignKey(
        Paper,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    topic = models.ForeignKey(
        Topic,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='questions'
    )
    
    # Question content (renamed from questionText/answerText to match Node.js)
    question_text = models.TextField(db_column='questionText')
    answer_text = models.TextField(db_column='answerText')
    
    # Inline images (base64 encoded)
    question_inline_images = models.JSONField(
        default=list,
        blank=True,
        db_column='questionInlineImages'
    )
    answer_inline_images = models.JSONField(
        default=list,
        blank=True,
        db_column='answerInlineImages'
    )
    
    # Image positions for drag-and-drop positioning
    question_image_positions = models.JSONField(
        default=dict,
        blank=True,
        db_column='questionImagePositions',
        help_text='Stores x,y coordinates for positioned images in question'
    )
    answer_image_positions = models.JSONField(
        default=dict,
        blank=True,
        db_column='answerImagePositions',
        help_text='Stores x,y coordinates for positioned images in answer'
    )
    
    # Answer lines configuration for students to write answers
    question_answer_lines = models.JSONField(
        default=list,
        blank=True,
        db_column='questionAnswerLines',
        help_text='Stores answer line configurations in question section'
    )
    answer_answer_lines = models.JSONField(
        default=list,
        blank=True,
        db_column='answerAnswerLines',
        help_text='Stores answer line configurations in answer section'
    )
    
    # Question metadata
    question_type = models.CharField(
        max_length=20,
        choices=QUESTION_TYPE_CHOICES,
        default='structured'
    )
    kcse_question_type = models.CharField(
        max_length=30,
        choices=KCSE_QUESTION_TYPE_CHOICES,
        null=True,
        blank=True,
        help_text='KCSE-specific question type for Biology Paper 1 generation'
    )
    paper2_category = models.CharField(
        max_length=20,
        choices=PAPER2_CATEGORY_CHOICES,
        null=True,
        blank=True,
        help_text='Category for Paper 2 questions (graph/essay/structured). Used for Section B question selection.'
    )
    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default='medium'
    )
    marks = models.IntegerField()
    
    # Nested question support for KCSE papers
    is_nested = models.BooleanField(
        default=False,
        help_text='True if question has multiple parts (a, b, c, d). Only the total marks need to be specified.'
    )
    nested_parts = models.JSONField(
        default=list,
        blank=True,
        null=True,
        help_text='OPTIONAL: Can store part breakdowns if needed, but not required for paper generation.'
    )
    is_graph = models.BooleanField(
            default=False,
            help_text='True if this question requires a graph as part of the answer.'
        )
    is_essay = models.BooleanField(
            default=False,
            help_text='True if this question is an essay type.'
        )
    # MCQ options (for multiple choice questions)
    options = models.JSONField(null=True, blank=True)
    correct_answer = models.TextField(null=True, blank=True)
    answer_explanation = models.TextField(null=True, blank=True)
    
    # Status and usage
    is_active = models.BooleanField(default=True)
    times_used = models.IntegerField(default=0)
    last_used = models.DateTimeField(null=True, blank=True)
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_questions'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'questions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['subject', 'paper', 'topic']),
            models.Index(fields=['is_active']),
            models.Index(fields=['question_type', 'difficulty']),
        ]
    
    def __str__(self):
        return f"{self.subject.name} - {self.question_text[:50]}..."


# ==================== PAPER CONFIGURATION MODEL ====================

class PaperConfiguration(models.Model):
    """Configuration and constraints for paper generation"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    paper = models.OneToOneField(
        Paper,
        on_delete=models.CASCADE,
        related_name='configuration'
    )
    
    # Mark distribution constraints (percentages)
    one_mark_min_percent = models.FloatField(
        default=30.0,
        help_text='Minimum percentage of 1-mark questions'
    )
    one_mark_max_percent = models.FloatField(
        default=40.0,
        help_text='Maximum percentage of 1-mark questions'
    )
    
    two_mark_min_percent = models.FloatField(
        default=35.0,
        help_text='Minimum percentage of 2-mark questions'
    )
    two_mark_max_percent = models.FloatField(
        default=45.0,
        help_text='Maximum percentage of 2-mark questions'
    )
    
    three_mark_min_percent = models.FloatField(
        default=15.0,
        help_text='Minimum percentage of 3-mark questions'
    )
    three_mark_max_percent = models.FloatField(
        default=25.0,
        help_text='Maximum percentage of 3-mark questions'
    )
    
    four_mark_min_percent = models.FloatField(
        default=0.0,
        help_text='Minimum percentage of 4-mark questions'
    )
    four_mark_max_percent = models.FloatField(
        default=5.0,
        help_text='Maximum percentage of 4-mark questions'
    )
    
    # Question type distribution (percentages)
    name_identify_min_percent = models.FloatField(
        default=20.0,
        help_text='Minimum percentage of name/identify questions'
    )
    name_identify_max_percent = models.FloatField(
        default=30.0,
        help_text='Maximum percentage of name/identify questions'
    )
    
    state_reasons_min_percent = models.FloatField(
        default=25.0,
        help_text='Minimum percentage of state/give reasons questions'
    )
    state_reasons_max_percent = models.FloatField(
        default=35.0,
        help_text='Maximum percentage of state/give reasons questions'
    )
    
    distinguish_min_percent = models.FloatField(
        default=10.0,
        help_text='Minimum percentage of distinguish questions'
    )
    distinguish_max_percent = models.FloatField(
        default=15.0,
        help_text='Maximum percentage of distinguish questions'
    )
    
    explain_min_percent = models.FloatField(
        default=20.0,
        help_text='Minimum percentage of explain questions'
    )
    explain_max_percent = models.FloatField(
        default=30.0,
        help_text='Maximum percentage of explain questions'
    )
    
    describe_min_percent = models.FloatField(
        default=10.0,
        help_text='Minimum percentage of describe questions'
    )
    describe_max_percent = models.FloatField(
        default=20.0,
        help_text='Maximum percentage of describe questions'
    )
    
    calculate_min_percent = models.FloatField(
        default=0.0,
        help_text='Minimum percentage of calculate questions'
    )
    calculate_max_percent = models.FloatField(
        default=5.0,
        help_text='Maximum percentage of calculate questions'
    )
    
    # Question count constraints
    min_questions = models.IntegerField(
        default=25,
        help_text='Minimum number of questions in paper'
    )
    max_questions = models.IntegerField(
        default=30,
        help_text='Maximum number of questions in paper'
    )
    
    # Additional configuration
    max_backtracking_attempts = models.IntegerField(
        default=100,
        help_text='Maximum backtracking attempts before restart'
    )
    max_generation_attempts = models.IntegerField(
        default=5,
        help_text='Maximum full generation attempts'
    )
    
    # Instructions and metadata
    instructions = models.TextField(
        default='Answer all questions in the spaces provided on this paper.',
        help_text='Standard instructions for candidates'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'paper_configurations'
        ordering = ['paper']
    
    def __str__(self):
        return f"Configuration for {self.paper}"


# ==================== GENERATED PAPER MODEL ====================

class GeneratedPaper(models.Model):
    """Store generated examination papers"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('validated', 'Validated'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    paper = models.ForeignKey(
        Paper,
        on_delete=models.CASCADE,
        related_name='generated_papers'
    )
    
    # Generation metadata
    unique_code = models.CharField(
        max_length=20,
        unique=True,
        help_text='Unique identifier for this generated paper'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    
    # Selected questions (stored as JSON array of question IDs in order)
    question_ids = models.JSONField(
        help_text='Ordered list of question IDs in this paper'
    )
    
    # Topic selections and adjustments
    selected_topics = models.JSONField(
        help_text='List of topic IDs selected for generation'
    )
    topic_adjustments = models.JSONField(
        null=True,
        blank=True,
        help_text='Proportional adjustments made to topic mark ranges'
    )
    
    # Generation statistics
    total_marks = models.IntegerField()
    total_questions = models.IntegerField()
    
    mark_distribution = models.JSONField(
        help_text='Distribution of questions by mark value'
    )
    topic_distribution = models.JSONField(
        help_text='Distribution of marks by topic'
    )
    question_type_distribution = models.JSONField(
        help_text='Distribution of question types'
    )
    
    # Validation results
    validation_passed = models.BooleanField(default=False)
    validation_report = models.JSONField(
        null=True,
        blank=True,
        help_text='Detailed validation results'
    )
    
    # Generation process info
    generation_attempts = models.IntegerField(
        default=1,
        help_text='Number of attempts before successful generation'
    )
    backtracking_count = models.IntegerField(
        default=0,
        help_text='Number of backtracking operations performed'
    )
    generation_time_seconds = models.FloatField(
        null=True,
        blank=True,
        help_text='Time taken to generate this paper'
    )
    
    # Coverpage data
    coverpage_data = models.JSONField(
        null=True,
        blank=True,
        help_text='Coverpage information (school name, logo, instructions, etc.)'
    )
    
    # Additional metadata for paper generation
    metadata = models.JSONField(
        null=True,
        blank=True,
        default=dict,
        help_text='Additional metadata about the paper (paper_type, generation_algorithm, sections, etc.)'
    )
    
    # User tracking
    generated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='generated_papers'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'generated_papers'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['paper', 'status']),
            models.Index(fields=['unique_code']),
        ]
    
    def __str__(self):
        return f"{self.paper.name} - {self.unique_code}"
