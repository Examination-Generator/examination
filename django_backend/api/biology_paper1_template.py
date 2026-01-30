"""
Biology Paper 1 Exam Template
Dedicated template for KCSE Biology Paper 1 with optimized styling and print layout
"""

from .coverpage_templates import BiologyPaper1Coverpage
from .exam_paper_template import _process_question_text


def generate_biology_paper1_html(coverpage_data, questions, paper_data=None, coverpage_class=None):
    """
    Generate Biology Paper 1 specific HTML with optimized styling
    This template fixes the print alignment and content flow issues specific to Biology Paper 1
    
    Args:
        coverpage_data (dict): Coverpage information
        questions (list): List of question dictionaries
        paper_data (dict): Paper metadata (optional)
        coverpage_class: Coverpage class to use (optional, defaults to BiologyPaper1Coverpage)
    
    Returns:
        str: Complete HTML document for Biology Paper 1
    """
    # Use Biology Paper 1 coverpage if not specified
    if coverpage_class is None:
        coverpage_class = BiologyPaper1Coverpage
    
    # Generate coverpage HTML
    coverpage_content = coverpage_class.generate_html(coverpage_data)
    
    # Process all questions in flowing order
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
    
    # Generate complete HTML with Biology Paper 1 specific styling
    full_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{coverpage_data.get('paper_name', 'BIOLOGY PAPER 1')} - Full Preview</title>
    <style>
        @page {{
            size: A4;
            margin: 0;
        }}
        
        @media print {{
            body {{
                margin: auto;
                width: 210mm !important;
                padding: 0;
                font-family: 'Times New Roman', Times, serif !important;
                font-size: 12pt !important;
                background: white !important;
            }}
            
            .coverpage-container {{
                page-break-after: always !important;
                width: 210mm !important;
                min-height: 297mm;
                padding: 20mm;
                margin: 0;
            }}
            
            .questions-container {{
                width: 210mm !important;
                padding: 20mm;
                margin: 0;
            }}
            
            .question {{
                page-break-inside: avoid;
                break-inside: avoid;
                margin-bottom: 20px;
            }}
            
            .question-text {{
                font-size: 14pt !important;
                line-height: 1.8 !important;
            }}
            
            .question-number {{
                font-size: 15pt !important;
                font-weight: bold !important;
            }}
        }}
        
        * {{
            margin: auto !important;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Times New Roman', Times, serif;
            background: #f0f0f0;
        }}
        
        .coverpage-container {{
            width: 210mm;
            min-height: 297mm;
            padding: 20mm;
            background: white;
            margin: 10mm auto;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            page-break-after: always;
        }}
        
        .questions-container {{
            width: 210mm;
            padding: 20mm;
            background: white;
            margin: 10mm auto;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}
        
        .question {{
            margin-bottom: 20px;
            page-break-inside: avoid;
            break-inside: avoid;
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
            margin: 10px 0;
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
        
        @media print {{
            .answer-line {{
                border-bottom: 2px dotted #000 !important;
                height: 28px !important;
            }}
            
            .answer-line.solid {{
                border-bottom: 2px solid #000 !important;
            }}
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
    </style>
</head>
<body>
    <!-- Coverpage -->
    <div class="coverpage-container">
        {coverpage_content}
    </div>
    
    <!-- Questions -->
    <div class="questions-container">
        {questions_html}
    </div>
</body>
</html>
"""
    
    return full_html
