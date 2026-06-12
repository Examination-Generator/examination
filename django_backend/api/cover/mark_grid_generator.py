def generate_marking_table(total_questions):
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