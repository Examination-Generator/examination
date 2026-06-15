from .coverpage_templates import (
    BiologyPaper2MarkingSchemeCoverpage,
    MarkingSchemeCoverpage,
    BiologyPaper2MarkingSchemeCoverpage
)
from api.cover.math.math_coverpage import MathematicsPaper1Coverpage, MathematicsPaper2Coverpage
from api.cover.chem.chem_coverpage import ChemistryPaper1Coverpage, ChemistryPaper2Coverpage
from api.cover.bio.bio_coverpage import BiologyPaper1Coverpage, BiologyPaper2Coverpage
from api.cover.kis.kis_coverpage import KiswahiliPaper1Coverpage, KiswahiliPaper2Coverpage
from api.cover.cre.cre_coverpage import CREPaper1Coverpage, CREPaper2Coverpage
from api.cover.geo.geo_coverpage import GeographyPaper1Coverpage, GeographyPaper2Coverpage
from api.cover.bus.bus_coverpage import BusinessPaper1Coverpage, BusinessPaper2Coverpage
from api.cover.phy.phy_coverpage import PhysicsPaper1Coverpage
from api.cover.agric.agric_coverpage import AgricultureCoverpage
import re
from .page_number_extrctor import extract_paper_number_from_name
from api.exam_template_functions.paper2_question_pages import _generate_paper2_question_pages
from api.exam_template_functions.question_pages import _generate_question_pages
from api.exam_template_functions.kiswahili_paper1 import _generate_kiswahili_paper1_page
from api.exam_template_functions.cre import _generate_cre_paper1_pages
from api.exam_template_functions.bus import _generate_business_paper2_pages
from api.exam_template_functions.answer_lines import _generate_answer_lines_pages



def get_coverpage_class(paper_data, is_marking_scheme=False):
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
        'AGRICULTURE': AgricultureCoverpage,
    }

    PAPER_2_COVERS = {
        'BIOLOGY': BiologyPaper2Coverpage,
        'CHEMISTRY': ChemistryPaper2Coverpage,
        'MATHEMATICS': MathematicsPaper2Coverpage,
        'KISWAHILI': KiswahiliPaper2Coverpage,
        'CRE': CREPaper2Coverpage,
        'GEOGRAPHY': GeographyPaper2Coverpage,
        'BUSINESS': BusinessPaper2Coverpage,
        'AGRICULTURE': AgricultureCoverpage,
    }

    # Then your function becomes:
    if is_marking_scheme:
        return BiologyPaper2MarkingSchemeCoverpage if subject_name == 'BIOLOGY' else MarkingSchemeCoverpage

    if paper_number == 1:
        return PAPER_1_COVERS.get(subject_name, BiologyPaper1Coverpage)
    elif paper_number == 2:
        return PAPER_2_COVERS.get(subject_name, BiologyPaper2Coverpage)
        


