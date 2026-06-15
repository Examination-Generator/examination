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
from .process_text import _process_question_text


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



def _generate_business_paper2_pages(questions, total_pages, coverpage_data=None):
    
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
    <div style="font-size:15pt; line-height:1.8;"  class="question-flow business-paper2">
        <div class="question bus-con" >                
            <div class="question-part" >
                <div style="text-align: left; font-size:15pt;">
                   {question_number}.(a){q_a_text}
                </div>
            </div>
            
            <div class="question-part" >
                <div style="text-align: left; font-size:15pt;">
                    (b){q_b_text}
                </div>
            </div>
        </div>
    </div>
"""
            pages_html.append(page_html)
            current_page += 1
    
    return '\n'.join(pages_html)


def _generate_paper2_question_pages(questions, total_pages, coverpage_data=None, answer_lines_pages=2):
    
    from .page_number_extrctor import extract_paper_number_from_name
    
    pages_html = []
    current_page = 2
    is_biology_paper = False
    flow_answer_lines = False

    # Section boundaries
    metadata = coverpage_data or {}
    paper_name = metadata.get('paper_name', '').upper()
    
    try:
        paper_number = extract_paper_number_from_name(paper_name)
    except ValueError:
        raise ValueError(f"Invalid paper name format. Cannot extract paper number.{paper_name}")

    # Physics Paper 2: render questions in one continuous flow (no forced per-page splitting)
    is_physics_paper2 = 'PHYSICS' in paper_name and paper_number == 2
    if is_physics_paper2:
        all_questions_html = _generate_physics_paper2_continuous_pages(
            questions,
            current_page,
            total_pages
        )
        pages_html.append(all_questions_html['html'])
        current_page = all_questions_html['next_page']

        # Add answer lines if needed
        if answer_lines_pages > 0:
            answer_lines_html = _generate_answer_lines_pages(
                answer_lines_pages,
                current_page,
                total_pages,
                show_page_numbers=False
            )
            pages_html.append(answer_lines_html)

        return '\n'.join(pages_html)
    
    
    is_kiswahili_paper2 = 'KISWAHILI' in paper_name and paper_number == 2
    is_business_paper1 = 'BUSINESS' in paper_name and paper_number == 1
    is_chemistry_paper1 = 'CHEMISTRY' in paper_name and paper_number == 1
    
    if is_kiswahili_paper2 or is_business_paper1 or is_chemistry_paper1:
        all_questions_html = _generate_non_sectioned_pages(
            questions,
            current_page,
            total_pages
        )
        pages_html.append(all_questions_html['html'])
        current_page = all_questions_html['next_page']
        
        # Add answer lines if needed
        if answer_lines_pages > 0:
            answer_lines_html = _generate_answer_lines_pages(answer_lines_pages, current_page, total_pages)
            pages_html.append(answer_lines_html)
        
        return '\n'.join(pages_html)
    
    # Papers that should have sections (explicitly allowed list) - ONLY if paper number is 2
    is_biology = 'BIOLOGY' in paper_name and paper_number == 2
    is_geography = 'GEOGRAPHY' in paper_name and paper_number == 2
    is_mathematics = 'MATHEMATICS' in paper_name or 'MATHS' in paper_name
    is_agriculture = 'AGRICULTURE' in paper_name
    
    # has_sections is TRUE only for allowed papers
    has_sections = (is_biology or is_geography or is_mathematics or is_agriculture)
    
    # Check if this is Agriculture paper (has 3 sections)
    is_agriculture = 'AGRICULTURE' in paper_name
    
    # Check if this is CRE paper (continuous flow, no fixed page split)
    is_cre_paper = ('CRE' in paper_name or 'CHRISTIAN RELIGIOUS EDUCATION' in paper_name)
    
    # Check if this is English Paper 1 (special handling with titled sections)
    is_english_paper1 = 'ENGLISH' in paper_name and paper_number == 1
    
    if is_english_paper1:
        # English Paper 1: Three titled sections (Functional Skills, Cloze Test, Oral Skills)
        english_pages_html = _generate_english_paper1_pages(questions, current_page, total_pages)
        pages_html.append(english_pages_html['html'])
        current_page = english_pages_html['next_page']
    elif is_cre_paper:
        cre_html = _generate_cre_question_page(questions, current_page, total_pages, inline_answer_lines=answer_lines_pages)
        pages_html.append(cre_html)
        current_page += 1
    elif not has_sections:
        # Papers without sections (other non-sectioned papers)
        all_questions_html = _generate_non_sectioned_pages(
            questions,
            current_page,
            total_pages
        )
        pages_html.append(all_questions_html['html'])
        current_page = all_questions_html['next_page']
    elif has_sections:
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
            is_geography_paper = 'GEOGRAPHY' in paper_name
            is_biology_paper = 'BIOLOGY' in paper_name
            
            # Section A/I - Set default marks based on paper type
            if is_geography_paper:
                default_section_a_marks = 25
            elif is_biology_paper:
                default_section_a_marks = 40
            else:
                default_section_a_marks = 40
            
            section_a_marks = metadata.get('section_a_marks', default_section_a_marks)
            if is_mathematics:
                section_a_title = f"SECTION I ({section_a_marks} MARKS)" if section_a_marks else "SECTION I"
            else:
                section_a_title = f"SECTION A ({section_a_marks} MARKS)" if section_a_marks else "SECTION A"
            section_a_instruction = metadata.get('section_a_instruction', 'Answer ALL questions in this section')
            # If this is Biology Paper 2, render in one flowing container (no per-page splitting)
            if is_biology_paper:
                bio_html = _generate_biology_paper2_flow(questions, current_page, total_pages, metadata, inline_answer_pages=answer_lines_pages)
                pages_html.append(bio_html['html'])
                current_page = bio_html['next_page']
                # mark that biology inlined answer lines were handled
                flow_answer_lines = True if answer_lines_pages > 0 else False
            else:
                # Section A
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

                # Section B/II - Set default marks based on paper type
                if is_geography_paper:
                    default_section_b_marks = 75
                elif is_biology_paper:
                    default_section_b_marks = 40
                else:
                    default_section_b_marks = 40
                
                section_b_marks = metadata.get('section_b_marks', default_section_b_marks)
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
                    
                flow_answer_lines = is_biology_paper and answer_lines_pages > 0

                section_b_html = _generate_section_pages(
                    section_b_questions,
                    section_b_title,
                    section_b_instruction,
                    current_page,
                    total_pages,
                    is_last_section=True,
                    answer_lines=0,
                    paper_name=paper_name,
                    flow_last_page=flow_answer_lines,
                    inline_answer_lines=(answer_lines_pages if flow_answer_lines else 0)
                )
                pages_html.append(section_b_html['html'])
                current_page = section_b_html['next_page']
    # Insert pages of dotted answer lines (only if answer_lines_pages > 0)
    if answer_lines_pages > 0:
        if is_biology_paper and flow_answer_lines:
            pass
        else:
            if is_biology_paper:
                answer_lines_html = _generate_answer_lines_pages(
                    answer_lines_pages,
                    current_page,
                    total_pages,
                    show_page_numbers=False,
                    flow_after_previous=True
                )
            else:
                answer_lines_html = _generate_answer_lines_pages(answer_lines_pages, current_page, total_pages)
            pages_html.append(answer_lines_html)

    return '\n'.join(pages_html)


def _generate_cre_question_page(questions, page_number, total_pages, inline_answer_lines=0):
    questions_html = ""
    for q in questions:
        processed_text = _process_question_text(
            q.get('text', ''),
            q.get('question_inline_images', []),
            q.get('question_answer_lines', [])
        )
        
        questions_html += f"""
        <div class="question" style="text-align: left !important; width: 100%;">
            <div class="question-text"><span class="question-number">{q['number']}.</span> {processed_text}</div>
        </div>
