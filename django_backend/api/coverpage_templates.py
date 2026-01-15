"""
Coverpage Templates for KCSE Examination Papers
Generates professional coverpages with dynamic marking grids
"""

from datetime import datetime


def format_time_allocation(minutes):
    """
    Convert time in minutes to human-readable hours format
    
    Args:
        minutes (int): Time in minutes
    
    Returns:
        str: Formatted time string (e.g., "2 hours", "1 hour 30 minutes", "45 minutes")
    """
    if minutes >= 60:
        hours = minutes // 60
        remaining_minutes = minutes % 60
        if remaining_minutes == 0:
            return f"{hours} {'HOUR' if hours == 1 else 'HOURS'}"
        else:
            return f"{hours} {'HOUR' if hours == 1 else 'HOURS'} {remaining_minutes} MINUTES"
    else:
        return f"{minutes} MINUTES"


def generate_marking_table(total_questions):
    """
    Generate the marking grid HTML based on number of questions
    
    The grid layout (matching KCSE format):
    - Row 1: Questions 1-16 with answer boxes
    - SPACE/GAP between rows
    - Row 2: Questions 17-32 with answer boxes + EMPTY SPACE + Grand Total (inline with row 2)
    
    Args:
        total_questions (int): Total number of questions
    
    Returns:
        str: HTML for marking grid table
    """
    
    # Determine how many questions per row
    # Maximum 16 questions in first row, rest in second row
    first_row_count = min(16, total_questions)
    second_row_count = max(0, total_questions - 16)
    
    # Build first row (question numbers)
    first_row_html = '<tr>\n'
    for i in range(1, first_row_count + 1):
        first_row_html += f'    <td style="min-width: 35px; width: 35px; border-right: 2px solid black; border-bottom: 2px solid black; text-align: center; padding: 8px;">{i}</td>\n'
    first_row_html += '</tr>\n'
    
    # Build first row (answer boxes)
    first_row_boxes = '<tr>\n'
    for i in range(first_row_count):
        first_row_boxes += '    <td style="min-width: 35px; width: 35px; border-right: 2px solid black; border-bottom: 2px solid black; padding: 8px;">&nbsp;</td>\n'
    first_row_boxes += '</tr>\n'
    
    # Build second row if needed
    second_row_html = ''
    second_row_boxes = ''
    
    # Always show second row (even if no questions)
    # Second row question numbers (with spacing)
    second_row_html = '<tr class="row-with-spacing" style="border-top: 2px solid black; padding-top: 8px;">\n'
    
    # Add question numbers for second row (17 onwards)
    for i in range(17, 17 + second_row_count):
        second_row_html += f'    <td style="min-width: 35px; width: 35px; border-right: 2px solid black; border-bottom: 2px solid black; text-align: center; padding: 8px;">{i}</td>\n'
    
    # Fill remaining cells in second row with empty cells (up to 16 total cells)
    remaining_cells = 16 - second_row_count
    for i in range(remaining_cells):
        second_row_html += '    <td class="empty-question-cell" style="min-width: 35px; width: 35px;background-color: white; border: none !important;">&nbsp;</td>\n'
    
    # Add empty gap cell before Grand Total
    second_row_html += '    <td class="gap-cell" style="border: none !important; background-color: white;min-width: 15px; width: 15px;">&nbsp;</td>\n'
    
    # Add Grand Total cell (spans 2 rows - question numbers and answer boxes)
    second_row_html += f'    <td rowspan="2" class="grand-total-cell" style="background-color: #f0f0f0; font-size: 10px; font-weight: bold; border: 2px solid black; padding: 5px 10px; min-width: 80px;">Grand Total</td>\n'
    second_row_html += f'    <td rowspan="2" class="total-box" style="min-width: 60px; width: 60px; min-height: 60px; border: 2px solid black; background-color: white;">&nbsp;</td>\n'
    second_row_html += '</tr>\n'
    
    # Second row answer boxes
    second_row_boxes = '<tr>\n'
    
    # Add answer boxes for actual questions
    for i in range(second_row_count):
        second_row_boxes += '    <td style="min-width: 35px; width: 35px;  border-right: 2px solid black; padding: 8px;">&nbsp;</td>\n'
    
    # Fill remaining answer boxes
    for i in range(remaining_cells):
        second_row_boxes += '    <td class="empty-question-cell" style="min-width: 35px; width: 35px;background-color: white; padding: 8px; border: none !important;">&nbsp;</td>\n'
    
    # Add empty gap cell (matching the one above)
    second_row_boxes += '    <td class="gap-cell" style="border: none !important; background-color: white;min-width: 15px; width: 15px;">&nbsp;</td>\n'
    # Grand Total cells already added with rowspan
    second_row_boxes += '</tr>\n'
    
    # Combine all rows into table
    grid_html = f"""
    <table class="marking-grid" style="width: 100%; border-collapse: collapse; border: 2px solid black;">
        {first_row_html}
        {first_row_boxes}
        {second_row_html}
        {second_row_boxes}
    </table>
    """
    
    return grid_html



