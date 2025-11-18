"""
Marking Scheme Template for KCSE Examination Papers
Generates professional marking schemes with coverpage and answers
"""

from .coverpage_templates import MarkingSchemeCoverpage


def generate_marking_scheme_html(coverpage_data, marking_scheme_items):
    """
    Generate complete marking scheme HTML with coverpage and all answers
    
    Args:
        coverpage_data (dict): Coverpage information
        marking_scheme_items (list): List of marking scheme items with answers
    
    Returns:
        str: Complete HTML for marking scheme
    """
    
    # Generate coverpage HTML
    coverpage_html = MarkingSchemeCoverpage.generate_html(coverpage_data)
    
    # Generate marking scheme body
    answers_html = generate_answers_html(marking_scheme_items)
    
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
        }}
        
        body {{
            font-family: 'Times New Roman', Times, serif;
            font-size: 12pt;
            line-height: 1.6;
            color: #000;
        }}
        
        .coverpage {{
            page-break-after: always;
        }}
        
        .marking-scheme-page {{
            padding: 20px 0;
        }}
        
        .answer-item {{
            margin-bottom: 30px;
            page-break-inside: avoid;
        }}
        
        .question-header {{
            background: #f0f0f0;
            padding: 10px;
            border-left: 4px solid #2563eb;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .question-number {{
            font-weight: bold;
            font-size: 14pt;
            color: #1e40af;
        }}
        
        .question-marks {{
            background: #2563eb;
            color: white;
            padding: 4px 12px;
            border-radius: 4px;
            font-weight: bold;
        }}
        
        .question-preview {{
            font-style: italic;
            color: #666;
            margin-bottom: 10px;
            padding: 8px;
            background: #f9fafb;
            border-left: 2px solid #cbd5e1;
        }}
        
        .answer-content {{
            padding: 10px;
            background: #ffffff;
        }}
        
        .answer-text {{
            margin-bottom: 10px;
            white-space: pre-wrap;
        }}
        
        .marking-points {{
            margin-top: 10px;
            padding: 10px;
            background: #fef3c7;
            border-left: 3px solid #f59e0b;
        }}
        
        .marking-points-title {{
            font-weight: bold;
            color: #92400e;
            margin-bottom: 8px;
        }}
        
        .marking-point {{
            margin: 5px 0;
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
            border: 1px solid #ddd;
            padding: 5px;
        }}
        
        @media print {{
            .coverpage {{
                page-break-after: always;
            }}
            
            .answer-item {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    {coverpage_html}
    
    <div class="marking-scheme-page">
        {answers_html}
    </div>
</body>
</html>
    """
    
    return full_html.strip()


def generate_answers_html(marking_scheme_items):
    """
    Generate HTML for all answers in the marking scheme
    
    Args:
        marking_scheme_items (list): List of marking scheme items
    
    Returns:
        str: HTML for all answers
    """
    answers_html_parts = []
    
    for item in marking_scheme_items:
        answer_html = generate_single_answer_html(item)
        answers_html_parts.append(answer_html)
    
    return '\n'.join(answers_html_parts)


def generate_single_answer_html(item):
    """
    Generate HTML for a single answer
    
    Args:
        item (dict): Marking scheme item with answer details
    
    Returns:
        str: HTML for single answer
    """
    number = item.get('number', 1)
    question_preview = item.get('question_preview', '')
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
            <div class="marking-points-title">📌 Marking Points:</div>
            {points_list}
        </div>
        """
    
    # Build answer with images
    answer_text_with_images = render_text_with_images(answer, answer_images, image_positions)
    
    html = f"""
    <div class="answer-item">
        <div class="question-header">
            <div>
                <span class="question-number">Question {number}</span>
                {nested_badge}
            </div>
            <span class="question-marks">{marks} mark{'' if marks == 1 else 's'}</span>
        </div>
        <div class="question-preview">
            <strong>Question:</strong> {question_preview}
        </div>
        <div class="answer-content">
            <div class="answer-text">
                <strong>Answer:</strong><br>
                {answer_text_with_images}
            </div>
            {marking_points_html}
        </div>
    </div>
    """
    
    return html


def render_text_with_images(text, images, image_positions):
    """
    Render text with inline images at specified positions
    
    Args:
        text (str): The text content
        images (list): List of base64 encoded images
        image_positions (dict): Dictionary mapping image indices to character positions
    
    Returns:
        str: HTML with images inserted at correct positions
    """
    if not text:
        return "No answer provided"
    
    if not images or not image_positions:
        return text
    
    # Convert image_positions keys to integers and sort by position
    try:
        positions = []
        for img_idx_str, pos in image_positions.items():
            img_idx = int(img_idx_str)
            if img_idx < len(images):
                positions.append((pos, img_idx))
        
        positions.sort(reverse=True)  # Sort in reverse to insert from end
        
        # Insert images at positions
        result = text
        for pos, img_idx in positions:
            image_data = images[img_idx]
            img_tag = f'<br><img src="{image_data}" class="answer-image" alt="Answer Image {img_idx + 1}"><br>'
            result = result[:pos] + img_tag + result[pos:]
        
        return result
    except (ValueError, IndexError, TypeError):
        return text
