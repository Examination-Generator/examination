from api.process_text import _process_question_text


def _generate_kiswahili_paper1_page(questions, total_pages, coverpage_data=None):
    current_page = 2
    
    # Add instruction before questions
    instruction_html = """
        <div style="font-weight: bold; margin-bottom: 10px; margin-top: 0; font-size: 12pt;">
            Swali la kwanza ni lazima kisha uchague lingine moja kwa zilizo salia
        </div>
"""
    
    # Generate all questions on one page
    questions_html = ""
    for q in questions:
        processed_text = _process_question_text(
            q.get('text', ''),
            q.get('question_inline_images', []),
            q.get('question_answer_lines', [])
        )
        
        questions_html += f"""
        <div class="question" style="text-align: left !important; margin-top:0; background-color: blue;">
            <div class="question-text" style="background-color:grey;margin: 0; text-align: left !important;"><span class="question-number">{q['number']}.</span> {processed_text}</div>
        </div>
"""
    
    page_html = f"""
    <!-- Page {current_page} -->
    <div class="exam-page page-break">
        {instruction_html}
        <div class="question-flow chemistry-paper1" style="width: 100%; max-width: 210mm; margin-left: auto; margin-right: auto; text-align: left;">
         {questions_html}
        </div>
    </div>
"""
    
    return page_html