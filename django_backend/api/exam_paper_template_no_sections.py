"""
Non-Sectioned Exam Paper Template Generator
Generates complete exam papers WITHOUT sections
Used for: Kiswahili Paper 2, Business Paper 1, Chemistry Paper 1
"""

from .coverpage_templates import (
    BiologyPaper1Coverpage, 
    BiologyPaper2Coverpage,
    BusinessPaper1Coverpage,
    BusinessPaper2Coverpage,
    ChemistryPaper1Coverpage,
    ChemistryPaper2Coverpage,
    KiswahiliPaper2Coverpage,
)
import re
from .page_number_extrctor import extract_paper_number_from_name


def get_coverpage_class(paper_data, is_marking_scheme=False):
    """Get appropriate coverpage class for the paper"""
    paper_name = paper_data.get('paper_name', '').upper()
    
    try:
        paper_number = extract_paper_number_from_name(paper_name)
    except ValueError:
        paper_number = 1
    
    if is_marking_scheme:
        from .coverpage_templates import MarkingSchemeCoverpage
        return MarkingSchemeCoverpage
    
    # Map paper names to coverpage classes
    if 'KISWAHILI' in paper_name and paper_number == 2:
        return KiswahiliPaper2Coverpage
    elif 'BUSINESS' in paper_name and paper_number == 1:
        return BusinessPaper1Coverpage
    elif 'CHEMISTRY' in paper_name and paper_number == 1:
        return ChemistryPaper1Coverpage
    
    # Default fallback
    return BusinessPaper1Coverpage


def generate_full_exam_html(coverpage_data, questions, paper_data=None, coverpage_class=None):
    """
    Generate complete exam paper HTML WITHOUT sections
    For: Kiswahili Paper 2, Business Paper 1, Chemistry Paper 1
    
    Args:
        coverpage_data (dict): Coverpage information
        questions (list): List of question dictionaries
        paper_data (dict): Paper metadata
        coverpage_class: Coverpage class to use
    
    Returns:
        str: Complete HTML document WITHOUT any section headers
    """
    
    # Auto-detect coverpage class if not provided
    if coverpage_class is None:
        if paper_data:
            coverpage_class = get_coverpage_class(paper_data)
        else:
            coverpage_class = get_coverpage_class(coverpage_data)
    
    # Generate coverpage HTML (page 1)
    coverpage_html = coverpage_class.generate_html(coverpage_data)
    
    # Extract coverpage content
    coverpage_body = re.search(r'<body>(.*?)</body>', coverpage_html, re.DOTALL)
    if coverpage_body:
        coverpage_content = coverpage_body.group(1)
    else:
        coverpage_content = coverpage_html
    
    # Get paper name
    paper_name = coverpage_data.get('paper_name', '').upper()
    
    # Determine if answer lines are needed
    needs_answer_lines = False  # These papers typically don't need answer lines
    answer_lines_page_count = 0
    
    # Calculate total pages
    questions_per_page = 2
    question_pages = (len(questions) + questions_per_page - 1) // questions_per_page
    total_pages = 1 + question_pages + answer_lines_page_count
    
    # Generate question pages WITHOUT sections
    questions_html = _generate_non_sectioned_pages(questions, 2, total_pages)
    
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
        
        /* Questions styling */
        .question {{
            margin-bottom: 30px;
        }}
        
        .question-number {{
            font-weight: bold;
            font-size: 14px;
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
        
        /* Coverpage styles */
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
    
    <!-- Question Pages (NO SECTIONS) -->
    {questions_html}
</body>
</html>
"""
    
    return full_html


def _process_question_text(text, images=None, answer_lines=None):
    """Process question text to render images, answer lines, and formatting"""
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
    
    # Pattern for formatting tags
    pattern = r'(\*\*.*?\*\*|\*.*?\*|__.*?__|_.*?_|\[SUP\].*?\[/SUP\]|\[SUB\].*?\[/SUB\]|\[FRAC:[^\]]+\]|\[MIX:[^\]]+\]|\[TABLE:[^\]]+\]|\[MATRIX:[^\]]+\]|\[IMAGE:[\d.]+:(?:\d+x\d+|\d+)px\]|\[LINES:[\d.]+\])'
    parts = re.split(pattern, text)
    
    result = []
    
    for part in parts:
        if not part:
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
            
        # Italic: *text*
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
                    lines_html = '<div class="answer-lines">'
                    for _ in range(int(num_lines)):
                        lines_html += '<div class="answer-line dotted"></div>'
                    lines_html += '</div>'
                    result.append(lines_html)
        
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
        
        # Regular text
        else:
            result.append(part)
    
    return ''.join(result)


def _generate_non_sectioned_pages(questions, start_page, total_pages):
    """
    Generate pages WITHOUT any section headers
    This is the ONLY generation function used in this template
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
        
        # NO SECTION HEADERS - just questions and page number
        page_html = f"""
    <!-- Page {current_page} -->
    <div class="exam-page page-break">
        {questions_html}        
        <div class="page-number">Page {current_page} of {total_pages}</div>
    </div>
"""
        pages_html.append(page_html)
        current_page += 1
    
    return '\n'.join(pages_html)
