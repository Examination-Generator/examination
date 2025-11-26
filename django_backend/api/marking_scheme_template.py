"""
Marking Scheme Template for KCSE Examination Papers
Generates professional marking schemes with coverpage and answers
"""

import re
from .coverpage_templates import MarkingSchemeCoverpage


class DataIntegrityError(Exception):
    """Raised when there's a mismatch between placeholders and provided data"""
    pass


def validate_data_integrity(marking_scheme_items):
    """
    Validate data integrity - ensures placeholders match provided image/line arrays
    This catches data structure issues, not missing database records
    
    Args:
        marking_scheme_items (list): List of marking scheme items
    
    Returns:
        dict: Validation results with 'valid', 'mismatches', 'errors'
    """
    validation_results = {
        'valid': True,
        'mismatches': [],
        'errors': []
    }
    
    # Pattern to find all image and line placeholders
    image_pattern = r'\[IMAGE:([\d.]+):(?:\d+x\d+|\d+)px\]'
    lines_pattern = r'\[LINES:([\d.]+)\]'
    
    for idx, item in enumerate(marking_scheme_items):
        question_num = item.get('number', idx + 1)
        answer_text = item.get('answer', '')
        
        if not answer_text:
            continue
        
        # Get provided images and lines arrays
        provided_images = item.get('answer_inline_images', [])
        provided_lines = item.get('answer_answer_lines', [])
        
        # Create lookup dictionaries
        image_dict = {float(img.get('id', 0)): img for img in provided_images if img.get('id') is not None}
        line_dict = {float(line.get('id', 0)): line for line in provided_lines if line.get('id') is not None}
        
        # Find all image references in text
        image_matches = re.findall(image_pattern, answer_text)
        for img_id_str in image_matches:
            img_id = float(img_id_str)
            
            # Check if ID exists in provided array
            if img_id not in image_dict:
                validation_results['mismatches'].append({
                    'type': 'image',
                    'question': question_num,
                    'id': img_id,
                    'error': f'Question {question_num}: Image placeholder [IMAGE:{img_id}:...] found but ID {img_id} not in answer_inline_images array'
                })
                validation_results['valid'] = False
            else:
                # Check if image has URL (data integrity)
                img_data = image_dict[img_id]
                if not img_data.get('url'):
                    validation_results['mismatches'].append({
                        'type': 'image_url',
                        'question': question_num,
                        'id': img_id,
                        'error': f'Question {question_num}: Image ID {img_id} exists but has no URL property'
                    })
                    validation_results['valid'] = False
        
        # Find all line references in text
        line_matches = re.findall(lines_pattern, answer_text)
        for line_id_str in line_matches:
            line_id = float(line_id_str)
            
            # Check if ID exists in provided array
            if line_id not in line_dict:
                validation_results['mismatches'].append({
                    'type': 'line',
                    'question': question_num,
                    'id': line_id,
                    'error': f'Question {question_num}: Line placeholder [LINES:{line_id}] found but ID {line_id} not in answer_answer_lines array'
                })
                validation_results['valid'] = False
    
    # Compile all errors
    validation_results['errors'] = [item['error'] for item in validation_results['mismatches']]
    
    return validation_results


