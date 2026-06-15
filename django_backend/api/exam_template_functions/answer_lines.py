def _generate_answer_lines_pages(num_pages, start_page, total_pages, show_page_numbers=True, flow_after_previous=False):
    lines_per_page = 25

    if flow_after_previous:
        lines_html = ''
        for _ in range(num_pages * lines_per_page):
            lines_html += '<div class="answer-line dotted" style="height: 28px; margin: 8px 0;"></div>'
        return f'''
    <div class="answer-lines-flow">
        {lines_html}
    </div>
'''

    pages_html = []
    
    for i in range(num_pages):
        lines_html = ''
        for _ in range(lines_per_page):
            lines_html += '<div class="answer-line dotted" style="height: 25px; margin: 8px 0;"></div>'
        page_number_html = ''
        if show_page_numbers:
            page_number_html = f'<div class="page-number">Page {start_page + i} of {total_pages}</div>'
        page_html = f'''
    <div class="exam-page">
        {lines_html}
    </div>
'''
        pages_html.append(page_html)
    
    return '\n'.join(pages_html)