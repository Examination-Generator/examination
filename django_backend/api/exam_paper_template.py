"""
Full Exam Paper Template Generator
Generates complete exam papers with coverpage and paginated questions
"""

from .coverpage_templates import BiologyPaper1Coverpage
import re
import base64


def generate_full_exam_html(coverpage_data, questions, coverpage_class=None):
    """
    Generate complete exam paper HTML with coverpage and all questions
    
    Args:
        coverpage_data (dict): Coverpage information
        questions (list): List of question dictionaries with 'number', 'text', 'marks', 
                         'question_inline_images', 'question_answer_lines'
        coverpage_class: Coverpage class to use (defaults to BiologyPaper1Coverpage)
    
    Returns:
        str: Complete HTML document
    """
    
    # Use provided coverpage class or default
    if coverpage_class is None:
        coverpage_class = BiologyPaper1Coverpage
    
    # Generate coverpage HTML (page 1)
    coverpage_html = coverpage_class.generate_html(coverpage_data)
    
    # Extract coverpage content (remove html/body tags to combine later)
    coverpage_body = re.search(r'<body>(.*?)</body>', coverpage_html, re.DOTALL)
    if coverpage_body:
        coverpage_content = coverpage_body.group(1)
    else:
        coverpage_content = coverpage_html
    
    # Detect paper type from coverpage data
    is_paper2 = coverpage_data.get('paper_type') == 'Paper 2'
    
    # Use total_pages from coverpage_data if available (Paper 2 has dynamic calculation)
    total_pages = coverpage_data.get('total_pages')
    
    # Fallback to calculated pages if not provided
    if total_pages is None:
        if is_paper2:
            # Paper 2: 1 coverpage + 3 Section A pages + 2 Section B pages + 4 answer pages
            total_pages = 10
        else:
            # Paper 1: Assuming ~3-4 questions per page
            total_pages = 1 + ((len(questions) + 2) // 3)
    
    # Generate question pages (use specialized function for Paper 2)
    if is_paper2:
        questions_html = _generate_paper2_question_pages(questions, total_pages)
    else:
        questions_html = _generate_question_pages(questions, total_pages)
    
    # Combine everything
    full_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{coverpage_data.get('paper_name', 'Exam Paper')} - Full Preview</title>
    <style>
        @page {{
            size: A4;
            margin: 0;
        }}
        
        @media print {{
            .page-break {{
                page-break-after: always;
                break-after: page;
            }}
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Times New Roman', Times, serif;
            background: #f0f0f0;
        }}
        
        .exam-page {{
            width: 210mm;
            min-height: 297mm;
            padding: 20mm;
            background: white;
            margin: 10mm auto;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            position: relative;
        }}
        
        @media print {{
            .exam-page {{
                margin: 0;
                box-shadow: none;
            }}
        }}
        
        /* Page number styling */
        .page-number {{
            position: absolute;
            bottom: 15mm;
            right: 20mm;
            font-size: 11px;
            font-weight: bold;
        }}
        
        /* Question page header */
        .question-page-header {{
            text-align: center;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid black;
        }}
        
        .question-page-header h2 {{
            font-size: 16px;
            margin-bottom: 5px;
        }}
        
        .question-page-header p {{
            font-size: 12px;
            font-style: italic;
        }}
        
        /* Questions styling */
        .question {{
            margin-bottom: 30px;
        }}
        
        .question-header {{
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            margin-bottom: 10px;
        }}
        
        .question-number {{
            font-weight: bold;
            font-size: 14px;
        }}
        
        .question-marks {{
            font-size: 12px;
            font-weight: bold;
            background: #f0f0f0;
            padding: 2px 8px;
            border-radius: 3px;
        }}
        
        .question-text {{
            font-size: 12px;
            line-height: 1.8;
            text-align: justify;
            white-space: pre-wrap;
        }}
        
        /* Image styling */
        .question-image {{
            display: block;
            margin: 10px auto;
            max-width: 100%;
            border: 1px solid #ccc;
            border-radius: 4px;
        }}
        
        .question-image.inline {{
            display: inline-block;
            vertical-align: middle;
            margin: 0 5px;
        }}
        
        /* Answer lines styling */
        .answer-lines {{
            margin: 10px 0;
            max-width: 700px;
        }}
        
        .answer-line {{
            width: 100%;
            height: 25px;
            margin: 0;
            padding: 0;
            border-bottom: 1px solid #333;
        }}
        
        .answer-line.dotted {{
            border-bottom: 2px dotted rgba(0, 0, 0, 0.5);
        }}
        
        .answer-line.solid {{
            border-bottom: 2px solid rgba(0, 0, 0, 0.5);
        }}
        
        .answer-space {{
            margin-top: 10px;
            border-top: 1px dotted #999;
            min-height: 80px;
        }}
        
        /* Section styling for Paper 2 */
        .section-header {{
            text-align: center;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 3px solid black;
        }}
        
        .section-header h2 {{
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 8px;
            text-transform: uppercase;
        }}
        
        .section-instruction {{
            font-size: 12px;
            font-style: italic;
            margin-top: 5px;
        }}
        
        /* Answer section header */
        .answer-section-header {{
            text-align: center;
            margin-bottom: 15px;
            padding: 10px;
            background: #f5f5f5;
            border: 2px solid #333;
        }}
        
        .answer-section-header p {{
            margin: 3px 0;
        }}
        
        .answer-lines-container {{
            margin: 20px 0;
        }}
        
        /* Formatting styles */
        .bold {{
            font-weight: bold;
        }}
        
        .italic {{
            font-style: italic;
        }}
        
        .underline {{
            text-decoration: underline;
        }}
        
        /* Coverpage styles from original template */
        .coverpage {{
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 20px;
            position: relative;
        }}
        
        .logo-container {{
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }}
        
        .logo-container.left {{ justify-content: flex-start; }}
        .logo-container.center {{ justify-content: center; }}
        .logo-container.right {{ justify-content: flex-end; }}
        
        .logo-container img {{
            max-width: 100px;
            max-height: 100px;
            object-fit: contain;
        }}
        
        .school-name {{
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 5px;
            text-transform: uppercase;
        }}
        
        .class-name {{
            font-size: 14px;
            margin-bottom: 15px;
        }}
        
        .exam-title {{
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 10px;
            text-transform: uppercase;
        }}
        
        .paper-details {{
            font-size: 14px;
            margin-bottom: 20px;
        }}
        
        .candidate-info {{
            border: none;
            padding: 15px;
            margin-bottom: 20px;
        }}
        
        .info-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px 20px;
        }}
        
        .info-row {{
            display: flex;
            align-items: center;
        }}
        
        .info-row-full {{
            grid-column: 1 / -1;
            display: flex;
            align-items: center;
        }}
        
        .info-label {{
            font-weight: bold;
            font-size: 12px;
            min-width: 120px;
        }}
        
        .info-field {{
            flex: 1;
            border-bottom: 1px dotted black;
            min-height: 25px;
            padding: 2px 5px;
        }}
        
        .instructions {{
            margin-bottom: 20px;
        }}
        
        .instructions-title {{
            font-weight: bold;
            font-size: 14px;
            margin-bottom: 10px;
            text-decoration: underline;
        }}
        
        .instructions ol {{
            margin-left: 20px;
            font-size: 12px;
            line-height: 1.6;
        }}
        
        .instructions li {{
            margin-bottom: 8px;
        }}
        
        .instructions li.bold {{
            font-weight: bold;
        }}
        
        .marking-grid-container {{
            margin-top: auto;
            padding-top: 20px;
        }}
        
        .grid-title {{
            font-weight: bold;
            font-size: 13px;
            margin-bottom: 10px;
            text-align: center;
        }}
        
        .marking-grid {{
            width: 100%;
            border-collapse: collapse;
            border: 2px solid black;
        }}
        
        .marking-grid td {{
            border: 1px solid black;
            text-align: center;
            font-size: 10px;
            font-weight: bold;
            padding: 8px 4px;
            height: 30px;
        }}
        
        .question-number {{
            min-width: 35px;
            width: 35px;
        }}
        
        /* Empty question cells (shown but no number) */
        .empty-question-cell {{
            min-width: 35px;
            width: 35px;
            background-color: white;
            border: none !important;
        }}
        
        /* Add spacing before second row */
        .row-with-spacing td {{
            border-top: 2px solid black;
            padding-top: 8px;
        }}
        
        /* Override border-top for empty and gap cells in spacing row */
        .row-with-spacing .empty-question-cell,
        .row-with-spacing .gap-cell {{
            border-top: none !important;
        }}
        
        /* Gap cell between questions and Grand Total */
        .gap-cell {{
            border: none !important;
            background-color: white;
            min-width: 15px;
            width: 15px;
        }}
        
        .grand-total-cell {{
            background-color: #f0f0f0;
            font-size: 10px;
            font-weight: bold;
            border: 2px solid black;
            padding: 5px 10px;
            min-width: 80px;
        }}
        
        .total-box {{
            min-width: 60px;
            width: 60px;
            min-height: 60px;
            border: 2px solid black;
            background-color: white;
        }}
    </style>