def generate_marking_scheme_html(coverpage_data, marking_scheme_items, validate_integrity=True):
    """
    Generate complete marking scheme HTML with coverpage, answers, and page numbers
    
    Args:
        coverpage_data (dict): Coverpage information
        marking_scheme_items (list): List of marking scheme items with answers
        validate_integrity (bool): If True, validates data structure integrity before generating
    
    Returns:
        str: Complete HTML for marking scheme
    
    Raises:
        DataIntegrityError: If validate_integrity=True and data structure issues found
    """
    
    # VALIDATE DATA INTEGRITY
    if validate_integrity:
        validation = validate_data_integrity(marking_scheme_items)
        
        if not validation['valid']:
            error_summary = f"\n❌ DATA INTEGRITY ERROR - {len(validation['errors'])} mismatch(es) found:\n\n"
            error_summary += "This indicates a bug in the application - placeholders and data arrays don't match.\n\n"
            
            image_mismatches = [m for m in validation['mismatches'] if m['type'] in ['image', 'image_url']]
            line_mismatches = [m for m in validation['mismatches'] if m['type'] == 'line']
            
            if image_mismatches:
                error_summary += f"📷 Image Mismatches ({len(image_mismatches)}):\n"
                for item in image_mismatches:
                    error_summary += f"  • {item['error']}\n"
                error_summary += "\n"
            
            if line_mismatches:
                error_summary += f"📝 Line Mismatches ({len(line_mismatches)}):\n"
                for item in line_mismatches:
                    error_summary += f"  • {item['error']}\n"
                error_summary += "\n"
            
            error_summary += "⚠️  This is likely a data serialization issue.\n"
            error_summary += "Check that answer_inline_images and answer_answer_lines arrays are properly populated.\n"
            
            raise DataIntegrityError(error_summary)
    
    # Generate coverpage HTML (page 1)
    coverpage_html = MarkingSchemeCoverpage.generate_html(coverpage_data)
    
    # Extract coverpage content (remove html/body tags to combine later)
    coverpage_body = re.search(r'<body>(.*?)</body>', coverpage_html, re.DOTALL)
    if coverpage_body:
        coverpage_content = coverpage_body.group(1)
    else:
        coverpage_content = coverpage_html
    
    # Calculate total pages (coverpage + answer pages)
    # Assuming ~2 answers per page
    total_pages = 1 + ((len(marking_scheme_items) + 1) // 2)
    
    # Generate answer pages
    answers_html = _generate_answer_pages(marking_scheme_items, total_pages)
    
    # Combine everything
    full_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Marking Scheme - {coverpage_data.get('paper_name', 'EXAM PAPER')}</title>
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
            font-size: 11pt;
            font-weight: bold;
            color: #666;
        }}
        
        /* Answer page header */
        .answer-page-header {{
            text-align: center;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid black;
        }}
        
        .answer-page-header h2 {{
            font-size: 16px;
            margin-bottom: 5px;
        }}
        
        .answer-page-header p {{
            font-size: 12px;
            font-style: italic;
        }}
        
        /* Answer item styling */
        .answer-item {{
            margin-bottom: 30px;
            page-break-inside: avoid;
        }}
        
        .answer-content {{
            padding: 12px 0;
            background: #ffffff;
        }}
        
        .answer-text {{
            font-size: 12pt;
            line-height: 1.8;
            text-align: left;
            white-space: pre-wrap;
        }}
        
        .question-number {{
            font-weight: bold;
            font-size: 13pt;
            color: black;
        }}
        
        /* Marking points styling */
        .marking-points {{
            margin-top: 12px;
            padding: 12px;
            background: #fef3c7;
            border-left: 3px solid #f59e0b;
        }}
        
        .marking-points-title {{
            font-weight: bold;
            color: #92400e;
            margin-bottom: 8px;
            font-size: 11pt;
        }}
        
        .marking-point {{
            margin: 6px 0;
            padding-left: 20px;
            font-size: 11pt;
        }}
        
        /* Image styling */
        .answer-image {{
            display: block;
            margin: 15px auto;
            max-width: 100%;
            border: 2px solid #60a5fa;
            border-radius: 4px;
            padding: 5px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            background: white;
        }}
        
        .answer-image.inline {{
            display: inline-block;
            vertical-align: middle;
            margin: 5px;
        }}
        
        /* Answer lines styling */
        .answer-lines {{
            margin: 15px 0;
            max-width: 700px;
        }}
        
        .answer-line {{
            width: 100%;
            margin: 0;
            padding: 0;
            box-sizing: border-box;
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
    </style>
</head>
<body>
    <!-- Page 1: Coverpage -->
    <div class="exam-page page-break">
        {coverpage_content}
    </div>
    
    <!-- Answer Pages -->
    {answers_html}
</body>
</html>
"""
    
    return full_html.strip()


def _generate_answer_pages(marking_scheme_items, total_pages):
    """
    Generate paginated answer pages
    
    Args:
        marking_scheme_items (list): List of marking scheme items
        total_pages (int): Total number of pages in the marking scheme
    
    Returns:
        str: HTML for all answer pages
    """
    
    answers_per_page = 2  # Approximately 2 answers per page
    pages_html = []
    current_page = 2  # Page 1 is coverpage
    
    for i in range(0, len(marking_scheme_items), answers_per_page):
        page_answers = marking_scheme_items[i:i + answers_per_page]
        
        answers_html = ""
        for item in page_answers:
            answer_html = _generate_single_answer_html(item)
            answers_html += answer_html
        
        page_html = f"""
    <!-- Page {current_page} -->
    <div class="exam-page {'page-break' if current_page < total_pages else ''}">
        <div class="answer-page-header">
            <h2>MARKING SCHEME</h2>
            <p>(Detailed answers and marking points)</p>
        </div>
        
        {answers_html}
        
        <div class="page-number">Page {current_page} of {total_pages}</div>
    </div>
"""
        
        pages_html.append(page_html)
        current_page += 1
    
    return '\n'.join(pages_html)


def _generate_single_answer_html(item):
    """
    Generate HTML for a single answer (NO question text, only answer)
    
    Args:
        item (dict): Marking scheme item with answer details
    
    Returns:
        str: HTML for single answer
    """
    number = item.get('number', 1)
    answer = item.get('answer', 'No answer provided')
    marking_points = item.get('marking_points', None)
    
    # Get images and lines - SIMPLE AND DIRECT
    answer_images = item.get('answer_inline_images', [])
    answer_lines = item.get('answer_answer_lines', [])
    
    # Build marking points HTML
    marking_points_html = ''
    if marking_points and isinstance(marking_points, list):
        points_list = ''.join([
            f'<div class="marking-point">• Part {chr(97 + i)}: {point.get("marks", 0)} mark(s) - {point.get("text", "N/A")}</div>'
            for i, point in enumerate(marking_points)
        ])
        marking_points_html = f"""
        <div class="marking-points">
            <div class="marking-points-title">Marking Points:</div>
            {points_list}
        </div>
        """
    
    # Process answer text with images and lines
    processed_answer = _process_answer_text(answer, answer_images, answer_lines)
    
    html = f"""
        <div class="answer-item">
            <div class="answer-content">
                <div class="answer-text">
<span class="question-number">{number}.</span>  {processed_answer}
                </div>
                {marking_points_html}
            </div>
        </div>
"""
    
    return html


def _process_answer_text(text, images=None, answer_lines=None):
    """
    Process answer text to render images, lines, and formatting
    
    Args:
        text (str): Answer text with placeholders
        images (list): List of image objects with id, url, width, height
        answer_lines (list): List of answer line configurations
    
    Returns:
        str: Processed HTML with images, lines, and formatting rendered
    """
    if not text:
        return "No answer provided"
    
    # Create lookup dictionaries
    images_dict = {}
    if images:
        for img in images:
            img_id = img.get('id')
            if img_id is not None:
                images_dict[float(img_id)] = img
    
    lines_dict = {}
    if answer_lines:
        for line in answer_lines:
            line_id = line.get('id')
            if line_id is not None:
                lines_dict[float(line_id)] = line
    
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
            result.append(f'<strong class="bold">{content}</strong>')
            
        # Italic: *text* (not **)
        elif part.startswith('*') and part.endswith('*') and not part.startswith('**') and len(part) > 2:
            content = part[1:-1]
            result.append(f'<em class="italic">{content}</em>')
            
        # Underline: __text__
        elif part.startswith('__') and part.endswith('__') and len(part) > 4:
            content = part[2:-2]
            result.append(f'<u class="underline">{content}</u>')
            
        # Single underscore italic: _text_
        elif part.startswith('_') and part.endswith('_') and not part.startswith('__') and len(part) > 2:
            content = part[1:-1]
            result.append(f'<em class="italic">{content}</em>')
            
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
                        lines_html += f'<div class="answer-line" style="height: {line_height}px; border-bottom: 2px {line_style} rgba(0, 0, 0, {opacity}); margin: 0; padding: 0;"></div>'
                    
                    # Half line if needed
                    if has_half_line:
                        half_height = line_height / 2
                        lines_html += f'<div class="answer-line" style="height: {half_height}px; border-bottom: 2px {line_style} rgba(0, 0, 0, {opacity}); margin: 0; padding: 0;"></div>'
                    
                    lines_html += '</div>'
                    result.append(lines_html)
        
        # Images: [IMAGE:id:WxHpx] or [IMAGE:id:Wpx]
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
                    img_alt = image.get('name', 'Answer image')
                    
                    # Build style
                    style = f"width: {image_width}px;"
                    if image_height:
                        style += f" height: {image_height}px;"
                    else:
                        style += " height: auto;"
                    
                    result.append(f'<br><img src="{img_url}" alt="{img_alt}" class="answer-image" style="{style}" /><br>')
        
        else:
            result.append(part)
    
    return ''.join(result)


# Utility function for checking data integrity of specific items
def check_item_integrity(item):
    """
    Check a single marking scheme item for data integrity issues
    
    Args:
        item (dict): Single marking scheme item
    
    Returns:
        dict: Integrity check results with 'valid', 'mismatches', 'errors'
    """
    validation = validate_data_integrity([item])
    return {
        'valid': validation['valid'],
        'mismatches': validation['mismatches'],
        'errors': validation['errors']
    }