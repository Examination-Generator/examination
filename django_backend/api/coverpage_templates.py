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
            'Write your name and index number in the spaces provided above.',
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
        marking_grid_html = BiologyPaper1Coverpage._generate_marking_grid(total_questions)
        
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
            grid-template-columns: 1fr 1fr;
            gap: 15px 20px;
        }}
        
        .info-row {{
            display: flex;
            align-items: center;
        }}
        
        .info-row-full {{
            grid-column: 1 / -1;
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
        
        /* Instructions Section */
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
            border: none !important;
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
            <div class="info-grid">
                {f'''
                <div class="info-row">
                    <div class="info-label">NAME:</div>
                    <div class="info-field"></div>
                </div>
                ''' if show_name else ''}
                
                {f'''
                <div class="info-row">
                    <div class="info-label">ADM NO:</div>
                    <div class="info-field"></div>
                </div>
                ''' if show_number else ''}
                
                <div class="info-row">
                    <div class="info-label">CLASS:</div>
                    <div class="info-field"></div>
                </div>
                
                {f'''
                <div class="info-row">
                    <div class="info-label">DATE:</div>
                    <div class="info-field"></div>
                </div>
                ''' if show_date else ''}
                
                <div class="info-row-full">
                    <div class="info-label">SIGNATURE:</div>
                    <div class="info-field"></div>
                </div>
            </div>
        </div>
        
        <!-- Instructions -->
        <div class="instructions">
            <div class="instructions-title">INSTRUCTIONS TO CANDIDATES</div>
            <ol>
                {''.join([f'<li class="{"bold" if idx >= 4 else ""}">{instruction}</li>' for idx, instruction in enumerate(instructions)])}
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
            second_row_html += '    <td class="empty-question-cell">&nbsp;</td>\n'
        
        # Add empty gap cell before Grand Total
        second_row_html += '    <td class="gap-cell">&nbsp;</td>\n'
        
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
            second_row_boxes += '    <td class="empty-question-cell">&nbsp;</td>\n'
        
        # Add empty gap cell (matching the one above)
        second_row_boxes += '    <td class="gap-cell">&nbsp;</td>\n'
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


# Example usage and testing
if __name__ == '__main__':
    # Test with different question counts
    test_cases = [
        {'total_questions': 18, 'name': '18 questions'},
        {'total_questions': 25, 'name': '25 questions'},
        {'total_questions': 15, 'name': '15 questions'},
        {'total_questions': 27, 'name': '27 questions (max)'},
    ]
    
    for test in test_cases:
        print(f"\n{'='*50}")
        print(f"Testing: {test['name']}")
        print(f"{'='*50}")
        
        sample_data = {
            'school_name': 'KENYA HIGH SCHOOL',
            'exam_title': 'END TERM 3 EXAMINATION 2025',
            'paper_name': 'BIOLOGY PAPER 1',
            'total_questions': test['total_questions'],
            'total_marks': 80,
            'time_allocation': 120,
        }
        
        html = BiologyPaper1Coverpage.generate_html(sample_data)
        
        # Save to file for visual inspection
        filename = f'biology_paper1_coverpage_{test["total_questions"]}q.html'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✓ Generated: {filename}")
    
    print(f"\n{'='*50}")
    print("All test files generated successfully!")
    print(f"{'='*50}")



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
        first_row_html += f'    <td style="min-width: 35px; width: 35px; border-right: 2px solid black; border-bottom: 2px solid black; padding: 5px;">{i}</td>\n'
    first_row_html += '</tr>\n'
    
    # Build first row (answer boxes)
    first_row_boxes = '<tr>\n'
    for i in range(first_row_count):
        first_row_boxes += '    <td style="min-width: 35px; width: 35px; border-right: 2px solid black; border-bottom: 2px solid black; padding: 5px;">&nbsp;</td>\n'
    first_row_boxes += '</tr>\n'
    
    # Build second row if needed
    second_row_html = ''
    second_row_boxes = ''
    
    # Always show second row (even if no questions)
    # Second row question numbers (with spacing)
    second_row_html = '<tr class="row-with-spacing" style="border-top: 2px solid black; padding-top: 8px;">\n'
    
    # Add question numbers for second row (17 onwards)
    for i in range(17, 17 + second_row_count):
        second_row_html += f'    <td style="min-width: 35px; width: 35px; border-right: 2px solid black; border-bottom: 2px solid black; padding: 5px;">{i}</td>\n'
    
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
        second_row_boxes += '    <td style="min-width: 35px; width: 35px;  border-right: 2px solid black; padding: 5px;">&nbsp;</td>\n'
    
    # Fill remaining answer boxes
    for i in range(remaining_cells):
        second_row_boxes += '    <td class="empty-question-cell" style="min-width: 35px; width: 35px;background-color: white; border: none !important;">&nbsp;</td>\n'
    
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
        
        # Generate marking grid (same as question paper)
        marking_grid = generate_marking_table(total_questions)
        
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
        
        /* Marking Grid Section - at bottom */
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
            border: none !important;
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
                {"".join([f"<li style=\"margin-bottom: 8px;\">{instruction}</li>" for instruction in instructions])}
            </ol>
        </div>
        
        <!-- Marking Grid Section - at bottom -->
        <div class="marking-grid-container" style="margin-top: auto; padding-top: 40px;">
            <div class="grid-title" style="font-weight: bold;">For Examiner's Use Only</div>
            {marking_grid}
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
        }