</head>
<body>
    <!-- Page 1: Coverpage -->
    <div class="exam-page page-break">
        {coverpage_content}
    </div>
    
    <!-- Question Pages -->
    {questions_html}
</body>
</html>
"""
    
    return full_html


def _process_question_text(text, images=None, answer_lines=None):
    """
    Process question text to render images and answer lines
    
    Args:
        text (str): Question text with placeholders
        images (list): List of image objects with id, url, width, height
        answer_lines (list): List of answer line configurations
    
    Returns:
        str: Processed HTML with images and lines rendered
    """
    if not text:
        return ""
    
    # Create lookup dictionaries
    images_dict = {}
    if images:
        for img in images:
            images_dict[float(img.get('id', 0))] = img
    
    lines_dict = {}
    if answer_lines:
        for line in answer_lines:
            lines_dict[float(line.get('id', 0))] = line
    
    # Split text by formatting, images, and lines
    pattern = r'(\*\*.*?\*\*|\*.*?\*|__.*?__|_.*?_|\[IMAGE:[\d.]+:(?:\d+x\d+|\d+)px\]|\[LINES:[\d.]+\])'
    parts = re.split(pattern, text)
    
    result = []
    
    for part in parts:
        if not part:
            continue
            
        # Bold: **text**
        if part.startswith('**') and part.endswith('**') and len(part) > 4:
            content = part[2:-2]
            result.append(f'<strong>{content}</strong>')
            
        # Italic: *text* (not **)
        elif part.startswith('*') and part.endswith('*') and not part.startswith('**') and len(part) > 2:
            content = part[1:-1]
            result.append(f'<em>{content}</em>')
            
        # Underline: __text__
        elif part.startswith('__') and part.endswith('__') and len(part) > 4:
            content = part[2:-2]
            result.append(f'<u>{content}</u>')
            
        # Single underscore italic: _text_
        elif part.startswith('_') and part.endswith('_') and not part.startswith('__') and len(part) > 2:
            content = part[1:-1]
            result.append(f'<em>{content}</em>')
            
        # Answer lines: [LINES:id]
        elif part.startswith('[LINES:') and part.endswith(']'):
            line_match = re.match(r'\[LINES:([\d.]+)\]', part)
            if line_match:
                line_id = float(line_match.group(1))
                line_config = lines_dict.get(line_id)
                
                if line_config:
                    num_lines = line_config.get('numberOfLines', 5)
                    line_height = line_config.get('lineHeight', 30)
                    line_style = line_config.get('lineStyle', 'dotted')
                    opacity = line_config.get('opacity', 0.5)
                    
                    full_lines = int(num_lines)
                    has_half_line = (num_lines % 1) != 0
                    
                    lines_html = '<div class="answer-lines">'
                    
                    # Full lines
                    for _ in range(full_lines):
                        lines_html += f'<div class="answer-line {line_style}" style="height: {line_height}px; border-bottom: 2px {line_style} rgba(0, 0, 0, {opacity});"></div>'
                    
                    # Half line if needed
                    if has_half_line:
                        half_height = line_height / 2
                        lines_html += f'<div class="answer-line {line_style}" style="height: {half_height}px; border-bottom: 2px {line_style} rgba(0, 0, 0, {opacity});"></div>'
                    
                    lines_html += '</div>'
                    result.append(lines_html)
                else:
                    # Line config not found - show placeholder
                    result.append(f'<div style="margin: 10px 0; padding: 10px; background: #fff3cd; border: 1px solid #ffc107; border-radius: 4px; font-size: 11px;">⚠️ Answer Lines (ID: {int(line_id)})</div>')
        
        # Images: [IMAGE:id:WxH] or [IMAGE:id:Wpx]
        elif part.startswith('[IMAGE:') and part.endswith('px]'):
            # New format: [IMAGE:id:300x200px]
            image_match_new = re.match(r'\[IMAGE:([\d.]+):(\d+)x(\d+)px\]', part)
            # Old format: [IMAGE:id:300px]
            image_match_old = re.match(r'\[IMAGE:([\d.]+):(\d+)px\]', part)
            
            if image_match_new or image_match_old:
                if image_match_new:
                    image_id = float(image_match_new.group(1))
                    image_width = int(image_match_new.group(2))
                    image_height = int(image_match_new.group(3))
                else:
                    image_id = float(image_match_old.group(1))
                    image_width = int(image_match_old.group(2))
                    image_height = None
                
                image = images_dict.get(image_id)
                
                if image and image.get('url'):
                    img_url = image['url']
                    img_alt = image.get('name', 'Question image')
                    
                    # Determine if image should be inline or block
                    style = f"width: {image_width}px;"
                    if image_height:
                        style += f" height: {image_height}px;"
                    
                    result.append(f'<img src="{img_url}" alt="{img_alt}" class="question-image" style="{style}" />')
                else:
                    # Image not found - show placeholder
                    result.append(f'<div style="margin: 10px 0; padding: 10px; background: #f8d7da; border: 1px solid #dc3545; border-radius: 4px; font-size: 11px;">❌ Image Not Found (ID: {int(image_id)}, Size: {image_width}×{image_height or "auto"}px)</div>')
        
        # Regular text
        else:
            result.append(part)
    
    return ''.join(result)


def _generate_paper2_question_pages(questions, total_pages):
    """
    Generate paginated question pages for Biology Paper 2
    Split into Section A (Questions 1-5) and Section B (Questions 6-8)
    Add 250 answer lines immediately after Section B (no page break)
    
    Args:
        questions (list): List of questions with 'number', 'text', 'marks'
        total_pages (int): Total number of pages in the exam
    
    Returns:
        str: HTML for all question pages
    """
    
    pages_html = []
    current_page = 2  # Page 1 is coverpage
    
    # Section A: Questions 1-5
    section_a_questions = [q for q in questions if q['number'] <= 5]
    section_b_questions = [q for q in questions if q['number'] >= 6]
    
    # Generate Section A pages
    section_a_html = _generate_section_pages(
        section_a_questions, 
        "SECTION A (40 MARKS)", 
        "Answer ALL questions in this section",
        current_page,
        total_pages,
        is_last_section=False
    )
    pages_html.append(section_a_html['html'])
    current_page = section_a_html['next_page']
    
    # Generate Section B pages with answer lines immediately after
    section_b_html = _generate_section_pages(
        section_b_questions, 
        "SECTION B (40 MARKS)", 
        "Answer question 6 (compulsory) and EITHER question 7 or 8",
        current_page,
        total_pages,
        is_last_section=True,
        answer_lines=100
    )
    pages_html.append(section_b_html['html'])
    
    return '\n'.join(pages_html)


def _generate_section_pages(questions, section_title, section_instruction, start_page, total_pages, is_last_section=False, answer_lines=0):
    """
    Generate pages for a specific section
    
    Args:
        is_last_section (bool): If True, add answer lines on the same page as the last question
        answer_lines (int): Number of answer lines to add after last section
    
    Returns:
        dict: {'html': str, 'next_page': int}
    """
    pages_html = []
    current_page = start_page
    questions_per_page = 2  # Fewer questions per page for Paper 2
    
    # Process all questions with section header on first page only
    for i in range(0, len(questions), questions_per_page):
        page_questions = questions[i:i + questions_per_page]
        is_first_page = (i == 0)
        is_last_page_of_questions = (i + questions_per_page >= len(questions))
        
        questions_html = ""
        for q in page_questions:
            processed_text = _process_question_text(
                q.get('text', ''),
                q.get('question_inline_images', []),
                q.get('question_answer_lines', [])
            )
            
            questions_html += f"""
        <div class="question">
            <div class="question-text"><span class="question-number">{q['number']}.</span> {processed_text} <span class="marks">({q.get('marks', 0)} marks)</span></div>
        </div>
