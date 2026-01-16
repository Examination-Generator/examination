"""
Full Exam Paper Template Generator
Generates complete exam papers with coverpage and paginated questions
Updated to dynamically select the correct coverpage class based on paper type
"""

from .coverpage_templates import (
    BiologyPaper1Coverpage, 
    BiologyPaper2Coverpage, 
    BiologyPaper2MarkingSchemeCoverpage,
    BusinessPaper1Coverpage,
    BusinessPaper2Coverpage,
    PhysicsPaper1Coverpage,
    PhysicsPaper2Coverpage,
    ChemistryPaper1Coverpage,
    ChemistryPaper2Coverpage,
    MathematicsPaper1Coverpage,
    MathematicsPaper2Coverpage,
    CREPaper1Coverpage,
    CREPaper2Coverpage,
    GeographyPaper1Coverpage,
    GeographyPaper2Coverpage,
    KiswahiliPaper1Coverpage,
    KiswahiliPaper2Coverpage,
    MarkingSchemeCoverpage,
    BiologyPaper2MarkingSchemeCoverpage
)
import re
from .page_number_extrctor import extract_paper_number_from_name


def get_coverpage_class(paper_data, is_marking_scheme=False):
    # Extract paper type information
    # paper_type = paper_data.get('paper_type', '').upper()
    paper_name = paper_data.get('paper_name', '').upper()
    subject_name = paper_data.get('subject_name', '').upper()
    paper_number = extract_paper_number_from_name(paper_name)
    
    # Define mappings at module level or class level
    PAPER_1_COVERS = {
        'BIOLOGY': BiologyPaper1Coverpage,
        'PHYSICS': PhysicsPaper1Coverpage,
        'CHEMISTRY': ChemistryPaper1Coverpage,
        'MATHEMATICS': MathematicsPaper1Coverpage,
        'KISWAHILI': KiswahiliPaper1Coverpage,
        'CRE': CREPaper1Coverpage,
        'GEOGRAPHY': GeographyPaper1Coverpage,
        'BUSINESS': BusinessPaper1Coverpage,
    }

    PAPER_2_COVERS = {
        'BIOLOGY': BiologyPaper2Coverpage,
        'CHEMISTRY': ChemistryPaper2Coverpage,
        'MATHEMATICS': MathematicsPaper2Coverpage,
        'KISWAHILI': KiswahiliPaper2Coverpage,
        'CRE': CREPaper2Coverpage,
        'GEOGRAPHY': GeographyPaper2Coverpage,
        'BUSINESS': BusinessPaper2Coverpage,
    }

    # Then your function becomes:
    if is_marking_scheme:
        return BiologyPaper2MarkingSchemeCoverpage if subject_name == 'BIOLOGY' else MarkingSchemeCoverpage

    if paper_number == 1:
        return PAPER_1_COVERS.get(subject_name, BiologyPaper1Coverpage)
    elif paper_number == 2:
        return PAPER_2_COVERS.get(subject_name, BiologyPaper2Coverpage)
        


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
        print(f"Auto-detected coverpage class: {coverpage_class.__name__}")
    
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
    is_paper1 = coverpage_data.get('paper_type') == 'Paper 1'
    
    # Get paper name and extract paper number using the helper function
    paper_name = coverpage_data.get('paper_name', '').upper()
    try:
        paper_number = extract_paper_number_from_name(paper_name)
    except ValueError:
        paper_number = 1  # Default to Paper 1 if extraction fails
    
    # Add Mathematics section data if not present
    is_mathematics = 'MATHEMATICS' in paper_name or 'MATHS' in paper_name
    is_agriculture = 'AGRICULTURE' in paper_name
    
    if is_mathematics:
        # Mathematics has Section I (Questions 1-16, 50 marks) and Section II (Questions 17-24, 50 marks, answer any 5)
        if 'section_a_questions' not in coverpage_data:
            coverpage_data['section_a_questions'] = 16
        if 'section_a_marks' not in coverpage_data:
            coverpage_data['section_a_marks'] = 50
        if 'section_b_marks' not in coverpage_data:
            coverpage_data['section_b_marks'] = 50
        if 'section_a_instruction' not in coverpage_data:
            coverpage_data['section_a_instruction'] = 'Answer ALL questions in this section'
        if 'section_b_instruction' not in coverpage_data:
            coverpage_data['section_b_instruction'] = 'Answer any FIVE questions from this section'
    elif is_agriculture:
        # Agriculture has 3 sections: A (1-15, 30 marks), B (16-19, 20 marks), C (20-22, 40 marks)
        if 'section_a_questions' not in coverpage_data:
            coverpage_data['section_a_questions'] = 15
        if 'section_a_marks' not in coverpage_data:
            coverpage_data['section_a_marks'] = 30
        if 'section_b_questions' not in coverpage_data:
            coverpage_data['section_b_questions'] = 19
        if 'section_b_marks' not in coverpage_data:
            coverpage_data['section_b_marks'] = 20
        if 'section_c_questions' not in coverpage_data:
            coverpage_data['section_c_questions'] = 22
        if 'section_c_marks' not in coverpage_data:
            coverpage_data['section_c_marks'] = 40
        if 'section_a_instruction' not in coverpage_data:
            coverpage_data['section_a_instruction'] = 'Answer ALL questions in this section'
        if 'section_b_instruction' not in coverpage_data:
            coverpage_data['section_b_instruction'] = 'Answer any TWO questions from this section'
        if 'section_c_instruction' not in coverpage_data:
            coverpage_data['section_c_instruction'] = 'Answer ALL questions in this section'
    
    # Determine if continuous answer lines are needed
    # Biology Paper 2, Geography Paper 1, Geography Paper 2, CRE Paper 1, CRE Paper 2, and Kiswahili Paper 1 need answer lines
    needs_answer_lines = (
        ('BIOLOGY' in paper_name and is_paper2) or 
        ('GEOGRAPHY' in paper_name and (is_paper1 or is_paper2)) or
        ('CRE' in paper_name or 'CHRISTIAN RELIGIOUS EDUCATION' in paper_name) or
        ('KISWAHILI' in paper_name and paper_number == 1)
    )
    
    # Check if this is Business Paper 2 (special rendering with parts a and b)
    is_business_paper_2 = 'BUSINESS' in paper_name and is_paper2
    
    # Check if this is Kiswahili Paper 1 (special rendering: all 4 questions on one page)
    is_kiswahili_paper_1 = 'KISWAHILI' in paper_name and paper_number == 1
    
    # Determine number of answer line pages (4 for Kiswahili Paper 1, 3 for CRE, 2 for others)
    is_cre_paper = 'CRE' in paper_name or 'CHRISTIAN RELIGIOUS EDUCATION' in paper_name
    if is_kiswahili_paper_1:
        answer_lines_page_count = 4
    elif is_cre_paper:
        answer_lines_page_count = 3
    else:
        answer_lines_page_count = 2

    # Dynamic page calculation
    if is_business_paper_2:
        # Business Paper 2: 12 questions displayed as 6 questions with parts a and b
        # Questions are paired: Q1(a)=Question 1, Q1(b)=Question 2, etc.
        total_pages = 1 + ((len(questions) + 1) // 2)  # 1 coverpage + question pages
        questions_html = _generate_business_paper2_pages(questions, total_pages, coverpage_data)
    elif is_paper2:
        # Calculate answer line pages based on subject
        answer_lines_pages = answer_lines_page_count if needs_answer_lines else 0
        
        # CRE papers have special pagination: 5 questions on page 1, 1 question on page 2
        if is_cre_paper:
            question_pages = 2  # Always 2 pages for CRE (5 questions + 1 question)
        else:
            # 1 cover + ceil(questions/2) + answer pages (if needed)
            question_pages = (len(questions) + 1) // 2
        
        total_pages = 1 + question_pages + answer_lines_pages
        questions_html = _generate_paper2_question_pages(questions, total_pages, coverpage_data, answer_lines_pages=answer_lines_pages)
    else:
        # For Paper 1 with answer lines (Geography Paper 1, CRE Paper 1, Kiswahili Paper 1)
        answer_lines_pages = answer_lines_page_count if needs_answer_lines else 0
        
        # CRE Paper 1: 5 questions on page 1, 1 question on page 2
        if is_cre_paper:
            question_pages = 2  # Always 2 pages for CRE Paper 1 (5 questions + 1 question)
            total_pages = 1 + question_pages + answer_lines_pages
            questions_html = _generate_cre_paper1_pages(questions, total_pages, coverpage_data)
        # Kiswahili Paper 1: All 4 questions on one page
        elif is_kiswahili_paper_1:
            question_pages = 1  # All 4 questions on one page
            total_pages = 1 + question_pages + answer_lines_pages
            questions_html = _generate_kiswahili_paper1_page(questions, total_pages, coverpage_data)
        else:
            total_pages = 1 + ((len(questions) + 2) // 3) + answer_lines_pages
            questions_html = _generate_question_pages(questions, total_pages, coverpage_data)
        
        # Add continuous answer lines for Geography Paper 1 and CRE Paper 1
        if answer_lines_pages > 0:
            answer_lines_html = _generate_answer_lines_pages(answer_lines_pages, total_pages - answer_lines_pages + 1, total_pages)
            questions_html += answer_lines_html
    
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
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }}
        
        .info-row-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 15px;
        }}
        
        .info-row-item {{
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
            list-style: none;
            counter-reset: list-counter;
        }}
        
        .instructions li {{
            margin-bottom: 8px;
            counter-increment: list-counter;
        }}
        
        .instructions li::before {{
            content: "(" counter(list-counter, lower-alpha) ") ";
        }}
        
        .instructions li.bold {{
            font-weight: bold;
        }}
        
        .instructions-list {{
            list-style: none;
            counter-reset: list-counter;
            padding-left: 25px;
        }}
        
        .instructions-list li {{
            margin-bottom: 8px;
            line-height: 1.4;
            counter-increment: list-counter;
        }}
        
        .instructions-list li::before {{
            content: "(" counter(list-counter, lower-alpha) ") ";
        }}
        
        .instructions-list li strong {{
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
    Process question text to render images, answer lines, tables, matrices, fractions, 
    superscript, subscript, and other formatting
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
    
    # Enhanced pattern to include SUP, SUB, FRAC, MIX, TABLE, and MATRIX tags
    pattern = r'(\*\*.*?\*\*|\*.*?\*|__.*?__|_.*?_|\[SUP\].*?\[/SUP\]|\[SUB\].*?\[/SUB\]|\[FRAC:[^\]]+\]|\[MIX:[^\]]+\]|\[TABLE:[^\]]+\]|\[MATRIX:[^\]]+\]|\[IMAGE:[\d.]+:(?:\d+x\d+|\d+)px\]|\[LINES:[\d.]+\])'
    parts = re.split(pattern, text)
    
    result = []
    
    for part in parts:
        if not part:
            continue
        
        # Table: [TABLE:RxC:data] or [TABLE:RxC:data:W:widths:H:heights:M:merged]
        if part.startswith('[TABLE:') and part.endswith(']'):
            try:
                inner = part[7:-1]  # Remove [TABLE: and ]
                parts_list = inner.split(':')
                dimension_match = re.match(r'(\d+)x(\d+)', parts_list[0])
                if dimension_match:
                    rows = int(dimension_match.group(1))
                    cols = int(dimension_match.group(2))
                    cell_data = parts_list[1].split('|') if len(parts_list) > 1 else []
                    
                    # Parse optional widths and heights
                    col_widths = [60] * cols
                    row_heights = [30] * rows
                    
                    # Look for width data (W:width1,width2,...)
                    try:
                        width_index = parts_list.index('W')
                        if width_index != -1 and len(parts_list) > width_index + 1:
                            col_widths = [int(w) or 60 for w in parts_list[width_index + 1].split(',')]
                    except (ValueError, IndexError):
                        pass
                    
                    # Look for height data (H:height1,height2,...)
                    try:
                        height_index = parts_list.index('H')
                        if height_index != -1 and len(parts_list) > height_index + 1:
                            row_heights = [int(h) or 30 for h in parts_list[height_index + 1].split(',')]
                    except (ValueError, IndexError):
                        pass
                    
                    # Build HTML table
                    table_html = '<table style="border: 1px solid #000; border-collapse: collapse; margin: 8px 0; display: inline-table;"><tbody>'
                    
                    for row_idx in range(rows):
                        table_html += '<tr>'
                        for col_idx in range(cols):
                            cell_index = row_idx * cols + col_idx
                            cell_value = cell_data[cell_index] if cell_index < len(cell_data) else ''
                            width = col_widths[col_idx] if col_idx < len(col_widths) else 60
                            height = row_heights[row_idx] if row_idx < len(row_heights) else 30
                            
                            table_html += f'<td style="border: 1px solid #000; padding: 8px; width: {width}px; height: {height}px; min-width: 60px; min-height: 30px;">{cell_value or "&nbsp;"}</td>'
                        table_html += '</tr>'
                    
                    table_html += '</tbody></table>'
                    result.append(table_html)
                    continue
            except Exception:
                result.append(part)
                continue
        
        # Matrix: [MATRIX:RxC:data]
        if part.startswith('[MATRIX:') and part.endswith(']'):
            try:
                inner = part[8:-1]  # Remove [MATRIX: and ]
                parts_list = inner.split(':')
                dimension_match = re.match(r'(\d+)x(\d+)', parts_list[0])
                if dimension_match:
                    rows = int(dimension_match.group(1))
                    cols = int(dimension_match.group(2))
                    cell_data = parts_list[1].split('|') if len(parts_list) > 1 else []
                    
                    # Build HTML matrix with brackets
                    matrix_html = '<span style="display: inline-flex; align-items: center; margin: 8px 4px; font-size: 1.2em;">'
                    matrix_html += '<span style="font-size: 2em; line-height: 1;">⎡</span>'
                    matrix_html += '<table style="border-collapse: collapse; margin: 0 4px;"><tbody>'
                    
                    for row_idx in range(rows):
                        matrix_html += '<tr>'
                        for col_idx in range(cols):
                            cell_index = row_idx * cols + col_idx
                            cell_value = cell_data[cell_index] if cell_index < len(cell_data) else ''
                            matrix_html += f'<td style="padding: 4px 8px; text-align: center; min-width: 40px;">{cell_value or "&nbsp;"}</td>'
                        matrix_html += '</tr>'
                    
                    matrix_html += '</tbody></table>'
                    matrix_html += '<span style="font-size: 2em; line-height: 1;">⎤</span>'
                    matrix_html += '</span>'
                    result.append(matrix_html)
                    continue
            except Exception:
                result.append(part)
                continue
        
        # Fraction: [FRAC:num:den]
        if part.startswith('[FRAC:') and part.endswith(']'):
            try:
                inner = part[6:-1]
                num, den = inner.split(':')
                frac_html = f'<span style="display: inline-block; vertical-align: middle; text-align: center; line-height: 1;"><span style="display: block; font-size: 0.85em;">{num}</span><span style="display: block; border-top: 1px solid; padding-top: 1px; font-size: 0.85em;">{den}</span></span>'
                result.append(frac_html)
                continue
            except Exception:
                result.append(part)
                continue
        
        # Mixed fraction: [MIX:whole:num:den]
        if part.startswith('[MIX:') and part.endswith(']'):
            try:
                inner = part[5:-1]
                whole, num, den = inner.split(':')
                mix_html = f'<span style="display: inline-flex; align-items: center; gap: 4px;"><span style="font-size: 0.95em;">{whole}</span><span style="display: inline-block; vertical-align: middle; text-align: center; line-height: 1;"><span style="display: block; font-size: 0.85em;">{num}</span><span style="display: block; border-top: 1px solid; padding-top: 1px; font-size: 0.85em;">{den}</span></span></span>'
                result.append(mix_html)
                continue
            except Exception:
                result.append(part)
                continue
        
        # Superscript: [SUP]content[/SUP]
        if part.startswith('[SUP]') and part.endswith('[/SUP]'):
            content = part[5:-6]
            result.append(f'<sup style="font-size: 0.75em;">{content}</sup>')
            continue
            
        # Subscript: [SUB]content[/SUB]
        if part.startswith('[SUB]') and part.endswith('[/SUB]'):
            content = part[5:-6]
            result.append(f'<sub style="font-size: 0.75em;">{content}</sub>')
            continue
            
        # Bold: **text**
        if part.startswith('**') and part.endswith('**') and len(part) > 4:
            content = part[2:-2]
            result.append(f'<strong>{content}</strong>')
            continue
            
        # Italic: *text* (not **)
        if part.startswith('*') and part.endswith('*') and not part.startswith('**') and len(part) > 2:
            content = part[1:-1]
            result.append(f'<em>{content}</em>')
            continue
            
        # Underline: __text__
        if part.startswith('__') and part.endswith('__') and len(part) > 4:
            content = part[2:-2]
            result.append(f'<u>{content}</u>')
            continue
            
        # Single underscore italic: _text_
        if part.startswith('_') and part.endswith('_') and not part.startswith('__') and len(part) > 2:
            content = part[1:-1]
            result.append(f'<em>{content}</em>')
            continue
            
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


def _generate_business_paper2_pages(questions, total_pages, coverpage_data=None):
    """
    Generate paginated question pages for Business Paper 2
    12 questions displayed as 6 questions with parts a and b
    Q1(a) = Question 1, Q1(b) = Question 2, etc.
    """
    pages_html = []
    current_page = 2
    
    # Group every 2 consecutive questions as one question with parts a and b
    for i in range(0, len(questions), 2):
        if i + 1 < len(questions):
            question_number = (i // 2) + 1  # 1, 2, 3, 4, 5, 6
            
            q_a = questions[i]
            q_b = questions[i + 1]
            
            # Process question texts with images and answer lines
            q_a_text = _process_question_text(
                q_a.get('text', ''),
                q_a.get('question_inline_images', []),
                q_a.get('question_answer_lines', [])
            )
            
            q_b_text = _process_question_text(
                q_b.get('text', ''),
                q_b.get('question_inline_images', []),
                q_b.get('question_answer_lines', [])
            )
            
            # Calculate total marks for this combined question
            total_marks = (q_a.get('marks', 0) or 0) + (q_b.get('marks', 0) or 0)
            
            # Generate page HTML with combined question
            page_html = f"""
    <div class="exam-page {'page-break' if current_page < total_pages else ''}">
        <div class="question">                
            <div class="question-part">
                <div style="text-align: left;">
                   {question_number}.(a){q_a_text}
                </div>
            </div>
            
            <div class="question-part" >
                <div style="text-align: left;">
                    (b){q_b_text}
                </div>
            </div>
        </div>
        
        <div class="page-number">Page {current_page} of {total_pages}</div>
    </div>
"""
            pages_html.append(page_html)
            current_page += 1
    
    return '\n'.join(pages_html)


def _generate_paper2_question_pages(questions, total_pages, coverpage_data=None, answer_lines_pages=2):
    """
    Generate paginated question pages for Paper 2
    Biology and Geography Paper 2 have sections, others don't
    After the last question, insert answer lines if needed
    """
    pages_html = []
    current_page = 2

    # Section boundaries
    metadata = coverpage_data or {}
    paper_name = metadata.get('paper_name', '').upper()
    
    # Extract paper number to identify specific papers
    try:
        paper_number = extract_paper_number_from_name(paper_name)
    except ValueError:
        raise ValueError(f"Invalid paper name format. Cannot extract paper number.{paper_name}")
    
    # CRITICAL: These papers must NEVER show section headers
    # Explicitly exclude FIRST before any section logic
    is_kiswahili_paper2 = 'KISWAHILI' in paper_name and paper_number == 2
    is_business_paper1 = 'BUSINESS' in paper_name and paper_number == 1
    is_chemistry_paper1 = 'CHEMISTRY' in paper_name and paper_number == 1
    
    # ABSOLUTE EXCLUSION: These papers must NEVER have sections
    never_has_sections = is_kiswahili_paper2 or is_business_paper1 or is_chemistry_paper1
    
    # For excluded papers, remove ANY section metadata to prevent accidental section generation
    if never_has_sections:
        metadata.pop('section_a_questions', None)
        metadata.pop('section_b_questions', None)
        metadata.pop('section_a_marks', None)
        metadata.pop('section_b_marks', None)
        metadata.pop('section_a_instruction', None)
        metadata.pop('section_b_instruction', None)
    
    # Papers that should have sections (explicitly allowed list) - ONLY if paper number is 2
    is_biology = 'BIOLOGY' in paper_name and paper_number == 2
    is_geography = 'GEOGRAPHY' in paper_name and paper_number == 2
    is_mathematics = 'MATHEMATICS' in paper_name or 'MATHS' in paper_name
    is_agriculture = 'AGRICULTURE' in paper_name
    
    # has_sections is TRUE only for allowed papers AND not excluded papers
    has_sections = (
        (is_biology or is_geography or is_mathematics or is_agriculture)
        and not never_has_sections
    )
    
    # Check if this is Agriculture paper (has 3 sections)
    is_agriculture = 'AGRICULTURE' in paper_name
    
    # Check if this is CRE paper (special pagination: 5 questions on page 1, question 6 on page 2)
    is_cre_paper = ('CRE' in paper_name or 'CHRISTIAN RELIGIOUS EDUCATION' in paper_name)
    
    if is_cre_paper:
        # CRE papers: 5 questions on first page, 6th question on second page
        first_page_questions = questions[:5] if len(questions) >= 5 else questions
        second_page_questions = questions[5:] if len(questions) > 5 else []
        
        # Generate first page with 5 questions
        if first_page_questions:
            page_1_html = _generate_cre_question_page(first_page_questions, current_page, total_pages)
            pages_html.append(page_1_html)
            current_page += 1
        
        # Generate second page with 6th question
        if second_page_questions:
            page_2_html = _generate_cre_question_page(second_page_questions, current_page, total_pages)
            pages_html.append(page_2_html)
            current_page += 1
    elif never_has_sections or not has_sections:
        # Papers without sections (Kiswahili Paper 2, Business Paper 1, Chemistry Paper 1, and other non-sectioned papers)
        # Use dedicated non-sectioned function that has NO section header logic
        all_questions_html = _generate_non_sectioned_pages(
            questions,
            current_page,
            total_pages
        )
        pages_html.append(all_questions_html['html'])
        current_page = all_questions_html['next_page']
    elif has_sections:
        # CRITICAL SAFETY CHECK: Double-check that excluded papers don't enter this block
        # This should never happen due to has_sections calculation, but adding as defense-in-depth
        if never_has_sections:
            # If we somehow got here, use non-sectioned generation instead
            all_questions_html = _generate_non_sectioned_pages(
                questions,
                current_page,
                total_pages
            )
            pages_html.append(all_questions_html['html'])
            current_page = all_questions_html['next_page']
        else:
            # Check if this is Agriculture paper (3 sections: A, B, C)
            is_agriculture = 'AGRICULTURE' in paper_name
            
            if is_agriculture:
                # Agriculture: Section A (1-15, 30 marks), Section B (16-19, 20 marks), Section C (20-22, 40 marks)
                section_a_count = metadata.get('section_a_questions', 15)
                section_b_count = metadata.get('section_b_questions', 19)
                section_c_count = metadata.get('section_c_questions', 22)
                
                try:
                    section_a_count = int(section_a_count)
                    section_b_count = int(section_b_count)
                    section_c_count = int(section_c_count)
                except Exception:
                    section_a_count = 15
                    section_b_count = 19
                    section_c_count = 22
                
                section_a_questions = [q for q in questions if q['number'] <= section_a_count]
                section_b_questions = [q for q in questions if section_a_count < q['number'] <= section_b_count]
                section_c_questions = [q for q in questions if section_b_count < q['number'] <= section_c_count]
                
                # Section A
                section_a_marks = metadata.get('section_a_marks', 30)
                section_a_title = f"SECTION A ({section_a_marks} MARKS)" if section_a_marks else "SECTION A"
                section_a_instruction = metadata.get('section_a_instruction', 'Answer ALL questions in this section')
                section_a_html = _generate_section_pages(
                    section_a_questions,
                    section_a_title,
                    section_a_instruction,
                    current_page,
                    total_pages,
                    is_last_section=False,
                    answer_lines=0,
                    paper_name=paper_name
                )
                pages_html.append(section_a_html['html'])
                current_page = section_a_html['next_page']
                
                # Section B
                section_b_marks = metadata.get('section_b_marks', 20)
                section_b_title = f"SECTION B ({section_b_marks} MARKS)" if section_b_marks else "SECTION B"
                section_b_instruction = metadata.get('section_b_instruction', 'Answer any TWO questions from this section')
                section_b_html = _generate_section_pages(
                    section_b_questions,
                    section_b_title,
                    section_b_instruction,
                    current_page,
                    total_pages,
                    is_last_section=False,
                    answer_lines=0,
                    paper_name=paper_name
                )
                pages_html.append(section_b_html['html'])
                current_page = section_b_html['next_page']
                
                # Section C
                section_c_marks = metadata.get('section_c_marks', 40)
                section_c_title = f"SECTION C ({section_c_marks} MARKS)" if section_c_marks else "SECTION C"
                section_c_instruction = metadata.get('section_c_instruction', 'Answer ALL questions in this section')
                section_c_html = _generate_section_pages(
                    section_c_questions,
                    section_c_title,
                    section_c_instruction,
                    current_page,
                    total_pages,
                    is_last_section=True,
                    answer_lines=0,
                    paper_name=paper_name
                )
                pages_html.append(section_c_html['html'])
                current_page = section_c_html['next_page']
            else:
                # Papers with 2 sections (Biology, Geography, Mathematics)
                section_a_count = metadata.get('section_a_questions', 5)
                try:
                    section_a_count = int(section_a_count)
                except Exception:
                    section_a_count = 5

                section_a_questions = [q for q in questions if q['number'] <= section_a_count]
                section_b_questions = [q for q in questions if q['number'] > section_a_count]

                # Paper-specific section naming
                is_mathematics = 'MATHEMATICS' in paper_name or 'MATHS' in paper_name
                
                # Section A/I
                section_a_marks = metadata.get('section_a_marks', 40)
                if is_mathematics:
                    section_a_title = f"SECTION I ({section_a_marks} MARKS)" if section_a_marks else "SECTION I"
                else:
                    section_a_title = f"SECTION A ({section_a_marks} MARKS)" if section_a_marks else "SECTION A"
                section_a_instruction = metadata.get('section_a_instruction', 'Answer ALL questions in this section')
                section_a_html = _generate_section_pages(
                    section_a_questions,
                    section_a_title,
                    section_a_instruction,
                    current_page,
                    total_pages,
                    is_last_section=False,
                    answer_lines=0,
                    paper_name=paper_name
                )
                pages_html.append(section_a_html['html'])
                current_page = section_a_html['next_page']

                # Section B/II
                # ABSOLUTE CHECK: Never create section titles for excluded papers
                if never_has_sections:
                    # This should never happen, but if it does, skip section generation entirely
                    pass
                else:
                    section_b_marks = metadata.get('section_b_marks', 40)
                    if is_mathematics:
                        section_b_title = f"SECTION II ({section_b_marks} MARKS)" if section_b_marks else "SECTION II"
                    else:
                        section_b_title = f"SECTION B ({section_b_marks} MARKS)" if section_b_marks else "SECTION B"
                    
                    # Paper-specific instructions for Section B
                    is_geography = 'GEOGRAPHY' in paper_name
                    
                    if is_geography:
                        section_b_instruction = metadata.get('section_b_instruction', 'Answer question 6 and any other TWO questions from this section')
                    elif is_mathematics:
                        section_b_instruction = metadata.get('section_b_instruction', 'Answer any FIVE questions from this section')
                    else:
                        section_b_instruction = metadata.get('section_b_instruction', 'Answer ALL questions in this section')
                        
                    section_b_html = _generate_section_pages(
                        section_b_questions,
                        section_b_title,
                        section_b_instruction,
                        current_page,
                        total_pages,
                        is_last_section=True,
                        answer_lines=0,
                        paper_name=paper_name
                    )
                    pages_html.append(section_b_html['html'])
                    current_page = section_b_html['next_page']
    # Insert pages of dotted answer lines (only if answer_lines_pages > 0)
    if answer_lines_pages > 0:
        answer_lines_html = _generate_answer_lines_pages(answer_lines_pages, current_page, total_pages)
        pages_html.append(answer_lines_html)

    return '\n'.join(pages_html)


def _generate_cre_question_page(questions, page_number, total_pages):
    """
    Generate a single page for CRE papers with multiple questions
    Designed to fit 5 questions on first page, then 6th question on second page
    
    Args:
        questions: List of question dictionaries
        page_number: Current page number
        total_pages: Total pages in the paper
    
    Returns:
        str: HTML for the page
    """
    questions_html = ""
    for q in questions:
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
    
    page_html = f"""
    <!-- Page {page_number} -->
    <div class="exam-page page-break">
        {questions_html}        
        <div class="page-number">Page {page_number} of {total_pages}</div>
    </div>
"""
    return page_html


def _generate_non_sectioned_pages(questions, start_page, total_pages):
    """
    Generate pages for papers WITHOUT sections
    Used for: Kiswahili Paper 2, Business Paper 1, Chemistry Paper 1, and other non-sectioned papers
    This function has NO section header logic at all
    
    Args:
        questions: List of question dictionaries
        start_page: Starting page number
        total_pages: Total pages in the paper
    
    Returns:
        dict: {'html': str, 'next_page': int}
    """
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
        <div class="question">
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


def _generate_answer_lines_pages(num_pages, start_page, total_pages):
    """
    Generate continuous answer line pages
    
    Args:
        num_pages: Number of answer line pages to generate
        start_page: Starting page number
        total_pages: Total pages in the paper
    
    Returns:
        str: HTML for answer line pages
    """
    pages_html = []
    lines_per_page = 25
    
    for i in range(num_pages):
        lines_html = ''
        for _ in range(lines_per_page):
            lines_html += '<div class="answer-line dotted" style="height: 28px; margin: 8px 0;"></div>'
        page_html = f'''
    <div class="exam-page page-break">
        {lines_html}
        <div class="page-number">Page {start_page + i} of {total_pages}</div>
    </div>
'''
        pages_html.append(page_html)
    
    return '\n'.join(pages_html)


def _generate_section_pages(questions, section_title, section_instruction, start_page, total_pages, is_last_section=False, answer_lines=0, paper_name=''):
    """
    Generate pages for a specific section
    If section_title is None, no section header will be generated
    Papers without sections (Chemistry Paper 1, Business Paper 1, Kiswahili Paper 2) will never show section headers
    """
    pages_html = []
    current_page = start_page
    questions_per_page = 2
    
    # Extract paper number if paper_name provided
    paper_number = 1
    if paper_name:
        try:
            paper_number = extract_paper_number_from_name(paper_name)
        except ValueError:
            paper_number = 1
    
    # Explicitly check if this paper should NEVER have section headers
    is_kiswahili_paper2 = 'KISWAHILI' in paper_name.upper() and paper_number == 2
    is_business_paper1 = 'BUSINESS' in paper_name.upper() and paper_number == 1
    is_chemistry_paper1 = 'CHEMISTRY' in paper_name.upper() and paper_number == 1
    
    # Force section_title to None for papers that should not have sections
    if is_kiswahili_paper2 or is_business_paper1 or is_chemistry_paper1:
        section_title = None
        section_instruction = None
    
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
        # ABSOLUTE CHECK: Only generate section header if section_title is provided, it's the first page,
        # AND the paper is not in the excluded list (Kiswahili Paper 2, Business Paper 1, Chemistry Paper 1)
        if is_first_page and section_title is not None and not (is_kiswahili_paper2 or is_business_paper1 or is_chemistry_paper1):
            section_header_html = f"""
        <div class="section-header">
            <h2>{section_title}</h2>
            <p class="section-instruction">{section_instruction}</p>
        </div>
        """
        
        
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
        # remaining_lines = answer_lines - initial_lines
        # answer_lines_html = _generate_answer_lines_continuation(remaining_lines, current_page, total_pages)
        # pages_html.append(answer_lines_html)
    
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


def _generate_cre_paper1_pages(questions, total_pages, coverpage_data=None):
    """
    Generate paginated question pages for CRE Paper 1
    5 questions on first page, 6th question on second page
    
    Args:
        questions: List of question dictionaries
        total_pages: Total pages in paper
        coverpage_data: Metadata from coverpage
    
    Returns:
        str: HTML for all question pages
    """
    pages_html = []
    current_page = 2
    
    # Split questions: first 5 on page 1, rest on page 2
    first_page_questions = questions[:5] if len(questions) >= 5 else questions
    second_page_questions = questions[5:] if len(questions) > 5 else []
    
    # Generate first page with 5 questions
    if first_page_questions:
        questions_html = ""
        for q in first_page_questions:
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
        
        page_html = f"""
    <!-- Page {current_page} -->
    <div class="exam-page page-break">
        {questions_html}        
        <div class="page-number">Page {current_page} of {total_pages}</div>
    </div>
"""
        pages_html.append(page_html)
        current_page += 1
    
    # Generate second page with remaining questions (typically just question 6)
    if second_page_questions:
        questions_html = ""
        for q in second_page_questions:
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
        
        page_html = f"""
    <!-- Page {current_page} -->
    <div class="exam-page page-break">
        {questions_html}        
        <div class="page-number">Page {current_page} of {total_pages}</div>
    </div>
"""
        pages_html.append(page_html)
    
    return '\n'.join(pages_html)


def _generate_kiswahili_paper1_page(questions, total_pages, coverpage_data=None):
    """
    Generate single question page for Kiswahili Paper 1
    All 4 questions on one page, no answer spaces within questions
    
    Args:
        questions: List of question dictionaries (should be 4 questions)
        total_pages: Total pages in paper
        coverpage_data: Metadata from coverpage
    
    Returns:
        str: HTML for the single question page
    """
    current_page = 2
    
    # Generate all questions on one page
    questions_html = ""
    for q in questions:
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
    
    page_html = f"""
    <!-- Page {current_page} -->
    <div class="exam-page page-break">
        {questions_html}        
        <div class="page-number">Page {current_page} of {total_pages}</div>
    </div>
"""
    
    return page_html


def _generate_question_pages(questions, total_pages, coverpage_data=None):
    """
    Generate paginated question pages for standard papers
    Handles sections for Geography Paper 1, Mathematics Paper 1, and Agriculture Paper 1
    """
    questions_per_page = 3
    pages_html = []
    current_page = 2
    
    # Determine section boundaries from coverpage_data if available
    metadata = coverpage_data or {}
    paper_name_check = metadata.get('paper_name', '').upper()
    is_agriculture = 'AGRICULTURE' in paper_name_check
    
    # For Agriculture, get all section boundaries
    if is_agriculture:
        section_a_count = metadata.get('section_a_questions', 15)
        section_b_count = metadata.get('section_b_questions', 19)
        section_c_count = metadata.get('section_c_questions', 22)
        try:
            section_a_count = int(section_a_count)
            section_b_count = int(section_b_count)
            section_c_count = int(section_c_count)
        except Exception:
            section_a_count = 15
            section_b_count = 19
            section_c_count = 22
    else:
        section_a_count = metadata.get('section_a_questions', 0)
        section_b_count = 0
        section_c_count = 0
        
        # Handle string format like "1-5" for Geography papers
        if isinstance(section_a_count, str):
            try:
                # Extract the end number from "1-5" format
                if '-' in section_a_count:
                    section_a_count = int(section_a_count.split('-')[1])
                else:
                    section_a_count = int(section_a_count)
            except Exception:
                section_a_count = 0
        else:
            try:
                section_a_count = int(section_a_count)
            except Exception:
                section_a_count = 0

    page_last_section = None
    for i in range(0, len(questions), questions_per_page):
        page_questions = questions[i:i + questions_per_page]
        
        # Determine paper type for section naming
        paper_name_for_sections = metadata.get('paper_name', '').upper()
        is_mathematics_paper = 'MATHEMATICS' in paper_name_for_sections or 'MATHS' in paper_name_for_sections
        is_agriculture_paper = 'AGRICULTURE' in paper_name_for_sections
        
        # Determine first and last question sections for this page
        first_qnum = int(page_questions[0].get('number', 0)) if page_questions else 0
        if is_agriculture_paper:
            if first_qnum <= section_a_count:
                first_section = 'A'
            elif first_qnum <= section_b_count:
                first_section = 'B'
            else:
                first_section = 'C'
        elif is_mathematics_paper:
            first_section = 'I' if (section_a_count and first_qnum <= section_a_count) else 'II'
        else:
            first_section = 'A' if (section_a_count and first_qnum <= section_a_count) else 'B'
            
        last_qnum = int(page_questions[-1].get('number', 0)) if page_questions else 0
        if is_agriculture_paper:
            if last_qnum <= section_a_count:
                last_section_on_page = 'A'
            elif last_qnum <= section_b_count:
                last_section_on_page = 'B'
            else:
                last_section_on_page = 'C'
        elif is_mathematics_paper:
            last_section_on_page = 'I' if (section_a_count and last_qnum <= section_a_count) else 'II'
        else:
            last_section_on_page = 'A' if (section_a_count and last_qnum <= section_a_count) else 'B'

        # If this page continues the same section from previous page, show a small continue header
        page_header_html = ''
        if page_last_section is not None and page_last_section == first_section:
            if is_mathematics_paper and first_section == 'II':
                page_header_html = f"""
        <div class=\"question-page-header\"> 
            <h2>Continue answering any FIVE questions from this section</h2>
        </div>
"""
            else:
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
            if is_agriculture_paper:
                if qnum <= section_a_count:
                    current_section = 'A'
                elif qnum <= section_b_count:
                    current_section = 'B'
                else:
                    current_section = 'C'
            elif is_mathematics_paper:
                current_section = 'I' if (section_a_count and qnum <= section_a_count) else 'II'
            else:
                current_section = 'A' if (section_a_count and qnum <= section_a_count) else 'B'

            # If section changed (or starting), insert section header
            if last_section != current_section:
                # Get marks for section from coverpage_data if present
                if current_section in ['A', 'I']:
                    s_marks = metadata.get('section_a_marks', None)
                elif current_section in ['B', 'II']:
                    s_marks = metadata.get('section_b_marks', None)
                elif current_section == 'C':
                    s_marks = metadata.get('section_c_marks', None)
                else:
                    s_marks = None

                s_marks_text = f" ({s_marks} MARKS)" if s_marks else ''
                # Instruction text: depends on section and paper type
                paper_name = metadata.get('paper_name', '').upper()
                is_geography = 'GEOGRAPHY' in paper_name
                is_mathematics = 'MATHEMATICS' in paper_name or 'MATHS' in paper_name
                is_agriculture_instr = 'AGRICULTURE' in paper_name
                
                if current_section in ['A', 'I']:
                    instruction_text = metadata.get('section_a_instruction', 'Answer ALL questions in this section.')
                elif current_section in ['B', 'II']:
                    # Section B/II special instructions for different papers
                    if is_geography:
                        instruction_text = metadata.get('section_b_instruction', 'Answer question 6 and any other TWO questions from this section.')
                    elif is_mathematics:
                        instruction_text = metadata.get('section_b_instruction', 'Answer any FIVE questions from this section.')
                    else:
                        instruction_text = metadata.get('section_b_instruction', 'Answer ALL questions in this section.')
                elif current_section == 'C':
                    # Section C (Agriculture only)
                    instruction_text = metadata.get('section_c_instruction', 'Answer ALL questions in this section.')

                questions_html += f"""
        <div class=\"section-header\"> 
            <h2>SECTION {current_section}{s_marks_text}</h2>
            <div class=\"section-instruction\" style=\"font-style: italic;\">{instruction_text}</div>
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