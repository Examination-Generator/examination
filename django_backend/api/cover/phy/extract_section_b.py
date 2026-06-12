from api.models import Question

def _extract_physics_section_b_marks(generated_paper, section_b_count=5):
    fallback_marks = [11, 10, 10, 12, 12]

    metadata = getattr(generated_paper, 'metadata', {}) or {}
    metadata_marks = metadata.get('section_b_question_marks')
    if isinstance(metadata_marks, list) and metadata_marks:
        normalized = []
        for i in range(section_b_count):
            value = metadata_marks[i] if i < len(metadata_marks) else fallback_marks[i]
            try:
                normalized.append(int(value))
            except (TypeError, ValueError):
                normalized.append(fallback_marks[i])
        return normalized

    question_ids = list(getattr(generated_paper, 'question_ids', []) or [])
    if len(question_ids) >= section_b_count:
        section_b_ids = [str(qid) for qid in question_ids[-section_b_count:]]
        questions = Question.objects.filter(id__in=section_b_ids).only('id', 'marks')
        question_map = {str(question.id): question for question in questions}

        ordered_marks = []
        for qid in section_b_ids:
            question = question_map.get(qid)
            if question is None:
                break
            try:
                ordered_marks.append(int(question.marks))
            except (TypeError, ValueError):
                break

        if len(ordered_marks) == section_b_count:
            return ordered_marks

    return fallback_marks[:section_b_count]