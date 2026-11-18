import re
from html import escape
from urllib.parse import unquote


def _root_html(radicand_html, degree_html=''):
    """Radical sign drawn as an inline SVG check-mark that stretches with the content and joins the top bar."""
    degree = (
        '<span style="align-self:flex-start; font-size:0.6em; line-height:1; margin-right:-0.3em; '
        f'position:relative; top:0.2em;">{degree_html}</span>'
        if degree_html else ''
    )
    return (
        '<span style="display:inline-flex; align-items:stretch; vertical-align:middle; margin:0 2px;">'
        f'{degree}'
        '<span style="position:relative; flex:none; width:0.85em; margin-top:1px; min-height:1.1em;">'
        '<svg viewBox="0 0 12 100" preserveAspectRatio="none" aria-hidden="true" '
        'style="position:absolute; top:0; left:0; width:100%; height:100%; overflow:visible;">'
        '<polyline points="0,66 2.5,62 5.5,97 12,0" fill="none" stroke="#111" stroke-width="1.6" '
        'stroke-linejoin="miter" stroke-linecap="butt" vector-effect="non-scaling-stroke"/></svg></span>'
        f'<span style="border-top:2px solid #111; padding:1px 3px 0; min-width:0.8em;">{radicand_html}</span></span>'
    )


def render_root_token(part, render_inner=None):
    """Render [ROOT:encodedDegree|radicand] (blank degree = square root).

    The radicand may contain nested tokens, so it is formatted with ``render_inner``.
    """
    inner = part[6:-1]
    separator = inner.find('|')
    degree = unquote(inner[:separator]) if separator >= 0 else ''
    radicand = inner[separator + 1:] if separator >= 0 else inner
    fmt = render_inner or escape
    return _root_html(fmt(radicand), fmt(degree.strip()) if degree.strip() else '')


def render_sqrt_token(part, render_inner=None):
    """Render the older [SQRT:encodedEquation] token as a root with no degree."""
    fmt = render_inner or escape
    return _root_html(fmt(unquote(part[6:-1])))


def render_roots_in_html(content):
    """Render [ROOT:degree|..] and [SQRT:..] tokens left inside already-formatted fraction parts."""
    if not content:
        return content
    content = re.sub(
        r'\[ROOT:[^\]]*\]',
        lambda match: render_root_token(match.group(0), lambda value: value),
        content,
    )
    return re.sub(r'\[SQRT:(.*?)\]', lambda match: render_sqrt_token(match.group(0)), content)


def render_formula_token(part, render_inner=None):
    """Render [FORMULA:supBefore|subBefore|main|supAfter|subAfter|squareRoot|degree].

    Every field is formatted with ``render_inner`` so roots, fractions and
    sup/sub inside the scripts display. Returns None when malformed.
    """
    values = part[9:-1].split('|')
    if len(values) not in (5, 6, 7):
        return None
    fmt = render_inner or escape
    sup_before, sub_before, main, sup_after, sub_after = [fmt(unquote(v)) for v in values[:5]]
    square_root = len(values) >= 6 and unquote(values[5]) == 'true'
    degree = unquote(values[6]).strip() if len(values) == 7 else ''
    main_html = _root_html(main, fmt(degree) if degree else '') if square_root else f'<span>{main}</span>'
    side = (
        '<span style="display:inline-flex; flex-direction:column; justify-content:center; text-align:center; '
        'line-height:1; font-size:0.8em;"><sup>{}</sup><sub style="font-size:0.75em;">{}</sub></span>'
    )
    return (
        '<span style="display:inline-flex; align-items:center; vertical-align:middle;">'
        + side.format(sup_before, sub_before) + main_html + side.format(sup_after, sub_after) + '</span>'
    )


DEFAULT_SPACE_MM = 20
_SPACE_RE = re.compile(r'\[SPACE:([\d.]+)(?::([\d.]+)mm)?\]')
_COLUMNS_RE = re.compile(r'\[COLS:(\d+)(\|line)?\](.*?)\[/COLS\]', re.DOTALL)


