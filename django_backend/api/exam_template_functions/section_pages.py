from api.page_number_extrctor import extract_paper_number_from_name
from api.process_text import _process_question_text
from api.exam_template_functions.answer_lines import _generate_answer_lines_pages

def _generate_section_pages(questions, section_title, section_instruction, start_page, total_pages, is_last_section=False, answer_lines=0, paper_name='', flow_last_page=False, inline_answer_lines=0):
    pages_html = []
    current_page = start_page

    # Extract paper number if paper_name provided
    paper_number = 1
    if paper_name:
        try:
            paper_number = extract_paper_number_from_name(paper_name)
        except ValueError:
            paper_number = 1

    is_kiswahili_paper2 = 'KISWAHILI' in paper_name.upper() and paper_number == 2
    is_business_paper1 = 'BUSINESS' in paper_name.upper() and paper_number == 1
    is_chemistry_paper1 = 'CHEMISTRY' in paper_name.upper() and paper_number == 1

    if is_kiswahili_paper2 or is_business_paper1 or is_chemistry_paper1:
        section_title = None
        section_instruction = None

    questions_html = ""
    for q in questions:
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

    if inline_answer_lines and flow_last_page:
        inline_lines_html = _generate_answer_lines_pages(inline_answer_lines, current_page, total_pages, show_page_numbers=False, flow_after_previous=True)
        questions_html += inline_lines_html

    section_header_html = ""
    if section_title is not None and not (is_kiswahili_paper2 or is_business_paper1 or is_chemistry_paper1):
        section_header_html = f"""
        <div class="section-header">
            <h2>{section_title}</h2>
            <p class="section-instruction">{section_instruction}</p>
        </div>
        """

    page_class = 'exam-page'
    if not flow_last_page:
        # page_class += ' page-break'
        pass

    page_html = f"""
        <!-- Page {current_page} -->
        <div class="{page_class} question-flow chemistry-paper1">
            {section_header_html}
            {questions_html}
        </div>
    """
    pages_html.append(page_html)
    current_page += 1

    if is_last_section and answer_lines > 0:
        initial_lines = 8

    return {'html': '\n'.join(pages_html), 'next_page': current_page}