def generate_full_exam_html(coverpage_data, questions, paper_data=None, coverpage_class=None):
       
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
    
    # Add Geography section data if not present
    is_geography = 'GEOGRAPHY' in paper_name
    if is_geography and (paper_number == 1 or is_paper1):
        coverpage_data['section_a_marks'] = 25
        coverpage_data['section_b_marks'] = 75
        if 'section_a_instruction' not in coverpage_data:
            coverpage_data['section_a_instruction'] = 'Answer ALL questions in this section'
        if 'section_b_instruction' not in coverpage_data:
            coverpage_data['section_b_instruction'] = 'Answer question 6 and any other TWO questions from this section'
    elif is_geography and (paper_number == 2 or is_paper2):
        coverpage_data['section_a_marks'] = 25
        coverpage_data['section_b_marks'] = 75
        if 'section_a_instruction' not in coverpage_data:
            coverpage_data['section_a_instruction'] = 'Answer ALL questions in this section'
        if 'section_b_instruction' not in coverpage_data:
            coverpage_data['section_b_instruction'] = 'Answer question 6 and any other TWO questions from this section'
    
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
    
    # Check if this is Biology Paper 1 (needs special template)
    is_biology_paper_1 = 'BIOLOGY' in paper_name and paper_number == 1
    
    # Route Biology Paper 1 to its own template
    if is_biology_paper_1:
        from .biology_paper1_template import generate_biology_paper1_html
        return generate_biology_paper1_html(coverpage_data, questions, paper_data, coverpage_class)
    
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
            questions_html = _generate_cre_paper1_pages(questions, total_pages, coverpage_data, inline_answer_lines=answer_lines_pages)
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
            
            body {{
                background: white !important;
            }}
            
            .exam-page {{
                margin: 0 !important;
                box-shadow: none !important;
                page-break-after: always;
            }}
            
            .bus-con{{
                width:100% !important;
            }}
            
            /* Ensure consistent font sizes in print */
            body {{
                font-size: 12pt !important;
            }}
            
            .question-page-header p {{
                font-size: 12pt !important;
            }}
            
            .section-instruction {{
                font-size: 12pt !important;
            }}
            
            .question-text {{
                font-size: 14pt !important;
                line-height: 1.8 !important;
            }}
            
            .question-number {{
                font-size: 15pt !important;
                font-weight: bold !important;
            }}
            
            .question-marks {{
                font-size: 13pt !important;
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

            /* Inline answer lines flow (used when lines should continue after last question) */
            .answer-lines-flow {{
                max-width: 210mm;
                margin-left: auto;
                margin-right: auto;
            }}
            /* Center the question flow container specifically for Biology Paper 2 */
            .question-flow.biology-paper2 {{
                max-width: 210mm;
                margin-left: auto;
                margin-right: auto;
                text-align: left !important;
            }}
            .question-flow.physics-paper2 {{
                max-width: 210mm;
                margin-left: auto;
                margin-right: auto;
                text-align: left !important;
                align-self: stretch;
            }}
            
            .question-flow.business-paper2{{
                max-width: 210mm;
                margin-left: auto;
                margin-right: auto;
                text-align: left !important;
                font-size: 15pt !important;
            }}
            .question{{
                background-color: blue;
                font-size: 15pt !important;
            }}
            .question-part{{
                width: 90% !important;
                font-size: 15pt !important; 
            }}
            
            .question-flow.physics-paper1 {{
                max-width: 210mm;
                margin-left: auto;
                margin-right: auto;
                text-align: left !important;
                align-self: stretch;
            }}
            .question-flow.physics-paper1 .question-text {{
                text-align: left !important;
            }}
            .answer-lines-flow .answer-line {{
                width: 100%;
            }}
            
            /* Force page breaks to be respected */
            .page-break {{
                page-break-after: always !important;
                break-after: page !important;
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
        
        .bus-con{{
            margin:auto; 
            width:70%;
        }}
        
        @media print {{
            .exam-page {{
                margin: 0 auto;
                box-shadow: none;
                padding: 12mm 20mm 30mm 20mm !important;
                min-height: 297mm;
                page-break-after: always !important;
                font-size: 12pt !important;
                width: 210mm;
            }}
            .question-con{{
                margin: 0 auto;
                box-shadow: none;
                padding: 5mm !important;
                min-height: 297mm;
                font-size: 12pt !important;
                width: 210mm;
            }}
            
            /* Ensure page number stays in footer */
            .page-number {{
                position: absolute !important;
                bottom: 10mm !important;
                right: 15mm !important;
                font-size: 11pt !important;
            }}
            
            /* Scale coverpage to fit on one page */
            .coverpage {{
                height: 100%;
                max-height: 273mm; /* 297mm - 24mm padding */
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
                font-size: 14pt !important;
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
                font-size: 11pt !important;
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
            
            .instructions ol, .instructions-list {{
                font-size: 11pt !important;
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
                font-size: 11pt !important;
                margin-bottom: 6px !important;
            }}
            
            .marking-grid td {{
                font-size: 9pt !important;
                padding: 6px 3px !important;
                height: 25px !important;
            }}
        }}
        
        /* Page number in footer */
        .page-number {{
            position: absolute;
            bottom: 10mm;
            right: 20mm;
            font-size: 11pt;
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
            font-size: 16pt;
            margin-bottom: 5px;
        }}
        
        .question-page-header p {{
            font-size: 14pt;
            font-style: italic;
        }}
        
        /* Questions styling */
        .question {{
            margin-bottom: 4px;
        }}
        
        .question-header {{
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            margin-bottom: 10px;
        }}
        
        .question-number {{
            font-weight: bold;
            font-size: 15pt;
        }}
        
        .question-marks {{
            font-size: 13pt;
            font-weight: bold;
            background: #f0f0f0;
            padding: 2px 8px;
            border-radius: 3px;
        }}
        
        .question-text {{
            font-size: 14pt;
            line-height: 1.8;
            text-align: justify;
            white-space: pre-wrap;
        }}

        /* Center question flow for Biology Paper 2 on screen as well */
        .question-flow.biology-paper2 {{
            max-width: 210mm;
            width: 210mm;
            margin-left: auto;
            margin-right: auto;
        }}

        .question-flow.physics-paper2 {{
            max-width: 210mm;
            width: 210mm;
            margin-left: auto;
            margin-right: auto;
            text-align: left !important;
            align-self: stretch;
        }}

        .question-flow.physics-paper1 {{
            max-width: 210mm;
            width: 210mm;
            margin-left: auto;
            margin-right: auto;
            text-align: left !important;
            align-self: stretch;
            display: block;
        }}

        .question-flow.physics-paper1 .question-text {{
            text-align: left !important;
        }}

        .question-flow.chemistry-paper1 {{
            max-width: 210mm;
            width: 100%;
            margin-left: auto;
            margin-right: auto;
            padding: 0 20mm;
            text-align: left !important;
            display: block;
        }}

        .question-flow.chemistry-paper1 .question-text {{
            text-align: left !important;
        }}
        
        /* Ensure exam-page supports centering children */
        .exam-page {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
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
        
        .answer-space {{
            margin-top: 10px;
            border-top: 2px dotted #000;
            min-height: 80px;
        }}
        
        @media print {{
            .answer-line {{
                border-bottom: 2px dotted #000 !important;
                height: 28px !important;
            }}
            
            .answer-line.solid {{
                border-bottom: 2px solid #000 !important;
            }}
            
            .answer-space {{
                border-top: 2px dotted #000 !important;
            }}
            
            /* Center Chemistry Paper 1 questions in print */
            .question-flow.chemistry-paper1 {{
                max-width: 210mm !important;
                width: 100% !important;
                margin-left: auto !important;
                margin-right: auto !important;
                text-align: left !important;
                padding: 0 20mm !important;
                display: block !important;
            }}

            .question-flow.chemistry-paper1 .question-text {{
                text-align: left !important;
            }}
        }}
        
        /* Section styling for Paper 2 */
        .section-header {{
            text-align: center;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 3px solid black;
            page-break-after: avoid;
        }}
        
        .section-header h2 {{
            font-size: 16pt;
            font-weight: bold;
            margin-bottom: 8px;
            text-transform: uppercase;
        }}
        
        .section-instruction {{
            font-size: 14pt;
            font-style: italic;
            margin-top: 5px;
            line-height: 1.8;
        }}
        
        @media print {{
            .section-header {{
                page-break-inside: avoid;
                page-break-after: avoid;
            }}
            
            .section-instruction {{
                font-size: 14pt !important;
                line-height: 1.8 !important;
            }}
            
            .question{{
                background-color: blue;
                font-size: 12pt !important;
            }}
            .question-part{{
                width: 90% !important;
                font-size: 12pt !important; 
            }}
        }}
        
        /* Simple section title for English Paper 1 (bold, left-aligned) */
        .simple-section-title {{
            font-size: 14pt;
            font-weight: bold;
            text-align: left;
            margin: 20px 0 10px 0;
            padding: 0;
            border: none;
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
            font-size: 18pt;
            font-weight: bold;
            margin-bottom: 5px;
            text-transform: uppercase;
        }}
        
        .class-name {{
            font-size: 14pt;
            margin-bottom: 15px;
        }}
        
        .exam-title {{
            font-size: 16pt;
            font-weight: bold;
            margin-bottom: 10px;
            text-transform: uppercase;
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