def render_space_token(part):
    """Render [SPACE:id:50mm] as a blank block of exactly that many millimetres on paper.

    Older [SPACE:id] tokens carry no height and use the 20mm default.
    Returns None when the token is malformed.
    """
    match = _SPACE_RE.fullmatch(part)
    if not match:
        return None
    height = float(match.group(2)) if match.group(2) else DEFAULT_SPACE_MM
    height = max(5.0, min(300.0, height))
    height_text = f'{height:g}'
    return (
        f'<div class="working-space" style="width:100%; height:{height_text}mm; min-height:{height_text}mm; '
        'margin:0; background:white; border:none; break-inside:avoid; page-break-inside:avoid;"></div>'
    )


def render_with_columns(text, render):
    """Split text on [COLS:n|line] ... [COL] ... [/COLS] blocks.

    ``render`` formats a plain segment (and every individual column), so every
    other token (formulas, fractions, brackets, tables, images...) still works in a column.
    """
    output = []
    position = 0
    for match in _COLUMNS_RE.finditer(text):
        if match.start() > position:
            output.append(render(text[position:match.start()]))
        columns = [column.removeprefix('\n').removesuffix('\n') for column in match.group(3).split('[COL]')]
        columns += [''] * (int(match.group(1)) - len(columns))
        ruled = bool(match.group(2))
        cells = ''.join(
            '<div style="white-space:pre-wrap; overflow-wrap:anywhere; min-width:0;'
            + (' border-left:1px solid #111; padding-left:3mm; margin-left:-3mm;' if ruled and index else '')
            + f'">{render(column)}</div>'
            for index, column in enumerate(columns)
        )
        output.append(
            f'<div class="answer-columns" style="display:grid; grid-template-columns:repeat({len(columns)}, minmax(0, 1fr)); '
            f'column-gap:6mm; width:100%; align-items:start; margin:4px 0;">{cells}</div>'
        )
        position = match.end()
    if position < len(text):
        output.append(render(text[position:]))
    return ''.join(output)


def render_bracket_token(part, render_inner=None):
    """Render a [BRACKET:side|shape|height|encodedText] token as HTML.

    Mirrors the frontend renderer (renderTextWithImages.js): a scaled
    Times New Roman bracket glyph beside the text. ``render_inner`` formats the
    decoded text so nested formatting (fractions, sup/sub, bold...) renders too.
    Returns None when the token is malformed so callers can emit it unchanged.
    """
    try:
        side, shape, height_text, encoded_text = part[9:-1].split('|', 3)
        height = max(20, min(400, int(height_text)))
    except (ValueError, TypeError):
        return None
    decoded = unquote(encoded_text)
    inner = render_inner(decoded) if render_inner else escape(decoded)
    opening = side != 'closing'
    glyph = (
        ('{' if opening else '}') if shape == 'curly'
        else ('[' if opening else ']') if shape == 'square'
        else ('(' if opening else ')')
    )
    glyph_html = (
        f'<span style="font-family:\'Times New Roman\', serif; font-size:{height}px; '
        f'line-height:{height}px; font-weight:400;">{glyph}</span>'
    )
    return (
        f'<span style="display:inline-flex; align-items:stretch; min-height:{height}px; '
        'line-height:1.2; vertical-align:middle; margin:2px;">'
        f'{glyph_html if opening else ""}'
        f'<span style="display:inline-flex; align-items:center; text-align:left; padding:0 6px; '
        f'min-width:20px; white-space:pre-wrap; overflow-wrap:anywhere;">{inner}</span>'
        f'{"" if opening else glyph_html}</span>'
    )

