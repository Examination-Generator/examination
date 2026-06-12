from datetime import datetime
from api.cover.format_time import format_time_allocation


class MathematicsPaper1Coverpage:
    
    @staticmethod
    def generate_html(data):
        
        # Extract data with defaults
        school_name = data.get('school_name', 'EXAMINATION CENTRE')
        school_logo = data.get('school_logo', '/exam.png')
        logo_position = data.get('logo_position', 'center')
        class_name = data.get('class_name', '')
        exam_title = data.get('exam_title', 'END TERM EXAMINATION 2025')
        paper_name = data.get('paper_name', 'MATHEMATICS PAPER 1')
        
        # Section configuration
        section_1_questions = data.get('section_1_questions', 16)
        section_1_marks = data.get('section_1_marks', 50)
        section_2_questions = data.get('section_2_questions', 8)
        section_2_marks = data.get('section_2_marks', 50)
        total_marks = data.get('total_marks', 100)
        time_allocation = data.get('time_allocation', '2 HOURS 30 MINUTES')
        
        # Calculate total questions and pages
        total_questions = section_1_questions + section_2_questions
        total_pages = data.get('total_pages', 16)  # Default 16 printed pages for Math Paper 1
        
        instructions = data.get('instructions', [
            'Write your name and admission number in the spaces provided above.',
            'Sign and write the date of examination in the spaces provided above.',
            f'This paper consists of two sections: Section I and Section II.',
            f'Answer all the questions in Section I and only five questions in Section II.',
            f'Show all the steps in your calculations, giving your answers at each stage in the spaces provided below each question.',
            'Marks may be given for correct working even if the answer is wrong.',
            'Non-programmable silent electronic calculators and KNEC Mathematical tables may be used, except where stated otherwise.',
            'Candidates should check the question paper to ascertain that all the pages are printed as indicated and that no questions are missing.'
        ])
        
        exam_date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        show_name = data.get('candidate_name_field', True)
        show_number = data.get('candidate_number_field', True)
        show_date = data.get('date_field', True)
        
        # Generate marking grid for Mathematics Paper 1
        marking_grid_html = MathematicsPaper1Coverpage._generate_marking_grid(
            section_1_questions, section_1_marks,
            section_2_questions, section_2_marks,
            total_marks
        )
        
        # Build HTML
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{paper_name} - Coverpage</title>
    <style>
        @page {{
            size: A4;
            margin: 20mm;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Times New Roman', Times, serif;
            font-size: 12pt;
            line-height: 1.5;
            color: black;
            background: white;
        }}
        
        .coverpage {{
            width: 100%;
            min-height: 100vh;
            padding: 15mm;
            display: flex;
            flex-direction: column;
            page-break-after: always;
        }}
        
        /* Header Section */
        .header {{
            text-align: center;
            margin-bottom: 20px;
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
            max-width: 90px;
            max-height: 90px;
            object-fit: contain;
        }}
        
        .school-name {{
            font-size: 1.8rem;
            font-weight: bold;
            margin-bottom: 5px;
            text-transform: uppercase;
        }}
        
        .class-name {{
            font-size: 1.3rem;
            font-weight: bold;
            margin-bottom: 8px;
        }}
        
        .exam-title {{
            font-size: 1.4rem;
            font-weight: bold;
            margin-bottom: 15px;
            text-transform: uppercase;
        }}
        
        .paper-details {{
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 20px;
            margin-bottom: 5px;
        }}
        
        .paper-name {{
            font-size: 1.5rem;
            font-weight: bold;
            text-transform: uppercase;
        }}
        
        .time-allocation {{
            font-size: 1.3rem;
            margin-top: 5px;
        }}
        
        /* Candidate Info Section */
        .candidate-info {{
            margin: 20px 0;
            padding: 15px;
            border: none;
        }}
        
        .candidate-info-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr 1fr 1fr;
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
            min-width: 40px;
        }}
        
        .info-field {{
            flex: 1;
            border-bottom: 1px dotted black;
            min-height: 25px;
            padding: 2px 5px;
        }}
        
        /* Instructions Section */
        .instructions {{
            margin-bottom: 20px;
        }}
        
        .instructions-title {{
            font-weight: bold;
            font-size: 1.6rem;
            margin-bottom: 10px;
            text-decoration: underline;
        }}
        
        .instructions ol {{
            margin-left: 20px;
            font-size: 1.5rem;
            line-height: 1.6;
            font-style: italic;
        }}
        
        .instructions li {{
            margin-bottom: 8px;
        }}
        
        .instructions li.bold {{
            font-weight: bold;
        }}
        
        /* Marking Grid Section for Mathematics Paper 1 */
        .marking-grid-container {{
            margin-top: auto;
            padding-top: 20px;
        }}
        
        .grid-title {{
            font-weight: bold;
            font-size: 14px;
            margin-bottom: 12px;
            text-align: center;
            text-transform: uppercase;
        }}
        
        .marking-grid {{
            width: 100%;
            margin: 0 auto;
            border-collapse: collapse;
            border: 2px solid black;
        }}
        
        .marking-grid td {{
            border: 1px solid black;
            text-align: center;
            font-size: 11px;
            font-weight: bold;
            padding: 8px 4px;
            vertical-align: middle;
        }}
        
        .section-label-cell {{
            font-size: 12px;
            font-weight: bold;
            background-color: #f5f5f5;
            min-width: 80px;
        }}
        
        .question-number-cell {{
            min-width: 35px;
            width: 35px;
        }}
        
        .total-label-cell {{
            background-color: #e0e0e0;
            font-weight: bold;
            min-width: 80px;
        }}
        
        .grand-total-cell {{
            background-color: #d0d0d0;
            font-weight: bold;
            font-size: 12px;
            min-width: 100px;
        }}
        
        /* Print Styles */
        @media print {{
            body {{
                margin: 0;
                padding: 20mm;
            }}
            
            .coverpage {{
                page-break-after: always;
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
            {f'<div class="class-name">{class_name}</div>' if class_name else ''}
            <div class="exam-title">{exam_title}</div>
            
            <div class="paper-details">
                <span class="paper-name">{paper_name}</span>
            </div>
            
            <div class="time-allocation">{time_allocation}</div>
        </div>
        
        <!-- Candidate Information -->
        <div class="candidate-info">
            <div class="candidate-info-grid">
                {f'<div class="info-row-full"><span class="info-label">NAME:</span><div class="info-field"></div></div>' if show_name else ''}
                <div class="info-row-full" style="display: flex; gap: 20px;">
                    {f'<div class="info-row" style="flex: 1;"><span class="info-label">Adm No:</span><div class="info-field"></div></div>' if show_number else ''}
                    <div class="info-row" style="flex: 1;"><span class="info-label">Class:</span><div class="info-field"></div></div>
                    {f'<div class="info-row-item"><span class="info-label">DATE:</span><div class="info-field"></div></div>' if show_date else ''}
                    <div class="info-row" style="flex: 1;"><span class="info-label">Signature:</span><div class="info-field"></div></div>
                </div>
            </div>
        </div>
        
        <!-- Instructions -->
        <div class="instructions">
            <div class="instructions-title">Instructions to Candidates</div>
            <ol style="font-style: italic; list-style: none; counter-reset: list-counter; margin-left: 20px;">
"""
        
        # Add instructions
        for idx, instruction in enumerate(instructions, 1):
            # Make section-related instructions bold
            is_bold = 'section' in instruction.lower() or 'all' in instruction.lower() or 'five' in instruction.lower()
            class_attr = ' class="bold"' if is_bold else ''
            html += f'                <li style="counter-increment: list-counter;"{class_attr}>{instruction}</li>\n'
        
        html += f"""
            </ol>
        </div>
        
        <!-- Marking Grid -->
        <div class="marking-grid-container">
            <div class="grid-title">For Examiner's Use Only</div>
            {marking_grid_html}
        </div>
    </div>
</body>
</html>
"""
        
        return html
    
    @staticmethod
    def _generate_marking_grid(section_1_questions, section_1_marks, 
                               section_2_questions, section_2_marks, total_marks):
       
        
        grid_html = '<table class="marking-grid">\n'
        
        # Row 1: Section I label + Question numbers (1-16) + Total
        grid_html += '    <tr>\n'
        grid_html += f'        <td rowspan="2" class="section-label-cell">Section I</td>\n'
        for i in range(1, section_1_questions + 1):
            grid_html += f'        <td class="question-number-cell">{i}</td>\n'
        grid_html += f'        <td rowspan="2" class="total-label-cell">Total</td>\n'
        grid_html += '    </tr>\n'
        
        # Row 2: Answer boxes for Section I + Total box
        grid_html += '    <tr>\n'
        for i in range(section_1_questions):
            grid_html += '        <td class="question-number-cell">&nbsp;</td>\n'
        grid_html += '    </tr>\n'
        
        # Row 3: Section II label + Question numbers (17-24) + Total + Grand Total label
        grid_html += '    <tr>\n'
        grid_html += f'        <td rowspan="2" class="section-label-cell">Section II</td>\n'
        question_start = section_1_questions + 1
        for i in range(question_start, question_start + section_2_questions):
            grid_html += f'        <td class="question-number-cell">{i}</td>\n'
        grid_html += f'        <td rowspan="2" class="total-label-cell">Total</td>\n'
        grid_html += f'        <td rowspan="2" class="grand-total-cell">Grand Total</td>\n'
        grid_html += '    </tr>\n'
        
        # Row 4: Answer boxes for Section II + Total box (Grand Total box already added with rowspan)
        grid_html += '    <tr>\n'
        for i in range(section_2_questions):
            grid_html += '        <td class="question-number-cell">&nbsp;</td>\n'
        grid_html += '    </tr>\n'
        
        grid_html += '</table>\n'
        
        return grid_html
    
    @staticmethod
    def generate_default_coverpage_data(generated_paper, paper):
        # Generate paper name
        paper_name_upper = paper.name.upper()
        subject_name_upper = paper.subject.name.upper()
        
        if subject_name_upper in paper_name_upper:
            display_paper_name = paper_name_upper
        else:
            display_paper_name = f'{subject_name_upper} {paper_name_upper}'
        
        # Get section details from metadata if available
        metadata = getattr(generated_paper, 'metadata', {}) or {}
        section_1_questions = metadata.get('section_1_questions', 16)
        section_2_questions = metadata.get('section_2_questions', 8)
        
        # Calculate total pages dynamically
        # 1 page: Coverpage
        # Section I: 16 questions (approximately 5-6 pages, estimate 6 pages)
        # Section II: 8 questions (approximately 8-9 pages, estimate 9 pages)
        # Total: 1 + 6 + 9 = 16 pages
        section_1_pages = 6
        section_2_pages = 9
        total_pages = 1 + section_1_pages + section_2_pages
        
        return {
            'school_name': 'EXAMINATION CENTRE',
            'school_logo': '/exam.png',
            'logo_position': 'center',
            'class_name': '',
            'exam_title': 'END TERM EXAMINATION 2025',
            'paper_name': display_paper_name,
            'paper_type': 'Paper 1',
            'section_1_questions': section_1_questions,
            'section_1_marks': 50,
            'section_2_questions': section_2_questions,
            'section_2_marks': 50,
            'total_marks': generated_paper.total_marks or 100,
            'time_allocation': format_time_allocation(paper.time_allocation),
            'total_pages': total_pages,
            'instructions': [
                'Write your name and admission number in the spaces provided above.',
                'Sign and write the date of examination in the spaces provided above.',
                'This paper consists of two sections: Section I and Section II.',
                'Answer all the questions in Section I and only five questions in Section II.',
                'Show all the steps in your calculations, giving your answers at each stage in the spaces provided below each question.',
                'Marks may be given for correct working even if the answer is wrong.',
                'Non-programmable silent electronic calculators and KNEC Mathematical tables may be used, except where stated otherwise.',
                'Candidates should check the question paper to ascertain that all the pages are printed as indicated and that no questions are missing.'
            ],
            'date': datetime.now().strftime('%Y-%m-%d'),
            'candidate_name_field': True,
            'candidate_number_field': True,
            'date_field': True
        }
        

class MathematicsPaper2Coverpage:
    
    @staticmethod
    def generate_html(data):
        
        # Extract data with defaults
        school_name = data.get('school_name', 'EXAMINATION CENTRE')
        school_logo = data.get('school_logo', '/exam.png')
        logo_position = data.get('logo_position', 'center')
        class_name = data.get('class_name', '')
        exam_title = data.get('exam_title', 'END TERM EXAMINATION 2025')
        paper_name = data.get('paper_name', 'MATHEMATICS PAPER 2')
        
        # Section configuration (same as Paper 1)
        section_1_questions = data.get('section_1_questions', 16)
        section_1_marks = data.get('section_1_marks', 50)
        section_2_questions = data.get('section_2_questions', 8)
        section_2_marks = data.get('section_2_marks', 50)
        total_marks = data.get('total_marks', 100)
        time_allocation = data.get('time_allocation', '2 HOURS 30 MINUTES')
        
        # Calculate total questions and pages
        total_questions = section_1_questions + section_2_questions
        total_pages = data.get('total_pages', 16)  # Default 16 printed pages
        
        instructions = data.get('instructions', [
            'Write your name and admission number in the spaces provided above.',
            'Sign and write the date of examination in the spaces provided above.',
            f'This paper consists of two sections: Section I and Section II.',
            f'Answer all the questions in Section I and only five questions in Section II.',
            f'Show all the steps in your calculations, giving your answers at each stage in the spaces provided below each question.',
            'Marks may be given for correct working even if the answer is wrong.',
            'Non-programmable silent electronic calculators and KNEC Mathematical tables may be used, except where stated otherwise.',
            'Candidates should check the question paper to ascertain that all the pages are printed as indicated and that no questions are missing.'
        ])
        
        exam_date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        show_name = data.get('candidate_name_field', True)
        show_number = data.get('candidate_number_field', True)
        show_date = data.get('date_field', True)
        
        # Generate marking grid for Mathematics Paper 2 (same structure as Paper 1)
        marking_grid_html = MathematicsPaper1Coverpage._generate_marking_grid(
            section_1_questions, section_1_marks,
            section_2_questions, section_2_marks,
            total_marks
        )
        
        # Build HTML (reusing Paper 1 styles)
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{paper_name} - Coverpage</title>
    <style>
        @page {{
            size: A4;
            margin: 20mm;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Times New Roman', Times, serif;
            font-size: 12pt;
            line-height: 1.5;
            color: black;
            background: white;
        }}
        
        .coverpage {{
            width: 100%;
            min-height: 100vh;
            padding: 15mm;
            display: flex;
            flex-direction: column;
            page-break-after: always;
        }}
        
        /* Header Section */
        .header {{
            text-align: center;
            margin-bottom: 20px;
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
            max-width: 90px;
            max-height: 90px;
            object-fit: contain;
        }}
        
        .school-name {{
            font-size: 1.8rem;
            font-weight: bold;
            margin-bottom: 5px;
            text-transform: uppercase;
        }}
        
        .class-name {{
            font-size: 1.3rem;
            font-weight: bold;
            margin-bottom: 8px;
        }}
        
        .exam-title {{
            font-size: 1.4rem;
            font-weight: bold;
            margin-bottom: 15px;
            text-transform: uppercase;
        }}
        
        .paper-details {{
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 20px;
            margin-bottom: 5px;
        }}
        
        .paper-name {{
            font-size: 1.5rem;
            font-weight: bold;
            text-transform: uppercase;
        }}
        
        .time-allocation {{
            font-size: 1.3rem;
            margin-top: 5px;
        }}
        
        /* Candidate Info Section */
        .candidate-info {{
            margin: 20px 0;
            padding: 15px;
            border: none;
        }}
        
        .candidate-info-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr 1fr 1fr;
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
            min-width: 40px;
        }}
        
        .info-field {{
            flex: 1;
            border-bottom: 1px dotted black;
            min-height: 25px;
            padding: 2px 5px;
        }}
        
        /* Instructions Section */
        .instructions {{
            margin-bottom: 20px;
        }}
        
        .instructions-title {{
            font-weight: bold;
            font-size: 1.6rem;
            margin-bottom: 10px;
            text-decoration: underline;
        }}
        
        .instructions ol {{
            margin-left: 20px;
            font-size: 1.5rem;
            line-height: 1.6;
            font-style: italic;
        }}
        
        .instructions li {{
            margin-bottom: 8px;
        }}
        
        .instructions li.bold {{
            font-weight: bold;
        }}
        
        /* Marking Grid Section */
        .marking-grid-container {{
            margin-top: auto;
            padding-top: 20px;
        }}
        
        .grid-title {{
            font-weight: bold;
            font-size: 14px;
            margin-bottom: 12px;
            text-align: center;
            text-transform: uppercase;
        }}
        
        .marking-grid {{
            width: 100%;
            margin: 0 auto;
            border-collapse: collapse;
            border: 2px solid black;
        }}
        
        .marking-grid td {{
            border: 1px solid black;
            text-align: center;
            font-size: 11px;
            font-weight: bold;
            padding: 8px 4px;
            vertical-align: middle;
        }}
        
        .section-label-cell {{
            font-size: 12px;
            font-weight: bold;
            background-color: #f5f5f5;
            min-width: 80px;
        }}
        
        .question-number-cell {{
            min-width: 35px;
            width: 35px;
        }}
        
        .total-label-cell {{
            background-color: #e0e0e0;
            font-weight: bold;
            min-width: 80px;
        }}
        
        .grand-total-cell {{
            background-color: #d0d0d0;
            font-weight: bold;
            font-size: 12px;
            min-width: 100px;
        }}
        
        /* Print Styles */
        @media print {{
            body {{
                margin: 0;
                padding: 20mm;
            }}
            
            .coverpage {{
                page-break-after: always;
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
            {f'<div class="class-name">{class_name}</div>' if class_name else ''}
            <div class="exam-title">{exam_title}</div>
            
            <div class="paper-details">
                <span class="paper-name">{paper_name}</span>
            </div>
            
            <div class="time-allocation">{time_allocation}</div>
        </div>
        
        <!-- Candidate Information -->
        <div class="candidate-info">
            <div class="candidate-info-grid">
                {f'<div class="info-row-full"><span class="info-label">NAME:</span><div class="info-field"></div></div>' if show_name else ''}
                <div class="info-row-full" style="display: flex; gap: 20px;">
                    {f'<div class="info-row" style="flex: 1;"><span class="info-label">Adm No:</span><div class="info-field"></div></div>' if show_number else ''}
                    <div class="info-row" style="flex: 1;"><span class="info-label">Class:</span><div class="info-field"></div></div>
                    {f'<div class="info-row-item"><span class="info-label">DATE:</span><div class="info-field"></div></div>' if show_date else ''}
                    <div class="info-row" style="flex: 1;"><span class="info-label">Signature:</span><div class="info-field"></div></div>
                </div>
            </div>
        </div>
        
        <!-- Instructions -->
        <div class="instructions">
            <div class="instructions-title">Instructions to Candidates</div>
            <ol style="font-style: italic; list-style: none; counter-reset: list-counter; margin-left: 20px;">
"""
        
        # Add instructions
        for idx, instruction in enumerate(instructions, 1):
            # Make section-related instructions bold
            is_bold = 'section' in instruction.lower() or 'all' in instruction.lower() or 'five' in instruction.lower()
            class_attr = ' class="bold"' if is_bold else ''
            html += f'                <li style="counter-increment: list-counter;"{class_attr}>{instruction}</li>\n'
        
        html += f"""
            </ol>
        </div>
        
        <!-- Marking Grid -->
        <div class="marking-grid-container">
            <div class="grid-title">For Examiner's Use Only</div>
            {marking_grid_html}
        </div>
    </div>
</body>
</html>
"""
        
        return html
    
    @staticmethod
    def generate_default_coverpage_data(generated_paper, paper):
        """
        Generate default coverpage data for Mathematics Paper 2
        
        Args:
            generated_paper: GeneratedPaper instance
            paper: Paper instance
        
        Returns:
            dict: Default coverpage data for Math Paper 2
        """
        # Generate paper name
        paper_name_upper = paper.name.upper()
        subject_name_upper = paper.subject.name.upper()
        
        if subject_name_upper in paper_name_upper:
            display_paper_name = paper_name_upper
        else:
            display_paper_name = f'{subject_name_upper} {paper_name_upper}'
        
        # Get section details from metadata if available
        metadata = getattr(generated_paper, 'metadata', {}) or {}
        section_1_questions = metadata.get('section_1_questions', 16)
        section_2_questions = metadata.get('section_2_questions', 8)
        
        # Calculate total pages (similar to Paper 1)
        section_1_pages = 6
        section_2_pages = 9
        total_pages = 1 + section_1_pages + section_2_pages
        
        return {
            'school_name': 'EXAMINATION CENTRE',
            'school_logo': '/exam.png',
            'logo_position': 'center',
            'class_name': '',
            'exam_title': 'END TERM EXAMINATION 2025',
            'paper_name': display_paper_name,
            'paper_type': 'Paper 2',
            'section_1_questions': section_1_questions,
            'section_1_marks': 50,
            'section_2_questions': section_2_questions,
            'section_2_marks': 50,
            'total_marks': generated_paper.total_marks or 100,
            'time_allocation': format_time_allocation(paper.time_allocation),
            'total_pages': total_pages,
            'instructions': [
                'Write your name and admission number in the spaces provided above.',
                'Sign and write the date of examination in the spaces provided above.',
                'This paper consists of two sections: Section I and Section II.',
                'Answer all the questions in Section I and only five questions in Section II.',
                'Show all the steps in your calculations, giving your answers at each stage in the spaces provided below each question.',
                'Marks may be given for correct working even if the answer is wrong.',
                'Non-programmable silent electronic calculators and KNEC Mathematical tables may be used, except where stated otherwise.',
                'Candidates should check the question paper to ascertain that all the pages are printed as indicated and that no questions are missing.'
            ],
            'date': datetime.now().strftime('%Y-%m-%d'),
            'candidate_name_field': True,
            'candidate_number_field': True,
            'date_field': True
        }
        