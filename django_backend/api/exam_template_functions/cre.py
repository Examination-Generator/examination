from api.process_text import _process_question_text
from api.exam_template_functions.answer_lines import _generate_answer_lines_pages

def _generate_cre_question_page(questions, page_number, total_pages, inline_answer_lines=0):
    questions_html = ""
    for q in questions:
        processed_text = _process_question_text(
            q.get('text', ''),
            q.get('question_inline_images', []),
            q.get('question_answer_lines', [])
        )
        
        questions_html += f"""
        <div class="question" style="text-align: left !important; width: 100%;">
            <div class="question-text"><span class="question-number">{q['number']}.</span> {processed_text}</div>
        </div>
"""
    
    inline_answer_html = ""
    if inline_answer_lines and inline_answer_lines > 0:
        inline_answer_html = _generate_answer_lines_pages(
            inline_answer_lines,
            page_number,
            total_pages,
            show_page_numbers=False,
            flow_after_previous=True
        )

    page_html = f"""
    <div class="exam-page">
        <div class="question-flow cre-paper" style="width: 100%; max-width: 210mm; margin-left: auto; margin-right: auto; text-align: left;">
            {questions_html}
            {inline_answer_html}
        </div>
    </div>
"""
    return page_html


def _generate_cre_paper1_pages(questions, total_pages, coverpage_data=None, inline_answer_lines=0):
    return _generate_cre_question_page(questions, 2, total_pages, inline_answer_lines=inline_answer_lines)


