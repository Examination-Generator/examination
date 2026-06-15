from api.process_text import _process_question_text

def _generate_english_paper1_pages(questions, start_page, total_pages):
    # Define section titles for each question
    section_titles = {
        1: "Functional Skills",
        2: "Cloze Test",
        3: "Oral Skills"
    }
    
    questions_html = ""
    for q in questions:
        q_number = int(q.get('number', 0))
        
        # Add section title before the question if it's question 1, 2, or 3
        if q_number in section_titles:
            section_title = section_titles[q_number]
            questions_html += f"""
        <div class="simple-section-title">{section_title}</div>
"""
        
        processed_text = _process_question_text(
            q.get('text', ''),
            q.get('question_inline_images', []),
            q.get('question_answer_lines', [])
        )
        
        questions_html += f"""
        <div class="question" style="text-align: left !important;">
            <div class="question-text"><span class="question-number">{q['number']}.</span> {processed_text}</div>
        </div>
"""
    
    page_html = f"""
    <!-- Page {start_page} -->
    <div class="exam-page page-break">
        {questions_html}        
        <div class="page-number">Page {start_page} of {total_pages}</div>
    </div>
"""
    
    return {
        'html': page_html,
        'next_page': start_page + 1
    }