"""
        
        # Add section header only on first page
        section_header_html = ""
        if is_first_page:
            section_header_html = f"""
        <div class="section-header">
            <h2>{section_title}</h2>
            <p class="section-instruction">{section_instruction}</p>
        </div>
        """
        
        # If this is the last section and last page, add answer lines immediately
        answer_section_html = ""
        if is_last_section and is_last_page_of_questions and answer_lines > 0:
            # Add answer section header and start lines on same page
            answer_section_html = f"""
        
        <div class="answer-section-header" style="margin-top: 30px;">
            <p><strong>ANSWER SECTION B HERE</strong></p>
            <p style="font-size: 11px; color: #666;">Use these lines to write your answers for Section B questions (6, 7 or 8)</p>
        </div>
        
        <div class="answer-lines-container">
"""
            # Add initial lines to fill this page (estimate remaining space)
            initial_lines = 8  # Approximately 8 lines fit after a question on same page
            for _ in range(initial_lines):
                answer_section_html += '            <div class="answer-line"></div>\n'
            
            answer_section_html += "        </div>"
        
        page_html = f"""
    <!-- Page {current_page} -->
    <div class="exam-page page-break">
        {section_header_html}
        {questions_html}
        {answer_section_html}
        
        <div class="page-number">Page {current_page} of {total_pages}</div>
    </div>