"""
    
    inline_answer_html = ""
    if inline_answer_lines and inline_answer_lines > 0:
        inline_answer_html = _generate_answer_lines_pages(
            inline_answer_lines,
            page_number,
            total_pages,
            show_page_numbers=False,
            flow_after_previous=True
        )

    page_html = f"""
    <div class="exam-page">
        <div class="question-flow cre-paper" style="width: 100%; max-width: 210mm; margin-left: auto; margin-right: auto; text-align: left;">
            {questions_html}
            {inline_answer_html}
        </div>
    </div>
"""
    return page_html


def _generate_english_paper1_pages(questions, start_page, total_pages):
    # Define section titles for each question
    section_titles = {
        1: "Functional Skills",
        2: "Cloze Test",
        3: "Oral Skills"
    }
    
    questions_html = ""
    for q in questions:
        q_number = int(q.get('number', 0))
        
        # Add section title before the question if it's question 1, 2, or 3
        if q_number in section_titles:
            section_title = section_titles[q_number]
            questions_html += f"""
        <div class="simple-section-title">{section_title}</div>
"""
        
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
    
    page_html = f"""
    <!-- Page {start_page} -->
    <div class="exam-page page-break">
        {questions_html}        
        <div class="page-number">Page {start_page} of {total_pages}</div>
    </div>
