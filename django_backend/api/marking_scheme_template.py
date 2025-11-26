"""
Marking Scheme Template for KCSE Examination Papers
Generates professional marking schemes with coverpage and answers
"""

import re
from .coverpage_templates import MarkingSchemeCoverpage


def generate_marking_scheme_html(coverpage_data, marking_scheme_items):
    """
    Generate complete marking scheme HTML with coverpage, answers, and page numbers
    
    Args:
        coverpage_data (dict): Coverpage information
        marking_scheme_items (list): List of marking scheme items with answers
    
    Returns:
        str: Complete HTML for marking scheme
    """
    
    # Generate coverpage HTML
    coverpage_html = MarkingSchemeCoverpage.generate_html(coverpage_data)
    
    # Generate marking scheme body with pagination
    answers_html = generate_answers_with_pagination(marking_scheme_items, coverpage_data.get('total_questions', 25))
    
    # Combine coverpage and answers
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
            margin: 20mm;
            
            @bottom-center {{
                content: "Page " counter(page) " of " counter(pages);
            }}
        }}
        
        body {{
            font-family: 'Times New Roman', Times, serif;
            font-size: 12pt;
            line-height: 1.6;
            color: #000;
        }}
        
        .page {{
            page-break-after: always;
            position: relative;
            min-height: 250mm;
            padding-bottom: 30px;
        }}
        
        .page:last-child {{
            page-break-after: auto;
        }}
        
        .page-number {{
            position: absolute;
            bottom: 10px;
            right: 10px;
            font-size: 11pt;
            color: #666;
        }}
        
        .answer-item {{
            margin-bottom: 25px;
            page-break-inside: avoid;
        }}
        
        .question-header {{
            background: #f0f0f0;
            padding: 8px 12px;
            border-left: 4px solid #2563eb;
            margin-bottom: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .question-number {{
            font-weight: bold;
            font-size: 13pt;
            color: black;
        }}
        
        .question-marks {{
            background: #2563eb;
            color: white;
            padding: 3px 10px;
            border-radius: 3px;
            font-weight: bold;
            font-size: 11pt;
        }}
        
        .answer-content {{
            padding: 12px 2px;
            background: #ffffff;
        }}
        
        .answer-text {{
            margin-bottom: 10px;
            white-space: pre-wrap;
            line-height: 1.8;
        }}
        
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
        }}
        
        .marking-point {{
            margin: 6px 0;
            padding-left: 20px;
        }}
        
        .nested-label {{
            background: #10b981;
            color: white;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 10pt;
            margin-left: 10px;
        }}
        
        .answer-image {{
            max-width: 100%;
            height: auto;
            margin: 10px 0;
            border: 2px solid #60a5fa;
            border-radius: 4px;
            padding: 5px;
            display: block;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        
        .answer-image-inline {{
            display: inline-block;
            vertical-align: middle;
            margin: 8px 4px;
            border: 2px solid #60a5fa;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        
        .image-placeholder {{
            display: inline-block;
            margin: 8px 0;
            padding: 16px;
            background: #fef2f2;
            border: 2px dashed #dc2626;
            border-radius: 8px;
        }}
        
        .image-placeholder-header {{
            display: flex;
            align-items: center;
            gap: 8px;
            color: #991b1b;
            font-size: 11pt;
            font-weight: 600;
            margin-bottom: 8px;
        }}
        
        .image-placeholder-details {{
            margin-top: 8px;
            font-size: 10pt;
            color: #7f1d1d;
        }}
        
        .image-placeholder-details div {{
            margin: 4px 0;
        }}
        
        .bold-text {{
            font-weight: bold;
        }}
        
        .italic-text {{
            font-style: italic;
        }}
        
        .underline-text {{
            text-decoration: underline;
        }}
        
        @media print {{
            .page {{
                page-break-after: always;
            }}
            
            .answer-item {{
                page-break-inside: avoid;
            }}
            
            .page-number {{
                position: fixed;
                bottom: 10mm;
                right: 10mm;
            }}
        }}
    </style>
</head>
<body>
    {coverpage_html}
    {answers_html}
</body>
</html>
    """
    
    return full_html.strip()


def generate_answers_with_pagination(marking_scheme_items, total_questions):
    """
    Generate HTML for all answers with pagination (approx 2-3 answers per page)
    
    Args:
        marking_scheme_items (list): List of marking scheme items
        total_questions (int): Total number of questions for page calculation
    
    Returns:
        str: HTML for all answers with page breaks
    """
    pages_html = []
    current_page_answers = []
    answers_per_page = 2  # Approximately 2 answers per page
    total_pages = 1 + ((len(marking_scheme_items) + answers_per_page - 1) // answers_per_page)
    current_page = 2  # Page 1 is coverpage
    
    for idx, item in enumerate(marking_scheme_items):
        answer_html = generate_single_answer_html(item)
        current_page_answers.append(answer_html)
        
        # Create new page after every 2 answers or at the end
        if len(current_page_answers) >= answers_per_page or idx == len(marking_scheme_items) - 1:
            page_content = '\n'.join(current_page_answers)
            page_html = f"""
    <div class="page">
        {page_content}
        <div class="page-number">Page {current_page} of {total_pages}</div>
    </div>
            """
            pages_html.append(page_html)
            current_page_answers = []
            current_page += 1
    
    return '\n'.join(pages_html)


def generate_single_answer_html(item):
    """
    Generate HTML for a single answer (NO question text, only answer)
    
    Args:
        item (dict): Marking scheme item with answer details
    
    Returns:
        str: HTML for single answer
    """
    number = item.get('number', 1)
    answer = item.get('answer', 'No answer provided')
    marks = item.get('marks', 0)
    is_nested = item.get('is_nested', False)
    marking_points = item.get('marking_points', None)
    answer_images = item.get('answer_inline_images', [])
    image_positions = item.get('answer_image_positions', {})
    
    # Build nested label
    nested_badge = f'<span class="nested-label">NESTED ({marks} marks)</span>' if is_nested else ''
    
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
    
    # Build answer with images using new rendering function
    answer_text_with_images = render_text_with_images(answer, answer_images)
    
    html = f"""
    <div class="answer-item">
        <div class="answer-content">
            <div class="answer-text">
             <span class="question-number">{number}</span> {answer_text_with_images}
            </div>
            {marking_points_html}
        </div>
    </div>
    """
    
    return html


def render_text_with_images(text, images):
    """
    Render text with inline images, diagrams, and formatting
    Supports: **bold**, *italic*, __underline__, _underline_, [IMAGE:id:WxH], [LINES:id]
    
    Args:
        text (str): The text content with placeholders
        images (list): List of image objects/data (base64 or URLs)
    
    Returns:
        str: HTML with images and formatting applied
    """
    if not text:
        return "No answer provided"
    
    # Create image lookup dictionary
    image_dict = {}
    if images:
        for img in images:
            if isinstance(img, dict):
                img_id = img.get('id')
                img_url = img.get('url') or img.get('data')
                if img_id is not None and img_url:
                    image_dict[float(img_id)] = img_url
            elif isinstance(img, str):
                # If images is just a list of base64 strings, use index as ID
                image_dict[float(len(image_dict))] = img
    
    # Split text by formatting markers and image placeholders
    pattern = r'(\*\*.*?\*\*|\*.*?\*|__.*?__|_.*?_|\[IMAGE:[\d.]+:(?:\d+x\d+|\d+)px\]|\[LINES:[\d.]+\])'
    parts = re.split(pattern, text)
    
    result_html = []
    
    for part in parts:
        if not part:
            continue
        
        # Handle bold text **text**
        if part.startswith('**') and part.endswith('**'):
            content = part[2:-2]
            result_html.append(f'<span class="bold-text">{content}</span>')
            continue
        
        # Handle italic text *text*
        if part.startswith('*') and part.endswith('*') and not part.startswith('**'):
            content = part[1:-1]
            result_html.append(f'<span class="italic-text">{content}</span>')
            continue
        
        # Handle underline __text__
        if part.startswith('__') and part.endswith('__'):
            content = part[2:-2]
            result_html.append(f'<span class="underline-text">{content}</span>')
            continue
        
        # Handle underline _text_
        if part.startswith('_') and part.endswith('_') and not part.startswith('__'):
            content = part[1:-1]
            result_html.append(f'<span class="underline-text">{content}</span>')
            continue
        
        # Handle images [IMAGE:id:WxHpx] or [IMAGE:id:Wpx]
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
            
            # Find matching image (with tolerance for floating point comparison)
            image_url = None
            for img_id, img_url in image_dict.items():
                if abs(img_id - image_id) < 0.001:
                    image_url = img_url
                    break
            
            if image_url:
                height_style = f'height: {image_height}px;' if image_height else ''
                result_html.append(f'''
                <br>
                <img src="{image_url}" 
                     alt="Answer Image {int(image_id)}"
                     class="answer-image"
                     style="width: {image_width}px; {height_style} max-width: 100%;">
                <br>
                ''')
            else:
                # Image not found - show placeholder
                height_info = f'{image_height}px' if image_height else 'auto'
                result_html.append(f'''
                <div class="image-placeholder">
                    <div class="image-placeholder-header">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                                  d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                        </svg>
                        <span>Image Not Found</span>
                    </div>
                    <div class="image-placeholder-details">
                        <div>Image ID: {int(image_id)}</div>
                        <div>Expected Size: {image_width}px × {height_info}</div>
                        <div style="margin-top: 4px; font-style: italic;">
                            The image data is missing from the database. This question may need to be re-edited.
                        </div>
                    </div>
                </div>
                ''')
            continue
        
        # Handle answer lines [LINES:id]
        lines_match = re.match(r'\[LINES:([\d.]+)\]', part)
        if lines_match:
            lines_id = float(lines_match.group(1))
            # For now, just show a placeholder for lines
            result_html.append(f'<div style="margin: 10px 0; color: #666;">[Answer Lines: {int(lines_id)}]</div>')
            continue
        
        # Regular text - escape HTML entities
        escaped_text = (part
                       .replace('&', '&amp;')
                       .replace('<', '&lt;')
                       .replace('>', '&gt;')
                       .replace('"', '&quot;')
                       .replace("'", '&#39;'))
        result_html.append(escaped_text)
    
    return ''.join(result_html)