"""
        pages_html.append(page_html)
        current_page += 1
    
    # If answer lines were added, generate remaining answer line pages
    if is_last_section and answer_lines > 0:
        initial_lines = 8
        remaining_lines = answer_lines - initial_lines
        answer_lines_html = _generate_answer_lines_continuation(remaining_lines, current_page, total_pages)
        pages_html.append(answer_lines_html)
    
    return {'html': '\n'.join(pages_html), 'next_page': current_page}


def _generate_answer_lines_continuation(num_lines, start_page, total_pages):
    """
    Generate continuation pages with answer lines (after initial lines on last question page)
    
    Args:
        num_lines (int): Number of remaining answer lines
        start_page (int): Starting page number
        total_pages (int): Total pages in exam
    
    Returns:
        str: HTML for answer line continuation pages
    """
    lines_per_page = 25
    total_answer_pages = (num_lines + lines_per_page - 1) // lines_per_page
    pages_html = []
    current_page = start_page
    
    for page_num in range(total_answer_pages):
        lines_on_this_page = min(lines_per_page, num_lines - (page_num * lines_per_page))
        
        lines_html = ""
        for i in range(lines_on_this_page):
            lines_html += '            <div class="answer-line"></div>\n'
        
        is_last_page = current_page >= total_pages
        
        page_html = f"""
    <!-- Page {current_page} - Answer Lines (continued) -->
    <div class="exam-page {'page-break' if not is_last_page else ''}">
        <div class="answer-lines-container">
            {lines_html}
        </div>
        
        <div class="page-number">Page {current_page} of {total_pages}</div>
    </div>
