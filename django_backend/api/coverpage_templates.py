from datetime import datetime
from api.cover.format_time import format_time_allocation

class BiologyPaper2MarkingSchemeCoverpage:
    
    @staticmethod
    def generate_html(data):
        """
        Generate HTML for Biology Paper 2 Marking Scheme coverpage
        """
        school_name = data.get('school_name', 'EXAMINATION CENTRE')
        school_logo = data.get('school_logo', '/exam.png')
        logo_position = data.get('logo_position', 'center')
        class_name = data.get('class_name', '')
        exam_title = data.get('exam_title', 'END TERM EXAMINATION 2025')
        paper_name = data.get('paper_name', 'BIOLOGY PAPER 2')
        
        # Section configuration
        section_a_questions = data.get('section_a_questions', 5)
        section_a_marks = data.get('section_a_marks', 8)
        section_b_questions = data.get('section_b_questions', 3)
        section_b_marks = data.get('section_b_marks', 20)
        total_marks = data.get('total_marks', 80)
        total_questions = section_a_questions + section_b_questions
        
        # Calculate total pages for marking scheme
        total_pages = data.get('total_pages', 15)  # Marking scheme usually has more pages
        
        # Instructions for marking scheme
        instructions = [
            'This is a confidential document for authorized examiners only.',
            'Do not distribute to candidates before or during examination.',
            'Award marks strictly according to the marking points provided.',
            'Accept any valid alternative answers that demonstrate understanding.',
            'For Section A: Award marks for each of the 5 questions (8 marks each).',
            'For Section B: Question 6 is compulsory (20 marks). For Questions 7 & 8, mark only the one attempted by the candidate.',
            f'This marking scheme consists of {total_pages} printed pages.',
            'Check that all pages are printed and no answers are missing.'
        ]
        
        # Generate instruction items HTML
        instruction_items = "".join([f'<li style="margin-bottom: 8px;">{instruction}</li>' for instruction in instructions])
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{paper_name} - MARKING SCHEME</title>
    <style>
        @page {{
            size: A4;
            margin: 0;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Times New Roman', Times, serif;
            width: 210mm;
            height: 297mm;
            padding: 20mm;
            background: white;
        }}
        
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
            margin-bottom: 15px;
        }}
        
        .logo-container.left {{
            text-align: left;
        }}
        
        .logo-container.center {{
            text-align: center;
        }}
        
        .logo-container.right {{
            text-align: right;
        }}
        
        .school-logo {{
            max-width: 80px;
            max-height: 80px;
            object-fit: contain;
        }}
        
        .school-name {{
            font-size: 1.6rem;
            font-weight: bold;
            margin-bottom: 5px;
            text-transform: uppercase;
        }}
        
        .class-title {{
            font-size: 1.2rem;
            font-weight: bold;
            margin-bottom: 8px;
        }}
        
        .exam-title {{
            font-size: 1.3rem;
            font-weight: bold;
            margin-bottom: 10px;
            text-transform: uppercase;
        }}
        
        .paper-title {{
            font-size: 1.4rem;
            font-weight: bold;
            margin-bottom: 15px;
            text-transform: uppercase;
        }}
        
        .marking-scheme-label {{
            font-size: 1.2rem;
            font-weight: bold;
            color: #d32f2f;
            margin: 10px 0;
            padding: 8px;
            border: 2px solid #d32f2f;
            display: inline-block;
        }}
        
        .confidential-notice {{
            margin: 15px 0;
            padding: 12px;
            background-color: #fff3cd;
            border: 2px solid #856404;
            border-radius: 4px;
        }}
        
        .confidential-text {{
            font-size: 1.1rem;
            font-weight: bold;
            color: #856404;
            text-align: center;
        }}
        
        .instructions {{
            border: 2px solid #000;
            padding: 15px;
            margin: 20px 0;
            flex-grow: 1;
            display: flex;
            flex-direction: column;
        }}
        
        .instructions-title {{
            font-size: 1.2rem;
            font-weight: bold;
            margin-bottom: 12px;
            text-decoration: underline;
        }}
        
        .instructions ol {{
            margin-left: 20px;
            font-size: 12px;
            line-height: 1.6;
        }}
        
        @media print {{
            body {{
                margin: 0;
                padding: 20mm;
            }}
            
            
        }}
    </style>
