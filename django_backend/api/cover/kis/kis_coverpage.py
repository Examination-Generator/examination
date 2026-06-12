from datetime import datetime
from api.cover.format_time import format_time_allocation


class KiswahiliPaper2Coverpage:
    
    @staticmethod
    def generate_html(data):
        
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
    
    @staticmethod
    def generate_html(data):
        
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