"""
        pages_html.append(page_html)
        current_page += 1
    
    return '\n'.join(pages_html)


def _generate_answer_lines_pages(num_lines, start_page, total_pages):
    """
    Generate pages with answer lines for Section B
    
    Args:
        num_lines (int): Number of answer lines (250 for Paper 2)
        start_page (int): Starting page number
        total_pages (int): Total pages in exam
    
    Returns:
        str: HTML for answer line pages
    """
    lines_per_page = 25
    total_answer_pages = (num_lines + lines_per_page - 1) // lines_per_page
    pages_html = []
    current_page = start_page
    
    for page_num in range(total_answer_pages):
        lines_on_this_page = min(lines_per_page, num_lines - (page_num * lines_per_page))
        
        lines_html = ""
        for i in range(lines_on_this_page):
            lines_html += '<div class="answer-line"></div>\n'
        
        is_last_page = current_page >= total_pages
        
        page_html = f"""
    <!-- Page {current_page} - Answer Lines -->
    <div class="exam-page {'page-break' if not is_last_page else ''}">
        <div class="answer-section-header">
            <p><strong>ANSWER SECTION B HERE</strong></p>
            <p style="font-size: 11px; color: #666;">Use these lines to write your answers for Section B questions (6, 7 or 8)</p>
        </div>
        
        <div class="answer-lines-container">
            {lines_html}
        </div>
        
        <div class="page-number">Page {current_page} of {total_pages}</div>
    </div>
"""
        pages_html.append(page_html)
        current_page += 1
    
    return '\n'.join(pages_html)


def _generate_question_pages(questions, total_pages):
    """
    Generate paginated question pages
    
    Args:
        questions (list): List of questions with 'number', 'text', 'marks', 
                         'question_inline_images', 'question_answer_lines'
        total_pages (int): Total number of pages in the exam
    
    Returns:
        str: HTML for all question pages
    """
    
    questions_per_page = 3  # Adjust based on question length
    pages_html = []
    current_page = 2  # Page 1 is coverpage
    
    for i in range(0, len(questions), questions_per_page):
        page_questions = questions[i:i + questions_per_page]
        
        questions_html = ""
        for q in page_questions:
            # Process question text to render images and lines
            processed_text = _process_question_text(
                q.get('text', ''),
                q.get('question_inline_images', []),
                q.get('question_answer_lines', [])
            )
            
            questions_html += f"""
        <div class="question">
            <div class="question-text"><span class="question-number">{q['number']}.</span> {processed_text}</div>
            <!--<div class="answer-space"></div>-->
        </div>
"""
        
        page_html = f"""
    <!-- Page {current_page} -->
    <div class="exam-page {'page-break' if current_page < total_pages else ''}">
        <div class="question-page-header">
            <h2>BIOLOGY PAPER 1</h2>
            <p>(Continue answering all questions in the spaces provided)</p>
        </div>
        
        {questions_html}
        
        <div class="page-number">Page {current_page} of {total_pages}</div>
    </div>
"""
        
        pages_html.append(page_html)
        current_page += 1
    
    return '\n'.join(pages_html)