"""
    
    return {
        'html': page_html,
        'next_page': start_page + 1
    }


def _generate_physics_paper2_continuous_pages(questions, start_page, total_pages):
    questions_html = ""
    for q in questions:
        q_number = int(q.get('number', 0))
        if q_number == 1:
            questions_html += """
        <div class="question-flow physics-paper2" style="width:100%; max-width:210mm; margin-left:auto; margin-right:auto; text-align:left;">
            <div class="physics-section-a" style="width:100%; text-align:left;">
            <div class="simple-section-title" style="text-align: center;">SECTION A (25 MARKS)</div>
            <div class="section-instruction" style="text-align: center; font-style: italic;">Answer all questions in this section</div>
"""
        elif q_number == 14:
            # Close Section A container before starting Section B
            questions_html += """
            </div>
            <div class="physics-section-b" style="width:100%; text-align:left;">
            <div class="simple-section-title" style="text-align: center;">SECTION B (55 MARKS)</div>
            <div class="section-instruction" style="text-align: center; font-style: italic;">Answer all questions in this section</div>
"""

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

    page_html = f"""
    <div class="exam-page page-break">
        {questions_html}
        <!-- close any open physics section container -->
        </div>
    </div>
"""

    return {
        'html': page_html,
        'next_page': start_page + 1
    }


def _generate_non_sectioned_pages(questions, start_page, total_pages):
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
        <div class="question" style="text-align: left !important;">
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


def _generate_answer_lines_pages(num_pages, start_page, total_pages, show_page_numbers=True, flow_after_previous=False):
    lines_per_page = 25

    if flow_after_previous:
        lines_html = ''
        for _ in range(num_pages * lines_per_page):
            lines_html += '<div class="answer-line dotted" style="height: 28px; margin: 8px 0;"></div>'
        return f'''
    <div class="answer-lines-flow">
        {lines_html}
    </div>
'''

    pages_html = []
    
    for i in range(num_pages):
        lines_html = ''
        for _ in range(lines_per_page):
            lines_html += '<div class="answer-line dotted" style="height: 28px; margin: 8px 0;"></div>'
        page_number_html = ''
        if show_page_numbers:
            page_number_html = f'<div class="page-number">Page {start_page + i} of {total_pages}</div>'
        page_html = f'''
    <div class="exam-page page-break">
        {lines_html}
        {page_number_html}
    </div>
'''
        pages_html.append(page_html)
    
    return '\n'.join(pages_html)


def _generate_section_pages(questions, section_title, section_instruction, start_page, total_pages, is_last_section=False, answer_lines=0, paper_name='', flow_last_page=False, inline_answer_lines=0):
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
    
   
    is_kiswahili_paper2 = 'KISWAHILI' in paper_name.upper() and paper_number == 2
    is_business_paper1 = 'BUSINESS' in paper_name.upper() and paper_number == 1
    is_chemistry_paper1 = 'CHEMISTRY' in paper_name.upper() and paper_number == 1
    
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
        <div class="question" style="text-align: left !important;">
            <div class="question-text"><span class="question-number">{q['number']}.</span> {processed_text}</div>
        </div>
"""
        
        if is_last_page_of_questions and inline_answer_lines and flow_last_page:
            inline_lines_html = _generate_answer_lines_pages(inline_answer_lines, current_page, total_pages, show_page_numbers=False, flow_after_previous=True)
            questions_html += inline_lines_html
        
        section_header_html = ""
        if is_first_page and section_title is not None and not (is_kiswahili_paper2 or is_business_paper1 or is_chemistry_paper1):
            section_header_html = f"""
        <div class="section-header">
            <h2>{section_title}</h2>
            <p class="section-instruction">{section_instruction}</p>
        </div>
        """
        page_class = 'exam-page'
        if not (flow_last_page and is_last_page_of_questions):
            page_class += ' page-break'

        page_html = f"""
        <!-- Page {current_page} -->
        <div class="{page_class}">
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


def _generate_cre_paper1_pages(questions, total_pages, coverpage_data=None, inline_answer_lines=0):
    """
    Generate CRE Paper 1 questions in one continuous flow.
    
    Args:
        questions: List of question dictionaries
        total_pages: Total pages in paper
        coverpage_data: Metadata from coverpage
    
    Returns:
        str: HTML for the flowing CRE Paper 1 content
    """
    return _generate_cre_question_page(questions, 2, total_pages, inline_answer_lines=inline_answer_lines)


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
    
    # Add instruction before questions
    instruction_html = """
        <div style="font-weight: bold; margin-bottom: 10px; font-size: 12pt;">
            Swali la kwanza ni lazima kisha uchague lingine moja kwa zilizo salia
        </div>
