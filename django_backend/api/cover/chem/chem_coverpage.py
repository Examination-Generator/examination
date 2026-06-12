from datetime import datetime
from api.cover.format_time import format_time_allocation
from api.cover.bio.bio_coverpage import BiologyPaper1Coverpage


class ChemistryPaper2Coverpage:
    pass

class ChemistryPaper1Coverpage:
    """
    Chemistry Paper 1 Coverpage Template
    Includes dynamic marking grid based on question count (similar to Biology Paper 1)
    """
    
    @staticmethod
    def generate_html(data):
        
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
        from api.models import Question
        
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