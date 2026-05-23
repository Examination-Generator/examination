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
from .process_text import _process_question_text


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
    questions_per_page = 3
    question_pages = (len(questions) + questions_per_page - 1) // questions_per_page
    total_pages = 1 + question_pages + answer_lines_page_count
    
    # Generate question pages WITHOUT sections
    questions_html = _generate_non_sectioned_pages(questions, 2, total_pages, paper_name)
    
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
            
            body {{
                background: white !important;
            }}
            
            .exam-page {{
                margin: 0 !important;
                box-shadow: none !important;
                padding: 12mm 15mm 30mm 15mm !important;
                height: 297mm;
                max-height: 297mm;
                page-break-after: always !important;
            }}
            
            /* Ensure page number stays in footer */
            .page-number {{
                position: absolute !important;
                bottom: 10mm !important;
                right: 15mm !important;
                font-size: 12pt !important;
            }}
            
            /* Ensure consistent font sizes in print */
            .question-text {{
                font-size: 12pt !important;
                line-height: 1.8 !important;
            }}

            .question-flow.business-paper1 {{
                max-width: 205mm;
                margin-left: auto;
                margin-right: auto;
                text-align: left !important;
                font-size: 12pt;
            }}
            /* Center question flow for Chemistry Paper 1 in print */
            .question-flow.chemistry-paper1 {{
                max-width: 210mm;
                width: 100% !important;
                margin-left: auto !important;
                margin-right: auto !important;
                text-align: left !important;
                font-size: 12pt !important;
            }}

            .question-flow.chemistry-paper1 .question-text {{
                text-align: left !important;
            }}
            
            .question-number {{
                font-size: 12pt !important;
            }}
            
            /* Ensure answer lines are visible in print */
            .answer-line {{
                border-bottom: 2px dotted #000 !important;
                height: 28px !important;
                page-break-inside: avoid;
            }}
            
            .answer-line.solid {{
                border-bottom: 2px solid #000 !important;
            }}
            
            /* Force page breaks to be respected */
            .page-break {{
                page-break-after: always !important;
                break-after: page !important;
            }}
            
            /* Scale coverpage to fit on one page */
            .coverpage {{
                height: 100%;
                max-height: 273mm;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                transform-origin: top center;
            }}
            
            /* Reduce font sizes and spacing in print for coverpage */
            .coverpage .school-name {{
                font-size: 16pt !important;
                margin-bottom: 3px !important;
            }}
            
            .coverpage .class-name {{
                font-size: 12pt !important;
                margin-bottom: 10px !important;
            }}
            
            .coverpage .exam-title {{
                font-size: 12pt !important;
                margin-bottom: 8px !important;
            }}
            
            .coverpage .paper-details {{
                font-size: 12pt !important;
                margin-bottom: 12px !important;
            }}
            
            .header {{
                margin-bottom: 10px !important;
            }}
            
            .candidate-info {{
                margin-bottom: 12px !important;
                padding: 10px !important;
            }}
            
            .info-label {{
                font-size: 12pt !important;
            }}
            
            .info-field {{
                min-height: 22px !important;
            }}
            
            .instructions {{
                margin-bottom: 4px !important;
            }}
            
            .instructions-title {{
                font-size: 12pt !important;
                margin-bottom: 6px !important;
            }}
            
            .instructions ol {{
                font-size: 12pt !important;
                line-height: 1.4 !important;
            }}
            
            .instructions li {{
                margin-bottom: 4px !important;
            }}
            
            .marking-grid-container {{
                margin-top: 8px !important;
                padding-top: 12px !important;
            }}
            
            .grid-title {{
                font-size: 17px !important;
                margin-bottom: 6px !important;
            }}
            
            .marking-grid td {{
                font-size: 10px !important;
                padding: 6px 3px !important;
                height: 25px !important;
            }}
            
            /* Ensure consistent font sizes in print */
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
        
        @media print {{
            .exam-page {{
                margin: 0;
                box-shadow: none;
            }}
        }}
        
        /* Page number in footer */
        .page-number {{
            position: absolute;
            bottom: 10mm;
            right: 20mm;
            font-size: 12pt !important;
            font-weight: bold;
        }}
        
        /* Questions styling */
        .question {{
            margin-bottom: 18px;
            page-break-inside: avoid;
        }}
        
        .question-number {{
            font-weight: bold;
            font-size: 12pt !important;
        }}
        
        .question-text {{
            font-size: 12pt !important;
            line-height: 1.8 !important;
            text-align: justify;
            white-space: pre-wrap;
        }}

        .question-flow.business-paper1 {{
            max-width: 210mm;
            margin-left: auto;
            margin-right: auto;
        }}
        /* Center question flow for Chemistry Paper 1 on screen as well */
        .question-flow.chemistry-paper1 {{
            max-width: 210mm;
            width: 100%;
            margin-left: auto;
            margin-right: auto;
            padding: 0 20mm;
            display: block;
        }}

        .question-flow.chemistry-paper1 .question-text {{
            text-align: left !important;
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
        
        /* Coverpage styles */
        .coverpage {{
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            page-break-after: always;
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



def _generate_non_sectioned_pages(questions, start_page, total_pages, paper_name=''):
    questions_html = ""

    for q in questions:
        processed_text = _process_question_text(
            q.get('text', ''),
            q.get('question_inline_images', []),
            q.get('question_answer_lines', [])
        )

        questions_html += f"""
        <div class="question" style="text-align: left !important;">
            <div class="question-text"><span class="question-number">{q['number']}.</span> {processed_text}</div>
        </div>
"""

    # Flow naturally across printed pages instead of forcing page-sized chunks.
    is_business_paper1 = 'BUSINESS' in paper_name.upper() and extract_paper_number_from_name(paper_name) == 1
    is_chemistry_paper1 = 'CHEMISTRY' in paper_name.upper() and extract_paper_number_from_name(paper_name) == 1

    if is_business_paper1:
        flow_class = 'question-flow business-paper1'
    elif is_chemistry_paper1:
        flow_class = 'question-flow chemistry-paper1'
    else:
        flow_class = 'question-flow'

    return f"""
    <div class="{flow_class} " style="text-align: left !important;">
        {questions_html}
    </div>
"""