def _process_question_text(text, images=None, answer_lines=None, image_positions=None):
    """
    Process question text to render images, answer lines, tables, matrices, fractions, 
    superscript, subscript, and other formatting with support for nested formatting
    """
    if not text:
        return ""

    # Answer columns: each segment/column is rendered by this same function, so all tokens work inside columns.
    if '[COLS:' in text and '[/COLS]' in text:
        return render_with_columns(text, lambda segment: _process_question_text(segment, images, answer_lines, image_positions))
    
    # Helper function to render nested formatting within fractions and other content
    def render_nested_format(content):
        """Process nested formatting like [SUP], [SUB], bold, italic, underline"""
        if not content:
            return content
        
        # Pattern to match nested formatting tags
        nested_pattern = r'(\[SUP\].*?\[/SUP\]|\[SUB\].*?\[/SUB\]|\*\*.*?\*\*|\*(?!\*)[^*]+?\*|__.*?__|_(?!_)[^_]+?_)'
        nested_parts = re.split(nested_pattern, content)
        
        nested_result = []
        for p in nested_parts:
            if not p:
                continue
            # Superscript
            if p.startswith('[SUP]') and p.endswith('[/SUP]'):
                nested_result.append(f'<sup style="font-size: 0.75em;">{p[5:-6]}</sup>')
            # Subscript
            elif p.startswith('[SUB]') and p.endswith('[/SUB]'):
                nested_result.append(f'<sub style="font-size: 0.75em;">{p[5:-6]}</sub>')
            # Bold
            elif p.startswith('**') and p.endswith('**') and len(p) > 4:
                nested_result.append(f'<strong>{p[2:-2]}</strong>')
            # Italic (single asterisk, not double)
            elif p.startswith('*') and p.endswith('*') and not p.startswith('**') and len(p) > 2:
                nested_result.append(f'<em>{p[1:-1]}</em>')
            # Underline (double underscore)
            elif p.startswith('__') and p.endswith('__') and len(p) > 4:
                nested_result.append(f'<u>{p[2:-2]}</u>')
            # Italic (single underscore)
            elif p.startswith('_') and p.endswith('_') and not p.startswith('__') and len(p) > 2:
                nested_result.append(f'<em>{p[1:-1]}</em>')
            else:
                nested_result.append(p)
        
        return ''.join(nested_result)

    def render_square_roots(content):
        return render_roots_in_html(content)

    # Create lookup dictionaries
    images_dict = {}
    if images:
        for img in images:
            images_dict[float(img.get('id', 0))] = img
    
    lines_dict = {}
    if answer_lines:
        for line in answer_lines:
            lines_dict[float(line.get('id', 0))] = line

    positions_dict = image_positions or {}
    
    # Enhanced pattern to include all formatting tags - using more specific patterns for fractions
    pattern = r'(\*\*.*?\*\*|\*.*?\*|__.*?__|_.*?_|\[SUP\].*?\[/SUP\]|\[SUB\].*?\[/SUB\]|\[FORMULA:[^\]]+\]|\[ROOT:(?:[^\[\]]|\[[^\]]+\])+\]|\[SQRT:[^\]]+\]|\[BRACKET:[^\]]+\]|\[FRAC:(?:[^:\[\]]|\[[^\]]+\])+:(?:[^:\[\]]|\[[^\]]+\])+\]|\[MIX:(?:[^:\[\]]|\[[^\]]+\])+:(?:[^:\[\]]|\[[^\]]+\])+:(?:[^:\[\]]|\[[^\]]+\])+\]|\[TABLE:(?:[^\[\]]|\[[^\]]+\])+\]|\[MATRIX:(?:[^\[\]]|\[[^\]]+\])+\]|\[GRAPH:[\d.]+:[\d.]+x[\d.]+cm\]|\[IMAGE:[\d.]+:(?:\d+x\d+|\d+)px\]|\[LINES:[\d.]+\]|\[SPACE:[\d.]+(?::[\d.]+mm)?\])'
    parts = re.split(pattern, text)
    
    result = []

    def render_inner(inner_text):
        return _process_question_text(inner_text, images, answer_lines, image_positions)

    def build_graph_html(graph_id, width_cm, height_cm):
        # Browser print often omits background graphics; SVG line art prints reliably.
        width_mm = max(10, int(round(width_cm * 10)))
        height_mm = max(10, int(round(height_cm * 10)))
        svg_lines = []

        for x in range(width_mm + 1):
            if x % 10 == 0:
                stroke = '#15803d'
                stroke_width = 0.45
            elif x % 5 == 0:
                stroke = '#16a34a'
                stroke_width = 0.28
            else:
                stroke = '#86efac'
                stroke_width = 0.18
            svg_lines.append(
                f'<line x1="{x}" y1="0" x2="{x}" y2="{height_mm}" stroke="{stroke}" stroke-width="{stroke_width}" />'
            )

        for y in range(height_mm + 1):
            if y % 10 == 0:
                stroke = '#15803d'
                stroke_width = 0.45
            elif y % 5 == 0:
                stroke = '#16a34a'
                stroke_width = 0.28
            else:
                stroke = '#86efac'
                stroke_width = 0.18
            svg_lines.append(
                f'<line x1="0" y1="{y}" x2="{width_mm}" y2="{y}" stroke="{stroke}" stroke-width="{stroke_width}" />'
            )

        svg_content = ''.join(svg_lines)
        return (
            '<span style="display:inline-block; margin:8px 4px; vertical-align:middle;">'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width_cm}cm" height="{height_cm}cm" '
            f'viewBox="0 0 {width_mm} {height_mm}" preserveAspectRatio="none" '
            f'style="display:block; background:#fff; border:2px solid #15803d; border-radius:4px; box-sizing:border-box; print-color-adjust:exact; -webkit-print-color-adjust:exact;">'
            f'<rect x="0" y="0" width="{width_mm}" height="{height_mm}" fill="#ffffff" />'
            f'{svg_content}'
            f'<rect x="0" y="0" width="{width_mm}" height="{height_mm}" fill="none" stroke="#15803d" stroke-width="0.5" />'
            '</svg>'
            '</span>'
        )
    
    for part in parts:
        if not part:
            continue
        
        # Table: [TABLE:RxC:data] or [TABLE:RxC:data:W:widths:H:heights:M:merged]
        if part.startswith('[TABLE:') and part.endswith(']'):
            try:
                inner = part[7:-1]  # Remove [TABLE: and ]
                parts_list = inner.split(':')
                dimension_match = re.match(r'(\d+)x(\d+)', parts_list[0])
                if dimension_match:
                    rows = int(dimension_match.group(1))
                    cols = int(dimension_match.group(2))
                    cell_data = parts_list[1].split('|') if len(parts_list) > 1 else []
                    
                    # Parse optional widths, heights, and merged cells
                    col_widths = [60] * cols
                    row_heights = [30] * rows
                    merged_cells = {}
                    
                    # Look for width data (W:width1,width2,...)
                    try:
                        width_index = parts_list.index('W')
                        if width_index != -1 and len(parts_list) > width_index + 1:
                            col_widths = [int(w) or 60 for w in parts_list[width_index + 1].split(',')]
                    except (ValueError, IndexError):
                        pass
                    
                    # Look for height data (H:height1,height2,...)
                    try:
                        height_index = parts_list.index('H')
                        if height_index != -1 and len(parts_list) > height_index + 1:
                            row_heights = [int(h) or 30 for h in parts_list[height_index + 1].split(',')]
                    except (ValueError, IndexError):
                        pass
                    
                    # Look for merged cell data (M:r,c,colspan,rowspan;...)
                    try:
                        merge_index = parts_list.index('M')
                        if merge_index != -1 and len(parts_list) > merge_index + 1:
                            merge_data = parts_list[merge_index + 1].split(';')
                            for m in merge_data:
                                cell_info = m.split(',')
                                if len(cell_info) == 4:
                                    r, c, colspan, rowspan = map(int, cell_info)
                                    if r not in merged_cells:
                                        merged_cells[r] = {}
                                    merged_cells[r][c] = {'colspan': colspan, 'rowspan': rowspan}
                    except (ValueError, IndexError):
                        pass
                    
                    # Helper to check if cell should be skipped (part of merged cell)
                    def is_cell_merged(row_idx, col_idx):
                        for r in range(row_idx + 1):
                            for c in range(col_idx + 1):
                                if r in merged_cells and c in merged_cells[r]:
                                    cell = merged_cells[r][c]
                                    colspan = cell.get('colspan', 1)
                                    rowspan = cell.get('rowspan', 1)
                                    end_row = r + rowspan - 1
                                    end_col = c + colspan - 1
                                    
                                    if (row_idx >= r and row_idx <= end_row and 
                                        col_idx >= c and col_idx <= end_col):
                                        # This cell is within a merged cell's span
                                        if r == row_idx and c == col_idx:
                                            return False  # This is the origin cell
                                        return True  # This cell should be skipped
                        return False
                    
                    # Build HTML table
                    table_html = '<table style="border: 1px solid #000; border-collapse: collapse; margin: 8px 0; display: inline-table;"><tbody>'
                    
                    for row_idx in range(rows):
                        table_html += '<tr>'
                        for col_idx in range(cols):
                            # Skip cells that are part of a merged cell
                            if is_cell_merged(row_idx, col_idx):
                                continue
                            
                            cell_index = row_idx * cols + col_idx
                            cell_value = cell_data[cell_index] if cell_index < len(cell_data) else ''
                            # Process nested formatting in table cells
                            cell_html = render_nested_format(cell_value) if cell_value else '&nbsp;'
                            width = col_widths[col_idx] if col_idx < len(col_widths) else 60
                            height = row_heights[row_idx] if row_idx < len(row_heights) else 30
                            
                            # Check if this cell is the origin of a merged cell
                            merge_info = merged_cells.get(row_idx, {}).get(col_idx, {'colspan': 1, 'rowspan': 1})
                            colspan = merge_info.get('colspan', 1)
                            rowspan = merge_info.get('rowspan', 1)
                            
                            colspan_attr = f' colspan="{colspan}"' if colspan > 1 else ''
                            rowspan_attr = f' rowspan="{rowspan}"' if rowspan > 1 else ''
                            
                            table_html += f'<td{colspan_attr}{rowspan_attr} style="border: 1px solid #000; padding: 8px; width: {width}px; height: {height}px; min-width: 60px; min-height: 30px;">{cell_html}</td>'
                        table_html += '</tr>'
                    
                    table_html += '</tbody></table>'
                    result.append(table_html)
                    continue
            except Exception:
                result.append(part)
                continue
        
        # Matrix: [MATRIX:RxC:data] - with support for nested formatting in cells
        if part.startswith('[MATRIX:') and part.endswith(']'):
            try:
                inner = part[8:-1]  # Remove [MATRIX: and ]
                parts_list = inner.split(':')
                dimension_match = re.match(r'(\d+)x(\d+)', parts_list[0])
                if dimension_match:
                    rows = int(dimension_match.group(1))
                    cols = int(dimension_match.group(2))
                    cell_data = parts_list[1].split('|') if len(parts_list) > 1 else []
                    
                    # Build HTML matrix with brackets
                    matrix_html = '<span style="display:inline-flex; align-items:stretch; margin:8px 6px; font-size:1.2em; min-height:40px;">'
                    matrix_html += '<span style="width:14px; border-left:3px solid #111; border-top:3px solid #111; border-bottom:3px solid #111; border-radius:8px 0 0 8px; align-self:stretch;"></span>'
                    matrix_html += '<table style="border-collapse:collapse; margin:4px 6px; table-layout:fixed;"><tbody>'
                    
                    for row_idx in range(rows):
                        matrix_html += '<tr>'
                        for col_idx in range(cols):
                            cell_index = row_idx * cols + col_idx
                            cell_value = cell_data[cell_index] if cell_index < len(cell_data) else ''
                            # Process nested formatting in matrix cells
                            cell_html = render_nested_format(cell_value) if cell_value else '&nbsp;'
                            matrix_html += f'<td style="padding:4px 8px; text-align:center; min-width:40px; height:32px; vertical-align:middle; white-space:nowrap;">{cell_html}</td>'
                        matrix_html += '</tr>'
                    
                    matrix_html += '</tbody></table>'
                    matrix_html += '<span style="width:14px; border-right:3px solid #111; border-top:3px solid #111; border-bottom:3px solid #111; border-radius:0 8px 8px 0; align-self:stretch;"></span>'
                    matrix_html += '</span>'
                    result.append(matrix_html)
                    continue
            except Exception:
                result.append(part)
                continue
        
        # Fraction: [FRAC:num:den] - with support for nested formatting
        if part.startswith('[FRAC:') and part.endswith(']'):
            try:
                inner = part[6:-1]
                # Find the colon that separates numerator and denominator
                # Handle nested brackets within numerator/denominator
                colon_idx = -1
                bracket_depth = 0
                for i, char in enumerate(inner):
                    if char == '[':
                        bracket_depth += 1
                    elif char == ']':
                        bracket_depth -= 1
                    elif char == ':' and bracket_depth == 0:
                        colon_idx = i
                        break
                
                if colon_idx != -1:
                    num = inner[:colon_idx]
                    den = inner[colon_idx + 1:]
                else:
                    num = inner
                    den = ''
                
                # Process nested formatting in numerator and denominator
                num_html = render_nested_format(num)
                den_html = render_nested_format(den)
                num_html = render_square_roots(num_html)
                den_html = render_square_roots(den_html)
                
                frac_html = f'<span style="display: inline-block; vertical-align: middle; text-align: center; line-height: 1;"><span style="display: block; font-size: 0.85em;">{num_html}</span><span style="display: block; border-top: 1px solid; padding-top: 1px; font-size: 0.85em;">{den_html}</span></span>'
                result.append(frac_html)
                continue
            except Exception:
                result.append(part)
                continue
        
        # Mixed fraction: [MIX:whole:num:den] - with support for nested formatting
        if part.startswith('[MIX:') and part.endswith(']'):
            try:
                inner = part[5:-1]
                # Parse with support for nested brackets
                colon_positions = []
                bracket_depth = 0
                for i, char in enumerate(inner):
                    if char == '[':
                        bracket_depth += 1
                    elif char == ']':
                        bracket_depth -= 1
                    elif char == ':' and bracket_depth == 0:
                        colon_positions.append(i)
                
                if len(colon_positions) >= 2:
                    whole = inner[:colon_positions[0]]
                    num = inner[colon_positions[0] + 1:colon_positions[1]]
                    den = inner[colon_positions[1] + 1:]
                else:
                    whole = inner
                    num = ''
                    den = ''
                
                # Process nested formatting
                whole_html = render_nested_format(whole)
                num_html = render_nested_format(num)
                den_html = render_nested_format(den)
                num_html = render_square_roots(num_html)
                den_html = render_square_roots(den_html)
                
                mix_html = f'<span style="display: inline-flex; align-items: center; gap: 4px;"><span style="font-size: 0.95em;">{whole_html}</span><span style="display: inline-block; vertical-align: middle; text-align: center; line-height: 1;"><span style="display: block; font-size: 0.85em;">{num_html}</span><span style="display: block; border-top: 1px solid; padding-top: 1px; font-size: 0.85em;">{den_html}</span></span></span>'
                result.append(mix_html)
                continue
            except Exception:
                result.append(part)
                continue
        
        # Superscript: [SUP]content[/SUP]
        if part.startswith('[SUP]') and part.endswith('[/SUP]'):
            content = part[5:-6]
            result.append(f'<sup style="font-size: 0.75em;">{content}</sup>')
            continue
            
        # Subscript: [SUB]content[/SUB]
        if part.startswith('[SUB]') and part.endswith('[/SUB]'):
            content = part[5:-6]
            result.append(f'<sub style="font-size: 0.75em;">{content}</sub>')
            continue

        # Formula, root and square-root tokens (nested tokens inside are rendered recursively)
        if part.startswith('[FORMULA:') and part.endswith(']'):
            formula_html = render_formula_token(part, render_inner)
            result.append(formula_html if formula_html is not None else part)
            continue

        if part.startswith('[ROOT:') and part.endswith(']'):
            result.append(render_root_token(part, render_inner))
            continue

        if part.startswith('[SQRT:') and part.endswith(']'):
            result.append(render_sqrt_token(part, render_inner))
            continue

        if part.startswith('[BRACKET:') and part.endswith(']'):
            bracket_html = render_bracket_token(
                part, render_inner
            )
            result.append(bracket_html if bracket_html is not None else part)
            continue

        # Bold: **text**
        if part.startswith('**') and part.endswith('**') and len(part) > 4:
            content = part[2:-2]
            result.append(f'<strong>{content}</strong>')
            continue
            
        # Italic: *text* (not **)
        if part.startswith('*') and part.endswith('*') and not part.startswith('**') and len(part) > 2:
            content = part[1:-1]
            result.append(f'<em>{content}</em>')
            continue
            
        # Underline: __text__
        if part.startswith('__') and part.endswith('__') and len(part) > 4:
            content = part[2:-2]
            result.append(f'<u>{content}</u>')
            continue
            
        # Single underscore italic: _text_
        if part.startswith('_') and part.endswith('_') and not part.startswith('__') and len(part) > 2:
            content = part[1:-1]
            result.append(f'<em>{content}</em>')
            continue
            
        # Answer lines: [LINES:id]
        elif part.startswith('[LINES:') and part.endswith(']'):
            line_match = re.match(r'\[LINES:([\d.]+)\]', part)
            if line_match:
                line_id = float(line_match.group(1))
                line_config = lines_dict.get(line_id)
                
                if line_config:
                    num_lines = line_config.get('numberOfLines', 5)
                    line_height = line_config.get('lineHeight', 30)
                    line_style = line_config.get('lineStyle', 'dotted')
                    opacity = line_config.get('opacity', 0.5)
                    
                    full_lines = int(num_lines)
                    has_half_line = (num_lines % 1) != 0
                    
                    lines_html = '<div class="answer-lines">'
                    
                    # Full lines
                    for _ in range(full_lines):
                        lines_html += f'<div class="answer-line {line_style}" style="height: {line_height}px; border-bottom: 2px {line_style} rgba(0, 0, 0, {opacity});"></div>'
                    
                    # Half line if needed
                    if has_half_line:
                        half_height = line_height / 2
                        lines_html += f'<div class="answer-line {line_style}" style="height: {half_height}px; border-bottom: 2px {line_style} rgba(0, 0, 0, {opacity});"></div>'
                    
                    lines_html += '</div>'
                    result.append(lines_html)
                else:
                    result.append(f'<div style="margin: 10px 0; padding: 10px; background: #fff3cd; border: 1px solid #ffc107; border-radius: 4px; font-size: 11pt;"> Answer Lines (ID: {int(line_id)})</div>')
        
        # Working space: [SPACE:id:HEIGHTmm] (old [SPACE:id] = 20mm)
        elif part.startswith('[SPACE:') and part.endswith(']'):
            space_html = render_space_token(part)
            result.append(space_html if space_html is not None else part)


        # Graphs: [GRAPH:id:WxHcm]
        elif part.startswith('[GRAPH:') and part.endswith(']'):
            graph_match = re.match(r'\[GRAPH:([\d.]+):([\d.]+)x([\d.]+)cm\]', part)
            if graph_match:
                graph_id = float(graph_match.group(1))
                width_cm = float(graph_match.group(2))
                height_cm = float(graph_match.group(3))
                
                # Validate dimensions
                width_cm = max(1, width_cm)
                height_cm = max(1, height_cm)
                result.append(build_graph_html(graph_id, width_cm, height_cm))
        
        # Images: [IMAGE:id:WxH] or [IMAGE:id:Wpx]
        elif part.startswith('[IMAGE:') and part.endswith('px]'):
            image_match_new = re.match(r'\[IMAGE:([\d.]+):(\d+)x(\d+)px\]', part)
            image_match_old = re.match(r'\[IMAGE:([\d.]+):(\d+)px\]', part)
            
            if image_match_new or image_match_old:
                if image_match_new:
                    image_id = float(image_match_new.group(1))
                    image_width = int(image_match_new.group(2))
                    image_height = int(image_match_new.group(3))
                else:
                    image_id = float(image_match_old.group(1))
                    image_width = int(image_match_old.group(2))
                    image_height = None
                
                image = images_dict.get(image_id)
                
                if image and image.get('url'):
                    img_url = image['url']
                    img_alt = image.get('name', 'Question image')
                    
                    style = f"width: {image_width}px;"
                    if image_height:
                        style += f" height: {image_height}px;"
                    position = positions_dict.get(str(image_id)) or positions_dict.get(int(image_id))
                    if position:
                        try:
                            x = max(0, float(position.get('x', 0)))
                            y = max(0, float(position.get('y', 0)))
                            result.append(
                                f'<span style="position:absolute; left:{x}px; top:{y}px;">'
                                f'<img src="{img_url}" alt="{escape(str(img_alt))}" class="question-image" style="{style}" />'
                                '</span>'
                            )
                        except (TypeError, ValueError, AttributeError):
                            result.append(
                                f'<img src="{img_url}" alt="{escape(str(img_alt))}" class="question-image" '
                                f'style="{style} display:block; max-width:100%; margin:8px 0;" />'
                            )
                    else:
                        result.append(
                            f'<img src="{img_url}" alt="{escape(str(img_alt))}" class="question-image" '
                            f'style="{style} display:block; max-width:100%; margin:8px 0;" />'
                        )
                else:
                    result.append(f'<div style="margin: 10px 0; padding: 10px; background: #f8d7da; border: 1px solid #dc3545; border-radius: 4px; font-size: 11pt;">❌ Image Not Found (ID: {int(image_id)})</div>')
        
        # Regular text
        else:
            result.append(escape(part))
    
    return ''.join(result)