class BiologyPaper1Coverpage:
    """
    Biology Paper 1 Coverpage Template
    Includes dynamic marking grid based on question count
    """
    
    @staticmethod
    def generate_html(data):
        """
        Generate HTML for Biology Paper 1 coverpage
        
        Args:
            data (dict): Coverpage data with keys:
                - school_name: Name of the school
                - school_logo: Base64 encoded logo or URL
                - exam_title: e.g., "END TERM 3 EXAMINATION 2025"
                - paper_name: e.g., "BIOLOGY PAPER 1"
                - total_questions: Number of questions in the paper
                - total_marks: Total marks for the paper
                - time_allocation: Time in minutes
                - instructions: List of instruction strings
                - date: Exam date (optional)
                - candidate_name_field: Show name field (default: True)
                - candidate_number_field: Show admission number field (default: True)
                - date_field: Show date field (default: True)
        
        Returns:
            str: HTML content for coverpage
        """
        
        # Extract data with defaults
        school_name = data.get('school_name', 'EXAMINATION CENTRE')
        school_logo = data.get('school_logo', '/exam.png')
        logo_position = data.get('logo_position', 'center')  # left, center, right
        class_name = data.get('class_name', '')
        exam_title = data.get('exam_title', 'END TERM EXAMINATION 2025')
        paper_name = data.get('paper_name', 'BIOLOGY PAPER 1')
        total_questions = data.get('total_questions', 25)
        total_marks = data.get('total_marks', 80)
        time_allocation = data.get('time_allocation', '2 hours')
        
        # Calculate total pages: 1 coverpage + question pages (3-4 questions per page)
        total_pages = 1 + ((total_questions + 2) // 3)  # Coverpage + question pages
        
        instructions = data.get('instructions', [
            'Write your name and admission number in the spaces provided above.',
            'Sign and write the date of examination in the spaces provided above.',
            'Answer all the questions in this question paper.',
            'All answers must be written in the spaces provided.',
            f'This paper consists of {total_pages} printed pages.',
            'Candidates should check the question paper to ascertain that all the pages are printed as indicated and that no questions are missing.',
            'Candidates should answer the questions in English.'
        ])
        exam_date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        show_name = data.get('candidate_name_field', True)
        show_number = data.get('candidate_number_field', True)
        show_date = data.get('date_field', True)
        
        # Generate marking grid
        marking_grid_html = generate_marking_table(total_questions)
        
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
            position: relative;
        }}
        
        .coverpage {{
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}
        
        /* Header Section */
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
            margin-bottom: 10px;
        }}
        
        .paper-details {{
            font-size: 14px;
            margin-bottom: 20px;
        }}
        
        /* Candidate Information Section */
        .candidate-info {{
            border: none;
            padding: 15px;
            margin-bottom: 20px;
        }}
        
        .info-grid {{
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
            font-size: 13px;
            margin-bottom: 10px;
            text-align: center;
        }}
        
        .marking-grid {{
            width: 100%;
            border-collapse: collapse;
            border: 1px solid black;
        }}
        
        .marking-grid td {{
            border: 1px solid black;
            text-align: center;
            font-size: 10px;
            font-weight: bold;
            padding: 8px 4px;
            height: 30px;
        }}
        
        .question-number {{
            min-width: 35px;
            width: 35px;
        }}
        
        /* Empty question cells (shown but no number) */
        .empty-question-cell {{
            min-width: 35px;
            width: 35px;
            background-color: white;
            border: none !important;
        }}
        
        /* Add spacing before second row */
        .row-with-spacing td {{
            border-top: 2px solid black;
            padding-top: 8px;
        }}
        
        /* Override border-top for empty and gap cells in spacing row */
        .row-with-spacing .empty-question-cell,
        .row-with-spacing .gap-cell {{
            border-top: none !important;
        }}
        
        /* Gap cell between questions and Grand Total */
        .gap-cell {{
            border-right: none !important;
            border-left: none !important;
            border-bottom: none !important;
            background-color: white;
            min-width: 15px;
            width: 15px;
        }}
        
        .grand-total-cell {{
            background-color: #f0f0f0;
            font-size: 10px;
            font-weight: bold;
            border: 2px solid black;
            padding: 5px 10px;
            min-width: 80px;
        }}
        
        .total-box {{
            min-width: 60px;
            width: 60px;
            min-height: 60px;
            border: 2px solid black;
            background-color: white;
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
            {f'<div class="class-title">{class_name}</div>' if class_name else ''}
            <div class="exam-title">{exam_title}</div>
            <div class="paper-title">{paper_name}</div>
            <div class="paper-details">
                <div>Time: {time_allocation}</div>
            </div>
        </div>
        
        <!-- Candidate Information -->
        <div class="candidate-info">
            <div class="candidate-info-grid">
                {f'<div class="info-row-full"><span class="info-label">NAME:</span><div class="info-field"></div></div>' if show_name else ''}
                <div class="info-row-grid">
                    {f'<div class="info-row-item"><span class="info-label">ADM NO:</span><div class="info-field"></div></div>' if show_number else ''}
                    <div class="info-row-item"><span class="info-label">CLASS:</span><div class="info-field"></div></div>
                </div>
                <div class="info-row-grid">
                    {f'<div class="info-row-item"><span class="info-label">DATE:</span><div class="info-field"></div></div>' if show_date else ''}
                    <div class="info-row-item"><span class="info-label">SIGNATURE:</span><div class="info-field"></div></div>
                </div>
            </div>
        </div>
        
        <!-- Instructions -->
        <div class="instructions">
            <div class="instructions-title">INSTRUCTIONS TO CANDIDATES</div>
            <ol style="font-size: 12px; line-height: 1.6; font-style:italic; list-style: none; counter-reset: list-counter; margin-left: 20px;">
                {''.join([f'<li style="counter-increment: list-counter;" class="{"bold" if idx >= 4 else ""}">{instruction}</li>' for idx, instruction in enumerate(instructions)])}
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
    def _generate_marking_grid(total_questions):
        """
        Generate the marking grid HTML based on number of questions
        
        The grid layout (matching KCSE format):
        - Row 1: Questions 1-16 with answer boxes
        - SPACE/GAP between rows
        - Row 2: Questions 17-32 with answer boxes + EMPTY SPACE + Grand Total (inline with row 2)
        
        Args:
            total_questions (int): Total number of questions
        
        Returns:
            str: HTML for marking grid table
        """
        
        # Determine how many questions per row
        # Maximum 16 questions in first row, rest in second row
        first_row_count = min(16, total_questions)
        second_row_count = max(0, total_questions - 16)
        
        # Build first row (question numbers)
        first_row_html = '<tr>\n'
        for i in range(1, first_row_count + 1):
            first_row_html += f'    <td class="question-number">{i}</td>\n'
        first_row_html += '</tr>\n'
        
        # Build first row (answer boxes)
        first_row_boxes = '<tr>\n'
        for i in range(first_row_count):
            first_row_boxes += '    <td class="question-number">&nbsp;</td>\n'
        first_row_boxes += '</tr>\n'
        
        # Build second row if needed
        second_row_html = ''
        second_row_boxes = ''
        
        # Always show second row (even if no questions)
        # Second row question numbers (with spacing)
        second_row_html = '<tr class="row-with-spacing" >\n'
        
        # Add question numbers for second row (17 onwards)
        for i in range(17, 17 + second_row_count):
            second_row_html += f'    <td class="question-number">{i}</td>\n'
        
        # Fill remaining cells in second row with empty cells (up to 16 total cells)
        remaining_cells = 16 - second_row_count
        for i in range(remaining_cells):
            second_row_html += '    <td class="empty-question-cell" style="border: none;">&nbsp;</td>\n'
        
        # # Add empty gap cell before Grand Total
        # second_row_html += '    <td class="gap-cell">&nbsp;</td>\n'
        
        # Add Grand Total cell (spans 2 rows - question numbers and answer boxes)
        second_row_html += f'    <td rowspan="2" class="grand-total-cell">Grand Total</td>\n'
        second_row_html += f'    <td rowspan="2" class="total-box">&nbsp;</td>\n'
        second_row_html += '</tr>\n'
        
        # Second row answer boxes
        second_row_boxes = '<tr>\n'
        
        # Add answer boxes for actual questions
        for i in range(second_row_count):
            second_row_boxes += '    <td class="question-number">&nbsp;</td>\n'
        
        # Fill remaining answer boxes
        for i in range(remaining_cells):
            second_row_boxes += '    <td class="empty-question-cell" style="border: none;">&nbsp;</td>\n'
        
        # # Add empty gap cell (matching the one above)
        # second_row_boxes += '    <td class="gap-cell">&nbsp;</td>\n'
        # Grand Total cells already added with rowspan
        second_row_boxes += '</tr>\n'
        
        # Combine all rows into table
        grid_html = f"""
        <table class="marking-grid">
            {first_row_html}
            {first_row_boxes}
            {second_row_html}
            {second_row_boxes}
        </table>
        """
        
        return grid_html
    
    @staticmethod
    def generate_default_coverpage_data(generated_paper, paper):
        """
        Generate default coverpage data for a generated paper
        
        Args:
            generated_paper: GeneratedPaper instance
            paper: Paper instance
        
        Returns:
            dict: Default coverpage data
        """
        # Calculate total pages: 1 coverpage + question pages (3-4 questions per page)
        total_pages = 1 + ((generated_paper.total_questions + 2) // 3)
        
        # Generate paper name - avoid duplication if paper name already contains subject
        paper_name_upper = paper.name.upper()
        subject_name_upper = paper.subject.name.upper()
        
        if subject_name_upper in paper_name_upper:
            # Paper name already contains subject (e.g., "Biology Paper I")
            display_paper_name = paper_name_upper
        else:
            # Combine subject and paper name (e.g., "BIOLOGY" + "PAPER I")
            display_paper_name = f'{subject_name_upper} {paper_name_upper}'
        
        return {
            'school_name': 'EXAMINATION CENTRE',
            'school_logo': '/exam.png',
            'logo_position': 'center',
            'class_name': '',
            'exam_title': 'END TERM EXAMINATION 2025',
            'paper_name': display_paper_name,
            'total_questions': generated_paper.total_questions,
            'total_marks': generated_paper.total_marks,
            'time_allocation': format_time_allocation(paper.time_allocation),
            'instructions': [
                'Write your name and admission number in the spaces provided above.',
                'Sign and write the date of examination in the spaces provided above.',
                'Answer ALL questions in the spaces provided in this booklet.',
                'All working MUST be clearly shown where necessary.',
                f'This paper consists of {total_pages} printed pages.',
                'Candidates should check the question paper to ascertain that all the pages are printed as indicated and that no questions are missing.',
                'Candidates should check the question paper to ascertain that all pages are printed as indicated and that no questions are missing.'
            ],
            'date': datetime.now().strftime('%Y-%m-%d'),
            'candidate_name_field': True,
            'candidate_number_field': True,
            'date_field': True
        }



class BiologyPaper2Coverpage:
    """
    Biology Paper 2 Coverpage Template
    Includes sectioned marking grid (Section A and Section B)
    """
    
    @staticmethod
    def generate_html(data):
        """
        Generate HTML for Biology Paper 2 coverpage
        
        Args:
            data (dict): Coverpage data with keys:
                - school_name: Name of the school
                - school_logo: Base64 encoded logo or URL
                - exam_title: e.g., "END TERM 3 EXAMINATION 2025"
                - paper_name: e.g., "BIOLOGY PAPER 2"
                - section_a_questions: Number of questions in Section A (default: 5)
                - section_a_marks: Marks per question in Section A (default: 8)
                - section_b_questions: Number of questions in Section B (default: 3)
                - section_b_marks: Marks per question in Section B (default: 20)
                - total_marks: Total marks for the paper (default: 80)
                - time_allocation: Time in minutes
                - instructions: List of instruction strings
                - date: Exam date (optional)
                - candidate_name_field: Show name field (default: True)
                - candidate_number_field: Show admission number field (default: True)
                - date_field: Show date field (default: True)
        
        Returns:
            str: HTML content for coverpage
        """
        
        # Extract data with defaults
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
        time_allocation = data.get('time_allocation', '2 hours')
        
        # Calculate total questions and pages
        total_questions = section_a_questions + section_b_questions
        total_pages = data.get('total_pages', 12)  # Default 12 printed pages for Paper 2
        
        instructions = data.get('instructions', [
            'Write your name and admission number in the spaces provided above.',
            'Sign and write the date of examination in the spaces provided above.',
            f'This paper consists of two sections: A and B.',
            f'Answer all questions in section A answer question 6 (compulsory) and either question 7 or 8 in the spaces provided after question 8.',
            f'This paper consists of {total_pages} printed pages.',
            'Candidates should check the question paper to ascertain that all the pages are printed as indicated and that no questions are missing.',
            'Candidates should answer the questions in English.'
        ])
        
        exam_date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        show_name = data.get('candidate_name_field', True)
        show_number = data.get('candidate_number_field', True)
        show_date = data.get('date_field', True)
        
        # Generate marking grid for Paper 2
        marking_grid_html = BiologyPaper2Coverpage._generate_marking_grid(
            section_a_questions, section_a_marks,
            section_b_questions, section_b_marks,
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
        
        .paper-code {{
            font-size: 1.2rem;
            font-weight: normal;
        }}
        
        .time-allocation {{
            font-size: 1.3rem;
            margin-top: 5px;
        }}
        
        /* Candidate Info Section */
        .candidate-info {{
            margin: 20px 0;
            padding: 15px;
            border: 2px solid black;
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
        
        /* Marking Grid Section for Paper 2 */
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
            width: 70%;
            margin: 0 auto;
            border-collapse: collapse;
            border: 2px solid black;
        }}
        
        .marking-grid th,
        .marking-grid td {{
            border: 1px solid black;
            text-align: center;
            font-size: 12px;
            font-weight: normal;
            padding: 10px 8px;
        }}
        
        .marking-grid th {{
            background-color: #e8e8e8;
            font-weight: bold;
            font-size: 12px;
        }}
        
        .section-label {{
            font-size: 13px;
            font-weight: bold;
            vertical-align: middle;
            background-color: #f5f5f5;
        }}
        
        .total-row {{
            background-color: #d9d9d9;
            font-weight: bold;
            font-size: 13px;
        }}
        
        .total-row td {{
            font-weight: bold;
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
                {f'<div class="info-row"><span class="info-label">ADM NO:</span><div class="info-field"></div></div>' if show_number else ''}
                {f'<div class="info-row"><span class="info-label">DATE:</span><div class="info-field"></div></div>' if show_date else ''}
                <div class="info-row"><span class="info-label">Sign:</span><div class="info-field"></div></div>
            </div>
        </div>
        
        <!-- Instructions -->
        <div class="instructions">
            <div class="instructions-title">Instructions to candidates</div>
            <ol type="i">
"""
        
        # Add instructions
        for idx, instruction in enumerate(instructions, 1):
            # Make instruction (c) and (d) bold (typically sections and answer requirements)
            is_bold = '(c)' in instruction.lower() or '(d)' in instruction.lower() or 'section' in instruction.lower()
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
    def _generate_marking_grid(section_a_questions, section_a_marks, 
                               section_b_questions, section_b_marks, total_marks):
        """
        Generate marking grid HTML for Biology Paper 2
        
        Paper 2 has sectioned marking grid:
        - Section A: Multiple questions with same marks each
        - Section B: Multiple questions with same marks each
        - Total Score row at bottom
        
        Args:
            section_a_questions (int): Number of questions in Section A
            section_a_marks (int): Marks per question in Section A
            section_b_questions (int): Number of questions in Section B
            section_b_marks (int): Marks per question in Section B
            total_marks (int): Total marks for the paper
        
        Returns:
            str: HTML for marking grid
        """
        
        grid_html = '<table class="marking-grid">\n'
        grid_html += '    <thead>\n'
        grid_html += '        <tr>\n'
        grid_html += '            <th>Section</th>\n'
        grid_html += '            <th>Question</th>\n'
        grid_html += '            <th>Maximum Score</th>\n'
        grid_html += '            <th>Candidate\'s Score</th>\n'
        grid_html += '        </tr>\n'
        grid_html += '    </thead>\n'
        grid_html += '    <tbody>\n'
        
        # Section A rows
        for i in range(1, section_a_questions + 1):
            if i == 1:
                # First row of Section A with rowspan
                grid_html += f'        <tr>\n'
                grid_html += f'            <td rowspan="{section_a_questions}" class="section-label">A</td>\n'
                grid_html += f'            <td>{i}</td>\n'
                grid_html += f'            <td>{section_a_marks}</td>\n'
                grid_html += f'            <td>&nbsp;</td>\n'
                grid_html += f'        </tr>\n'
            else:
                grid_html += f'        <tr>\n'
                grid_html += f'            <td>{i}</td>\n'
                grid_html += f'            <td>{section_a_marks}</td>\n'
                grid_html += f'            <td>&nbsp;</td>\n'
                grid_html += f'        </tr>\n'
        
        # Section B rows
        question_number = section_a_questions + 1
        for i in range(section_b_questions):
            if i == 0:
                # First row of Section B with rowspan
                grid_html += f'        <tr>\n'
                grid_html += f'            <td rowspan="{section_b_questions}" class="section-label">B</td>\n'
                grid_html += f'            <td>{question_number}</td>\n'
                grid_html += f'            <td>{section_b_marks}</td>\n'
                grid_html += f'            <td>&nbsp;</td>\n'
                grid_html += f'        </tr>\n'
            else:
                grid_html += f'        <tr>\n'
                grid_html += f'            <td>{question_number}</td>\n'
                grid_html += f'            <td>{section_b_marks}</td>\n'
                grid_html += f'            <td>&nbsp;</td>\n'
                grid_html += f'        </tr>\n'
            question_number += 1
        
        # Total Score row
        grid_html += '        <tr class="total-row">\n'
        grid_html += '            <td colspan="2">Total Score</td>\n'
        grid_html += f'            <td>{total_marks}</td>\n'
        grid_html += '            <td>&nbsp;</td>\n'
        grid_html += '        </tr>\n'
        
        grid_html += '    </tbody>\n'
        grid_html += '</table>\n'
        
        return grid_html
    
    @staticmethod
    def generate_default_coverpage_data(generated_paper, paper):
        """
        Generate default coverpage data for Biology Paper 2
        
        Args:
            generated_paper: GeneratedPaper instance
            paper: Paper instance
        
        Returns:
            dict: Default coverpage data for Paper 2
        """
        # Generate paper name
        paper_name_upper = paper.name.upper()
        subject_name_upper = paper.subject.name.upper()
        
        if subject_name_upper in paper_name_upper:
            display_paper_name = paper_name_upper
        else:
            display_paper_name = f'{subject_name_upper} {paper_name_upper}'
        
        # Calculate total pages dynamically
        # 1 page: Coverpage
        # Section A: 5 questions (approximately 2-3 pages, estimate 3 pages)
        # Section B: 3 questions (only 2 pages since Q7 and Q8 have no answer spaces)
        # Answer lines: 100 lines = approximately 4 pages (25 lines per page)
        # Total: 1 + 3 + 2 + 4 = 10 pages
        section_a_pages = 3
        section_b_questions_pages = 2  # Q7 and Q8 don't have answer spaces
        answer_lines_pages = 4  # 100 / 25 lines per page
        total_pages = 1 + section_a_pages + section_b_questions_pages + answer_lines_pages
        
        return {
            'school_name': 'EXAMINATION CENTRE',
            'school_logo': '/exam.png',
            'logo_position': 'center',
            'class_name': '',
            'exam_title': 'END TERM EXAMINATION 2025',
            'paper_name': display_paper_name,
            'paper_type': 'Paper 2',
            'section_a_questions': 5,
            'section_a_marks': 8,
            'section_b_questions': 3,
            'section_b_marks': 20,
            'total_marks': generated_paper.total_marks or 80,
            'time_allocation': format_time_allocation(paper.time_allocation),
            'total_pages': total_pages,
            'instructions': [
                'Write your name and admission number in the spaces provided above.',
                'Sign and write the date of examination in the spaces provided above.',
                'This paper consists of two sections: A and B.',
                'Answer all questions in section A answer question 6 (compulsory) and either question 7 or 8 in the spaces provided after question 8.',
                f'This paper consists of {total_pages} printed pages.',
                'Candidates should check the question paper to ascertain that all the pages are printed as indicated and that no questions are missing.',
                'Candidates should answer the questions in English.'
            ],
            'date': datetime.now().strftime('%Y-%m-%d'),
            'candidate_name_field': True,
            'candidate_number_field': True,
            'date_field': True
        }


class BiologyPaper3Coverpage:
    """
    Biology Paper 3 Coverpage Template
    For papers that require a Paper 3 layout. Uses the same styles as Paper 2
    by default but allows separate defaults so the UI can select Paper III.
    """

    @staticmethod
    def generate_html(data):
        # Reuse BiologyPaper2Coverpage HTML structure but force the paper name
        data = dict(data)
        data['paper_name'] = data.get('paper_name', 'BIOLOGY PAPER 3')
        # Use BiologyPaper2Coverpage renderer for consistent styling
        return BiologyPaper2Coverpage.generate_html(data)

    @staticmethod
    def generate_default_coverpage_data(generated_paper, paper):
        # Start from Paper 2 defaults then adjust for Paper 3
        base = BiologyPaper2Coverpage.generate_default_coverpage_data(generated_paper, paper)
        base = dict(base)
        base['paper_name'] = base.get('paper_name', '').replace('PAPER 2', 'PAPER 3') if 'PAPER 2' in base.get('paper_name', '') else f"{paper.subject.name.upper()} {paper.name.upper()}"
        base['paper_type'] = 'Paper 3'
        # Adjust total_pages conservatively if needed
        base['total_pages'] = base.get('total_pages', 10)
        return base


class BiologyPaper2MarkingSchemeCoverpage:
    """
    Biology Paper 2 Marking Scheme Coverpage Template
    Uses sectioned marking grid (Section A and Section B) - same as question paper
    """
    
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
            f'This marking scheme consists of {total_pages} printed pages.',
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
        """
        Generate default marking scheme coverpage data (matches question paper coverpage structure)
        
        Args:
            generated_paper: GeneratedPaper instance
            paper: Paper instance
        
        Returns:
            dict: Default marking scheme coverpage data
        """
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


class PhysicsPaper1Coverpage:
    """
    Physics Paper 1 Coverpage Template
    Includes sectioned marking grid (Section A and Section B)
    """
    
    @staticmethod
    def generate_html(data):
        """
        Generate HTML for Physics Paper 1 coverpage
        """
        school_name = data.get('school_name', 'EXAMINATION CENTRE')
        school_logo = data.get('school_logo', '/exam.png')
        logo_position = data.get('logo_position', 'center')
        class_name = data.get('class_name', '')
        exam_title = data.get('exam_title', 'END TERM EXAMINATION 2025')
        paper_name = data.get('paper_name', 'PHYSICS PAPER 1')
        
        section_a_questions = data.get('section_a_questions', 13)
        section_a_marks = data.get('section_a_marks', 25)
        section_b_questions = data.get('section_b_questions', 5)
        section_b_marks = data.get('section_b_marks', 55)
        total_marks = data.get('total_marks', 80)
        total_questions = section_a_questions + section_b_questions
        total_pages = data.get('total_pages', 12)
        time_allocation = data.get('time_allocation', '2 HOURS 30 MINUTES')
        
        instructions = data.get('instructions', [
            'Write your name and admission number in the spaces provided above.',
            'Sign and write the date of examination in the spaces provided above.',
            'This paper consists of two sections: A and B.',
            'Answer ALL questions in section A and ANY FIVE questions in section B.',
            f'Show all the steps in your calculations, giving your answers at each stage in the spaces provided below each question.',
            'Marks may be given for correct working even if the answer is wrong.',
            'Non-programmable silent electronic calculators and KNEC Mathematical tables may be used, except where stated otherwise.',
            f'This paper consists of {total_pages} printed pages.',
            'Candidates should check the question paper to ascertain that all the pages are printed as indicated and that no questions are missing.'
        ])
        
        exam_date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        show_name = data.get('candidate_name_field', True)
        show_number = data.get('candidate_number_field', True)
        show_date = data.get('date_field', True)
        show_class = data.get('class_field', True)
        
        # Generate marking grid for Physics Paper 1
        marking_grid_html = PhysicsPaper1Coverpage._generate_marking_grid(
            section_a_questions, section_a_marks,
            section_b_questions, section_b_marks,
            total_marks
        )
        
        # Build HTML (reusing Biology Paper 2 styles)
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
            border:none;
        }}
        
        .grid-title {{
            font-weight: bold;
            font-size: 14px;
            margin-bottom: 12px;
            text-align: center;
            text-transform: uppercase;
        }}
        
        .marking-grid {{
            width: 70%;
            margin: 0 auto;
            border-collapse: collapse;
        }}
        
        .marking-grid th,
        .marking-grid td {{
            border: 1px solid black;
            text-align: center;
            font-size: 12px;
            font-weight: normal;
            padding: 10px 8px;
        }}
        
        .marking-grid th {{
            background-color: #e8e8e8;
            font-weight: bold;
            font-size: 12px;
        }}
        
        .section-label {{
            font-size: 13px;
            font-weight: bold;
            vertical-align: middle;
            background-color: #f5f5f5;
        }}
        
        .total-row {{
            background-color: #d9d9d9;
            font-weight: bold;
            font-size: 13px;
        }}
        
        .total-row td {{
            font-weight: bold;
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
                <div class="info-row-grid">
                    {f'<div class="info-row-item"><span class="info-label">ADM NO:</span><div class="info-field"></div></div>' if show_number else ''}
                    <div class="info-row-item"><span class="info-label">CLASS:</span><div class="info-field"></div></div>
                </div>
                <div class="info-row-grid">
                    {f'<div class="info-row-item"><span class="info-label">DATE:</span><div class="info-field"></div></div>' if show_date else ''}
                    <div class="info-row-item"><span class="info-label">SIGNATURE:</span><div class="info-field"></div></div>
                </div>
            </div>
        </div>
        
        <!-- Instructions -->
        <div class="instructions">
            <div class="instructions-title">Instructions to candidates</div>
            <ol style="font-style: italic; font-size: 1.5rem; line-height: 1.6; list-style: none; counter-reset: list-counter; margin-left: 20px;">
"""
        
        # Add instructions
        for idx, instruction in enumerate(instructions, 1):
            is_bold = 'section' in instruction.lower() or 'ALL' in instruction or 'ANY FIVE' in instruction
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
    def _generate_marking_grid(section_a_questions, section_a_marks, 
                               section_b_questions, section_b_marks, total_marks):
        """
        Generate marking grid HTML for Physics Paper 1
        Similar to Biology Paper 2 grid structure
        """
        
        html = f"""
            <table class="marking-grid" style="border: none; border-collapse: collapse;">
                <thead>
                    <tr>
                        <th style="background-color: white;">Section</th>
                        <th style="background-color: white;">Question</th>
                        <th style="background-color: white;">Maximum Score</th>
                        <th style="background-color: white;">Candidate's Score</th>
                    </tr>
                </thead>
                <tbody>
                    <!-- Section A -->
                    <tr>
                        <td class="section-label" rowspan="2">A</td>
                        <td>1-{section_a_questions}</td>
                        <td>{section_a_marks}</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td colspan="3" style="border-top: none; border-right: 1px solid black; "></td>
                    </tr>
                    
                    <!-- Section B -->
                    <tr>
                        <td class="section-label" rowspan="7">B</td>
                        <td>14</td>
                        <td>11</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td>15</td>
                        <td>10</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td>16</td>
                        <td>10</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td>17</td>
                        <td>12</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td>18</td>
                        <td>12</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td colspan="3"></td>
                    </tr>
                    
                    <!-- Total -->
                    <tr class="total-row">
                        <td style="background-color: white;">Total Score</td>
                        <td style="background-color: white;">{total_marks}</td>
                        <td style="background-color: white;"></td>
                    </tr>
                </tbody>
            </table>
"""
        
        return html
    
    @staticmethod
    def generate_default_coverpage_data(generated_paper, paper):
        """
        Generate default coverpage data for Physics Paper 1
        """
        # Generate paper name
        paper_name_upper = paper.name.upper()
        subject_name_upper = paper.subject.name.upper()
        
        if subject_name_upper in paper_name_upper:
            display_paper_name = paper_name_upper
        else:
            display_paper_name = f'{subject_name_upper} {paper_name_upper}'
        
        # Get section details from metadata (safe defaults)
        metadata = getattr(generated_paper, 'metadata', {}) or {}
        section_a_questions = int(metadata.get('section_a_questions', 13))
        section_b_questions = int(metadata.get('section_b_questions', 5))

        # Compute total pages dynamically: coverpage + question pages
        total_questions = getattr(generated_paper, 'total_questions', None) or (section_a_questions + section_b_questions)
        try:
            total_questions = int(total_questions)
        except Exception:
            total_questions = section_a_questions + section_b_questions

        # Assume ~3 questions per page for Paper 1
        questions_per_page = 3
        question_pages = 0
        if total_questions > 0:
            question_pages = (total_questions + questions_per_page - 1) // questions_per_page

        total_pages = 1 + question_pages

        return {
            'school_name': 'EXAMINATION CENTRE',
            'school_logo': '/exam.png',
            'logo_position': 'center',
            'class_name': '',
            'exam_title': 'END TERM EXAMINATION 2025',
            'paper_name': display_paper_name,
            'paper_type': 'Paper 1',
            'section_a_questions': section_a_questions,
            'section_a_marks': 25,
            'section_b_questions': section_b_questions,
            'section_b_marks': 55,
            'total_marks': generated_paper.total_marks or 80,
            'time_allocation': format_time_allocation(paper.time_allocation),
            'total_pages': total_pages,
            'instructions': [
                'Write your name and admission number in the spaces provided above.',
                'Sign and write the date of examination in the spaces provided above.',
                'This paper consists of two sections: A and B.',
                'Answer ALL questions in Section A and ALL questions in Section B.',
                'Show all the steps in your calculations, giving your answers at each stage in the spaces provided below each question.',
                'Marks may be given for correct working even if the answer is wrong.',
                'Non-programmable silent electronic calculators and KNEC Mathematical tables may be used, except where stated otherwise.',
                'This paper consists of 12 printed pages.',
                'Candidates should check the question paper to ascertain that all the pages are printed as indicated and that no questions are missing.'
            ],
            'date': datetime.now().strftime('%Y-%m-%d'),
            'candidate_name_field': True,
            'candidate_number_field': True,
            'date_field': True
        }
        
class PhysicsPaper2Coverpage:
    """
    Physics Paper 2 Coverpage Template
    Includes sectioned marking grid (Section A and Section B)
    """
    
    @staticmethod
    def generate_html(data):
        """
        Generate HTML for Physics Paper 2 coverpage
        
        Args:
            data (dict): Coverpage data with keys similar to other Paper 2 templates
        
        Returns:
            str: HTML content for coverpage
        """
        
        # Extract data with defaults
        school_name = data.get('school_name', 'EXAMINATION CENTRE')
        school_logo = data.get('school_logo', '/exam.png')
        logo_position = data.get('logo_position', 'center')
        class_name = data.get('class_name', '')
        exam_title = data.get('exam_title', 'END TERM EXAMINATION 2025')
        paper_name = data.get('paper_name', 'PHYSICS PAPER 2')
        
        # Section configuration (from screenshot)
        section_a_questions = data.get('section_a_questions', 5)  # Questions 1-13, 14, 15 (3 questions shown)
        section_b_questions = data.get('section_b_questions', 3)  # Questions 16, 17, 18 (3 questions)
        total_marks = data.get('total_marks', 80)
        time_allocation = data.get('time_allocation', '2 HOURS 30 MINUTES')
        
        # Calculate total questions and pages
        total_questions = section_a_questions + section_b_questions
        total_pages = data.get('total_pages', 16)  # Default 16 printed pages
        
        instructions = data.get('instructions', [
            'Write your name and admission number in the spaces provided above.',
            'Sign and write the date of examination in the spaces provided above.',
            'This paper consists of two sections: A and B.',
            'Answer all the questions in Section A and B in the spaces provided.',
            'All working must be clearly shown in the spaces provided in this booklet.',
            'Non-programmable silent electronic calculators and KNEC Mathematical tables may be used.',
            f'This paper consists of {total_pages} printed pages.',
            'Candidates should check the question paper to ascertain that all the pages are printed as indicated and that no questions are missing.',
            'Candidates should answer the questions in English.'
        ])
        
        exam_date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        show_name = data.get('candidate_name_field', True)
        show_number = data.get('candidate_number_field', True)
        show_date = data.get('date_field', True)
        
        # Generate marking grid for Physics Paper 2
        marking_grid_html = PhysicsPaper2Coverpage._generate_marking_grid()
        
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
            width: 60%;
            margin: 0 auto;
            border-collapse: collapse;
            border: 2px solid black;
        }}
        
        .marking-grid th,
        .marking-grid td {{
            border: 1px solid black;
            text-align: center;
            font-size: 12px;
            padding: 10px 8px;
        }}
        
        .marking-grid th {{
            background-color: #f0f0f0;
            font-weight: bold;
        }}
        
        .section-label {{
            font-size: 13px;
            font-weight: bold;
            vertical-align: middle;
            background-color: #f5f5f5;
        }}
        
        .total-row {{
            background-color: #e0e0e0;
            font-weight: bold;
            font-size: 13px;
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
                <div class="info-row-grid">
                    {f'<div class="info-row-item"><span class="info-label">ADM NO:</span><div class="info-field"></div></div>' if show_number else ''}
                    <div class="info-row-item"><span class="info-label">CLASS:</span><div class="info-field"></div></div>
                </div>
                <div class="info-row-grid">
                    {f'<div class="info-row-item"><span class="info-label">DATE:</span><div class="info-field"></div></div>' if show_date else ''}
                    <div class="info-row-item"><span class="info-label">SIGNATURE:</span><div class="info-field"></div></div>
                </div>
            </div>
        </div>
        
        <!-- Instructions -->
        <div class="instructions">
            <div class="instructions-title">Instructions to candidates</div>
            <ol style="font-style: italic; list-style: none; counter-reset: list-counter; margin-left: 20px;">
"""
        
        # Add instructions
        for idx, instruction in enumerate(instructions, 1):
            # Make section-related instructions bold
            is_bold = 'section' in instruction.lower() or 'all' in instruction.lower()
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
    def _generate_marking_grid():
        """
        Generate marking grid HTML for Physics Paper 2
        
        Based on screenshot, the grid structure is:
        - Section A: Questions 1-13 (25 marks), 14 (10 marks), 15 (18 marks)
        - Section B: Questions 16 (9 marks), 17 (13 marks), 18 (11 marks)
        - Total Score: 80 marks
        
        Returns:
            str: HTML for marking grid
        """
        
        grid_html = """
            <table class="marking-grid">
                <thead>
                    <tr>
                        <th>Section</th>
                        <th>Questions</th>
                        <th>Maximum<br>Score</th>
                        <th>Candidate's<br>Score</th>
                    </tr>
                </thead>
                <tbody>
                    <!-- Section A -->
                    <tr>
                        <td rowspan="3" class="section-label">A</td>
                        <td>1-13</td>
                        <td>25</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td>14</td>
                        <td>10</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td>15</td>
                        <td>18</td>
                        <td></td>
                    </tr>
                    
                    <!-- Section B -->
                    <tr>
                        <td rowspan="3" class="section-label">B</td>
                        <td>16</td>
                        <td>9</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td>17</td>
                        <td>13</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td>18</td>
                        <td>11</td>
                        <td></td>
                    </tr>
                    
                    <!-- Total Score -->
                    <tr class="total-row">
                        <td colspan="2">Total Score</td>
                        <td>80</td>
                        <td></td>
                    </tr>
                </tbody>
            </table>
        """
        
        return grid_html
    
    @staticmethod
    def generate_default_coverpage_data(generated_paper, paper):
        """
        Generate default coverpage data for Physics Paper 2
        
        Args:
            generated_paper: GeneratedPaper instance
            paper: Paper instance
        
        Returns:
            dict: Default coverpage data for Physics Paper 2
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
        
        # Calculate total pages
        total_pages = 16  # Standard for Physics Paper 2
        
        return {
            'school_name': 'EXAMINATION CENTRE',
            'school_logo': '/exam.png',
            'logo_position': 'center',
            'class_name': '',
            'exam_title': 'END TERM EXAMINATION 2025',
            'paper_name': display_paper_name,
            'paper_type': 'Paper 2',
            'section_a_questions': 5,
            'section_b_questions': 3,
            'total_marks': generated_paper.total_marks or 80,
            'time_allocation': format_time_allocation(paper.time_allocation),
            'total_pages': total_pages,
            'instructions': [
                'Write your name and admission number in the spaces provided above.',
                'Sign and write the date of examination in the spaces provided above.',
                'This paper consists of two sections: A and B.',
                'Answer all the questions in Section A and B in the spaces provided.',
                'All working must be clearly shown in the spaces provided in this booklet.',
                'Non-programmable silent electronic calculators and KNEC Mathematical tables may be used.',
                f'This paper consists of {total_pages} printed pages.',
                'Candidates should check the question paper to ascertain that all the pages are printed as indicated and that no questions are missing.',
                'Candidates should answer the questions in English.'
            ],
            'date': datetime.now().strftime('%Y-%m-%d'),
            'candidate_name_field': True,
            'candidate_number_field': True,
            'date_field': True
        }


        
class ChemistryPaper2Coverpage:
    """
    Chemistry Paper 2 Coverpage Template
    (To be implemented similarly to BiologyPaper2Coverpage)
    """
    pass

class ChemistryPaper1Coverpage:
    """
    Chemistry Paper 1 Coverpage Template
    Includes dynamic marking grid based on question count (similar to Biology Paper 1)
    """
    
    @staticmethod
    def generate_html(data):
        """
        Generate HTML for Chemistry Paper 1 coverpage
        
        Args:
            data (dict): Coverpage data with keys:
                - school_name: Name of the school
                - school_logo: Base64 encoded logo or URL
                - exam_title: e.g., "END TERM 3 EXAMINATION 2025"
                - paper_name: e.g., "CHEMISTRY PAPER 1"
                - total_questions: Number of questions in the paper
                - total_marks: Total marks for the paper
                - time_allocation: Time in minutes
                - instructions: List of instruction strings
                - date: Exam date (optional)
                - candidate_name_field: Show name field (default: True)
                - candidate_number_field: Show admission number field (default: True)
                - date_field: Show date field (default: True)
        
        Returns:
            str: HTML content for coverpage
        """
        
        # Extract data with defaults
        school_name = data.get('school_name', 'EXAMINATION CENTRE')
        school_logo = data.get('school_logo', '/exam.png')
        logo_position = data.get('logo_position', 'center')
        class_name = data.get('class_name', '')
        exam_title = data.get('exam_title', 'END TERM EXAMINATION 2025')
        paper_name = data.get('paper_name', 'CHEMISTRY PAPER 1')
        total_questions = data.get('total_questions', 25)
        total_marks = data.get('total_marks', 80)
        time_allocation = data.get('time_allocation', '2 HOURS')
        
        # Calculate total pages
        total_pages = 1 + ((total_questions + 2) // 3)
        
        instructions = data.get('instructions', [
            'Write your name and admission number in the spaces provided above.',
            'Sign and write the date of examination in the spaces provided above.',
            'Answer all the questions in the spaces provided.',
            'ALL working MUST be clearly shown where necessary.',
            'Non-programmable silent electronic calculators and KNEC Mathematical tables may be used, except where stated otherwise.',
            f'This paper consists of {total_pages} printed pages.',
            'Candidates should check the question paper to ascertain that all the pages are printed as indicated and that no questions are missing.'
        ])
        
        exam_date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        show_name = data.get('candidate_name_field', True)
        show_number = data.get('candidate_number_field', True)
        show_date = data.get('date_field', True)
        
        # Generate marking grid (reuse Biology Paper 1 grid structure)
        marking_grid_html = BiologyPaper1Coverpage._generate_marking_grid(total_questions)
        
        # Build HTML (similar to Biology Paper 1)
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
            position: relative;
        }}
        
        .coverpage {{
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}
        
        /* Header Section */
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
            margin-bottom: 10px;
        }}
        
        .paper-details {{
            font-size: 14px;
            margin-bottom: 20px;
        }}
        
        /* Candidate Information Section */
        .candidate-info {{
            border: none;
            padding: 15px;
            margin-bottom: 20px;
        }}
        
        .info-grid {{
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
            font-size: 13px;
            margin-bottom: 10px;
            text-align: center;
        }}
        
        .marking-grid {{
            width: 100%;
            border-collapse: collapse;
            border: 1px solid black;
        }}
        
        .marking-grid td {{
            border: 1px solid black;
            text-align: center;
            font-size: 10px;
            font-weight: bold;
            padding: 8px 4px;
            height: 30px;
        }}
        
        .question-number {{
            min-width: 35px;
            width: 35px;
        }}
        
        .empty-question-cell {{
            min-width: 35px;
            width: 35px;
            background-color: white;
            border: none !important;
        }}
        
        .row-with-spacing td {{
            border-top: 2px solid black;
            padding-top: 8px;
        }}
        
        .row-with-spacing .empty-question-cell,
        .row-with-spacing .gap-cell {{
            border-top: none !important;
        }}
        
        .gap-cell {{
            border-right: none !important;
            border-left: none !important;
            border-bottom: none !important;
            background-color: white;
            min-width: 15px;
            width: 15px;
        }}
        
        .grand-total-cell {{
            background-color: #f0f0f0;
            font-size: 10px;
            font-weight: bold;
            border: 2px solid black;
            padding: 5px 10px;
            min-width: 80px;
        }}
        
        .total-box {{
            min-width: 60px;
            width: 60px;
            min-height: 60px;
            border: 2px solid black;
            background-color: white;
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
            {f'<div class="class-title">{class_name}</div>' if class_name else ''}
            <div class="exam-title">{exam_title}</div>
            <div class="paper-title">{paper_name}</div>
            <div class="paper-details">
                <div>Time: {time_allocation}</div>
            </div>
        </div>
        
        <!-- Candidate Information -->
        <div class="candidate-info">
            <div class="candidate-info-grid">
                {f'<div class="info-row-full"><span class="info-label">NAME:</span><div class="info-field"></div></div>' if show_name else ''}
                <div class="info-row-grid">
                    {f'<div class="info-row-item"><span class="info-label">ADM NO:</span><div class="info-field"></div></div>' if show_number else ''}
                    <div class="info-row-item"><span class="info-label">CLASS:</span><div class="info-field"></div></div>
                </div>
                <div class="info-row-grid">
                    {f'<div class="info-row-item"><span class="info-label">DATE:</span><div class="info-field"></div></div>' if show_date else ''}
                    <div class="info-row-item"><span class="info-label">SIGNATURE:</span><div class="info-field"></div></div>
                </div>
            </div>
        </div>
        
        <!-- Instructions -->
        <div class="instructions">
            <div class="instructions-title">INSTRUCTIONS TO CANDIDATES</div>
            <ol style="font-size: 12px; line-height: 1.6; font-style:italic; list-style: none; counter-reset: list-counter; margin-left: 20px;">
                {''.join([f'<li style="counter-increment: list-counter;" class="{"bold" if idx >= 3 else ""}">{instruction}</li>' for idx, instruction in enumerate(instructions)])}
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
        Generate default coverpage data for a Chemistry Paper 1
        
        Args:
            generated_paper: GeneratedPaper instance
            paper: Paper instance
        
        Returns:
            dict: Default coverpage data
        """
        # Calculate total pages
        total_pages = 1 + ((generated_paper.total_questions + 2) // 3)
        
        # Generate paper name
        paper_name_upper = paper.name.upper()
        subject_name_upper = paper.subject.name.upper()
        
        if subject_name_upper in paper_name_upper:
            display_paper_name = paper_name_upper
        else:
            display_paper_name = f'{subject_name_upper} {paper_name_upper}'
        
        return {
            'school_name': 'EXAMINATION CENTRE',
            'school_logo': '/exam.png',
            'logo_position': 'center',
            'class_name': '',
            'exam_title': 'END TERM EXAMINATION 2025',
            'paper_name': display_paper_name,
            'total_questions': generated_paper.total_questions,
            'total_marks': generated_paper.total_marks,
            'time_allocation': format_time_allocation(paper.time_allocation),
            'instructions': [
                'Write your name and admission number in the spaces provided above.',
                'Sign and write the date of examination in the spaces provided above.',
                'Answer ALL the questions in the spaces provided.',
                'ALL working MUST be clearly shown where necessary.',
                'Non-programmable silent electronic calculators and KNEC Mathematical tables may be used, except where stated otherwise.',
                f'This paper consists of {total_pages} printed pages.',
                'Candidates should check the question paper to ascertain that all the pages are printed as indicated and that no questions are missing.'
            ],
            'date': datetime.now().strftime('%Y-%m-%d'),
            'candidate_name_field': True,
            'candidate_number_field': True,
            'date_field': True
        }


class ChemistryPaper2Coverpage:
    """
    Chemistry Paper 2 Coverpage Template
    Includes marking grid with individual question rows (Questions 1-8)
    """
    
    @staticmethod
    def generate_html(data):
        """
        Generate HTML for Chemistry Paper 2 coverpage
        
        Args:
            data (dict): Coverpage data with keys:
                - school_name: Name of the school
                - school_logo: Base64 encoded logo or URL
                - exam_title: e.g., "END TERM 3 EXAMINATION 2025"
                - paper_name: e.g., "CHEMISTRY PAPER 2"
                - total_questions: Number of questions (default: 8)
                - question_marks: List of marks per question (default: [11,12,13,13,11,10,10,10])
                - total_marks: Total marks for the paper (default: 80)
                - time_allocation: Time in minutes
                - instructions: List of instruction strings
                - date: Exam date (optional)
                - candidate_name_field: Show name field (default: True)
                - candidate_number_field: Show admission number field (default: True)
                - date_field: Show date field (default: True)
        
        Returns:
            str: HTML content for coverpage
        """
        
        # Extract data with defaults
        school_name = data.get('school_name', 'EXAMINATION CENTRE')
        school_logo = data.get('school_logo', '/exam.png')
        logo_position = data.get('logo_position', 'center')
        class_name = data.get('class_name', '')
        exam_title = data.get('exam_title', 'END TERM EXAMINATION 2025')
        paper_name = data.get('paper_name', 'CHEMISTRY PAPER 2')
        
        # Question configuration (from screenshot)
        total_questions = data.get('total_questions', 7)  # Default to 7 for Chemistry Paper 2
        question_marks = data.get('question_marks', [11, 12, 13, 12, 11, 11, 10])  # 7 questions totaling 80
        total_marks = data.get('total_marks', 80)
        time_allocation = data.get('time_allocation', '2 HOURS')
        
        # Calculate total pages
        total_pages = data.get('total_pages', 16)  # Default 16 printed pages
        
        instructions = data.get('instructions', [
            'Write your name and admission number in the spaces provided above.',
            'Sign and write the date of examination in the spaces provided above.',
            'Answer all questions in the spaces provided below each question.',
            'All working must be clearly shown in the spaces provided in this booklet.',
            'Non-programmable silent electronic calculators and KNEC Mathematical tables may be used.',
            f'This paper consists of {total_pages} printed pages.',
            'Candidates should check the question paper to ascertain that all the pages are printed as indicated and that no questions are missing.',
            'Candidates should answer the questions in English.'
        ])
        
        exam_date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        show_name = data.get('candidate_name_field', True)
        show_number = data.get('candidate_number_field', True)
        show_date = data.get('date_field', True)
        
        # Generate marking grid for Chemistry Paper 2
        marking_grid_html = ChemistryPaper2Coverpage._generate_marking_grid(
            total_questions, question_marks, total_marks
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
        
        /* Marking Grid Section for Chemistry Paper 2 */
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
            width: 50%;
            margin: 0 auto;
            border-collapse: collapse;
            border: 2px solid black;
        }}
        
        .marking-grid th,
        .marking-grid td {{
            border: 1px solid black;
            text-align: center;
            font-size: 12px;
            padding: 10px 8px;
        }}
        
        .marking-grid th {{
            background-color: #f0f0f0;
            font-weight: bold;
        }}
        
        .total-row {{
            background-color: #e0e0e0;
            font-weight: bold;
            font-size: 13px;
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
                <div class="info-row-grid">
                    {f'<div class="info-row-item"><span class="info-label">ADM NO:</span><div class="info-field"></div></div>' if show_number else ''}
                    <div class="info-row-item"><span class="info-label">CLASS:</span><div class="info-field"></div></div>
                </div>
                <div class="info-row-grid">
                    {f'<div class="info-row-item"><span class="info-label">DATE:</span><div class="info-field"></div></div>' if show_date else ''}
                    <div class="info-row-item"><span class="info-label">SIGNATURE:</span><div class="info-field"></div></div>
                </div>
            </div>
        </div>
        
        <!-- Instructions -->
        <div class="instructions">
            <div class="instructions-title">Instructions to candidates</div>
            <ol style="font-style: italic; list-style: none; counter-reset: list-counter; margin-left: 20px;">
"""
        
        # Add instructions
        for idx, instruction in enumerate(instructions, 1):
            # Make 'all' related instructions bold
            is_bold = 'all' in instruction.lower()
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
    def _generate_marking_grid(total_questions, question_marks, total_marks):
        """
        Generate marking grid HTML for Chemistry Paper 2
        
        Based on screenshot, the grid structure is:
        - Individual rows for each question (1-8)
        - Each row shows: Question number | Maximum Score | Candidate's Score
        - Total Score row at bottom
        
        Args:
            total_questions (int): Number of questions
            question_marks (list): List of marks per question
            total_marks (int): Total marks for the paper
        
        Returns:
            str: HTML for marking grid
        """
        
        # Ensure question_marks list has enough values
        if len(question_marks) < total_questions:
            question_marks.extend([10] * (total_questions - len(question_marks)))
        
        grid_html = """
            <table class="marking-grid">
                <thead>
                    <tr>
                        <th>Question</th>
                        <th>Maximum<br>Score</th>
                        <th>Candidate's<br>Score</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        # Individual question rows
        for i in range(1, total_questions + 1):
            marks = question_marks[i - 1] if i <= len(question_marks) else 10
            grid_html += f"""
                    <tr>
                        <td>{i}</td>
                        <td>{marks}</td>
                        <td></td>
                    </tr>
"""
        
        # Total Score row
        grid_html += f"""
                    <tr class="total-row">
                        <td>Total Score</td>
                        <td>{total_marks}</td>
                        <td></td>
                    </tr>
                </tbody>
            </table>
        """
        
        return grid_html
    
    @staticmethod
    def generate_default_coverpage_data(generated_paper, paper):
        """
        Generate default coverpage data for Chemistry Paper 2
        
        Args:
            generated_paper: GeneratedPaper instance
            paper: Paper instance
        
        Returns:
            dict: Default coverpage data for Chemistry Paper 2
        """
        from .models import Question
        
        # Generate paper name
        paper_name_upper = paper.name.upper()
        subject_name_upper = paper.subject.name.upper()
        
        if subject_name_upper in paper_name_upper:
            display_paper_name = paper_name_upper
        else:
            display_paper_name = f'{subject_name_upper} {paper_name_upper}'
        
        # Get actual total questions from generated_paper
        total_questions = generated_paper.total_questions if generated_paper.total_questions else 7
        
        # Get actual marks from the questions in the generated paper
        question_ids = generated_paper.question_ids or []
        question_marks = []
        
        if question_ids:
            # Load questions and get their marks in order
            questions = Question.objects.filter(id__in=question_ids).in_bulk(field_name='id')
            for qid in question_ids:
                question = questions.get(qid)
                if question:
                    question_marks.append(question.marks)
        
        # Fallback to default marks if no questions found
        if not question_marks:
            default_marks_7 = [11, 12, 13, 12, 11, 11, 10]  # Total: 80 marks
            default_marks_8 = [11, 12, 13, 13, 11, 10, 10, 10]  # Total: 90 marks
            
            if total_questions == 7:
                question_marks = default_marks_7
            elif total_questions == 8:
                question_marks = default_marks_8
            else:
                avg_marks = (generated_paper.total_marks or 80) // total_questions
                question_marks = [avg_marks] * total_questions
        
        # Calculate total pages
        # 1 page: Coverpage
        # Questions: approximately 2 pages each
        total_pages = 1 + (total_questions * 2)
        
        return {
            'school_name': 'EXAMINATION CENTRE',
            'school_logo': '/exam.png',
            'logo_position': 'center',
            'class_name': '',
            'exam_title': 'END TERM EXAMINATION 2025',
            'paper_name': display_paper_name,
            'paper_type': 'Paper 2',
            'total_questions': total_questions,
            'question_marks': question_marks[:total_questions],  # Ensure correct length
            'total_marks': generated_paper.total_marks or 80,
            'time_allocation': format_time_allocation(paper.time_allocation),
            'total_pages': total_pages,
            'instructions': [
                'Write your name and admission number in the spaces provided above.',
                'Sign and write the date of examination in the spaces provided above.',
                'Answer all questions in the spaces provided below each question.',
                'All working must be clearly shown in the spaces provided in this booklet.',
                'Non-programmable silent electronic calculators and KNEC Mathematical tables may be used.',
                f'This paper consists of {total_pages} printed pages.',
                'Candidates should check the question paper to ascertain that all the pages are printed as indicated and that no questions are missing.',
                'Candidates should answer the questions in English.'
            ],
            'date': datetime.now().strftime('%Y-%m-%d'),
            'candidate_name_field': True,
            'candidate_number_field': True,
            'date_field': True
        }


class MathematicsPaper1Coverpage:
    """
    Mathematics Paper 1 Coverpage Template
    Includes sectioned marking grid (Section I and Section II)
    """
    
    @staticmethod
    def generate_html(data):
        """
        Generate HTML for Mathematics Paper 1 coverpage
        
        Args:
            data (dict): Coverpage data with keys:
                - school_name: Name of the school
                - school_logo: Base64 encoded logo or URL
                - exam_title: e.g., "END TERM 3 EXAMINATION 2025"
                - paper_name: e.g., "MATHEMATICS PAPER 1"
                - section_1_questions: Number of questions in Section I (default: 16)
                - section_1_marks: Marks per question in Section I (default: 50)
                - section_2_questions: Number of questions in Section II (default: 8)
                - section_2_marks: Marks per question in Section II (default: 50)
                - total_marks: Total marks for the paper (default: 100)
                - time_allocation: Time in minutes
                - instructions: List of instruction strings
                - date: Exam date (optional)
                - candidate_name_field: Show name field (default: True)
                - candidate_number_field: Show admission number field (default: True)
                - date_field: Show date field (default: True)
        
        Returns:
            str: HTML content for coverpage
        """
        
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
            f'This paper consists of {total_pages} printed pages.',
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
        """
        Generate marking grid HTML for Mathematics Paper 1
        
        Grid structure (based on screenshot):
        - Row 1: Section I label | Questions 1-16 | Total
        - Row 2: (blank) | Answer boxes for 1-16 | Total box
        - Row 3: Section II label | Questions 17-24 | Total | Grand Total label
        - Row 4: (blank) | Answer boxes for 17-24 | Total box | Grand Total box
        
        Args:
            section_1_questions (int): Number of questions in Section I
            section_1_marks (int): Total marks for Section I
            section_2_questions (int): Number of questions in Section II
            section_2_marks (int): Total marks for Section II
            total_marks (int): Total marks for the paper
        
        Returns:
            str: HTML for marking grid
        """
        
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
        """
        Generate default coverpage data for Mathematics Paper 1
        
        Args:
            generated_paper: GeneratedPaper instance
            paper: Paper instance
        
        Returns:
            dict: Default coverpage data for Math Paper 1
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
                f'This paper consists of {total_pages} printed pages.',
                'Candidates should check the question paper to ascertain that all the pages are printed as indicated and that no questions are missing.'
            ],
            'date': datetime.now().strftime('%Y-%m-%d'),
            'candidate_name_field': True,
            'candidate_number_field': True,
            'date_field': True
        }
        

class MathematicsPaper2Coverpage:
    """
    Mathematics Paper 2 Coverpage Template
    Includes sectioned marking grid (Section I and Section II)
    """
    
    @staticmethod
    def generate_html(data):
        """
        Generate HTML for Mathematics Paper 2 coverpage
        
        Args:
            data (dict): Coverpage data with keys similar to Paper 1
        
        Returns:
            str: HTML content for coverpage
        """
        
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
            f'This paper consists of {total_pages} printed pages.',
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
                f'This paper consists of {total_pages} printed pages.',
                'Candidates should check the question paper to ascertain that all the pages are printed as indicated and that no questions are missing.'
            ],
            'date': datetime.now().strftime('%Y-%m-%d'),
            'candidate_name_field': True,
            'candidate_number_field': True,
            'date_field': True
        }
        
class GeographyPaper1Coverpage:
    """
    Geography Paper 1 Coverpage Template
    Includes sectioned marking grid (Section A and Section B)
    """
    
    @staticmethod
    def generate_html(data):
        """
        Generate HTML for Geography Paper 1 coverpage
        
        Args:
            data (dict): Coverpage data with keys:
                - school_name: Name of the school
                - school_logo: Base64 encoded logo or URL
                - exam_title: e.g., "END TERM 3 EXAMINATION 2025"
                - paper_name: e.g., "GEOGRAPHY PAPER 1"
                - section_a_questions: Questions in Section A (default: "1-5")
                - section_a_marks: Marks for Section A (default: 25)
                - section_b_question: Question in Section B (default: "6")
                - section_b_marks: Marks for Section B (default: 25)
                - total_marks: Total marks (default: 50)
                - time_allocation: Time in minutes (default: 165 for 2 hours 45 minutes)
                - total_pages: Total pages (default: 7)
        
        Returns:
            str: HTML content for coverpage
        """
        
        # Extract data with defaults
        school_name = data.get('school_name', 'EXAMINATION CENTRE')
        school_logo = data.get('school_logo', '/exam.png')
        logo_position = data.get('logo_position', 'center')
        class_name = data.get('class_name', '')
        exam_title = data.get('exam_title', 'END TERM EXAMINATION 2025')
        paper_name = data.get('paper_name', 'GEOGRAPHY PAPER 1')
        
        # Section configuration (from screenshot)
        section_a_questions = data.get('section_a_questions', '1-5')
        section_a_marks = data.get('section_a_marks', 25)
        section_b_question = data.get('section_b_question', '6')
        section_b_marks = data.get('section_b_marks', 75)
        total_marks = data.get('total_marks', 100)
        time_allocation = data.get('time_allocation', '2 HOURS 45 MINUTES')
        
        # Calculate total pages
        total_pages = data.get('total_pages', 7)
        
        instructions = data.get('instructions', [
            'Write your name and admission number in the spaces provided above.',
            'Sign and write the date of the examination in the spaces provided above.',
            'This paper consists of two sections: A and B.',
            'Answer all the questions in section A.',
            'In section B answer question 6 and any other two question from section B.',
            'All answers must be written in the answer booklet provided at the end of question 10.',
            f'This paper consists of {total_pages} printed pages.',
            'Candidates should check the question paper to ascertain that all the pages are printed as indicated and that no question are missing.',
            'Candidates should answer the questions in English'
        ])
        
        exam_date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        show_name = data.get('candidate_name_field', True)
        show_number = data.get('candidate_number_field', True)
        show_date = data.get('date_field', True)
        
        # Generate marking grid for Geography Paper 1
        marking_grid_html = GeographyPaper1Coverpage._generate_marking_grid(
            section_a_questions, section_a_marks,
            section_b_question, section_b_marks,
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
            width: 60%;
            margin: 0 auto;
            border-collapse: collapse;
            border: 2px solid black;
        }}
        
        .marking-grid th,
        .marking-grid td {{
            border: 1px solid black;
            text-align: center;
            font-size: 12px;
            padding: 10px 8px;
        }}
        
        .marking-grid th {{
            background-color: #f0f0f0;
            font-weight: bold;
        }}
        
        .section-label {{
            font-size: 13px;
            font-weight: bold;
            vertical-align: middle;
            background-color: #f5f5f5;
        }}
        
        .total-row {{
            background-color: #e0e0e0;
            font-weight: bold;
            font-size: 13px;
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
                <div class="info-row-grid">
                    {f'<div class="info-row-item"><span class="info-label">ADM NO:</span><div class="info-field"></div></div>' if show_number else ''}
                    <div class="info-row-item"><span class="info-label">CLASS:</span><div class="info-field"></div></div>
                </div>
                <div class="info-row-grid">
                    {f'<div class="info-row-item"><span class="info-label">DATE:</span><div class="info-field"></div></div>' if show_date else ''}
                    <div class="info-row-item"><span class="info-label">SIGNATURE:</span><div class="info-field"></div></div>
                </div>
            </div>
        </div>
        
        <!-- Instructions -->
        <div class="instructions">
            <div class="instructions-title">Instructions to candidates</div>
            <ol style="font-style: italic; list-style: none; counter-reset: list-counter; margin-left: 20px;">
"""
        
        # Add instructions
        for idx, instruction in enumerate(instructions, 1):
            # Make section-related instructions bold
            is_bold = 'section' in instruction.lower() or 'all' in instruction.lower()
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
    def _generate_marking_grid(section_a_questions, section_a_marks, 
                               section_b_question, section_b_marks, total_marks):
        """
        Generate marking grid HTML for Geography Paper 1
        
        Based on screenshot, the grid structure is:
        - Section A: Questions 1-5 (25 marks)
        - Section B: Question 6 (25 marks)
        - Total Score: 50 marks (with additional row for 25 marks)
        
        Args:
            section_a_questions (str): Question range for Section A (e.g., "1-5")
            section_a_marks (int): Marks for Section A
            section_b_question (str): Question for Section B (e.g., "6")
            section_b_marks (int): Marks for Section B
            total_marks (int): Total marks for the paper
        
        Returns:
            str: HTML for marking grid
        """
        
        grid_html = """
            <table class="marking-grid">
                <thead>
                    <tr>
                        <th>Section</th>
                        <th>Questions</th>
                        <th>Maximum<br>Score</th>
                        <th>Candidate's<br>Score</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        # Section A
        grid_html += f"""
                    <tr>
                        <td class="section-label">A</td>
                        <td>{section_a_questions}</td>
                        <td>{section_a_marks}</td>
                        <td></td>
                    </tr>
"""
        
        # Section B - Question 6 and any other TWO questions (from 7-10)
        grid_html += f"""
                    <tr>
                        <td rowspan="3" class="section-label">B</td>
                        <td>6</td>
                        <td>25</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td>7-10 (Any TWO)</td>
                        <td>25</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td></td>
                        <td>25</td>
                        <td></td>
                    </tr>
"""
        
        # Total Score row
        grid_html += f"""
                    <tr class="total-row">
                        <td colspan="2">Total Score</td>
                        <td>{total_marks}</td>
                        <td></td>
                    </tr>
                </tbody>
            </table>
        """
        
        return grid_html
    
    @staticmethod
    def generate_default_coverpage_data(generated_paper, paper):
        """
        Generate default coverpage data for Geography Paper 1
        
        Args:
            generated_paper: GeneratedPaper instance
            paper: Paper instance
        
        Returns:
            dict: Default coverpage data for Geography Paper 1
        """
        # Generate paper name
        paper_name_upper = paper.name.upper()
        subject_name_upper = paper.subject.name.upper()
        
        if subject_name_upper in paper_name_upper:
            display_paper_name = paper_name_upper
        else:
            display_paper_name = f'{subject_name_upper} {paper_name_upper}'
        
        # Get metadata for section details
        metadata = getattr(generated_paper, 'metadata', {}) or {}
        
        # Calculate total pages
        total_pages = 7  # Standard for Geography Paper 1
        
        return {
            'school_name': 'EXAMINATION CENTRE',
            'school_logo': '/exam.png',
            'logo_position': 'center',
            'class_name': '',
            'exam_title': 'END TERM EXAMINATION 2025',
            'paper_name': display_paper_name,
            'paper_type': 'Paper 1',
            'section_a_questions': '1-5',
            'section_a_marks': 25,
            'section_b_question': '6',
            'section_b_marks': 25,
            'total_marks': generated_paper.total_marks or 50,
            'time_allocation': format_time_allocation(paper.time_allocation),
            'total_pages': total_pages,
            'instructions': [
                'Write your name and admission number in the spaces provided above.',
                'Sign and write the date of the examination in the spaces provided above.',
                'This paper consists of two sections: A and B.',
                'Answer all the questions in section A.',
                'In section B answer question 6 and any other two question from section B.',
                'All answers must be written in the answer booklet provided at the end of question 10.',
                f'This paper consists of {total_pages} printed pages.',
                'Candidates should check the question paper to ascertain that all the pages are printed as indicated and that no question are missing.',
                'Candidates should answer the questions in English'
            ],
            'date': datetime.now().strftime('%Y-%m-%d'),
            'candidate_name_field': True,
            'candidate_number_field': True,
            'date_field': True
        }
        
        
class GeographyPaper2Coverpage:
    """
    Geography Paper 2 Coverpage Template
    Includes sectioned marking grid (Section A and Section B)
    """
    
    @staticmethod
    def generate_html(data):
        """
        Generate HTML for Geography Paper 2 coverpage
        
        Args:
            data (dict): Coverpage data with keys:
                - school_name: Name of the school
                - school_logo: Base64 encoded logo or URL
                - exam_title: e.g., "END TERM 3 EXAMINATION 2025"
                - paper_name: e.g., "GEOGRAPHY PAPER 2"
                - section_a_questions: Questions in Section A (default: "1-5")
                - section_a_marks: Marks for Section A (default: 25)
                - section_b_question: Question in Section B (default: "6")
                - section_b_marks: Marks for Section B (default: 75)
                - total_marks: Total marks (default: 100)
                - time_allocation: Time in minutes
                - total_pages: Total pages
        
        Returns:
            str: HTML content for coverpage
        """
        
        # Extract data with defaults
        school_name = data.get('school_name', 'EXAMINATION CENTRE')
        school_logo = data.get('school_logo', '/exam.png')
        logo_position = data.get('logo_position', 'center')
        class_name = data.get('class_name', '')
        exam_title = data.get('exam_title', 'END TERM EXAMINATION 2025')
        paper_name = data.get('paper_name', 'GEOGRAPHY PAPER 2')
        
        # Section configuration (from screenshot)
        section_a_questions = data.get('section_a_questions', '1-5')
        section_a_marks = data.get('section_a_marks', 25)
        section_b_question = data.get('section_b_question', '6')
        section_b_marks = data.get('section_b_marks', 75)
        total_marks = data.get('total_marks', 100)
        time_allocation = data.get('time_allocation', '2 HOURS 30 MINUTES')
        
        # Calculate total pages
        total_pages = data.get('total_pages', 11)
        
        instructions = data.get('instructions', [
            'Write your name and admission number in the spaces provided above.',
            'Sign and write the date of examination in the spaces provided above.',
            'This paper consists of two sections: A and B.',
            'Answer ALL questions in section A.',
            'Answer question 6 and any other two questions from section B.',
            'Answer must be written in the spaces provided in this booklet.',
            'All answers must be written in the answer booklets provided.',
            f'This paper consists of {total_pages} printed pages.',
            'Candidates should check the question paper to ascertain that all the pages are printed as indicated and that no questions are missing.',
            'Candidates should answer the questions in English'
        ])
        
        exam_date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        show_name = data.get('candidate_name_field', True)
        show_number = data.get('candidate_number_field', True)
        show_date = data.get('date_field', True)
        
        # Generate marking grid for Geography Paper 2
        marking_grid_html = GeographyPaper2Coverpage._generate_marking_grid(
            section_a_questions, section_a_marks,
            section_b_question, section_b_marks,
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
            width: 60%;
            margin: 0 auto;
            border-collapse: collapse;
            border: 2px solid black;
        }}
        
        .marking-grid th,
        .marking-grid td {{
            border: 1px solid black;
            text-align: center;
            font-size: 12px;
            padding: 10px 8px;
        }}
        
        .marking-grid th {{
            background-color: #f0f0f0;
            font-weight: bold;
        }}
        
        .section-label {{
            font-size: 13px;
            font-weight: bold;
            vertical-align: middle;
            background-color: #f5f5f5;
        }}
        
        .total-row {{
            background-color: #e0e0e0;
            font-weight: bold;
            font-size: 13px;
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
                <div class="info-row-grid">
                    {f'<div class="info-row-item"><span class="info-label">ADM NO:</span><div class="info-field"></div></div>' if show_number else ''}
                    <div class="info-row-item"><span class="info-label">CLASS:</span><div class="info-field"></div></div>
                </div>
                <div class="info-row-grid">
                    {f'<div class="info-row-item"><span class="info-label">DATE:</span><div class="info-field"></div></div>' if show_date else ''}
                    <div class="info-row-item"><span class="info-label">SIGNATURE:</span><div class="info-field"></div></div>
                </div>
            </div>
        </div>
        
        <!-- Instructions -->
        <div class="instructions">
            <div class="instructions-title">Instructions to candidates</div>
            <ol style="font-style: italic; list-style: none; counter-reset: list-counter; margin-left: 20px;">
"""
        
        # Add instructions
        for idx, instruction in enumerate(instructions, 1):
            # Make section-related and 'ALL' instructions bold
            is_bold = 'section' in instruction.lower() or 'ALL' in instruction
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
    def _generate_marking_grid(section_a_questions, section_a_marks, 
                               section_b_question, section_b_marks, total_marks):
        """
        Generate marking grid HTML for Geography Paper 2
        
        Based on screenshot, the grid structure is:
        - Section A: Questions 1-5 (25 marks)
        - Section B: Question 6 (25 marks) + additional row (25 marks)
        - Total Score: 100 marks
        
        Args:
            section_a_questions (str): Question range for Section A (e.g., "1-5")
            section_a_marks (int): Marks for Section A
            section_b_question (str): Question for Section B (e.g., "6")
            section_b_marks (int): Marks for Section B
            total_marks (int): Total marks for the paper
        
        Returns:
            str: HTML for marking grid
        """
        
        grid_html = """
            <table class="marking-grid">
                <thead>
                    <tr>
                        <th>Section</th>
                        <th>Questions</th>
                        <th>Maximum<br>Score</th>
                        <th>Candidate's<br>Score</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        # Section A
        grid_html += f"""
                    <tr>
                        <td class="section-label">A</td>
                        <td>{section_a_questions}</td>
                        <td>{section_a_marks}</td>
                        <td></td>
                    </tr>
"""
        
        # Section B - Question 6 (compulsory) and any other TWO questions (from 7-10)
        grid_html += f"""
                    <tr>
                        <td rowspan="3" class="section-label">B</td>
                        <td>6</td>
                        <td>25</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td>7-10 (Any TWO)</td>
                        <td>25</td>
                        <td></td>
                    </tr>
                    <tr>
                        <td></td>
                        <td>25</td>
                        <td></td>
                    </tr>
"""
        
        # Total Score row
        grid_html += f"""
                    <tr class="total-row">
                        <td colspan="2">Total Score</td>
                        <td>{total_marks}</td>
                        <td></td>
                    </tr>
                </tbody>
            </table>
        """
        
        return grid_html
    
    @staticmethod
    def generate_default_coverpage_data(generated_paper, paper):
        """
        Generate default coverpage data for Geography Paper 2
        
        Args:
            generated_paper: GeneratedPaper instance
            paper: Paper instance
        
        Returns:
            dict: Default coverpage data for Geography Paper 2
        """
        # Generate paper name
        paper_name_upper = paper.name.upper()
        subject_name_upper = paper.subject.name.upper()
        
        if subject_name_upper in paper_name_upper:
            display_paper_name = paper_name_upper
        else:
            display_paper_name = f'{subject_name_upper} {paper_name_upper}'
        
        # Get metadata for section details
        metadata = getattr(generated_paper, 'metadata', {}) or {}
        
        # Calculate total pages
        total_pages = 11  # Standard for Geography Paper 2
        
        return {
            'school_name': 'EXAMINATION CENTRE',
            'school_logo': '/exam.png',
            'logo_position': 'center',
            'class_name': '',
            'exam_title': 'END TERM EXAMINATION 2025',
            'paper_name': display_paper_name,
            'paper_type': 'Paper 2',
            'section_a_questions': '1-5',
            'section_a_marks': 25,
            'section_b_question': '6',
            'section_b_marks': 75,
            'total_marks': generated_paper.total_marks or 100,
            'time_allocation': format_time_allocation(paper.time_allocation),
            'total_pages': total_pages,
            'instructions': [
                'Write your name and admission number in the spaces provided above.',
                'Sign and write the date of examination in the spaces provided above.',
                'This paper consists of two sections: A and B.',
                'Answer ALL questions in section A.',
                'Answer question 6 and any other two questions from section B.',
                'Answer must be written in the spaces provided in this booklet.',
                'All answers must be written in the answer booklets provided.',
                f'This paper consists of {total_pages} printed pages.',
                'Candidates should check the question paper to ascertain that all the pages are printed as indicated and that no questions are missing.',
                'Candidates should answer the questions in English'
            ],
            'date': datetime.now().strftime('%Y-%m-%d'),
            'candidate_name_field': True,
            'candidate_number_field': True,
            'date_field': True
        }
        
        
        
class EnglishPaper1Coverpage:
    """
    English Paper 1 Coverpage Template
    Includes simple marking grid with individual questions
    """
    
    @staticmethod
    def generate_html(data):
        """
        Generate HTML for English Paper 1 coverpage
        
        Args:
            data (dict): Coverpage data with keys:
                - school_name: Name of the school
                - school_logo: Base64 encoded logo or URL
                - exam_title: e.g., "END TERM 3 EXAMINATION 2025"
                - paper_name: e.g., "ENGLISH PAPER 1"
                - total_questions: Number of questions (default: 3)
                - question_marks: List of marks per question (default: [20, 10, 30])
                - total_marks: Total marks (default: 60)
                - time_allocation: Time in minutes
                - total_pages: Total pages
        
        Returns:
            str: HTML content for coverpage
        """
        
        # Extract data with defaults
        school_name = data.get('school_name', 'EXAMINATION CENTRE')
        school_logo = data.get('school_logo', '/exam.png')
        logo_position = data.get('logo_position', 'center')
        class_name = data.get('class_name', '')
        exam_title = data.get('exam_title', 'END TERM EXAMINATION 2025')
        paper_name = data.get('paper_name', 'ENGLISH PAPER 1')
        
        # Question configuration (from screenshot)
        total_questions = data.get('total_questions', 3)
        question_marks = data.get('question_marks', [20, 10, 30])
        total_marks = data.get('total_marks', 60)
        time_allocation = data.get('time_allocation', '2 HOURS 30 MINUTES')
        
        # Calculate total pages
        total_pages = data.get('total_pages', 8)
        
        instructions = data.get('instructions', [
            'Write your name and admission number in the spaces provided above.',
            'Sign and write the date of examination in the spaces provided above.',
            'Answer all the questions in this paper.',
            'All your answers must be written in the question paper.',
            f'This paper consists of {total_pages} printed pages.',
            'Candidates should check the question paper to ascertain that all the pages are printed as indicated and that no questions are missing.',
            'Candidates must answer the questions in English.'
        ])
        
        exam_date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        show_name = data.get('candidate_name_field', True)
        show_number = data.get('candidate_number_field', True)
        show_date = data.get('date_field', True)
        
        # Generate marking grid for English Paper 1
        marking_grid_html = EnglishPaper1Coverpage._generate_marking_grid(
            total_questions, question_marks, total_marks
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
            width: 50%;
            margin: 0 auto;
            border-collapse: collapse;
            border: 2px solid black;
        }}
        
        .marking-grid th,
        .marking-grid td {{
            border: 1px solid black;
            text-align: center;
            font-size: 12px;
            padding: 10px 8px;
        }}
        
        .marking-grid th {{
            background-color: #f0f0f0;
            font-weight: bold;
        }}
        
        .total-row {{
            background-color: #e0e0e0;
            font-weight: bold;
            font-size: 13px;
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
                <div class="info-row-grid">
                    {f'<div class="info-row-item"><span class="info-label">ADM NO:</span><div class="info-field"></div></div>' if show_number else ''}
                    <div class="info-row-item"><span class="info-label">CLASS:</span><div class="info-field"></div></div>
                </div>
                <div class="info-row-grid">
                    {f'<div class="info-row-item"><span class="info-label">DATE:</span><div class="info-field"></div></div>' if show_date else ''}
                    <div class="info-row-item"><span class="info-label">SIGNATURE:</span><div class="info-field"></div></div>
                </div>
            </div>
        </div>
        
        <!-- Instructions -->
        <div class="instructions">
            <div class="instructions-title">Instructions to candidates</div>
            <ol style="font-style: italic; list-style: none; counter-reset: list-counter; margin-left: 20px;">
"""
        
        # Add instructions
        for idx, instruction in enumerate(instructions, 1):
            # Make 'all' related instructions bold
            is_bold = 'all' in instruction.lower()
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
    def _generate_marking_grid(total_questions, question_marks, total_marks):
        """
        Generate marking grid HTML for English Paper 1
        
        Based on screenshot, the grid structure is:
        - Individual rows for each question (1-3)
        - Each row shows: Question number | Maximum Score | Candidate's Score
        - Total Score row at bottom
        
        Args:
            total_questions (int): Number of questions
            question_marks (list): List of marks per question
            total_marks (int): Total marks for the paper
        
        Returns:
            str: HTML for marking grid
        """
        
        # Ensure question_marks list has enough values
        if len(question_marks) < total_questions:
            question_marks.extend([10] * (total_questions - len(question_marks)))
        
        grid_html = """
            <table class="marking-grid">
                <thead>
                    <tr>
                        <th>Question</th>
                        <th>Maximum<br>Score</th>
                        <th>Candidate's<br>Score</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        # Individual question rows
        for i in range(1, total_questions + 1):
            marks = question_marks[i - 1] if i <= len(question_marks) else 10
            grid_html += f"""
                    <tr>
                        <td>{i}</td>
                        <td>{marks}</td>
                        <td></td>
                    </tr>
"""
        
        # Total Score row
        grid_html += f"""
                    <tr class="total-row">
                        <td colspan="2">Total Score</td>
                        <td></td>
                    </tr>
                </tbody>
            </table>
        """
        
        return grid_html
    
    @staticmethod
    def generate_default_coverpage_data(generated_paper, paper):
        """
        Generate default coverpage data for English Paper 1
        
        Args:
            generated_paper: GeneratedPaper instance
            paper: Paper instance
        
        Returns:
            dict: Default coverpage data for English Paper 1
        """
        # Generate paper name
        paper_name_upper = paper.name.upper()
        subject_name_upper = paper.subject.name.upper()
        
        if subject_name_upper in paper_name_upper:
            display_paper_name = paper_name_upper
        else:
            display_paper_name = f'{subject_name_upper} {paper_name_upper}'
        
        # Get metadata for question details
        metadata = getattr(generated_paper, 'metadata', {}) or {}
        total_questions = metadata.get('total_questions', 3)
        
        # Default marks distribution (based on screenshot: 20, 10, 30)
        question_marks = metadata.get('question_marks', [20, 10, 30])
        
        # Calculate total pages
        total_pages = 8  # Standard for English Paper 1
        
        return {
            'school_name': 'EXAMINATION CENTRE',
            'school_logo': '/exam.png',
            'logo_position': 'center',
            'class_name': '',
            'exam_title': 'END TERM EXAMINATION 2025',
            'paper_name': display_paper_name,
            'paper_type': 'Paper 1',
            'total_questions': total_questions,
            'question_marks': question_marks,
            'total_marks': generated_paper.total_marks or 60,
            'time_allocation': format_time_allocation(paper.time_allocation),
            'total_pages': total_pages,
            'instructions': [
                'Write your name and admission number in the spaces provided above.',
                'Sign and write the date of examination in the spaces provided above.',
                'Answer all the questions in this paper.',
                'All your answers must be written in the question paper.',
                f'This paper consists of {total_pages} printed pages.',
                'Candidates should check the question paper to ascertain that all the pages are printed as indicated and that no questions are missing.',
                'Candidates must answer the questions in English.'
            ],
            'date': datetime.now().strftime('%Y-%m-%d'),
            'candidate_name_field': True,
            'candidate_number_field': True,
            'date_field': True
        }


class EnglishPaper2Coverpage:
    """
    English Paper 2 Coverpage Template
    Includes simple marking grid with individual questions
    """
    
    @staticmethod
    def generate_html(data):
        """
        Generate HTML for English Paper 2 coverpage
        
        Args:
            data (dict): Coverpage data with keys:
                - school_name: Name of the school
                - school_logo: Base64 encoded logo or URL
                - exam_title: e.g., "END TERM 3 EXAMINATION 2025"
                - paper_name: e.g., "ENGLISH PAPER 2"
                - total_questions: Number of questions (default: 4)
                - question_marks: List of marks per question (default: [20, 25, 20, 15])
                - total_marks: Total marks (default: 80)
                - time_allocation: Time in minutes
                - total_pages: Total pages
        
        Returns:
            str: HTML content for coverpage
        """
        
        # Extract data with defaults
        school_name = data.get('school_name', 'EXAMINATION CENTRE')
        school_logo = data.get('school_logo', '/exam.png')
        logo_position = data.get('logo_position', 'center')
        class_name = data.get('class_name', '')
        exam_title = data.get('exam_title', 'END TERM EXAMINATION 2025')
        paper_name = data.get('paper_name', 'ENGLISH PAPER 2')
        
        # Question configuration (from screenshot)
        total_questions = data.get('total_questions', 4)
        question_marks = data.get('question_marks', [20, 25, 20, 15])
        total_marks = data.get('total_marks', 80)
        time_allocation = data.get('time_allocation', '2 HOURS 30 MINUTES')
        
        # Calculate total pages
        total_pages = data.get('total_pages', 8)
        
        instructions = data.get('instructions', [
            'Write your name and admission number in the spaces provided above.',
            'Sign and write the date of examination in the spaces provided above.',
            'Answer all the questions in this question paper.',
            'All your answers must be written in the spaces provided in this question paper.',
            f'This paper consists of 12 printed pages.',
            'Candidates should check the question paper to ascertain that all the pages are printed as indicated and that no questions are missing.',
            'Candidates must answer the questions in English.'
        ])
        
        exam_date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        show_name = data.get('candidate_name_field', True)
        show_number = data.get('candidate_number_field', True)
        show_date = data.get('date_field', True)
        
        # Generate marking grid for English Paper 2
        marking_grid_html = EnglishPaper2Coverpage._generate_marking_grid(
            total_questions, question_marks, total_marks
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
            width: 50%;
            margin: 0 auto;
            border-collapse: collapse;
            border: 2px solid black;
        }}
        
        .marking-grid th,
        .marking-grid td {{
            border: 1px solid black;
            text-align: center;
            font-size: 12px;
            padding: 10px 8px;
        }}
        
        .marking-grid th {{
            background-color: #f0f0f0;
            font-weight: bold;
        }}
        
        .total-row {{
            background-color: #e0e0e0;
            font-weight: bold;
            font-size: 13px;
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
                <div class="info-row-grid">
                    {f'<div class="info-row-item"><span class="info-label">ADM NO:</span><div class="info-field"></div></div>' if show_number else ''}
                    <div class="info-row-item"><span class="info-label">CLASS:</span><div class="info-field"></div></div>
                </div>
                <div class="info-row-grid">
                    {f'<div class="info-row-item"><span class="info-label">DATE:</span><div class="info-field"></div></div>' if show_date else ''}
                    <div class="info-row-item"><span class="info-label">SIGNATURE:</span><div class="info-field"></div></div>
                </div>
            </div>
        </div>
        
        <!-- Instructions -->
        <div class="instructions">
            <div class="instructions-title">Instructions to candidates</div>
            <ol style="font-style: italic; list-style: none; counter-reset: list-counter; margin-left: 20px;">
"""
        
        # Add instructions
        for idx, instruction in enumerate(instructions, 1):
            # Make 'all' and specific instructions bold
            is_bold = 'all' in instruction.lower() or 'check' in instruction.lower()
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
    def _generate_marking_grid(total_questions, question_marks, total_marks):
        """
        Generate marking grid HTML for English Paper 2
        
        Based on screenshot, the grid structure is:
        - Individual rows for each question (1-4)
        - Each row shows: Question number | Maximum Score | Candidate's Score
        - Total Score row at bottom
        
        Args:
            total_questions (int): Number of questions
            question_marks (list): List of marks per question
            total_marks (int): Total marks for the paper
        
        Returns:
            str: HTML for marking grid
        """
        
        # Ensure question_marks list has enough values
        if len(question_marks) < total_questions:
            question_marks.extend([10] * (total_questions - len(question_marks)))
        
        grid_html = """
            <table class="marking-grid">
                <thead>
                    <tr>
                        <th>Question</th>
                        <th>Maximum<br>Score</th>
                        <th>Candidate's<br>Score</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        # Individual question rows
        for i in range(1, total_questions + 1):
            marks = question_marks[i - 1] if i <= len(question_marks) else 10
            grid_html += f"""
                    <tr>
                        <td>{i}</td>
                        <td>{marks}</td>
                        <td></td>
                    </tr>
"""
        
        # Total Score row
        grid_html += f"""
                    <tr class="total-row">
                        <td colspan="2">Total Score</td>
                        <td></td>
                    </tr>
                </tbody>
            </table>
        """
        
        return grid_html
    
    @staticmethod
    def generate_default_coverpage_data(generated_paper, paper):
        """
        Generate default coverpage data for English Paper 2
        
        Args:
            generated_paper: GeneratedPaper instance
            paper: Paper instance
        
        Returns:
            dict: Default coverpage data for English Paper 2
        """
        # Generate paper name
        paper_name_upper = paper.name.upper()
        subject_name_upper = paper.subject.name.upper()
        
        if subject_name_upper in paper_name_upper:
            display_paper_name = paper_name_upper
        else:
            display_paper_name = f'{subject_name_upper} {paper_name_upper}'
        
        # Get metadata for question details
        metadata = getattr(generated_paper, 'metadata', {}) or {}
        total_questions = metadata.get('total_questions', 4)
        
        # Default marks distribution (based on screenshot: 20, 25, 20, 15)
        question_marks = metadata.get('question_marks', [20, 25, 20, 15])
        
        # Calculate total pages
        total_pages = 12  # Standard for English Paper 2 (as per instructions)
        
        return {
            'school_name': 'EXAMINATION CENTRE',
            'school_logo': '/exam.png',
            'logo_position': 'center',
            'class_name': '',
            'exam_title': 'END TERM EXAMINATION 2025',
            'paper_name': display_paper_name,
            'paper_type': 'Paper 2',
            'total_questions': total_questions,
            'question_marks': question_marks,
            'total_marks': generated_paper.total_marks or 80,
            'time_allocation': format_time_allocation(paper.time_allocation),
            'total_pages': total_pages,
            'instructions': [
                'Write your name and admission number in the spaces provided above.',
                'Sign and write the date of examination in the spaces provided above.',
                'Answer all the questions in this question paper.',
                'All your answers must be written in the spaces provided in this question paper.',
                f'This paper consists of {total_pages} printed pages.',
                'Candidates should check the question paper to ascertain that all the pages are printed as indicated and that no questions are missing.',
                'Candidates must answer the questions in English.'
            ],
            'date': datetime.now().strftime('%Y-%m-%d'),
            'candidate_name_field': True,
            'candidate_number_field': True,
            'date_field': True
        }
        
    
class EnglishPaper3Coverpage:
    """
    English Paper 3 Coverpage Template
    Includes simple marking grid with individual questions
    """
    
    @staticmethod
    def generate_html(data):
        """
        Generate HTML for English Paper 3 coverpage
        
        Args:
            data (dict): Coverpage data with keys:
                - school_name: Name of the school
                - school_logo: Base64 encoded logo or URL
                - exam_title: e.g., "END TERM 3 EXAMINATION 2025"
                - paper_name: e.g., "ENGLISH PAPER 3"
                - total_questions: Number of questions (default: 3)
                - question_marks: List of marks per question (default: [20, 20, 20])
                - total_marks: Total marks (default: 60)
                - time_allocation: Time in minutes (default: 150 for 2 hours 30 minutes)
                - total_pages: Total pages
        
        Returns:
            str: HTML content for coverpage
        """
        
        # Extract data with defaults
        school_name = data.get('school_name', 'EXAMINATION CENTRE')
        school_logo = data.get('school_logo', '/exam.png')
        logo_position = data.get('logo_position', 'center')
        class_name = data.get('class_name', '')
        exam_title = data.get('exam_title', 'END TERM EXAMINATION 2025')
        paper_name = data.get('paper_name', 'ENGLISH PAPER 3')
        
        # Question configuration (from screenshot)
        total_questions = data.get('total_questions', 3)
        question_marks = data.get('question_marks', [20, 20, 20])
        total_marks = data.get('total_marks', 60)
        time_allocation = data.get('time_allocation', '2 HOURS 30 MINUTES')
        
        # Calculate total pages
        total_pages = data.get('total_pages', 16)
        
        instructions = data.get('instructions', [
            'Write your name and admission number in the spaces provided above.',
            'Sign and write the date of examination in the spaces provided above.',
            'Answer three questions only.',
            'Questions 1 and 2 are compulsory.',
            'In question 3 choose only one of the optional set texts you have prepared on.',
            'Where a candidate presents work on more than one optional set text, only the first one to appear will be marked.',
            'Each of your essays must not exceed 450 words.',
            'All your answers must be written in the spaces provided in this question paper.',
            f'This paper consists of {total_pages} printed pages.',
            'Candidates should check the question paper to ascertain that all the pages are printed as indicated and that no questions are missing.',
            'Candidates must answer the questions in English.'
        ])
        
        exam_date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        show_name = data.get('candidate_name_field', True)
        show_number = data.get('candidate_number_field', True)
        show_date = data.get('date_field', True)
        
        # Generate marking grid for English Paper 3
        marking_grid_html = EnglishPaper3Coverpage._generate_marking_grid(
            total_questions, question_marks, total_marks
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
            width: 50%;
            margin: 0 auto;
            border-collapse: collapse;
            border: 2px solid black;
        }}
        
        .marking-grid th,
        .marking-grid td {{
            border: 1px solid black;
            text-align: center;
            font-size: 12px;
            padding: 10px 8px;
        }}
        
        .marking-grid th {{
            background-color: #f0f0f0;
            font-weight: bold;
        }}
        
        .total-row {{
            background-color: #e0e0e0;
            font-weight: bold;
            font-size: 13px;
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
                <div class="info-row-grid">
                    {f'<div class="info-row-item"><span class="info-label">ADM NO:</span><div class="info-field"></div></div>' if show_number else ''}
                    <div class="info-row-item"><span class="info-label">CLASS:</span><div class="info-field"></div></div>
                </div>
                <div class="info-row-grid">
                    {f'<div class="info-row-item"><span class="info-label">DATE:</span><div class="info-field"></div></div>' if show_date else ''}
                    <div class="info-row-item"><span class="info-label">SIGNATURE:</span><div class="info-field"></div></div>
                </div>
            </div>
        </div>
        
        <!-- Instructions -->
        <div class="instructions">
            <div class="instructions-title">Instructions to candidates</div>
            <ol style="font-style: italic; list-style: none; counter-reset: list-counter; margin-left: 20px;">
"""
        
        # Add instructions
        for idx, instruction in enumerate(instructions, 1):
            # Make specific instructions bold (questions, word limit, checking pages)
            is_bold = ('three' in instruction.lower() or 
                      'compulsory' in instruction.lower() or 
                      'not exceed' in instruction.lower() or
                      'check' in instruction.lower())
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
    def _generate_marking_grid(total_questions, question_marks, total_marks):
        """
        Generate marking grid HTML for English Paper 3
        
        Based on screenshot, the grid structure is:
        - Individual rows for each question (1-3)
        - Each row shows: Question number | Maximum Score | Candidate's Score
        - Total Score row at bottom
        
        Args:
            total_questions (int): Number of questions
            question_marks (list): List of marks per question
            total_marks (int): Total marks for the paper
        
        Returns:
            str: HTML for marking grid
        """
        
        # Ensure question_marks list has enough values
        if len(question_marks) < total_questions:
            question_marks.extend([20] * (total_questions - len(question_marks)))
        
        grid_html = """
            <table class="marking-grid">
                <thead>
                    <tr>
                        <th>Question</th>
                        <th>Maximum<br>Score</th>
                        <th>Candidate's<br>Score</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        # Individual question rows
        for i in range(1, total_questions + 1):
            marks = question_marks[i - 1] if i <= len(question_marks) else 20
            grid_html += f"""
                    <tr>
                        <td>{i}</td>
                        <td>{marks}</td>
                        <td></td>
                    </tr>
"""
        
        # Total Score row
        grid_html += f"""
                    <tr class="total-row">
                        <td colspan="2">Total Score</td>
                        <td></td>
                    </tr>
                </tbody>
            </table>
        """
        
        return grid_html
    
    @staticmethod
    def generate_default_coverpage_data(generated_paper, paper):
        """
        Generate default coverpage data for English Paper 3
        
        Args:
            generated_paper: GeneratedPaper instance
            paper: Paper instance
        
        Returns:
            dict: Default coverpage data for English Paper 3
        """
        # Generate paper name
        paper_name_upper = paper.name.upper()
        subject_name_upper = paper.subject.name.upper()
        
        if subject_name_upper in paper_name_upper:
            display_paper_name = paper_name_upper
        else:
            display_paper_name = f'{subject_name_upper} {paper_name_upper}'
        
        # Get metadata for question details
        metadata = getattr(generated_paper, 'metadata', {}) or {}
        total_questions = metadata.get('total_questions', 3)
        
        # Default marks distribution (based on screenshot: 20, 20, 20)
        question_marks = metadata.get('question_marks', [20, 20, 20])
        
        # Calculate total pages
        total_pages = 16  # Standard for English Paper 3
        
        return {
            'school_name': 'EXAMINATION CENTRE',
            'school_logo': '/exam.png',
            'logo_position': 'center',
            'class_name': '',
            'exam_title': 'END TERM EXAMINATION 2025',
            'paper_name': display_paper_name,
            'paper_type': 'Paper 3',
            'total_questions': total_questions,
            'question_marks': question_marks,
            'total_marks': generated_paper.total_marks or 60,
            'time_allocation': format_time_allocation(paper.time_allocation),
            'total_pages': total_pages,
            'instructions': [
                'Write your name and admission number in the spaces provided above.',
                'Sign and write the date of examination in the spaces provided above.',
                'Answer three questions only.',
                'Questions 1 and 2 are compulsory.',
                'In question 3 choose only one of the optional set texts you have prepared on.',
                'Where a candidate presents work on more than one optional set text, only the first one to appear will be marked.',
                'Each of your essays must not exceed 450 words.',
                'All your answers must be written in the spaces provided in this question paper.',
                f'This paper consists of {total_pages} printed pages.',
                'Candidates should check the question paper to ascertain that all the pages are printed as indicated and that no questions are missing.',
                'Candidates must answer the questions in English.'
            ],
            'date': datetime.now().strftime('%Y-%m-%d'),
            'candidate_name_field': True,
            'candidate_number_field': True,
            'date_field': True
        }


class KiswahiliPaper2Coverpage:
    """
    Kiswahili Paper 2 Coverpage Template
    Includes sectioned marking grid (4 sections: Ufhamu, Ufupisho, Matumizi ya Lugha, Isimu Jamii)
    """
    
    @staticmethod
    def generate_html(data):
        """
        Generate HTML for Kiswahili Paper 2 coverpage
        
        Args:
            data (dict): Coverpage data with keys:
                - school_name: Name of the school
                - school_logo: Base64 encoded logo or URL
                - exam_title: e.g., "MTIHANI WA MWISHO WA MUHULA 2025"
                - paper_name: e.g., "KISWAHILI KARATASI YA PILI"
                - section_1_marks: Marks for Ufhamu (default: 15)
                - section_2_marks: Marks for Ufupisho (default: 15)
                - section_3_marks: Marks for Matumizi ya Lugha (default: 40)
                - section_4_marks: Marks for Isimu Jamii (default: 10)
                - total_marks: Total marks (default: 80)
                - time_allocation: Time in minutes
                - total_pages: Total pages
        
        Returns:
            str: HTML content for coverpage
        """
        
        # Extract data with defaults
        school_name = data.get('school_name', 'KITUO CHA MTIHANI')
        school_logo = data.get('school_logo', '/exam.png')
        logo_position = data.get('logo_position', 'center')
        class_name = data.get('class_name', '')
        exam_title = data.get('exam_title', 'MTIHANI WA MWISHO WA MUHULA 2025')
        paper_name = data.get('paper_name', 'KISWAHILI KARATASI YA PILI')
        
        # Section configuration (from screenshot)
        section_1_marks = data.get('section_1_marks', 15)  # Ufhamu
        section_2_marks = data.get('section_2_marks', 15)  # Ufupisho
        section_3_marks = data.get('section_3_marks', 40)  # Matumizi ya Lugha
        section_4_marks = data.get('section_4_marks', 10)  # Isimu Jamii
        total_marks = data.get('total_marks', 80)
        time_allocation = data.get('time_allocation', '2 HOURS 30 MINUTES')
        
        # Calculate total pages
        total_pages = data.get('total_pages', 16)
        
        instructions = data.get('instructions', [
            'Andika jina lako na nambari yako ya mtihani katika nafasi zilizotolewa hapa juu.',
            'Tia sahihi sasa kisha uandike tarehe ya mtihani katika nafasi zilizotolewa hapa juu.',
            'Jibu maswali yote.',
            'Majibu yako yaandikwe katika nafasi zilizotolewa katika kijitabu hiki cha maswali.',
            'Punguzo la alama hata kwa swali moja halitakubalika.',
            'Karatasi hii ina kurasa 12 zilizochapwa.',
            'Wagombea wanafaa kuziangalia karatasi zote ili zithibitishe chapa zote zimefanyika kama zilivyoorodheshwa na kuwa hakuna maswali yote yanaonekana.',
            'Wagombea wanapaswa kujibu maswali kwa Kiswahili sanifu.'
        ])
        
        exam_date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        show_name = data.get('candidate_name_field', True)
        show_number = data.get('candidate_number_field', True)
        show_date = data.get('date_field', True)
        
        # Generate marking grid for Kiswahili Paper 2
        marking_grid_html = KiswahiliPaper2Coverpage._generate_marking_grid(
            section_1_marks, section_2_marks, section_3_marks, section_4_marks, total_marks
        )
        
        # Build HTML
        html = f"""
<!DOCTYPE html>
<html lang="sw">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{paper_name} - Ukurasa wa Mbele</title>
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
        
        .header {{
            text-align: {logo_position};
            margin-bottom: 15px;
            border-bottom: 3px solid black;
            padding-bottom: 10px;
        }}
        
        .school-logo {{
            max-width: 80px;
            max-height: 80px;
            margin-bottom: 5px;
        }}
        
        .school-name {{
            font-size: 16pt;
            font-weight: bold;
            text-transform: uppercase;
            margin-bottom: 3px;
        }}
        
        .class-name {{
            font-size: 12pt;
            font-weight: bold;
            margin-top: 5px;
        }}
        
        .exam-title {{
            font-size: 13pt;
            font-weight: bold;
            text-align: left;
            margin: 15px 0;
            text-transform: uppercase;
        }}
        
        .paper-title {{
            font-size: 14pt;
            font-weight: bold;
            text-align: left;
            margin: 15px 0;
            text-transform: uppercase;
        }}
        
        .paper-details {{
            text-align: left;
            margin: 15px 0;
            font-size: 11pt;
        }}
        
        .candidate-info {{
            margin: 20px 0;
            border: 2px solid black;
            padding: 15px;
        }}
        
        .info-row {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 15px;
            align-items: center;
        }}
        
        .info-row-full {{
            display: flex;
            margin-bottom: 15px;
            align-items: center;
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
            min-width: 150px;
        }}
        
        .info-field {{
            flex: 1;
            border-bottom: 1px solid black;
            min-height: 30px;
            margin-left: 10px;
        }}
        
        .instructions {{
            margin: 20px 0;
        }}
        
        .instructions-title {{
            font-size: 13pt;
            font-weight: bold;
            margin-bottom: 10px;
            text-transform: uppercase;
        }}
        
        .instructions-list {{
            list-style-position: outside;
            padding-left: 25px;
        }}
        
        .instructions-list li {{
            margin-bottom: 8px;
            line-height: 1.4;
        }}
        
        .marking-section {{
            margin-top: 25px;
            page-break-inside: avoid;
        }}
        
        .marking-title {{
            font-size: 11pt;
            font-weight: bold;
            text-align: center;
            margin-bottom: 10px;
        }}
        
        .marking-grid {{
            width: 100%;
            border-collapse: collapse;
            margin: 0 auto;
            max-width: 400px;
        }}
        
        .marking-grid th,
        .marking-grid td {{
            border: 2px solid black;
            padding: 10px;
            text-align: center;
            font-size: 11pt;
        }}
        
        .marking-grid th {{
            background-color: #f0f0f0;
            font-weight: bold;
        }}
        
        .marking-grid .section-cell {{
            text-align: center;
            font-weight: bold;
        }}
        
        .marking-grid .marks-cell {{
            text-align: center;
        }}
        
        .marking-grid .answer-cell {{
            background-color: white;
            min-height: 40px;
        }}
        
        .marking-grid .total-row {{
            font-weight: bold;
            background-color: #f0f0f0;
        }}
        
        @media print {{
            .coverpage {{
                page-break-after: always;
            }}
            
            body {{
                print-color-adjust: exact;
                -webkit-print-color-adjust: exact;
            }}
        }}
    </style>
</head>
<body>
    <div class="coverpage">
        <!-- Header with Logo and School Name -->
        <div class="header">
            <img src="{school_logo}" alt="School Logo" class="school-logo">
            <div class="school-name">{school_name}</div>
            {f'<div class="class-name">{class_name}</div>' if class_name else ''}
            <!-- Exam Title -->
        <div class="exam-title">{exam_title}</div>
        
        <!-- Paper Title -->
        <div class="paper-title" >{paper_name}</div>
        
        <!-- Paper Details (Time and Total Marks) -->
        <div class="paper-details" >
            <strong>Muda:</strong> {time_allocation}<br>
        </div>
        </div>
        
        
        
        <!-- Candidate Information Box -->
        <div class="candidate-info">
            {f'''<div class="info-row-full">
                <span class="info-label">Jina la Mwanafunzi:</span>
                <div class="info-field"></div>
            </div>''' if show_name else ''}
            
            <div class="info-row-grid">
                {f'''<div class="info-row-item">
                    <span class="info-label">Nambari ya Usajili:</span>
                    <div class="info-field"></div>
                </div>''' if show_number else ''}
                
                <div class="info-row-item">
                    <span class="info-label">Darasa:</span>
                    <div class="info-field"></div>
                </div>
            </div>
            
            <div class="info-row-grid">
                {f'''<div class="info-row-item">
                    <span class="info-label">Tarehe:</span>
                    <div class="info-field"></div>
                </div>''' if show_date else ''}
                
                <div class="info-row-item">
                    <span class="info-label">Sahihi ya Mwanafunzi:</span>
                    <div class="info-field"></div>
                </div>
            </div>
        </div>
        
        <!-- Instructions -->
        <div class="instructions">
            <div class="instructions-title">Maagizo</div>
            <ol class="instructions-list" style="font-style: italic;">
"""
        
        # Add instructions
        for instruction in instructions:
            html += f'                <li>{instruction}</li>\n'
        
        html += f"""
            </ol>
        </div>
        
        <!-- Marking Grid Section -->
        <div class="marking-section">
            <div class="marking-title">Kwa matumizi ya mtahini peke yake</div>
            {marking_grid_html}
        </div>
    </div>
</body>
</html>
"""
        
        return html
    
    @staticmethod
    def _generate_marking_grid(section_1_marks, section_2_marks, section_3_marks, section_4_marks, total_marks):
        """
        Generate marking grid HTML for Kiswahili Paper 2
        
        Based on screenshot, the grid structure is:
        - 4 sections: Ufhamu (15), Ufupisho (15), Matumizi ya Lugha (40), Isimu Jamii (10)
        - Each row shows: Sehemu (Section) | Upeo (Range) | Alama (Marks)
        - Total row (JUMLA) at bottom showing 80 marks
        
        Args:
            section_1_marks (int): Marks for Ufhamu
            section_2_marks (int): Marks for Ufupisho
            section_3_marks (int): Marks for Matumizi ya Lugha
            section_4_marks (int): Marks for Isimu Jamii
            total_marks (int): Total marks for the paper
        
        Returns:
            str: HTML for marking grid
        """
        
        grid_html = f"""
            <table class="marking-grid">
                <thead>
                    <tr>
                        <th>Sehemu</th>
                        <th>Upeo</th>
                        <th>Alama</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td class="section-cell">1</td>
                        <td class="marks-cell">{section_1_marks}</td>
                        <td class="answer-cell"></td>
                    </tr>
                    <tr>
                        <td class="section-cell">2</td>
                        <td class="marks-cell">{section_2_marks}</td>
                        <td class="answer-cell"></td>
                    </tr>
                    <tr>
                        <td class="section-cell">3</td>
                        <td class="marks-cell">{section_3_marks}</td>
                        <td class="answer-cell"></td>
                    </tr>
                    <tr>
                        <td class="section-cell">4</td>
                        <td class="marks-cell">{section_4_marks}</td>
                        <td class="answer-cell"></td>
                    </tr>
                    <tr class="total-row">
                        <td colspan="2">JUMLA</td>
                        <td>{total_marks}</td>
                    </tr>
                </tbody>
            </table>
        """
        
        return grid_html
    
    @staticmethod
    def generate_default_coverpage_data(generated_paper, paper):
        """
        Generate default coverpage data for Kiswahili Paper 2
        
        Args:
            generated_paper: GeneratedPaper instance
            paper: Paper instance
        
        Returns:
            dict: Default coverpage data for Kiswahili Paper 2
        """
        # Generate paper name
        paper_name_upper = paper.name.upper()
        subject_name_upper = paper.subject.name.upper()
        
        if subject_name_upper in paper_name_upper:
            display_paper_name = paper_name_upper
        else:
            display_paper_name = f'{subject_name_upper} {paper_name_upper}'
        
        # Get metadata for section details
        metadata = getattr(generated_paper, 'metadata', {}) or {}
        section_1_marks = metadata.get('section_1_marks', 15)
        section_2_marks = metadata.get('section_2_marks', 15)
        section_3_marks = metadata.get('section_3_marks', 40)
        section_4_marks = metadata.get('section_4_marks', 10)
        
        # Calculate total pages
        total_pages = 16  # Standard for Kiswahili Paper 2
        
        return {
            'school_name': 'KITUO CHA MTIHANI',
            'school_logo': '/exam.png',
            'logo_position': 'center',
            'class_name': '',
            'exam_title': 'MTIHANI WA MWISHO WA MUHULA 2025',
            'paper_name': display_paper_name,
            'paper_type': 'Karatasi ya Pili',
            'section_1_marks': section_1_marks,
            'section_2_marks': section_2_marks,
            'section_3_marks': section_3_marks,
            'section_4_marks': section_4_marks,
            'total_marks': generated_paper.total_marks or 80,
            'time_allocation': format_time_allocation(paper.time_allocation),
            'total_pages': total_pages,
            'instructions': [
                'Andika jina lako na nambari yako ya mtihani katika nafasi zilizotolewa hapa juu.',
                'Tia sahihi sasa kisha uandike tarehe ya mtihani katika nafasi zilizotolewa hapa juu.',
                'Jibu maswali yote.',
                'Majibu yako yaandikwe katika nafasi zilizotolewa katika kijitabu hiki cha maswali.',
                'Punguzo la alama hata kwa swali moja halitakubalika.',
                f'Karatasi hii ina kurasa {total_pages} zilizochapwa.',
                'Wagombea wanafaa kuziangalia karatasi zote ili zithibitishe chapa zote zimefanyika kama zilivyoorodheshwa na kuwa hakuna maswali yote yanaonekana.',
                'Wagombea wanapaswa kujibu maswali kwa Kiswahili sanifu.'
            ],
            'date': datetime.now().strftime('%Y-%m-%d'),
            'candidate_name_field': True,
            'candidate_number_field': True,
            'date_field': True
        }



class KiswahiliPaper1Coverpage:
    """
    Kiswahili Paper 1 Coverpage Template
    Question 1 is compulsory, choose 1 from remaining 3 questions
    """
    
    @staticmethod
    def generate_html(data):
        """
        Generate HTML for Kiswahili Paper 1 coverpage
        
        Args:
            data (dict): Coverpage data with keys:
                - school_name: Name of the school
                - school_logo: Base64 encoded logo or URL
                - exam_title: e.g., "MTIHANI WA MWISHO WA MUHULA 2025"
                - paper_name: e.g., "KISWAHILI KARATASI YA KWANZA"
                - question_1_marks: Marks for Question 1 (default: 20)
                - question_2_4_marks: Marks for Questions 2-4 (default: 20)
                - total_marks: Total marks (default: 40)
                - time_allocation: Time in minutes
                - total_pages: Total pages
        
        Returns:
            str: HTML content for coverpage
        """
        
        # Extract data with defaults
        school_name = data.get('school_name', 'KITUO CHA MTIHANI')
        school_logo = data.get('school_logo', '/exam.png')
        logo_position = data.get('logo_position', 'center')
        class_name = data.get('class_name', '')
        exam_title = data.get('exam_title', 'MTIHANI WA MWISHO WA MUHULA 2025')
        paper_name = data.get('paper_name', 'KISWAHILI KARATASI YA KWANZA')
        
        # Question configuration (from screenshot)
        question_1_marks = data.get('question_1_marks', 20)  # Compulsory
        question_2_4_marks = data.get('question_2_4_marks', 20)  # Choose 1 from 3
        total_marks = data.get('total_marks', 40)
        time_allocation = data.get('time_allocation', '2 HOURS 30 MINUTES')
        
        # Calculate total pages
        total_pages = data.get('total_pages', 12)
        
        instructions = data.get('instructions', [
            'Andika jina lako na nambari yako ya mtihani katika nafasi ulizoachiwa hapa juu.',
            'Tia sahihi sasa uandike tarehe ya mtihani katika nafasi zilizoochiwa hapa juu.',
            'Andika insha mbili. Insha ya kwanza ni ya lazima.',
            'Kisha chagua insha nyingine moja kati ya hizo tatu zilizobakia.',
            'Kila insha isipungue maneno 450.',
            'Kila insha ina alama 20.',
            'Jibu maswali kwenye andikwe kwa lugha ya Kiswahili.',
            'Insha zote sharti zandikwe katika nafasi ulizoachibwa katika kijitabu hiki cha maswali.',
            'Karatasi hii ina kurasa 12 zilizopigwa chapa.',
            'Watahiniwa ni lazima wahakikishe kwamba kurasa zote za karatasi hii zimepigwa chapa sawasawa na kuwa maswali yote yamo.'
        ])
        
        exam_date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        show_name = data.get('candidate_name_field', True)
        show_number = data.get('candidate_number_field', True)
        show_date = data.get('date_field', True)
        
        # Generate marking grid for Kiswahili Paper 1
        marking_grid_html = KiswahiliPaper1Coverpage._generate_marking_grid(
            question_1_marks, question_2_4_marks, total_marks
        )
        
        # Build HTML
        html = f"""
<!DOCTYPE html>
<html lang="sw">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{paper_name} - Ukurasa wa Mbele</title>
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
        
        .header {{
            text-align: {logo_position};
            margin-bottom: 15px;
            border-bottom: 3px solid black;
            padding-bottom: 10px;
        }}
        
        .school-logo {{
            max-width: 80px;
            max-height: 80px;
            margin-bottom: 5px;
        }}
        
        .school-name {{
            font-size: 16pt;
            font-weight: bold;
            text-transform: uppercase;
            margin-bottom: 3px;
        }}
        
        .class-name {{
            font-size: 12pt;
            font-weight: bold;
            margin-top: 5px;
        }}
        
        .exam-title {{
            font-size: 13pt;
            font-weight: bold;
            text-align: left;
            margin: 15px 0;
            text-transform: uppercase;
        }}
        
        .paper-title {{
            font-size: 14pt;
            font-weight: bold;
            text-align: left;
            margin: 15px 0;
            text-transform: uppercase;
        }}
        
        .paper-details {{
            text-align: left;
            margin: 15px 0;
            font-size: 11pt;
        }}
        
        .candidate-info {{
            margin: 20px 0;
            border: 2px solid black;
            padding: 15px;
        }}
        
        .info-row {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 15px;
            align-items: center;
        }}
        
        .info-row-full {{
            display: flex;
            margin-bottom: 15px;
            align-items: center;
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
            min-width: 150px;
        }}
        
        .info-field {{
            flex: 1;
            border-bottom: 1px solid black;
            min-height: 30px;
            margin-left: 10px;
        }}
        
        .instructions {{
            margin: 20px 0;
        }}
        
        .instructions-title {{
            font-size: 13pt;
            font-weight: bold;
            margin-bottom: 10px;
            text-transform: uppercase;
        }}
        
        .instructions-list {{
            list-style-position: outside;
            padding-left: 25px;
        }}
        
        .instructions-list li {{
            margin-bottom: 8px;
            line-height: 1.4;
        }}
        
        .instructions-list li strong {{
            font-weight: bold;
        }}
        
        .marking-section {{
            margin-top: 25px;
            page-break-inside: avoid;
        }}
        
        .marking-title {{
            font-size: 11pt;
            font-weight: bold;
            text-align: center;
            margin-bottom: 10px;
        }}
        
        .marking-grid {{
            width: 100%;
            border-collapse: collapse;
            margin: 0 auto;
            max-width: 400px;
        }}
        
        .marking-grid th,
        .marking-grid td {{
            border: 2px solid black;
            padding: 10px;
            text-align: center;
            font-size: 11pt;
        }}
        
        .marking-grid th {{
            background-color: #f0f0f0;
            font-weight: bold;
        }}
        
        .marking-grid .question-cell {{
            text-align: center;
            font-weight: bold;
        }}
        
        .marking-grid .marks-cell {{
            text-align: center;
        }}
        
        .marking-grid .answer-cell {{
            background-color: white;
            min-height: 40px;
        }}
        
        .marking-grid .total-row {{
            font-weight: bold;
            background-color: #f0f0f0;
        }}
        
        @media print {{
            .coverpage {{
                page-break-after: always;
            }}
            
            body {{
                print-color-adjust: exact;
                -webkit-print-color-adjust: exact;
            }}
        }}
    </style>
</head>
<body>
    <div class="coverpage">
        <!-- Header with Logo and School Name -->
        <div class="header">
            <img src="{school_logo}" alt="School Logo" class="school-logo">
            <div class="school-name">{school_name}</div>
            {f'<div class="class-name">{class_name}</div>' if class_name else ''}
            <!-- Exam Title -->
        <div class="exam-title">{exam_title}</div>
        
        <!-- Paper Title -->
        <div class="paper-title">{paper_name}</div>
        
        <!-- Paper Details (Time and Total Marks) -->
        <div class="paper-details">
            <strong>Muda:</strong> {time_allocation}<br>
        </div>
        </div>
        
        
        
        <!-- Candidate Information Box -->
        <div class="candidate-info">
            {f'''<div class="info-row-full">
                <span class="info-label">Jina la Mwanafunzi:</span>
                <div class="info-field"></div>
            </div>''' if show_name else ''}
            
            <div class="info-row-grid">
                {f'''<div class="info-row-item">
                    <span class="info-label">Nambari ya Mtihani:</span>
                    <div class="info-field"></div>
                </div>''' if show_number else ''}
                
                <div class="info-row-item">
                    <span class="info-label">Darasa:</span>
                    <div class="info-field"></div>
                </div>
            </div>
            
            <div class="info-row-grid">
                {f'''<div class="info-row-item">
                    <span class="info-label">Tarehe:</span>
                    <div class="info-field"></div>
                </div>''' if show_date else ''}
                
                <div class="info-row-item">
                    <span class="info-label">Sahihi ya Mwanafunzi:</span>
                    <div class="info-field"></div>
                </div>
            </div>
        </div>
        
        <!-- Instructions -->
        <div class="instructions">
            <div class="instructions-title">Maagizo</div>
            <ol class="instructions-list">
"""
        
        # Add instructions with bold formatting for specific words
        for instruction in instructions:
            # Bold specific words like "mbili", "lazima", etc.
            instruction_html = instruction
            instruction_html = instruction_html.replace('mbili', '<strong>mbili</strong>')
            instruction_html = instruction_html.replace('lazima', '<strong>lazima</strong>')
            instruction_html = instruction_html.replace('Karatasi hii', '<strong>Karatasi hii')
            instruction_html = instruction_html.replace('zilizopigwa chapa.', 'zilizopigwa chapa.</strong>')
            instruction_html = instruction_html.replace('Watahiniwa ni lazima', '<strong>Watahiniwa ni lazima')
            instruction_html = instruction_html.replace('maswali yote yamo.', 'maswali yote yamo.</strong>')
            
            html += f'                <li>{instruction_html}</li>\n'
        
        html += f"""
            </ol>
        </div>
        
        <!-- Marking Grid Section -->
        <div class="marking-section">
            <div class="marking-title">Kwa Matumizi ya Mtahini Pekee</div>
            {marking_grid_html}
        </div>
    </div>
</body>
</html>
"""
        
        return html
    
    @staticmethod
    def _generate_marking_grid(question_1_marks, question_2_4_marks, total_marks):
        """
        Generate marking grid HTML for Kiswahili Paper 1
        
        Based on screenshot, the grid structure is:
        - Question 1 (Compulsory): 20 marks
        - Choose ONE from Questions 2-4: 20 marks
        - Total (Jumla): 40 marks
        
        Args:
            question_1_marks (int): Marks for Question 1 (compulsory)
            question_2_4_marks (int): Marks for one question from 2-4
            total_marks (int): Total marks for the paper
        
        Returns:
            str: HTML for marking grid
        """
        
        grid_html = f"""
            <table class="marking-grid">
                <thead>
                    <tr>
                        <th>Swali</th>
                        <th>Upeo</th>
                        <th>Alama</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td class="question-cell">1</td>
                        <td class="marks-cell">{question_1_marks}</td>
                        <td class="answer-cell"></td>
                    </tr>
                    <tr>
                        <td class="question-cell"></td>
                        <td class="marks-cell">{question_2_4_marks}</td>
                        <td class="answer-cell"></td>
                    </tr>
                    <tr class="total-row">
                        <td>Jumla</td>
                        <td>{total_marks}</td>
                        <td></td>
                    </tr>
                </tbody>
            </table>
        """
        
        return grid_html
    
    @staticmethod
    def generate_default_coverpage_data(generated_paper, paper):
        """
        Generate default coverpage data for Kiswahili Paper 1
        
        Args:
            generated_paper: GeneratedPaper instance
            paper: Paper instance
        
        Returns:
            dict: Default coverpage data for Kiswahili Paper 1
        """
        # Generate paper name
        paper_name_upper = paper.name.upper()
        subject_name_upper = paper.subject.name.upper()
        
        if subject_name_upper in paper_name_upper:
            display_paper_name = paper_name_upper
        else:
            display_paper_name = f'{subject_name_upper} {paper_name_upper}'
        
        # Get metadata for question details
        metadata = getattr(generated_paper, 'metadata', {}) or {}
        question_1_marks = metadata.get('question_1_marks', 20)
        question_2_4_marks = metadata.get('question_2_4_marks', 20)
        
        # Calculate total pages
        total_pages = 12  # Standard for Kiswahili Paper 1
        
        return {
            'school_name': 'KITUO CHA MTIHANI',
            'school_logo': '/exam.png',
            'logo_position': 'center',
            'class_name': '',
            'exam_title': 'MTIHANI WA MWISHO WA MUHULA 2025',
            'paper_name': display_paper_name,
            'paper_type': 'Karatasi ya Kwanza',
            'question_1_marks': question_1_marks,
            'question_2_4_marks': question_2_4_marks,
            'total_marks': generated_paper.total_marks or 40,
            'time_allocation': format_time_allocation(paper.time_allocation),
            'total_pages': total_pages,
            'instructions': [
                'Andika jina lako na nambari yako ya mtihani katika nafasi ulizoachiwa hapa juu.',
                'Tia sahihi sasa uandike tarehe ya mtihani katika nafasi zilizoochiwa hapa juu.',
                'Andika insha mbili. Insha ya kwanza ni ya lazima.',
                'Kisha chagua insha nyingine moja kati ya hizo tatu zilizobakia.',
                'Kila insha isipungue maneno 450.',
                'Kila insha ina alama 20.',
                'Jibu maswali kwenye andikwe kwa lugha ya Kiswahili.',
                'Insha zote sharti zandikwe katika nafasi ulizoachibwa katika kijitabu hiki cha maswali.',
                'Karatasi hii ina kurasa 12 zilizopigwa chapa.',
                'Watahiniwa ni lazima wahakikishe kwamba kurasa zote za karatasi hii zimepigwa chapa sawasawa na kuwa maswali yote yamo.'
            ],
            'date': datetime.now().strftime('%Y-%m-%d'),
            'candidate_name_field': True,
            'candidate_number_field': True,
            'date_field': True
        }



class BusinessPaper1Coverpage:
    """
    Business Studies Paper 1 Coverpage Template
    - 25 questions (Questions 1-25)
    - Individual marking grid for each question
    """
    
    @staticmethod
    def generate_html(data):
        """
        Generate HTML for Business Studies Paper 1 coverpage
        
        Args:
            data (dict): Coverpage data with keys:
                - school_name: Name of the school
                - school_logo: Base64 encoded logo or URL
                - exam_title: e.g., "END TERM EXAMINATION 2025"
                - paper_name: e.g., "BUSINESS STUDIES PAPER 1"
                - total_marks: Total marks (default: 100)
                - time_allocation: Time in minutes
                - total_pages: Total pages
        
        Returns:
            str: HTML content for coverpage
        """
        
        # Extract data with defaults
        school_name = data.get('school_name', 'EXAMINATION CENTRE')
        school_logo = data.get('school_logo', '/exam.png')
        logo_position = data.get('logo_position', 'center')
        class_name = data.get('class_name', '')
        exam_title = data.get('exam_title', 'END TERM EXAMINATION 2025')
        paper_name = data.get('paper_name', 'BUSINESS STUDIES PAPER 1')
        
        total_marks = data.get('total_marks', 100)
        time_allocation = data.get('time_allocation', '2 HOURS 30 MINUTES')
        total_pages = data.get('total_pages', 16)
        
        instructions = data.get('instructions', [
            'Write your name and admission number in the spaces provided above.',
            'Sign and write the date of examination in the spaces provided above.',
            'Answer all the questions in the spaces provided in the question paper.',
            'Non-programmable silent electronic calculators may be used.',
            f'This paper consists of {total_pages} printed pages.',
            'Candidates should check the question paper to ascertain that all the pages are printed as indicated and that no questions are missing.',
            'Candidates should answer the questions in English.'
        ])
        
        exam_date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        show_name = data.get('candidate_name_field', True)
        show_number = data.get('candidate_number_field', True)
        show_date = data.get('date_field', True)
        
        # Generate marking grid for Business Paper 1 (25 questions)
        marking_grid_html = BusinessPaper1Coverpage._generate_marking_grid()
        
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
            font-size: 1.4rem;
            margin-bottom: 10px;
        }}
        
        .instructions ol {{
            margin-left: 20px;
            font-size: 1.2rem;
            line-height: 1.6;
        }}
        
        .instructions li {{
            margin-bottom: 4px;
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
        
        .question-label {{
            background-color: #f5f5f5;
            font-size: 10px;
        }}
        
        .marks-cell {{
            min-height: 35px;
            background-color: white;
        }}
        
        .total-marks-container {{
            margin-top: 15px;
            text-align: center;
        }}
        
        .total-marks-box {{
            display: inline-block;
            border: 2px solid black;
            padding: 10px 20px;
        }}
        
        .total-marks-label {{
            font-weight: bold;
            font-size: 12px;
            margin-right: 20px;
        }}
        
        .total-marks-field {{
            width: 80px;
            height: 30px;
            vertical-align: middle;
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
                <div class="info-row-grid">
                    {f'<div class="info-row-item"><span class="info-label">ADM NO:</span><div class="info-field"></div></div>' if show_number else ''}
                    <div class="info-row-item"><span class="info-label">CLASS:</span><div class="info-field"></div></div>
                </div>
                <div class="info-row-grid">
                    {f'<div class="info-row-item"><span class="info-label">DATE:</span><div class="info-field"></div></div>' if show_date else ''}
                    <div class="info-row-item"><span class="info-label">SIGNATURE:</span><div class="info-field"></div></div>
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
            # Make "all" and "This paper consists" bold
            is_bold = 'all' in instruction.lower() or 'this paper consists' in instruction.lower()
            class_attr = ' class="bold"' if is_bold else ''
            html += f'                <li style="counter-increment: list-counter;"{class_attr}>{instruction}</li>\n'
        
        html += f"""
            </ol>
        </div>
        
        <!-- Marking Grid -->
        <div class="marking-grid-container">
            <div class="grid-title">For Examiner's Use Only</div>
            {marking_grid_html}
            
            <!-- Total Marks Box -->
            <div class="total-marks-container">
                <div class="total-marks-box">
                    <span class="total-marks-label">TOTAL MARKS</span>
                    <span class="total-marks-field"></span>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""
        
        return html
    
    @staticmethod
    def _generate_marking_grid():
        """
        Generate marking grid HTML for Business Studies Paper 1
        
        Based on screenshot, the grid structure is:
        - Row 1: Questions 1-13 with empty cells for marks
        - Row 2: Questions 14-25 with empty cells for marks
        
        Returns:
            str: HTML for marking grid
        """
        
        grid_html = '<table class="marking-grid">\n'
        
        # Row 1: Question numbers 1-13
        grid_html += '    <tr>\n'
        grid_html += '        <td class="question-label">Question</td>\n'
        for i in range(1, 14):
            grid_html += f'        <td class="question-label">{i}</td>\n'
        grid_html += '    </tr>\n'
        
        # Row 2: Marks cells for questions 1-13
        grid_html += '    <tr>\n'
        grid_html += '        <td class="question-label">Marks</td>\n'
        for i in range(1, 14):
            grid_html += '        <td class="marks-cell"></td>\n'
        grid_html += '    </tr>\n'
        
        # Row 3: Question numbers 14-25
        grid_html += '    <tr>\n'
        grid_html += '        <td class="question-label">Question</td>\n'
        for i in range(14, 26):
            grid_html += f'        <td class="question-label">{i}</td>\n'
        grid_html += '    </tr>\n'
        
        # Row 4: Marks cells for questions 14-25
        grid_html += '    <tr>\n'
        grid_html += '        <td class="question-label">Marks</td>\n'
        for i in range(14, 26):
            grid_html += '        <td class="marks-cell"></td>\n'
        grid_html += '    </tr>\n'
        
        grid_html += '</table>\n'
        
        return grid_html
    
    @staticmethod
    def generate_default_coverpage_data(generated_paper, paper):
        """
        Generate default coverpage data for Business Studies Paper 1
        
        Args:
            generated_paper: GeneratedPaper instance
            paper: Paper instance
        
        Returns:
            dict: Default coverpage data for Business Paper 1
        """
        # Generate paper name
        paper_name_upper = paper.name.upper()
        subject_name_upper = paper.subject.name.upper()
        
        if subject_name_upper in paper_name_upper:
            display_paper_name = paper_name_upper
        else:
            display_paper_name = f'{subject_name_upper} {paper_name_upper}'
        
        # Get metadata for question details
        metadata = getattr(generated_paper, 'metadata', {}) or {}
        
        # Calculate total pages
        total_pages = 16  # Standard for Business Paper 1
        
        return {
            'school_name': 'EXAMINATION CENTRE',
            'school_logo': '/exam.png',
            'logo_position': 'center',
            'class_name': '',
            'exam_title': 'END TERM EXAMINATION 2025',
            'paper_name': display_paper_name,
            'paper_type': 'Paper 1',
            'total_marks': generated_paper.total_marks or 100,
            'time_allocation': format_time_allocation(paper.time_allocation),
            'total_pages': total_pages,
            'instructions': [
                'Write your name and admission number in the spaces provided above.',
                'Sign and write the date of examination in the spaces provided above.',
                'Answer all the questions in the spaces provided in the question paper.',
                'Non-programmable silent electronic calculators may be used.',
                f'This paper consists of {total_pages} printed pages.',
                'Candidates should check the question paper to ascertain that all the pages are printed as indicated and that no questions are missing.',
                'Candidates should answer the questions in English.'
            ],
            'date': datetime.now().strftime('%Y-%m-%d'),
            'candidate_name_field': True,
            'candidate_number_field': True,
            'date_field': True
        }



class BusinessPaper2Coverpage:
    """
    Business Studies Paper 2 Coverpage Template
    - 6 questions available
    - Students answer 5 out of 6
    - Each question: 20 marks
    - Total: 100 marks
    """
    
    @staticmethod
    def generate_html(data):
        """
        Generate HTML for Business Studies Paper 2 coverpage
        
        Args:
            data (dict): Coverpage data with keys:
                - school_name: Name of the school
                - school_logo: Base64 encoded logo or URL
                - exam_title: e.g., "END TERM EXAMINATION 2025"
                - paper_name: e.g., "BUSINESS STUDIES PAPER 2"
                - total_marks: Total marks (default: 100)
                - time_allocation: Time in minutes
                - total_pages: Total pages
        
        Returns:
            str: HTML content for coverpage
        """
        
        # Extract data with defaults
        school_name = data.get('school_name', 'EXAMINATION CENTRE')
        school_logo = data.get('school_logo', '/exam.png')
        logo_position = data.get('logo_position', 'center')
        class_name = data.get('class_name', '')
        exam_title = data.get('exam_title', 'END TERM EXAMINATION 2025')
        paper_name = data.get('paper_name', 'BUSINESS STUDIES PAPER 2')
        
        total_marks = data.get('total_marks', 100)
        time_allocation = data.get('time_allocation', '2 HOURS 30 MINUTES')
        total_pages = data.get('total_pages', 18)
        
        instructions = data.get('instructions', [
            'Write your name and admission number in the spaces provided above.',
            'Sign and write the date of examination in the spaces provided above.',
            f'This paper consists of six questions.',
            'Answer any five questions in the spaces provided after question 6.',
            'All questions carry equal marks.',
            'Non-programmable silent electronic calculators may be used.',
            f'This paper consists of {total_pages} printed pages.',
            'Candidates should check the question paper to ascertain that all the pages are printed as indicated and that no questions are missing.',
            'Candidates should answer the questions in English.'
        ])
        
        exam_date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        show_name = data.get('candidate_name_field', True)
        show_number = data.get('candidate_number_field', True)
        show_date = data.get('date_field', True)
        
        # Generate marking grid for Business Paper 2 (5 questions × 20 marks)
        marking_grid_html = BusinessPaper2Coverpage._generate_marking_grid()
        
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
            width: 60%;
            margin: 0 auto;
            border-collapse: collapse;
            border: 2px solid black;
        }}
        
        .marking-grid th,
        .marking-grid td {{
            border: 1px solid black;
            text-align: center;
            font-size: 12px;
            padding: 12px 8px;
        }}
        
        .marking-grid th {{
            background-color: #f0f0f0;
            font-weight: bold;
        }}
        
        .question-row {{
            height: 45px;
        }}
        
        .total-row {{
            background-color: #e0e0e0;
            font-weight: bold;
            font-size: 13px;
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
                <div class="info-row-grid">
                    {f'<div class="info-row-item"><span class="info-label">ADM NO:</span><div class="info-field"></div></div>' if show_number else ''}
                    <div class="info-row-item"><span class="info-label">CLASS:</span><div class="info-field"></div></div>
                </div>
                <div class="info-row-grid">
                    {f'<div class="info-row-item"><span class="info-label">DATE:</span><div class="info-field"></div></div>' if show_date else ''}
                    <div class="info-row-item"><span class="info-label">SIGNATURE:</span><div class="info-field"></div></div>
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
            # Make specific instructions bold
            is_bold = ('six questions' in instruction.lower() or 
                      'any five' in instruction.lower() or 
                      'all questions' in instruction.lower() or
                      'this paper consists' in instruction.lower())
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
    def _generate_marking_grid():
        """
        Generate marking grid HTML for Business Studies Paper 2
        
        Based on screenshot, the grid structure is:
        - Header row: Question | Maximum Score | Candidate's Score
        - 5 rows for the 5 questions answered (each 20 marks)
        - Total Score row: 100 marks
        
        Returns:
            str: HTML for marking grid
        """
        
        grid_html = """
            <table class="marking-grid">
                <thead>
                    <tr>
                        <th>Question</th>
                        <th>Maximum<br>Score</th>
                        <th>Candidate's<br>Score</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        # 5 question rows (student answers 5 out of 6 questions)
        for i in range(5):
            grid_html += """
                    <tr class="question-row">
                        <td></td>
                        <td>20</td>
                        <td></td>
                    </tr>
"""
        
        # Total Score row
        grid_html += """
                    <tr class="total-row">
                        <td>Total Score</td>
                        <td>100</td>
                        <td></td>
                    </tr>
                </tbody>
            </table>
        """
        
        return grid_html
    
    @staticmethod
    def generate_default_coverpage_data(generated_paper, paper):
        """
        Generate default coverpage data for Business Studies Paper 2
        
        Args:
            generated_paper: GeneratedPaper instance
            paper: Paper instance
        
        Returns:
            dict: Default coverpage data for Business Paper 2
        """
        # Generate paper name
        paper_name_upper = paper.name.upper()
        subject_name_upper = paper.subject.name.upper()
        
        if subject_name_upper in paper_name_upper:
            display_paper_name = paper_name_upper
        else:
            display_paper_name = f'{subject_name_upper} {paper_name_upper}'
        
        # Get metadata for question details
        metadata = getattr(generated_paper, 'metadata', {}) or {}
        
        # Calculate total pages
        total_pages = 18  # Standard for Business Paper 2
        
        return {
            'school_name': 'EXAMINATION CENTRE',
            'school_logo': '/exam.png',
            'logo_position': 'center',
            'class_name': '',
            'exam_title': 'END TERM EXAMINATION 2025',
            'paper_name': display_paper_name,
            'paper_type': 'Paper 2',
            'total_marks': generated_paper.total_marks or 100,
            'time_allocation': format_time_allocation(paper.time_allocation),
            'total_pages': total_pages,
            'instructions': [
                'Write your name and admission number in the spaces provided above.',
                'Sign and write the date of examination in the spaces provided above.',
                f'This paper consists of six questions.',
                'Answer any five questions in the spaces provided after question 6.',
                'All questions carry equal marks.',
                'Non-programmable silent electronic calculators may be used.',
                f'This paper consists of {total_pages} printed pages.',
                'Candidates should check the question paper to ascertain that all the pages are printed as indicated and that no questions are missing.',
                'Candidates should answer the questions in English.'
            ],
            'date': datetime.now().strftime('%Y-%m-%d'),
            'candidate_name_field': True,
            'candidate_number_field': True,
            'date_field': True
        }



class CREPaper1Coverpage:
    """
    Christian Religious Education Paper 1 Coverpage Template
    - 6 questions available
    - Students answer 5 out of 6
    - Each question: 20 marks
    - Total: 100 marks
    """
    
    @staticmethod
    def generate_html(data):
        """
        Generate HTML for CRE Paper 1 coverpage
        
        Args:
            data (dict): Coverpage data with keys:
                - school_name: Name of the school
                - school_logo: Base64 encoded logo or URL
                - exam_title: e.g., "END TERM EXAMINATION 2025"
                - paper_name: e.g., "CHRISTIAN RELIGIOUS EDUCATION PAPER 1"
                - total_marks: Total marks (default: 100)
                - time_allocation: Time in minutes
                - total_pages: Total pages
        
        Returns:
            str: HTML content for coverpage
        """
        
        # Extract data with defaults
        school_name = data.get('school_name', 'EXAMINATION CENTRE')
        school_logo = data.get('school_logo', '/exam.png')
        logo_position = data.get('logo_position', 'center')
        class_name = data.get('class_name', '')
        exam_title = data.get('exam_title', 'END TERM EXAMINATION 2025')
        paper_name = data.get('paper_name', 'CHRISTIAN RELIGIOUS EDUCATION PAPER 1')
        
        total_marks = data.get('total_marks', 100)
        time_allocation = data.get('time_allocation', '2 HOURS 30 MINUTES')
        total_pages = data.get('total_pages', 16)
        
        instructions = data.get('instructions', [
            'Write your name and admission number in the spaces provided above.',
            'Sign and write the date of examination in the spaces provided above.',
            f'This paper consists of six questions.',
            'Answer five questions in the spaces provided at the end of question 6.',
            'Each question carries 20 marks.',
            f'This paper consists of {total_pages} printed pages.',
            'Candidates should answer from the Atlas provided.',
            'Candidates should check the question paper to ascertain that all the pages are printed as indicated and that no questions are missing.',
            'Candidates should answer the questions in English.'
        ])
        
        exam_date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        show_name = data.get('candidate_name_field', True)
        show_number = data.get('candidate_number_field', True)
        show_date = data.get('date_field', True)
        
        # Generate marking grid for CRE Paper 1
        marking_grid_html = CREPaper1Coverpage._generate_marking_grid()
        
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
            padding: 2px 0px;
        }}
        
        /* Instructions Section */
        .instructions {{
            margin-bottom: 20px;
        }}
        
        .instructions-title {{
            font-weight: bold;
            font-size: 1.6rem;
            margin-bottom: 10px;
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
            width: 70%;
            margin: 0 auto;
            border-collapse: collapse;
            border: 2px solid black;
        }}
        
        .marking-grid th,
        .marking-grid td {{
            border: 1px solid black;
            text-align: center;
            font-size: 12px;
            padding: 10px 8px;
        }}
        
        .marking-grid th {{
            background-color: #f0f0f0;
            font-weight: bold;
        }}
        
        .question-row {{
            height: 40px;
        }}
        
        .score-row {{
            background-color: #f5f5f5;
            font-weight: bold;
            height: 40px;
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
                <div class="info-row-grid">
                    {f'<div class="info-row-item"><span class="info-label">ADM NO:</span><div class="info-field"></div></div>' if show_number else ''}
                    <div class="info-row-item"><span class="info-label">CLASS:</span><div class="info-field"></div></div>
                </div>
                <div class="info-row-grid">
                    {f'<div class="info-row-item"><span class="info-label">DATE:</span><div class="info-field"></div></div>' if show_date else ''}
                    <div class="info-row-item"><span class="info-label">SIGNATURE:</span><div class="info-field"></div></div>
                </div>
            </div>
        </div>
        
        <!-- Instructions -->
        <div class="instructions">
            <div class="instructions-title">Instructions to candidates</div>
            <ol style="font-style: italic; list-style: none; counter-reset: list-counter; margin-left: 20px;">
"""
        
        # Add instructions
        for idx, instruction in enumerate(instructions, 1):
            # Make specific instructions bold
            is_bold = ('six questions' in instruction.lower() or 
                      'answer five' in instruction.lower() or 
                      'each question carries' in instruction.lower() or
                      'this paper consists' in instruction.lower())
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
    def _generate_marking_grid():
        """
        Generate marking grid HTML for CRE Paper 1
        
        Based on screenshot, the grid structure is:
        - First row: "Question" header with 5 empty columns and "Candidate's Total Score"
        - Second row: "Candidate's Score" with 5 empty columns (for the 5 answered questions)
        
        Returns:
            str: HTML for marking grid
        """
        
        grid_html = """
            <table class="marking-grid">
                <thead>
                    <tr>
                        <th>Question</th>
                        <th></th>
                        <th></th>
                        <th></th>
                        <th></th>
                        <th></th>
                        <th>Candidate's<br>Total Score</th>
                    </tr>
                </thead>
                <tbody>
                    <tr class="score-row">
                        <td>Candidate's<br>Score</td>
                        <td></td>
                        <td></td>
                        <td></td>
                        <td></td>
                        <td></td>
                        <td></td>
                    </tr>
                </tbody>
            </table>
        """
        
        return grid_html
    
    @staticmethod
    def generate_default_coverpage_data(generated_paper, paper):
        """
        Generate default coverpage data for CRE Paper 1
        
        Args:
            generated_paper: GeneratedPaper instance
            paper: Paper instance
        
        Returns:
            dict: Default coverpage data for CRE Paper 1
        """
        # Generate paper name
        paper_name_upper = paper.name.upper()
        subject_name_upper = paper.subject.name.upper()
        
        if subject_name_upper in paper_name_upper:
            display_paper_name = paper_name_upper
        else:
            display_paper_name = f'{subject_name_upper} {paper_name_upper}'
        
        # Get metadata for question details
        metadata = getattr(generated_paper, 'metadata', {}) or {}
        
        # Calculate total pages
        total_pages = 16  # Standard for CRE Paper 1
        
        return {
            'school_name': 'EXAMINATION CENTRE',
            'school_logo': '/exam.png',
            'logo_position': 'center',
            'class_name': '',
            'exam_title': 'END TERM EXAMINATION 2025',
            'paper_name': display_paper_name,
            'paper_type': 'Paper 1',
            'total_marks': generated_paper.total_marks or 100,
            'time_allocation': format_time_allocation(paper.time_allocation),
            'total_pages': total_pages,
            'instructions': [
                'Write your name and admission number in the spaces provided above.',
                'Sign and write the date of examination in the spaces provided above.',
                f'This paper consists of six questions.',
                'Answer five questions in the spaces provided at the end of question 6.',
                'Each question carries 20 marks.',
                f'This paper consists of {total_pages} printed pages.',
                'Candidates should answer from the Atlas provided.',
                'Candidates should check the question paper to ascertain that all the pages are printed as indicated and that no questions are missing.',
                'Candidates should answer the questions in English.'
            ],
            'date': datetime.now().strftime('%Y-%m-%d'),
            'candidate_name_field': True,
            'candidate_number_field': True,
            'date_field': True
        }



class CREPaper2Coverpage:
    """
    Christian Religious Education Paper 2 Coverpage Template
    - 6 questions available
    - Students answer 5 out of 6
    - Each question: 20 marks
    - Total: 100 marks
    """
    
    @staticmethod
    def generate_html(data):
        """
        Generate HTML for CRE Paper 2 coverpage
        
        Args:
            data (dict): Coverpage data with keys:
                - school_name: Name of the school
                - school_logo: Base64 encoded logo or URL
                - exam_title: e.g., "END TERM EXAMINATION 2025"
                - paper_name: e.g., "CHRISTIAN RELIGIOUS EDUCATION PAPER 2"
                - total_marks: Total marks (default: 100)
                - time_allocation: Time in minutes
                - total_pages: Total pages
        
        Returns:
            str: HTML content for coverpage
        """
        
        # Extract data with defaults
        school_name = data.get('school_name', 'EXAMINATION CENTRE')
        school_logo = data.get('school_logo', '/exam.png')
        logo_position = data.get('logo_position', 'center')
        class_name = data.get('class_name', '')
        exam_title = data.get('exam_title', 'END TERM EXAMINATION 2025')
        paper_name = data.get('paper_name', 'CHRISTIAN RELIGIOUS EDUCATION PAPER 2')
        
        total_marks = data.get('total_marks', 100)
        time_allocation = data.get('time_allocation', '2 HOURS 30 MINUTES')
        total_pages = data.get('total_pages', 16)
        
        instructions = data.get('instructions', [
            'Write your name and admission number in the spaces provided above.',
            'Sign and write the date of examination in the spaces provided above.',
            f'This paper consists of six questions.',
            'Answer any five questions in the spaces provided at the end of question 6.',
            'Each question carries 20 marks.',
            f'This paper consists of {total_pages} printed pages.',
            'Do not remove any pages from this booklet.',
            'Candidates should check the question paper to ascertain that all the pages are printed as indicated and that no questions are missing.',
            'Candidates should answer the questions in English.'
        ])
        
        exam_date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        show_name = data.get('candidate_name_field', True)
        show_number = data.get('candidate_number_field', True)
        show_date = data.get('date_field', True)
        
        # Generate marking grid for CRE Paper 2
        marking_grid_html = CREPaper2Coverpage._generate_marking_grid()
        
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
            width: 70%;
            margin: 0 auto;
            border-collapse: collapse;
            border: 2px solid black;
        }}
        
        .marking-grid th,
        .marking-grid td {{
            border: 1px solid black;
            text-align: center;
            font-size: 12px;
            padding: 10px 8px;
        }}
        
        .marking-grid th {{
            background-color: #f0f0f0;
            font-weight: bold;
        }}
        
        .question-row {{
            height: 40px;
        }}
        
        .score-row {{
            background-color: #f5f5f5;
            font-weight: bold;
            height: 40px;
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
                <div class="info-row-grid">
                    {f'<div class="info-row-item"><span class="info-label">ADM NO:</span><div class="info-field"></div></div>' if show_number else ''}
                    <div class="info-row-item"><span class="info-label">CLASS:</span><div class="info-field"></div></div>
                </div>
                <div class="info-row-grid">
                    {f'<div class="info-row-item"><span class="info-label">DATE:</span><div class="info-field"></div></div>' if show_date else ''}
                    <div class="info-row-item"><span class="info-label">SIGNATURE:</span><div class="info-field"></div></div>
                </div>
            </div>
        </div>
        
        <!-- Instructions -->
        <div class="instructions">
            <div class="instructions-title">Instructions to candidates</div>
            <ol style="font-style: italic; list-style: none; counter-reset: list-counter; margin-left: 20px;">
"""
        
        # Add instructions
        for idx, instruction in enumerate(instructions, 1):
            # Make specific instructions bold
            is_bold = ('six questions' in instruction.lower() or 
                      'answer any five' in instruction.lower() or 
                      'each question carries' in instruction.lower() or
                      'this paper consists' in instruction.lower() or
                      'do not remove' in instruction.lower())
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
    def _generate_marking_grid():
        """
        Generate marking grid HTML for CRE Paper 2
        
        Based on screenshot, the grid structure is:
        - First row: "Question" header with 5 empty columns and "Candidate's Total Score"
        - Second row: "Candidate's Score" with 5 empty columns (for the 5 answered questions)
        
        Returns:
            str: HTML for marking grid
        """
        
        grid_html = """
            <table class="marking-grid">
                <thead>
                    <tr>
                        <th>Question</th>
                        <th></th>
                        <th></th>
                        <th></th>
                        <th></th>
                        <th></th>
                        <th>Candidate's<br>Total Score</th>
                    </tr>
                </thead>
                <tbody>
                    <tr class="score-row">
                        <td>Candidate's<br>Score</td>
                        <td></td>
                        <td></td>
                        <td></td>
                        <td></td>
                        <td></td>
                        <td></td>
                    </tr>
                </tbody>
            </table>
        """
        
        return grid_html
    
    @staticmethod
    def generate_default_coverpage_data(generated_paper, paper):
        """
        Generate default coverpage data for CRE Paper 2
        
        Args:
            generated_paper: GeneratedPaper instance
            paper: Paper instance
        
        Returns:
            dict: Default coverpage data for CRE Paper 2
        """
        # Generate paper name
        paper_name_upper = paper.name.upper()
        subject_name_upper = paper.subject.name.upper()
        
        if subject_name_upper in paper_name_upper:
            display_paper_name = paper_name_upper
        else:
            display_paper_name = f'{subject_name_upper} {paper_name_upper}'
        
        # Get metadata for question details
        metadata = getattr(generated_paper, 'metadata', {}) or {}
        
        # Calculate total pages
        total_pages = 16  # Standard for CRE Paper 2
        
        return {
            'school_name': 'EXAMINATION CENTRE',
            'school_logo': '/exam.png',
            'logo_position': 'center',
            'class_name': '',
            'exam_title': 'END TERM EXAMINATION 2025',
            'paper_name': display_paper_name,
            'paper_type': 'Paper 2',
            'total_marks': generated_paper.total_marks or 100,
            'time_allocation': format_time_allocation(paper.time_allocation),
            'total_pages': total_pages,
            'instructions': [
                'Write your name and admission number in the spaces provided above.',
                'Sign and write the date of examination in the spaces provided above.',
                f'This paper consists of six questions.',
                'Answer any five questions in the spaces provided at the end of question 6.',
                'Each question carries 20 marks.',
                f'This paper consists of {total_pages} printed pages.',
                'Do not remove any pages from this booklet.',
                'Candidates should check the question paper to ascertain that all the pages are printed as indicated and that no questions are missing.',
                'Candidates should answer the questions in English.'
            ],
            'date': datetime.now().strftime('%Y-%m-%d'),
            'candidate_name_field': True,
            'candidate_number_field': True,
            'date_field': True
        }

