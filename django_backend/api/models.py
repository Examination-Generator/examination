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
    
    # Question metadata
    question_type = models.CharField(
        max_length=20,
        choices=QUESTION_TYPE_CHOICES,
        default='structured'
    )
    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default='medium'
    )
    marks = models.IntegerField()
    
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
