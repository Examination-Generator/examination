from api.process_text import _process_question_text

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