"""
    
    # Generate all questions on one page
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
    
    page_html = f"""
    <!-- Page {current_page} -->
    <div class="exam-page page-break">
        {instruction_html}
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
    # Generate all questions in a flowing container without fixed pages
    questions_html = ""
    
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

    # Track sections as we generate questions
    last_section = None
    questions_html = ""
    
    # Determine paper type for section naming
    paper_name_for_sections = metadata.get('paper_name', '').upper()
    is_mathematics_paper = 'MATHEMATICS' in paper_name_for_sections or 'MATHS' in paper_name_for_sections
    is_agriculture_paper = 'AGRICULTURE' in paper_name_for_sections
    # Detect Physics Paper 1 so Section A questions can be left-aligned without changing headers
    is_physics_paper1 = False
    try:
        pn = extract_paper_number_from_name(paper_name_for_sections)
        if 'PHYSICS' in paper_name_for_sections and pn == 1:
            is_physics_paper1 = True
    except Exception:
        if 'PHYSICS' in paper_name_for_sections and ('PAPER 1' in paper_name_for_sections or 'PAPER I' in paper_name_for_sections):
            is_physics_paper1 = True
    
    # Generate all questions in flowing order
    for q in questions:
        qnum = int(q.get('number', 0))
        # Determine section by question number
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
        <div class="section-header"> 
            <h2>SECTION {current_section}{s_marks_text}</h2>
            <div class="section-instruction" style="font-style: italic;">{instruction_text}</div>
        </div>
"""
        last_section = current_section
        
        # Process and add the question
        processed_text = _process_question_text(
            q.get('text', ''),
            q.get('question_inline_images', []),
            q.get('question_answer_lines', [])
        )

        question_wrapper_style = 'text-align: left !important; width: 100%; align-self: stretch;' if is_mathematics_paper else 'text-align: left !important;'
        
        questions_html += f"""
        <div class="question" style="{question_wrapper_style} background-color: red;">
            <div class="question-text"><span class="question-number">{q['number']}.</span> {processed_text}</div>
        </div>
