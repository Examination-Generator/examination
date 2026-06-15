def _generate_physics_paper2_continuous_pages(questions, start_page, total_pages):
    questions_html = ""
    for q in questions:
        q_number = int(q.get('number', 0))
        if q_number == 1:
            questions_html += """
        <div class="question-flow physics-paper2" style="width:100%; max-width:210mm; margin-left:auto; margin-right:auto; text-align:left;">
            <div class="physics-section-a" style="width:100%; text-align:left;">
            <div class="simple-section-title" style="text-align: center;">SECTION A (25 MARKS)</div>
            <div class="section-instruction" style="text-align: center; font-style: italic;">Answer all questions in this section</div>
"""
        elif q_number == 14:
            # Close Section A container before starting Section B
            questions_html += """
            </div>
            <div class="physics-section-b" style="width:100%; text-align:left;">
            <div class="simple-section-title" style="text-align: center;">SECTION B (55 MARKS)</div>
            <div class="section-instruction" style="text-align: center; font-style: italic;">Answer all questions in this section</div>
"""

        processed_text = _process_question_text(
            q.get('text', ''),
            q.get('question_inline_images', []),
            q.get('question_answer_lines', [])
        )

        questions_html += f"""
        <div class="question" style="text-align: left !important;">
            <div class="question-text"><span class="question-number">{q['number']}.</span> {processed_text}</div>
        </div>
"""

    page_html = f"""
    <div class="exam-page page-break">
        {questions_html}
        <!-- close any open physics section container -->
        </div>
    </div>
"""

    return {
        'html': page_html,
        'next_page': start_page + 1
    }
