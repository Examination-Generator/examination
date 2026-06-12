
from api.cover.format_time import format_time_allocation
from datetime import datetime

class BusinessPaper1Coverpage:
    
    @staticmethod
    def generate_html(data):        
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
    
    @staticmethod
    def generate_html(data):
        
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