"""
    
    # Determine if this is Chemistry Paper 1 so we can center the question flow
    paper_name_for_detection = (metadata.get('paper_name', '') or '').upper()
    is_chemistry_paper1 = False
    # Robust detection: try helper, fall back to keyword checks
    try:
        paper_num = extract_paper_number_from_name(paper_name_for_detection)
        if 'CHEMISTRY' in paper_name_for_detection and paper_num == 1:
            is_chemistry_paper1 = True
    except Exception:
        # Fallback: look for common "paper 1" keywords
        if 'CHEMISTRY' in paper_name_for_detection and (
            'PAPER 1' in paper_name_for_detection or
            'PAPER I' in paper_name_for_detection or
            'PAPER ONE' in paper_name_for_detection or
            'PAPER  1' in paper_name_for_detection
        ):
            is_chemistry_paper1 = True

    # Wrap all questions in a single flowing container. If Chemistry Paper 1,
    # place the questions inside a centered `question-flow chemistry-paper1` container.
    if is_physics_paper1:
        page_html = f"""
    <div class="exam-page page-break">
        <div class="question-flow physics-paper1">
            {questions_html}
        </div>
    </div>
"""
    elif is_chemistry_paper1:
        page_html = f"""
    <div class="exam-page page-break">
        <div class="question-flow chemistry-paper1 margin-auto">
            {questions_html}
        </div>
    </div>
"""
    else:
        page_html = f"""
    <div class="exam-page page-break ">
        <div class="question-flow chemistry-paper1 margin-auto" >
            {questions_html}
        </div>
    </div>
"""

    return page_html


def _generate_biology_paper2_flow(questions, start_page, total_pages, metadata=None, inline_answer_pages=0):
    
    meta = metadata or {}

    # Section A count (default 5)
    section_a_count = meta.get('section_a_questions', 5)
    try:
        section_a_count = int(section_a_count)
    except Exception:
        section_a_count = 5

    section_a_questions = [q for q in questions if int(q.get('number', 0)) <= section_a_count]
    section_b_questions = [q for q in questions if int(q.get('number', 0)) > section_a_count]

    try:
        section_a_marks = 40
    except Exception:
        section_a_marks = 40
    section_a_title = f"SECTION A ({section_a_marks} MARKS)" if section_a_marks is not None else "SECTION A"
    section_a_instruction = meta.get('section_a_instruction', 'Answer ALL questions in this section')

    try:
        section_b_marks = 40
    except Exception:
        section_b_marks = 40
    section_b_title = f"SECTION B ({section_b_marks} MARKS)" if section_b_marks is not None else "SECTION B"
    section_b_instruction = meta.get('section_b_instruction', 'Answer question 6 and either question 7 or 8')

    parts = []
    parts.append('<div class="question-flow biology-paper2">')

    # Section A header
    parts.append(f'<div class="section-header"><h2>{section_a_title}</h2><div class="section-instruction">{section_a_instruction}</div></div>')

    for q in section_a_questions:
        processed_text = _process_question_text(
            q.get('text', ''),
            q.get('question_inline_images', []),
            q.get('question_answer_lines', [])
        )
        parts.append(f"<div class=\"question\"><div class=\"question-text\"><span class=\"question-number\">{q['number']}.</span> {processed_text}</div></div>")

    # Section B header
    parts.append(f'<div class="section-header"><h2>{section_b_title}</h2><div class="section-instruction">{section_b_instruction}</div></div>')

    for q in section_b_questions:
        processed_text = _process_question_text(
            q.get('text', ''),
            q.get('question_inline_images', []),
            q.get('question_answer_lines', [])
        )
        parts.append(f"<div class=\"question\"><div class=\"question-text\"><span class=\"question-number\">{q['number']}.</span> {processed_text}</div></div>")

    # Inline answer lines appended directly after last question
    if inline_answer_pages and inline_answer_pages > 0:
        inline_html = _generate_answer_lines_pages(inline_answer_pages, start_page, total_pages, show_page_numbers=False, flow_after_previous=True)
        parts.append(inline_html)

    parts.append('</div>')

    html = '\n'.join(parts)
    return {'html': html, 'next_page': start_page + 1}