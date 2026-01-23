"""
English Paper 1 Template Generator
Specific template for KCSE English Paper 1 (Functional Skills)
With simple bold titles before each question (no section headers)
"""

from .coverpage_templates import (
    EnglishPaper1Coverpage,
    BiologyPaper1Coverpage, 
    MarkingSchemeCoverpage
)
import re


def generate_english_paper1_html(coverpage_data, questions, coverpage_class=None):
    """
    Generate English Paper 1 HTML with simple bold titles
    
    Q1: Functional Skills
    Q2: Cloze Test
    Q3: Oral Skills
    
    Args:
        coverpage_data (dict): Coverpage information
        questions (list): List of question dictionaries
        coverpage_class: Coverpage class to use
    
    Returns:
        str: Complete HTML document
    """
    
    # Use default coverpage if not provided
    if coverpage_class is None:
        from .coverpage_templates import EnglishPaper1Coverpage
        coverpage_class = EnglishPaper1Coverpage
    
    # Generate coverpage HTML (page 1)
    # EnglishPaper1Coverpage uses static method, not instance method
    if hasattr(coverpage_class, 'generate_html') and callable(getattr(coverpage_class, 'generate_html')):
        # Static method - call directly with data
        coverpage_html = coverpage_class.generate_html(coverpage_data)
    else:
        # Instance method - create instance first
        coverpage_instance = coverpage_class(coverpage_data)
        coverpage_html = coverpage_instance.generate_html()
    
    # Extract coverpage content (remove html/body tags to combine later)
    coverpage_body = re.search(r'<body>(.*?)</body>', coverpage_html, re.DOTALL)
    if coverpage_body:
        coverpage_content = coverpage_body.group(1)
    else:
        coverpage_content = coverpage_html
    
    # Calculate total pages
    total_pages = 2  # 1 coverpage + 1 question page (all questions continuous)
    
    # Generate question pages with simple titles
    questions_html = _generate_english_paper1_pages(questions, total_pages, coverpage_data)
    
    # Combine everything
    full_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{coverpage_data.get('paper_name', 'English Paper 1')} - Full Preview</title>
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
            
            body {{
                background: white !important;
            }}
            
            /* Hide page title and preview header in print */
            head title {{
                display: none;
            }}
            
            h1, h2, .preview-header {{
                display: none;
            }}
            
            .exam-page {{
                margin: 0 !important;
                box-shadow: none !important;
                padding: 12mm 15mm 30mm 15mm !important;
                height: 297mm !important;
                max-height: 297mm !important;
                page-break-after: always !important;
            }}
            
            /* Ensure page number stays in footer */
            .page-number {{
                position: absolute !important;
                bottom: 10mm !important;
                right: 15mm !important;
                font-size: 11px !important;
            }}
            
            /* Scale coverpage to fit on one page */
            .coverpage {{
                height: 100% !important;
                max-height: 273mm !important; /* 297mm - 24mm padding */
                margin-top: 0 !important;
                display: flex !important;
                flex-direction: column !important;
                justify-content: space-between !important;
                transform-origin: top center !important;
            }}
            
            /* Reduce font sizes and spacing in print for coverpage */
            .coverpage .school-name {{
                font-size: 16px !important;
                margin-bottom: 3px !important;
            }}
            
            .coverpage .class-name, .coverpage .class-title {{
                font-size: 12px !important;
                margin-bottom: 10px !important;
            }}
            
            .coverpage .exam-title {{
                font-size: 14px !important;
                margin-bottom: 8px !important;
            }}
            
            .coverpage .paper-title {{
                font-size: 16px !important;
                margin-bottom: 8px !important;
            }}
            
            .coverpage .paper-details {{
                font-size: 12px !important;
                margin-bottom: 12px !important;
            }}
            
            .header {{
                margin-top: 0 !important;
                margin-bottom: 10px !important;
            }}
            
            .candidate-info {{
                margin-bottom: 12px !important;
                padding: 10px !important;
            }}
            
            .info-label {{
                font-size: 11px !important;
            }}
            
            .info-field {{
                min-height: 22px !important;
            }}
            
            .instructions {{
                margin-bottom: 12px !important;
            }}
            
            .instructions-title {{
                font-size: 12pt !important;
                margin-bottom: 6px !important;
            }}
            
            .instructions ol, .instructions ul, .instructions-list {{
                font-size: 11pt !important;
                line-height: 1.4 !important;
                margin-left: 18px !important;
            }}
            
            .instructions li {{
                margin-bottom: 4px !important;
            }}
            
            .marking-grid-container {{
                margin-top: 8px !important;
                padding-top: 12px !important;
            }}
            
            .grid-title {{
                font-size: 11pt !important;
                margin-bottom: 6px !important;
            }}
            
            .marking-grid {{
                width: 100% !important;
                border-collapse: collapse !important;
                border: 2px solid black !important;
            }}
            
            .marking-grid td {{
                font-size: 9pt !important;
                padding: 6px 3px !important;
                height: 25px !important;
                border: 1px solid #000 !important;
                line-height: 1.2 !important;
            }}
            
            /* Ensure marking grid borders are visible */
            .marking-grid .question-number {{
                border-right: 2px solid black !important;
                border-bottom: 2px solid black !important;
            }}
            
            .marking-grid .grand-total-cell {{
                border: 2px solid black !important;
                background-color: #f0f0f0 !important;
            }}
            
            .marking-grid .total-box {{
                border: 2px solid black !important;
                background-color: white !important;
            }}
            
            .marking-grid .gap-cell {{
                border: none !important;
                background-color: white !important;
            }}
            
            .marking-grid .empty-question-cell {{
                border: none !important;
                background-color: white !important;
            }}
            
            /* Ensure consistent font sizes in print for questions */
            body {{
                font-size: 12pt !important;
            }}
            
            .question-text {{
                font-size: 12pt !important;
                line-height: 1.8 !important;
            }}
            
            .question-number {{
                font-size: 12pt !important;
                font-weight: bold !important;
            }}
            
            .simple-title {{
                font-size: 12pt !important;
                font-weight: bold !important;
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
            padding: 20mm 20mm 30mm 20mm;
            background: white;
            margin: 10mm auto;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            position: relative;
            page-break-after: always;
        }}
        
        .question-page {{
            min-height: auto;
        }}
        
        /* Page number in footer */
        .page-number {{
            position: absolute;
            bottom: 10mm;
            right: 20mm;
            font-size: 11pt;
            font-weight: bold;
        }}
        
        /* Simple title (bold, left-aligned) for English Paper 1 */
        .simple-title {{
            font-size: 14pt;
            font-weight: bold;
            margin-bottom: 15px;
            text-align: left;
        }}
        
        /* Questions styling */
        .question {{
            margin-bottom: 18px;
            page-break-inside: avoid;
        }}
        
        .question-number {{
            font-weight: bold;
            font-size: 15pt;
        }}
        
        .question-text {{
            font-size: 14pt;
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
            margin: 8px 0;
            max-width: 700px;
        }}
        
        .answer-line {{
            width: 100%;
            height: 28px;
            margin: 0;
            padding: 0;
            border-bottom: 2px dotted #000;
            page-break-inside: avoid;
        }}
        
        .answer-line.dotted {{
            border-bottom: 2px dotted #000;
        }}
        
        .answer-line.solid {{
            border-bottom: 2px solid #000;
        }}
        
        /* Coverpage styles */
        .coverpage {{
            width: 100%;
            height: auto;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            page-break-after: always;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 10px;
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
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 5px;
            text-transform: uppercase;
        }}
        
        .class-name, .class-title {{
            font-size: 16pt;
            font-weight: bold;
            margin-bottom: 10px;
            text-transform: uppercase;
        }}
        
        .exam-title {{
            font-size: 16pt;
            font-weight: bold;
            margin-bottom: 20px;
            text-transform: uppercase;
        }}
        
        .paper-title {{
            font-size: 18pt;
            font-weight: bold;
            text-decoration: underline;
            margin-bottom: 10px;
        }}
        
        .paper-details {{
            font-size: 14pt;
            margin-bottom: 20px;
        }}
        
        .candidate-info {{
            border: none;
            padding: 15px;
            margin-bottom: 20px;
        }}
        
        .candidate-info-grid {{
            display: flex;
            flex-direction: column;
            gap: 0;
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
            font-size: 12pt;
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
            font-size: 14pt;
            margin-bottom: 10px;
            text-decoration: underline;
        }}
        
        .instructions ol {{
            margin-left: 20px;
            font-size: 12pt;
            line-height: 1.6;
            list-style: none;
            counter-reset: list-counter;
        }}
        
        .instructions li {{
            margin-bottom: 6px;
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
            font-size: 13pt;
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
            font-size: 10pt;
            font-weight: bold;
            padding: 8px 4px;
            height: 30px;
            line-height: 1.2;
        }}
        
        .marking-grid .question-number {{
            min-width: 35px;
            width: 35px;
        }}
        
        /* Empty question cells (shown but no number) */
        .marking-grid .empty-question-cell {{
            min-width: 35px;
            width: 35px;
            background-color: white;
            border: none !important;
        }}
        
        /* Add spacing before second row */
        .marking-grid .row-with-spacing td {{
            border-top: 2px solid black;
            padding-top: 8px;
        }}
        
        /* Override border-top for empty and gap cells in spacing row */
        .marking-grid .row-with-spacing .empty-question-cell,
        .marking-grid .row-with-spacing .gap-cell {{
            border-top: none !important;
        }}
        
        /* Gap cell between questions and Grand Total */
        .marking-grid .gap-cell {{
            border-right: none !important;
            border-left: none !important;
            border-bottom: none !important;
            background-color: white;
            min-width: 15px;
            width: 15px;
        }}
        
        .marking-grid .grand-total-cell {{
            background-color: #f0f0f0;
            font-size: 10pt;
            font-weight: bold;
            border: 2px solid black;
            padding: 5px 10px;
            min-width: 80px;
        }}
        
        .marking-grid .total-box {{
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
    <!-- Question Pages with Simple Titles -->
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


def _generate_english_paper1_pages(questions, total_pages, coverpage_data):
    """
    Generate pages for English Paper 1 with simple bold titles
    Questions flow continuously (not each on separate page)
    Q1: Functional Skills
    Q2: Cloze Test
    Q3: Oral Skills
    """
    # Question titles mapping
    question_titles = {
        1: "FUNCTIONAL SKILLS",
        2: "CLOZE TEST",
        3: "ORAL SKILLS"
    }
    
    questions_html = []
    
    for q in questions:
        q_number = q.get('number', 0)
        title = question_titles.get(q_number, "")
        
        processed_text = _process_question_text(
            q.get('text', ''),
            q.get('question_inline_images', []),
            q.get('question_answer_lines', [])
        )
        
        # Questions flow continuously with titles
        question_html = f"""
        <div class="question">
            <div class="simple-title">{title}</div>
            <div class="question-text"><span class="question-number">{q_number}.</span> {processed_text}</div>
        </div>
"""
        questions_html.append(question_html)
    
    # All questions on continuous pages with page numbers
    page_html = f"""
    <!-- Question Pages -->
    <div class="exam-page question-page">
        {''.join(questions_html)}
        <div class="page-number">Page 2 of {total_pages}</div>
    </div>
"""
    
    return page_html
