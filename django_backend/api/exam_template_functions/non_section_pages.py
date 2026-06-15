from api.process_text import _process_question_text

def _generate_non_sectioned_pages(questions, start_page, total_pages):
    pages_html = []
    current_page = start_page
    questions_per_page = 2
    
    for i in range(0, len(questions), questions_per_page):
        page_questions = questions[i:i + questions_per_page]
        
        questions_html = ""
        for q in page_questions:
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
    <!-- Page {current_page} -->
    <div class="exam-page page-break">
        {questions_html}        
        <div class="page-number">Page {current_page} of {total_pages}</div>
    </div>
"""
        pages_html.append(page_html)
        current_page += 1
    
    return {'html': '\n'.join(pages_html), 'next_page': current_page}