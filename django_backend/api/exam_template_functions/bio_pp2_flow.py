from api.process_text import _process_question_text
from api.exam_template_functions.answer_lines import _generate_answer_lines_pages



def _generate_biology_paper2_flow(questions, start_page, total_pages, metadata=None, inline_answer_pages=0):
    
    meta = metadata or {}

    # Section A count (default 5)
    section_a_count = meta.get('section_a_questions', 5)
    try:
        section_a_count = int(section_a_count)
    except Exception:
        section_a_count = 5

    section_a_questions = [q for q in questions if int(q.get('number', 0)) <= section_a_count]
    section_b_questions = [q for q in questions if int(q.get('number', 0)) > section_a_count]

    try:
        section_a_marks = 40
    except Exception:
        section_a_marks = 40
    section_a_title = f"SECTION A ({section_a_marks} MARKS)" if section_a_marks is not None else "SECTION A"
    section_a_instruction = meta.get('section_a_instruction', 'Answer ALL questions in this section')

    try:
        section_b_marks = 40
    except Exception:
        section_b_marks = 40
    section_b_title = f"SECTION B ({section_b_marks} MARKS)" if section_b_marks is not None else "SECTION B"
    section_b_instruction = meta.get('section_b_instruction', 'Answer question 6 and either question 7 or 8')

    parts = []
    parts.append('<div class="question-flow biology-paper2">')

    # Section A header
    parts.append(f'<div class="section-header"><h2>{section_a_title}</h2><div class="section-instruction">{section_a_instruction}</div></div>')

    for q in section_a_questions:
        processed_text = _process_question_text(
            q.get('text', ''),
            q.get('question_inline_images', []),
            q.get('question_answer_lines', [])
        )
        parts.append(f"<div class=\"question\"><div class=\"question-text\"><span class=\"question-number\">{q['number']}.</span> {processed_text}</div></div>")

    # Section B header
    parts.append(f'<div class="section-header"><h2>{section_b_title}</h2><div class="section-instruction">{section_b_instruction}</div></div>')

    for q in section_b_questions:
        processed_text = _process_question_text(
            q.get('text', ''),
            q.get('question_inline_images', []),
            q.get('question_answer_lines', [])
        )
        parts.append(f"<div class=\"question\"><div class=\"question-text\"><span class=\"question-number\">{q['number']}.</span> {processed_text}</div></div>")

    # Inline answer lines appended directly after last question
    if inline_answer_pages and inline_answer_pages > 0:
        inline_html = _generate_answer_lines_pages(inline_answer_pages, start_page, total_pages, show_page_numbers=False, flow_after_previous=True)
        parts.append(inline_html)

    parts.append('</div>')

    html = '\n'.join(parts)
    return {'html': html, 'next_page': start_page + 1}