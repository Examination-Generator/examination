"""
Django REST Framework Serializers for Examination System
"""

import logging
from rest_framework import serializers
from .models import User, OTPLog, Subject, Paper, Topic, Section, Question

logger = logging.getLogger(__name__)


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
        fields = ['phone_number', 'full_name', 'phoneNumber', 'fullName', 'password', 'role']
        extra_kwargs = {
            'phone_number': {'required': False},
            'full_name': {'required': False},
            'role': {'required': False, 'default': 'user'}
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
        # Extract role if provided, default to 'user'
        role = validated_data.pop('role', 'user')
        
        user = User.objects.create_user(
            phone_number=validated_data.get('phone_number'),
            full_name=validated_data.get('full_name'),
            password=validated_data['password'],
            role=role
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
                  'sections', 'topics', 'time_allocation', 'total_marks',
                  'duration_hours', 'duration_minutes', 'created_at']
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
            
            # Extract duration fields if provided
            duration_hours = paper_data.pop('duration_hours', 2)
            duration_minutes = paper_data.pop('duration_minutes', 0)
            
            paper = Paper.objects.create(
                subject=subject,
                created_by=user,
                name=paper_data.get('name'),
                description=paper_data.get('description', ''),
                duration_hours=duration_hours,
                duration_minutes=duration_minutes
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
    
    def update(self, instance, validated_data):
        """Handle partial/full update of subject with papers, sections, and topics
        
        This method supports incremental updates:
        - Add new papers to existing subject
        - Update existing papers
        - Add topics/sections to existing or new papers
        """
        papers_data = validated_data.pop('papers', None)
        user = self.context['request'].user
        
        logger.info(f"[SUBJECT UPDATE] Updating subject ID={instance.id}, name={instance.name}")
        
        # Update subject basic fields (only if provided)
        if 'name' in validated_data:
            old_name = instance.name
            instance.name = validated_data['name']
            logger.info(f"[SUBJECT UPDATE] Name changed: '{old_name}' -> '{instance.name}'")
        if 'description' in validated_data:
            instance.description = validated_data['description']
        instance.save()
        
        # Only update papers if papers data is explicitly provided
        if papers_data is not None:
            logger.info(f"[SUBJECT UPDATE] Processing {len(papers_data)} paper(s)")
            
            # Get existing papers mapped by name for easier lookup
            existing_papers = {paper.name: paper for paper in instance.papers.all()}
            updated_paper_names = set()
            
            # Process each paper in the request
            for paper_data in papers_data:
                paper_name = paper_data.get('name', '').strip()
                if not paper_name:
                    continue
                    
                sections_data = paper_data.pop('sections', [])
                topics_data = paper_data.pop('topics', [])
                
                # Check if paper exists
                if paper_name in existing_papers:
                    # UPDATE existing paper
                    logger.info(f"[SUBJECT UPDATE] Updating existing paper: '{paper_name}'")
                    paper = existing_papers[paper_name]
                    updated_paper_names.add(paper_name)
                    
                    # Update paper description if provided
                    if 'description' in paper_data:
                        paper.description = paper_data.get('description', '')
                        paper.save()
                    
                    # Get existing topics and sections
                    existing_topics = {topic.name: topic for topic in paper.topics.all()}
                    existing_sections = {section.name: section for section in paper.sections.all()}
                    
                    # Update/Add Topics
                    provided_topic_names = set()
                    new_topics_count = 0
                    for topic_item in topics_data:
                        # Handle both string and object formats: 'topic_name' or {id: 'uuid', name: 'topic_name'}
                        if isinstance(topic_item, dict):
                            topic_name_clean = topic_item.get('name', '').strip()
                        else:
                            topic_name_clean = topic_item.strip() if topic_item else ''
                        
                        if topic_name_clean:
                            provided_topic_names.add(topic_name_clean)
                            if topic_name_clean not in existing_topics:
                                # Create new topic
                                Topic.objects.create(
                                    paper=paper,
                                    name=topic_name_clean,
                                    created_by=user
                                )
                                new_topics_count += 1
                    
                    if new_topics_count > 0:
                        logger.info(f"[SUBJECT UPDATE] Added {new_topics_count} new topic(s) to '{paper_name}'")
                    
                    # Remove topics that are not in the new list
                    topics_to_remove = set(existing_topics.keys()) - provided_topic_names
                    if topics_to_remove:
                        logger.info(f"[SUBJECT UPDATE] Removing {len(topics_to_remove)} topic(s) from '{paper_name}'")
                    for topic_name in topics_to_remove:
                        existing_topics[topic_name].delete()
                    
                    # Update/Add Sections
                    provided_section_names = set()
                    new_sections_count = 0
                    for i, section_item in enumerate(sections_data):
                        # Handle both string and object formats: 'section_name' or {id: 'uuid', name: 'section_name'}
                        if isinstance(section_item, dict):
                            section_name_clean = section_item.get('name', '').strip()
                        else:
                            section_name_clean = section_item.strip() if section_item else ''
                        
                        if section_name_clean:
                            provided_section_names.add(section_name_clean)
                            if section_name_clean not in existing_sections:
                                # Create new section
                                Section.objects.create(
                                    paper=paper,
                                    name=section_name_clean,
                                    order=i,
                                    created_by=user
                                )
                                new_sections_count += 1
                            else:
                                # Update order if section exists
                                section = existing_sections[section_name_clean]
                                section.order = i
                                section.save()
                    
                    if new_sections_count > 0:
                        logger.info(f"[SUBJECT UPDATE] Added {new_sections_count} new section(s) to '{paper_name}'")
                    
                    # Remove sections that are not in the new list
                    sections_to_remove = set(existing_sections.keys()) - provided_section_names
                    if sections_to_remove:
                        logger.info(f"[SUBJECT UPDATE] Removing {len(sections_to_remove)} section(s) from '{paper_name}'")
                    for section_name in sections_to_remove:
                        existing_sections[section_name].delete()
                
                else:
                    # CREATE new paper
                    logger.info(f"[SUBJECT UPDATE] Creating new paper: '{paper_name}' with {len(topics_data)} topic(s) and {len(sections_data)} section(s)")
                    updated_paper_names.add(paper_name)
                    
                    paper = Paper.objects.create(
                        subject=instance,
                        created_by=user,
                        name=paper_name,
                        description=paper_data.get('description', '')
                    )
                    
                    # Create sections
                    for i, section_item in enumerate(sections_data):
                        # Handle both string and object formats
                        if isinstance(section_item, dict):
                            section_name = section_item.get('name', '').strip()
                        else:
                            section_name = section_item.strip() if section_item else ''
                        
                        if section_name:
                            Section.objects.create(
                                paper=paper,
                                name=section_name,
                                order=i,
                                created_by=user
                            )
                    
                    # Create topics
                    for topic_item in topics_data:
                        # Handle both string and object formats
                        if isinstance(topic_item, dict):
                            topic_name = topic_item.get('name', '').strip()
                        else:
                            topic_name = topic_item.strip() if topic_item else ''
                        
                        if topic_name:
                            Topic.objects.create(
                                paper=paper,
                                name=topic_name,
                                created_by=user
                            )
            
            # Remove papers that are not in the updated list
            papers_to_remove = set(existing_papers.keys()) - updated_paper_names
            if papers_to_remove:
                logger.info(f"[SUBJECT UPDATE] Removing {len(papers_to_remove)} paper(s): {papers_to_remove}")
            for paper_name in papers_to_remove:
                existing_papers[paper_name].delete()
        else:
            logger.info(f"[SUBJECT UPDATE] No papers data provided - keeping existing papers")
        
        logger.info(f"[SUBJECT UPDATE] Update complete for subject ID={instance.id}")
        return instance


# ==================== QUESTION SERIALIZERS ====================

class QuestionListSerializer(serializers.ModelSerializer):
    """Serializer for listing questions (minimal fields)"""
    subject_name = serializers.SerializerMethodField()
    paper_name = serializers.SerializerMethodField()
    topic_name = serializers.SerializerMethodField()
    section_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    
    def get_subject_name(self, obj):
        return obj.subject.name if obj.subject else None
    
    def get_paper_name(self, obj):
        return obj.paper.name if obj.paper else None
    
    def get_topic_name(self, obj):
        if obj.topic:
            return obj.topic.name
        # Log if topic is missing
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Question {obj.id} has no topic! Paper: {obj.paper.name if obj.paper else 'None'}")
        return None
    
    def get_section_name(self, obj):
        return obj.section.name if obj.section else None
    
    def get_created_by_name(self, obj):
        """Get the full name of the user who created the question"""
        if obj.created_by:
            return obj.created_by.full_name
        return None
    
    class Meta:
        model = Question
        fields = ['id', 'subject', 'subject_name', 'paper', 'paper_name', 
                  'topic', 'topic_name', 'section', 'section_name',
                  'question_text', 'question_inline_images',
                  'answer_text', 'answer_inline_images',
                  'question_image_positions', 'answer_image_positions',
                  'question_answer_lines', 'answer_answer_lines',
                  'marks', 'question_type', 'kcse_question_type', 'paper2_category',
                  'difficulty', 'is_nested', 'is_active', 'times_used',
                  'created_by', 'created_by_name', 'created_at']
        read_only_fields = ['id', 'created_at', 'times_used']


class QuestionDetailSerializer(serializers.ModelSerializer):
    """Serializer for question detail view"""
    subject_name = serializers.SerializerMethodField()
    paper_name = serializers.SerializerMethodField()
    topic_name = serializers.SerializerMethodField()
    section_name = serializers.SerializerMethodField()
    created_by_name = serializers.SerializerMethodField()
    
    def get_subject_name(self, obj):
        return obj.subject.name if obj.subject else None
    
    def get_paper_name(self, obj):
        return obj.paper.name if obj.paper else None
    
    def get_topic_name(self, obj):
        return obj.topic.name if obj.topic else None
    
    def get_section_name(self, obj):
        return obj.section.name if obj.section else None
    
    def get_created_by_name(self, obj):
        return obj.created_by.full_name if obj.created_by else None
    
    class Meta:
        model = Question
        fields = ['id', 'subject', 'subject_name', 'paper', 'paper_name',
                  'topic', 'topic_name', 'section', 'section_name',
                  'question_text', 'question_inline_images', 
                  'answer_text', 'answer_inline_images',
                  'question_image_positions', 'answer_image_positions',
                  'question_answer_lines', 'answer_answer_lines',
                  'question_type', 'kcse_question_type', 'paper2_category', 'difficulty', 'marks',
                  'options', 'correct_answer', 'answer_explanation',
                  'is_nested', 'is_active', 'times_used', 'last_used',
                  'created_by', 'created_by_name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'times_used', 'last_used']


class QuestionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating questions"""
    
    is_graph = serializers.BooleanField(required=False, allow_null=True, default=False)
    is_essay = serializers.BooleanField(required=False, allow_null=True, default=False)
    is_map = serializers.BooleanField(required=False, allow_null=True, default=False)

    class Meta:
        model = Question
        fields = ['subject', 'paper', 'topic', 'section',
                  'question_text', 'question_inline_images',
                  'answer_text', 'answer_inline_images',
                  'question_image_positions', 'answer_image_positions',
                  'question_answer_lines', 'answer_answer_lines',
                  'question_type', 'kcse_question_type', 'paper2_category', 'difficulty', 'marks',
                  'options', 'correct_answer', 'answer_explanation',
                  'is_nested', 'is_active', 'is_graph', 'is_essay', 'is_map']
    
    def validate(self, data):
        """Validate relationships between subject, paper, topic, section"""
        import logging
        logger = logging.getLogger(__name__)
        
        subject = data.get('subject')
        paper = data.get('paper')
        topic = data.get('topic')
        section = data.get('section')
        
        logger.info(f"Validating question data:")
        logger.info(f"  - subject: {subject}")
        logger.info(f"  - paper: {paper}")
        logger.info(f"  - topic: {topic}")
        logger.info(f"  - section: {section}")
        
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
            logger.error(f"Section validation failed: section.paper={section.paper}, paper={paper}")
            raise serializers.ValidationError({
                'section': 'Section does not belong to the selected paper'
            })
        
        logger.info(f"Validation passed - section will be: {section}")
        return data
    
    def create(self, validated_data):
        user = self.context['request'].user
        
        # DEBUG: Log image data being saved
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Creating question with images: question_images={len(validated_data.get('question_inline_images', []))}, answer_images={len(validated_data.get('answer_inline_images', []))}")
        
        if validated_data.get('question_inline_images'):
            logger.info(f"Question images sample: {validated_data['question_inline_images'][0] if validated_data['question_inline_images'] else 'None'}")
        
        question = Question.objects.create(created_by=user, **validated_data)
        
        # DEBUG: Verify what was saved
        logger.info(f"Question created with ID: {question.id}, question_images_in_db={len(question.question_inline_images or [])}, answer_images_in_db={len(question.answer_inline_images or [])}")
        
        return question
    
    def update(self, instance, validated_data):
        """Update question with proper section handling"""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"Updating question {instance.id}")
        logger.info(f"Current section: {instance.section_id}")
        logger.info(f"New section from validated_data: {validated_data.get('section')}")
        
        # Update all fields from validated_data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        
        logger.info(f"After save - section_id: {instance.section_id}")
        
        return instance


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