</head>
<body>
    <div class="coverpage">
        <!-- Header -->
        <div class="header">
            <div class="logo-container {logo_position}">
                <img src="{school_logo}" alt="School Logo" class="school-logo" onerror="this.src='/exam.png'">
            </div>
            <div class="school-name">{school_name}</div>
            {f'<div class="class-title">{class_name}</div>' if class_name else ''}
            <div class="exam-title">{exam_title}</div>
            <div class="paper-title">{paper_name}</div>
            <div class="marking-scheme-label">*** MARKING SCHEME ***</div>
            
            <!-- Confidential Notice -->
            <div class="confidential-notice">
                <div class="confidential-text">CONFIDENTIAL - FOR EXAMINERS ONLY</div>
            </div>
        </div>
        
        <!-- Instructions Section -->
        <div class="instructions">
            <div class="instructions-title">INSTRUCTIONS TO EXAMINERS</div>
            <ol>
                {instruction_items}
            </ol>
        </div>
    </div>
</body>
</html>
        """
        
        return html.strip()
    
    @staticmethod
    def generate_default_data(generated_paper, paper):
        """
        Generate default marking scheme coverpage data for Biology Paper 2
        
        Args:
            generated_paper: GeneratedPaper instance
            paper: Paper instance
        
        Returns:
            dict: Default marking scheme coverpage data
        """
        # Get coverpage data from generated paper if available
        saved_coverpage = getattr(generated_paper, 'coverpage_data', None) or {}
        
        # Get metadata for section information
        metadata = generated_paper.metadata or {}
        
        # Generate paper name
        paper_name_upper = paper.name.upper()
        subject_name_upper = paper.subject.name.upper()
        
        if subject_name_upper in paper_name_upper:
            display_paper_name = paper_name_upper
        else:
            display_paper_name = f'{subject_name_upper} {paper_name_upper}'
        
        return {
            'school_name': saved_coverpage.get('school_name', 'EXAMINATION CENTRE'),
            'school_logo': saved_coverpage.get('school_logo', '/exam.png'),
            'logo_position': saved_coverpage.get('logo_position', 'center'),
            'class_name': saved_coverpage.get('class_name', ''),
            'exam_title': saved_coverpage.get('exam_title', 'END TERM EXAMINATION 2025'),
            'paper_name': display_paper_name,
            'section_a_questions': metadata.get('section_a_questions', 5),
            'section_a_marks': metadata.get('section_a_marks_per_question', 8),
            'section_b_questions': metadata.get('section_b_questions', 3),
            'section_b_marks': metadata.get('section_b_marks_per_question', 20),
            'total_marks': generated_paper.total_marks,
            'total_questions': generated_paper.total_questions,
            'total_pages': 15,
        }


class MarkingSchemeCoverpage:
    """
    Marking Scheme Coverpage Template - matches question paper style
    """
    
    @staticmethod
    def generate_html(data):
        """
        Generate HTML for Marking Scheme coverpage (similar to question paper but without candidate section)
        """
        school_name = data.get('school_name', 'EXAMINATION CENTRE')
        school_logo = data.get('school_logo', '/exam.png')
        logo_position = data.get('logo_position', 'center')
        class_name = data.get('class_name', '')
        exam_title = data.get('exam_title', 'END TERM EXAMINATION 2025')
        paper_name = data.get('paper_name', 'BIOLOGY PAPER 1')
        total_questions = data.get('total_questions', 25)
        total_marks = data.get('total_marks', 80)
        
        # Calculate total pages for marking scheme (coverpage + answer pages)
        total_pages = 1 + ((total_questions + 1) // 2)  # Approximately 2 answers per page
        
        # Instructions for marking scheme
        instructions = [
            'This is a confidential document for authorized examiners only.',
            'Do not distribute to candidates before or during examination.',
            'Award marks strictly according to the marking points provided.',
            'Accept any valid alternative answers that demonstrate understanding.',
            'Check that all pages are printed and no answers are missing.'
        ]
        
        # Generate instruction items HTML (can't use list comprehension with backslash in f-string)
        instruction_items = "".join([f'<li style="margin-bottom: 8px;">{instruction}</li>' for instruction in instructions])
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{paper_name} - MARKING SCHEME</title>
    <style>
        @page {{
            size: A4;
            margin: 0;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Times New Roman', Times, serif;
            width: 210mm;
            height: 297mm;
            padding: 20mm;
            background: white;
        }}
        
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
        
        .logo-container.left {{
            justify-content: flex-start;
        }}
        
        .logo-container.center {{
            justify-content: center;
        }}
        
        .logo-container.right {{
            justify-content: flex-end;
        }}
        
        .school-logo {{
            max-width: 100px;
            max-height: 100px;
            object-fit: contain;
        }}
        
        .school-name {{
            font-size: 20px;
            font-weight: bold;
            text-transform: uppercase;
            margin-bottom: 5px;
        }}
        
        .class-title {{
            font-size: 16px;
            font-weight: bold;
            text-transform: uppercase;
            margin-bottom: 5px;
        }}
        
        .exam-title {{
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 20px;
        }}
        
        .paper-title {{
            font-size: 18px;
            font-weight: bold;
            text-decoration: underline;
            margin-bottom: 5px;
        }}
        
        .marking-scheme-label {{
            font-size: 16px;
            font-weight: bold;
            color: #dc2626;
            margin-bottom: 10px;
        }}
        
        .paper-details {{
            font-size: 14px;
            margin-bottom: 20px;
        }}
        
        /* Instructions Section - positioned in middle */
        .instructions {{
            border: 2px solid #000;
            padding: 15px;
            margin: 20px 0;
            flex-grow: 1;
            display: flex;
            flex-direction: column;
        }}
        
        .instructions-title {{
            font-size: 14px;
            font-weight: bold;
            margin-bottom: 10px;
            text-decoration: underline;
            text-align: center;
        }}
        
        .instructions ol {{
            margin-left: 20px;
            font-size: 12px;
            line-height: 1.6;
        }}
        
        .instructions li {{
            margin-bottom: 8px;
        }}
        
        /* Confidential Notice - positioned relative to header */
        .confidential-notice {{
            background: #fee2e2;
            border: 2px solid #dc2626;
            padding: 10px;
            text-align: center;
            margin-top: 10px;
            position: relative;
        }}
        
        .confidential-text {{
            font-weight: bold;
            color: #991b1b;
            font-size: 14px;
        }}
        
        /* Print Styles */
        @media print {{
            @page {{
                size: A4;
                margin: 4mm;
            }}

            body {{
                margin: 0;
                padding: 0;
                overflow: hidden;
            }}
            
            .coverpage {{
                width: 100%;
                min-height: 0;
                height: auto;
                overflow: hidden;
                padding: 6mm 8mm 4mm 8mm;
                transform: scale(0.9);
                transform-origin: top center;
            }}

            .header {{
                margin-bottom: 8px;
            }}

            .logo-container {{
                margin-bottom: 6px;
            }}

            .school-logo {{
                max-width: 66px;
                max-height: 66px;
            }}

            .school-name {{
                font-size: 14pt;
                margin-bottom: 2px;
            }}

            .class-name {{
                font-size: 10pt;
                margin-bottom: 4px;
            }}

            .exam-title {{
                font-size: 12pt;
                margin-bottom: 6px;
            }}

            .paper-name {{
                font-size: 12pt;
            }}

            .time-allocation {{
                font-size: 10pt;
                margin-top: 0;
            }}

            .candidate-info {{
                margin: 8px 0;
                padding: 6px;
            }}

            .candidate-info-grid {{
                gap: 8px 10px;
            }}

            .info-row-full,
            .info-row-grid {{
                margin-bottom: 6px;
            }}

            .info-label {{
                font-size: 9px;
                min-width: 32px;
            }}

            .info-field {{
                min-height: 16px;
            }}

            .instructions {{
                margin-bottom: 8px;
            }}

            .instructions-title {{
                font-size: 10pt;
                margin-bottom: 4px;
            }}

            .instructions ol {{
                margin-left: 14px;
                font-size: 9pt;
                line-height: 1.25;
            }}

            .instructions li {{
                margin-bottom: 2px;
            }}

            .marking-grid-container {{
                margin-top: 6px;
                padding-top: 6px;
            }}

            .grid-title {{
                font-size: 9pt;
                margin-bottom: 4px;
            }}

            .marking-grid {{
                width: 100%;
            }}

            .marking-grid th,
            .marking-grid td {{
                font-size: 8pt;
                padding: 4px 3px;
            }}
        }}
    </style>
</head>
<body>
    <div class="coverpage">
        <!-- Header -->
        <div class="header">
            <div class="logo-container {logo_position}">
                <img src="{school_logo}" alt="School Logo" class="school-logo" onerror="this.src='/exam.png'">
            </div>
            <div class="school-name">{school_name}</div>
            {f'<div class="class-title">{class_name}</div>' if class_name else ''}
            <div class="exam-title">{exam_title}</div>
            <div class="paper-title">{paper_name}</div>
            <div class="marking-scheme-label">*** MARKING SCHEME ***</div>
            
            <!-- Confidential Notice - positioned relative to header -->
            <div class="confidential-notice">
                <div class="confidential-text">CONFIDENTIAL - FOR EXAMINERS ONLY</div>
            </div>
        </div>
        
        <!-- Instructions Section - positioned in middle -->
        <div class="instructions">
            <div class="instructions-title"  style="border: 2px solid #000; padding: 15px; margin: 20px 0; flex-grow: 1; display: flex; flex-direction: column;">INSTRUCTIONS TO EXAMINERS</div>
            <ol style="margin-left: 20px; font-size: 12px; line-height: 1.6;">
                {instruction_items}
            </ol>
        </div>
    </div>
</body>
</html>
        """
        
        return html.strip()
    
    @staticmethod
    def generate_default_data(generated_paper, paper):
        # Get coverpage data from generated paper if available (to match question paper settings)
        saved_coverpage = getattr(generated_paper, 'coverpage_data', None) or {}
        
        # Generate paper name - avoid duplication if paper name already contains subject
        paper_name_upper = paper.name.upper()
        subject_name_upper = paper.subject.name.upper()
        
        if subject_name_upper in paper_name_upper:
            display_paper_name = paper_name_upper
        else:
            display_paper_name = f'{subject_name_upper} {paper_name_upper}'
        
        return {
            'school_name': saved_coverpage.get('school_name', 'EXAMINATION CENTRE'),
            'school_logo': saved_coverpage.get('school_logo', '/exam.png'),
            'logo_position': saved_coverpage.get('logo_position', 'center'),
            'class_name': saved_coverpage.get('class_name', ''),
            'exam_title': saved_coverpage.get('exam_title', 'END TERM EXAMINATION 2025'),
            'paper_name': display_paper_name,
            'total_questions': generated_paper.total_questions,
            'total_marks': generated_paper.total_marks,
            'time_allocation': format_time_allocation(paper.time_allocation),
            'instructions': saved_coverpage.get('instructions', []),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'candidate_name_field': saved_coverpage.get('candidate_name_field', True),
            'candidate_number_field': saved_coverpage.get('candidate_number_field', True),
            'date_field': saved_coverpage.get('date_field', True)
        }
