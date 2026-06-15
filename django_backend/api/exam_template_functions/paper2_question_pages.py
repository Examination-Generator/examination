from api.english_paper1_template import _generate_english_paper1_pages
from api.exam_template_functions.physics_con import _generate_physics_paper2_continuous_pages
from api.exam_template_functions.cre import _generate_cre_question_page
from api.exam_template_functions.section_pages import _generate_section_pages
from api.exam_template_functions.non_section_pages import _generate_non_sectioned_pages
from api.exam_template_functions.answer_lines import _generate_answer_lines_pages
from api.exam_template_functions.bio_pp2_flow import _generate_biology_paper2_flow


def _generate_paper2_question_pages(questions, total_pages, coverpage_data=None, answer_lines_pages=2):
    
    from api.page_number_extrctor import extract_paper_number_from_name
    
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