"""
Django REST Framework Serializers for Examination System
"""

from rest_framework import serializers
from .models import User, OTPLog, Subject, Paper, Topic, Section, Question


# ==================== USER SERIALIZERS ====================

class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    class Meta:
        model = User
        fields = ['id', 'phone_number', 'full_name', 'role', 'is_active', 
                  'otp_verified', 'last_login', 'created_at']
        read_only_fields = ['id', 'created_at', 'last_login']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, min_length=4, max_length=4)
    phoneNumber = serializers.CharField(source='phone_number', required=False, write_only=True)
    fullName = serializers.CharField(source='full_name', required=False, write_only=True)
    
    class Meta:
        model = User
        fields = ['phone_number', 'full_name', 'phoneNumber', 'fullName', 'password']
        extra_kwargs = {
            'phone_number': {'required': False},
            'full_name': {'required': False}
        }
    
    def validate_password(self, value):
        """Validate that password is exactly 4 digits"""
        if len(value) != 4:
            raise serializers.ValidationError('Password must be exactly 4 digits')
        if not value.isdigit():
            raise serializers.ValidationError('Password must contain only digits')
        return value
    
    def validate(self, data):
        # Accept both camelCase and snake_case
        if 'phone_number' not in data and 'phoneNumber' not in data:
            raise serializers.ValidationError({'phoneNumber': 'Phone number is required'})
        if 'full_name' not in data and 'fullName' not in data:
            raise serializers.ValidationError({'fullName': 'Full name is required'})
        return data
    
    def create(self, validated_data):
        user = User.objects.create_user(
            phone_number=validated_data.get('phone_number'),
            full_name=validated_data.get('full_name'),
            password=validated_data['password']
        )
        user.otp_verified = True
        user.save()
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    phoneNumber = serializers.CharField(required=False)
    phone_number = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True, required=True)
    
    def validate(self, data):
        # Accept both phoneNumber (camelCase) and phone_number (snake_case)
        phone = data.get('phoneNumber') or data.get('phone_number')
        if not phone:
            raise serializers.ValidationError({'phoneNumber': 'Phone number is required'})
        data['phone_number'] = phone
        return data


# ==================== OTP SERIALIZERS ====================

class OTPSerializer(serializers.ModelSerializer):
    """Serializer for OTP logs"""
    
    class Meta:
        model = OTPLog
        fields = ['id', 'phone_number', 'purpose', 'status', 'expires_at', 
                  'verified_at', 'created_at']
        read_only_fields = ['id', 'created_at']


class SendOTPSerializer(serializers.Serializer):
    """Serializer for sending OTP"""
    phone_number = serializers.CharField(max_length=20, required=False)
    phoneNumber = serializers.CharField(max_length=20, required=False)
    purpose = serializers.ChoiceField(
        choices=['registration', 'login', 'password_reset'],
        default='registration'
    )
    
    def validate(self, data):
        # Accept both phoneNumber (camelCase) and phone_number (snake_case)
        phone = data.get('phoneNumber') or data.get('phone_number')
        if not phone:
            raise serializers.ValidationError({'phoneNumber': 'Phone number is required'})
        data['phone_number'] = phone
        return data


class VerifyOTPSerializer(serializers.Serializer):
    """Serializer for verifying OTP"""
    phone_number = serializers.CharField(max_length=20, required=False)
    phoneNumber = serializers.CharField(max_length=20, required=False)
    otp = serializers.CharField(max_length=6)
    
    def validate(self, data):
        # Accept both phoneNumber (camelCase) and phone_number (snake_case)
        phone = data.get('phoneNumber') or data.get('phone_number')
        if not phone:
            raise serializers.ValidationError({'phoneNumber': 'Phone number is required'})
        data['phone_number'] = phone
        return data


class ResetPasswordSerializer(serializers.Serializer):
    """Serializer for password reset"""
    phone_number = serializers.CharField(max_length=20, required=False)
    phoneNumber = serializers.CharField(max_length=20, required=False)
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(min_length=4, max_length=4, write_only=True, required=False)
    newPassword = serializers.CharField(min_length=4, max_length=4, write_only=True, required=False)
    
    def validate_new_password(self, value):
        """Validate that password is exactly 4 digits"""
        if value and len(value) == 4 and not value.isdigit():
            raise serializers.ValidationError('Password must contain only digits')
        return value
    
    def validate_newPassword(self, value):
        """Validate that password is exactly 4 digits"""
        if value and len(value) == 4 and not value.isdigit():
            raise serializers.ValidationError('Password must contain only digits')
        return value
    
    def validate(self, data):
        # Accept both phoneNumber (camelCase) and phone_number (snake_case)
        phone = data.get('phoneNumber') or data.get('phone_number')
        if not phone:
            raise serializers.ValidationError({'phoneNumber': 'Phone number is required'})
        data['phone_number'] = phone
        
        # Accept both newPassword (camelCase) and new_password (snake_case)
        new_pwd = data.get('newPassword') or data.get('new_password')
        if not new_pwd:
            raise serializers.ValidationError({'newPassword': 'New password is required'})
        if len(new_pwd) != 4:
            raise serializers.ValidationError({'newPassword': 'Password must be exactly 4 digits'})
        if not new_pwd.isdigit():
            raise serializers.ValidationError({'newPassword': 'Password must contain only digits'})
        data['new_password'] = new_pwd
        
        return data


# ==================== SUBJECT SERIALIZERS ====================

