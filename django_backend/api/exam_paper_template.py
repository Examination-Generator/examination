"""
Full Exam Paper Template Generator
Generates complete exam papers with coverpage and paginated questions
Updated to dynamically select the correct coverpage class based on paper type
"""

from .coverpage_templates import (
    BiologyPaper1Coverpage, 
    BiologyPaper2Coverpage, 
    PhysicsPaper1Coverpage,
    ChemistryPaper1Coverpage,
    ChemistryPaper2Coverpage,
    MarkingSchemeCoverpage,
    BiologyPaper2MarkingSchemeCoverpage
)
import re


def get_coverpage_class(paper_data, is_marking_scheme=False):
    """
    Determine the appropriate coverpage class based on paper data
    
    Args:
        paper_data (dict): Paper information containing paper_type, subject, etc.
        is_marking_scheme (bool): Whether this is for a marking scheme
    
    Returns:
        class: Appropriate coverpage class
    """
    # Extract paper type information
    paper_type = paper_data.get('paper_type', '').upper()
    paper_name = paper_data.get('paper_name', '').upper()
    subject_name = paper_data.get('subject_name', '').upper()
    
    # Detect Biology Paper 2
    is_biology_paper2 = ('BIOLOGY' in paper_name or 'BIOLOGY' in subject_name) and \
                       ('PAPER 2' in paper_type or 'PAPER 2' in paper_name or 'PAPER II' in paper_name)
    
    # Detect Physics Paper 1
    is_physics_paper1 = ('PHYSICS' in paper_name or 'PHYSICS' in subject_name) and \
                       ('PAPER 1' in paper_type or 'PAPER 1' in paper_name or 'PAPER I' in paper_name)
    
    # Detect Chemistry Paper 1
    is_chemistry_paper1 = ('CHEMISTRY' in paper_name or 'CHEMISTRY' in subject_name) and \
                         ('PAPER 1' in paper_type or 'PAPER 1' in paper_name or 'PAPER I' in paper_name)
    
    # Detect Chemistry Paper 2
    is_chemistry_paper2 = ('CHEMISTRY' in paper_name or 'CHEMISTRY' in subject_name) and \
                         ('PAPER 2' in paper_type or 'PAPER 2' in paper_name or 'PAPER II' in paper_name)
    
    # Return appropriate coverpage class
    if is_marking_scheme:
        if is_biology_paper2 or is_chemistry_paper2:
            return BiologyPaper2MarkingSchemeCoverpage
        else:
            return MarkingSchemeCoverpage
    else:
        if is_biology_paper2:
            return BiologyPaper2Coverpage
        elif is_physics_paper1:
            return PhysicsPaper1Coverpage
        elif is_chemistry_paper1:
            return ChemistryPaper1Coverpage
        elif is_chemistry_paper2:
            return ChemistryPaper2Coverpage
        else:
            # Default to Biology Paper 1 for standard papers
            return BiologyPaper1Coverpage


