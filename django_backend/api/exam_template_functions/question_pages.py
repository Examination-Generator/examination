from api.process_text import _process_question_text
from api.page_number_extrctor import extract_paper_number_from_name

def _generate_question_pages(questions, total_pages, coverpage_data=None):
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
        <div class="question" style="{question_wrapper_style} ">
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