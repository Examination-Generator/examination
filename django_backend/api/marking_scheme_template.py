"""
Marking Scheme Template for KCSE Examination Papers
Generates professional marking schemes with coverpage and answers
"""

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
            padding: 10px;
            background: #ffffff;
            text-align: left;
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
            border: 1px solid #ddd;
            padding: 5px;
            display: block;
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
    
    # Build answer with images
    answer_text_with_images = render_text_with_images(answer, answer_images, image_positions)
    
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