def generate_full_exam_html(coverpage_data, questions, paper_data=None, coverpage_class=None):
    """
    Generate complete exam paper HTML with coverpage and all questions
    
    Args:
        coverpage_data (dict): Coverpage information
        questions (list): List of question dictionaries with 'number', 'text', 'marks', 
                         'question_inline_images', 'question_answer_lines'
        paper_data (dict): Paper metadata (subject, paper_type, etc.) - used to auto-detect coverpage
        coverpage_class: Coverpage class to use (overrides auto-detection)
    
    Returns:
        str: Complete HTML document
    """
    
    # Auto-detect coverpage class if not provided
    if coverpage_class is None:
        if paper_data is None:
            # Fallback: try to extract paper data from coverpage_data
            paper_data = {
                'paper_type': coverpage_data.get('paper_type', ''),
                'paper_name': coverpage_data.get('paper_name', ''),
                'subject_name': ''
            }
        
        coverpage_class = get_coverpage_class(paper_data, is_marking_scheme=False)
        print(f"🎯 Auto-detected coverpage class: {coverpage_class.__name__}")
    
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
        questions_html = _generate_paper2_question_pages(questions, total_pages, coverpage_data)
    else:
        questions_html = _generate_question_pages(questions, total_pages, coverpage_data)
    
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
        
        .marks {{
            font-weight: bold;
            margin-left: 10px;
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
    (Same implementation as before)
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
                    result.append(f'<div style="margin: 10px 0; padding: 10px; background: #fff3cd; border: 1px solid #ffc107; border-radius: 4px; font-size: 11px;">⚠️ Answer Lines (ID: {int(line_id)})</div>')
        
        # Images: [IMAGE:id:WxH] or [IMAGE:id:Wpx]
        elif part.startswith('[IMAGE:') and part.endswith('px]'):
            image_match_new = re.match(r'\[IMAGE:([\d.]+):(\d+)x(\d+)px\]', part)
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
                    
                    style = f"width: {image_width}px;"
                    if image_height:
                        style += f" height: {image_height}px;"
                    
                    result.append(f'<img src="{img_url}" alt="{img_alt}" class="question-image" style="{style}" />')
                else:
                    result.append(f'<div style="margin: 10px 0; padding: 10px; background: #f8d7da; border: 1px solid #dc3545; border-radius: 4px; font-size: 11px;">❌ Image Not Found (ID: {int(image_id)})</div>')
        
        # Regular text
        else:
            result.append(part)
    
    return ''.join(result)


def _generate_paper2_question_pages(questions, total_pages, coverpage_data=None):
    """
    Generate paginated question pages for Biology Paper 2
    (Same implementation as before)
    """
    pages_html = []
    current_page = 2
    
    # Determine section boundaries from coverpage_data if provided
    metadata = coverpage_data or {}
    section_a_count = metadata.get('section_a_questions', 5)
    try:
        section_a_count = int(section_a_count)
    except Exception:
        section_a_count = 5

    section_a_questions = [q for q in questions if q['number'] <= section_a_count]
    section_b_questions = [q for q in questions if q['number'] > section_a_count]
    
    # Section A title and instruction - get marks/instruction from metadata if present
    section_a_marks = 40
    section_a_title = f"SECTION A ({section_a_marks} MARKS)" if section_a_marks else "SECTION A"
    section_a_instruction = metadata.get('section_a_instruction', 'Answer ALL questions in this section')

    section_a_html = _generate_section_pages(
        section_a_questions,
        section_a_title,
        section_a_instruction,
        current_page,
        total_pages,
        is_last_section=False
    )
    pages_html.append(section_a_html['html'])
    current_page = section_a_html['next_page']
    
    # Section B title and instruction - prefer metadata; default to answer ALL questions similar to Section A
    section_b_marks = 40
    section_b_title = f"SECTION B ({section_b_marks} MARKS)" if section_b_marks else "SECTION B"
    section_b_instruction = metadata.get('section_b_instruction', 'Answer ALL questions in this section')

    section_b_html = _generate_section_pages(
        section_b_questions,
        section_b_title,
        section_b_instruction,
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
    (Same implementation as before)
    """
    pages_html = []
    current_page = start_page
    questions_per_page = 2
    
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
            <div class="question-text"><span class="question-number">{q['number']}.</span> {processed_text}</div>
        </div>
"""
        
        section_header_html = ""
        if is_first_page:
            section_header_html = f"""
        <div class="section-header">
            <h2>{section_title}</h2>
            <p class="section-instruction">{section_instruction}</p>
        </div>
        """
        
#         answer_section_html = ""
#         if is_last_section and is_last_page_of_questions and answer_lines > 0:
#             answer_section_html = f"""
        
#         <div class="answer-section-header" style="margin-top: 30px;">
#             <p><strong>ANSWER SECTION B HERE</strong></p>
#             <p style="font-size: 11px; color: #666;">Use these lines to write your answers for Section B questions (6, 7 or 8)</p>
#         </div>
        
#         <div class="answer-lines-container">
# """
            # initial_lines = 8
            # for _ in range(initial_lines):
            #     answer_section_html += '            <div class="answer-line"></div>\n'
            
            # answer_section_html += "        </div>"
        
        page_html = f"""
    <!-- Page {current_page} -->
    <div class="exam-page page-break">
        {section_header_html}
        {questions_html}        
        <div class="page-number">Page {current_page} of {total_pages}</div>
    </div>
"""
        pages_html.append(page_html)
        current_page += 1
    
    if is_last_section and answer_lines > 0:
        initial_lines = 8
        remaining_lines = answer_lines - initial_lines
        answer_lines_html = _generate_answer_lines_continuation(remaining_lines, current_page, total_pages)
        pages_html.append(answer_lines_html)
    
    return {'html': '\n'.join(pages_html), 'next_page': current_page}


def _generate_answer_lines_continuation(num_lines, start_page, total_pages):
    """
    Generate continuation pages with answer lines
    (Same implementation as before)
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


def _generate_question_pages(questions, total_pages, coverpage_data=None):
    """
    Generate paginated question pages for standard papers
    (Same implementation as before)
    """
    questions_per_page = 3
    pages_html = []
    current_page = 2
    
    # Determine section boundaries from coverpage_data if available
    metadata = coverpage_data or {}
    section_a_count = metadata.get('section_a_questions') or metadata.get('section_a_questions', 0)
    try:
        section_a_count = int(section_a_count)
    except Exception:
        section_a_count = 0

    page_last_section = None
    for i in range(0, len(questions), questions_per_page):
        page_questions = questions[i:i + questions_per_page]
        
        # Determine first and last question sections for this page
        first_qnum = int(page_questions[0].get('number', 0)) if page_questions else 0
        first_section = 'A' if (section_a_count and first_qnum <= section_a_count) else 'B'
        last_qnum = int(page_questions[-1].get('number', 0)) if page_questions else 0
        last_section_on_page = 'A' if (section_a_count and last_qnum <= section_a_count) else 'B'

        # If this page continues the same section from previous page, show a small continue header
        page_header_html = ''
        if page_last_section is not None and page_last_section == first_section:
            page_header_html = f"""
        <div class=\"question-page-header\"> 
            <h2>Continue answering ALL questions in this section</h2>
        </div>
"""

        questions_html = ""
        # Track last section to insert headers when section changes within the page
        last_section = page_last_section
        for q in page_questions:
            processed_text = _process_question_text(
                q.get('text', ''),
                q.get('question_inline_images', []),
                q.get('question_answer_lines', [])
            )
            # Determine section by question number and available section count
            qnum = int(q.get('number', 0))
            current_section = 'A' if (section_a_count and qnum <= section_a_count) else 'B'

            # If section changed (or starting), insert section header
            if last_section != current_section:
                # Get marks for section from coverpage_data if present
                if current_section == 'A':
                    s_marks = metadata.get('section_a_marks', None)
                else:
                    s_marks = metadata.get('section_b_marks', None)

                s_marks_text = f" ({s_marks} MARKS)" if s_marks else ''
                # Instruction text: by default we show 'Answer ALL questions in this section.'
                instruction_text = metadata.get(f'section_{current_section.lower()}_instruction', 'Answer ALL questions in this section.')

                questions_html += f"""
        <div class=\"section-header\"> 
            <h2>Section {current_section}</h2>
            <div class=\"section-instruction\">{instruction_text}</div>
        </div>
"""
                last_section = current_section

            questions_html += f"""
        <div class="question">
            <div class="question-text"><span class="question-number">{q['number']}.</span> {processed_text}</div>
        </div>
"""
        
        page_html = f"""
    <div class="exam-page {'page-break' if current_page < total_pages else ''}">
        {page_header_html}
        
        {questions_html}
        
        <div class="page-number">Page {current_page} of {total_pages}</div>
    </div>
"""
        
        pages_html.append(page_html)
        current_page += 1
        # remember section for next page
        page_last_section = last_section_on_page
    
    return '\n'.join(pages_html)