class SectionSerializer(serializers.ModelSerializer):
    """Serializer for Section model"""
    
    class Meta:
        model = Section
        fields = ['id', 'name', 'description', 'order', 'is_active', 
                  'paper', 'created_at']
        read_only_fields = ['id', 'created_at']


class TopicSerializer(serializers.ModelSerializer):
    """Serializer for Topic model"""
    
    class Meta:
        model = Topic
        fields = ['id', 'name', 'description', 'is_active', 'paper', 'created_at']
        read_only_fields = ['id', 'created_at']


class PaperSerializer(serializers.ModelSerializer):
    """Serializer for Paper model with sections and topics"""
    sections = SectionSerializer(many=True, read_only=True)
    topics = TopicSerializer(many=True, read_only=True)
    
    class Meta:
        model = Paper
        fields = ['id', 'name', 'description', 'is_active', 'subject', 
                  'sections', 'topics', 'created_at']
        read_only_fields = ['id', 'created_at']


class SubjectSerializer(serializers.ModelSerializer):
    """Serializer for Subject model with papers"""
    papers = PaperSerializer(many=True, read_only=True)
    
    class Meta:
        model = Subject
        fields = ['id', 'name', 'description', 'is_active', 'papers', 'created_at']
        read_only_fields = ['id', 'created_at']


class SubjectCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating subjects with papers, sections, and topics"""
    papers = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        allow_empty=True
    )
    
    class Meta:
        model = Subject
        fields = ['name', 'description', 'papers']
    
    def create(self, validated_data):
        papers_data = validated_data.pop('papers', [])
        user = self.context['request'].user
        
        # Create subject
        subject = Subject.objects.create(
            created_by=user,
            **validated_data
        )
        
        # Create papers with sections and topics
        for paper_data in papers_data:
            sections_data = paper_data.pop('sections', [])
            topics_data = paper_data.pop('topics', [])
            
            paper = Paper.objects.create(
                subject=subject,
                created_by=user,
                name=paper_data.get('name'),
                description=paper_data.get('description', '')
            )
            
            # Create sections
            for i, section_name in enumerate(sections_data):
                if section_name and section_name.strip():
                    Section.objects.create(
                        paper=paper,
                        name=section_name.strip(),
                        order=i,
                        created_by=user
                    )
            
            # Create topics
            for topic_name in topics_data:
                if topic_name and topic_name.strip():
                    Topic.objects.create(
                        paper=paper,
                        name=topic_name.strip(),
                        created_by=user
                    )
        
        return subject


# ==================== QUESTION SERIALIZERS ====================

class QuestionListSerializer(serializers.ModelSerializer):
    """Serializer for listing questions (minimal fields)"""
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    paper_name = serializers.CharField(source='paper.name', read_only=True)
    topic_name = serializers.CharField(source='topic.name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'subject', 'subject_name', 'paper', 'paper_name', 
                  'topic', 'topic_name', 'section', 'section_name',
                  'question_text', 'answer_text', 'marks', 'question_type',
                  'difficulty', 'is_active', 'times_used', 'created_at']
        read_only_fields = ['id', 'created_at', 'times_used']


class QuestionDetailSerializer(serializers.ModelSerializer):
    """Serializer for question detail view"""
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    paper_name = serializers.CharField(source='paper.name', read_only=True)
    topic_name = serializers.CharField(source='topic.name', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True)
    
    class Meta:
        model = Question
        fields = ['id', 'subject', 'subject_name', 'paper', 'paper_name',
                  'topic', 'topic_name', 'section', 'section_name',
                  'question_text', 'question_inline_images', 
                  'answer_text', 'answer_inline_images',
                  'question_type', 'difficulty', 'marks',
                  'options', 'correct_answer', 'answer_explanation',
                  'is_active', 'times_used', 'last_used',
                  'created_by', 'created_by_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'times_used', 'last_used']


class QuestionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating questions"""
    
    class Meta:
        model = Question
        fields = ['subject', 'paper', 'topic', 'section',
                  'question_text', 'question_inline_images',
                  'answer_text', 'answer_inline_images',
                  'question_type', 'difficulty', 'marks',
                  'options', 'correct_answer', 'answer_explanation',
                  'is_active']
    
    def validate(self, data):
        """Validate relationships between subject, paper, topic, section"""
        subject = data.get('subject')
        paper = data.get('paper')
        topic = data.get('topic')
        section = data.get('section')
        
        # Verify paper belongs to subject
        if paper and paper.subject != subject:
            raise serializers.ValidationError({
                'paper': 'Paper does not belong to the selected subject'
            })
        
        # Verify topic belongs to paper
        if topic and topic.paper != paper:
            raise serializers.ValidationError({
                'topic': 'Topic does not belong to the selected paper'
            })
        
        # Verify section belongs to paper (if provided)
        if section and section.paper != paper:
            raise serializers.ValidationError({
                'section': 'Section does not belong to the selected paper'
            })
        
        return data
    
    def create(self, validated_data):
        user = self.context['request'].user
        return Question.objects.create(created_by=user, **validated_data)


class QuestionBulkCreateSerializer(serializers.Serializer):
    """Serializer for bulk creating questions"""
    questions = QuestionCreateSerializer(many=True)
    
    def create(self, validated_data):
        user = self.context['request'].user
        questions_data = validated_data['questions']
        
        questions = [
            Question(created_by=user, **question_data)
            for question_data in questions_data
        ]
        
        return Question.objects.bulk_create(questions)
